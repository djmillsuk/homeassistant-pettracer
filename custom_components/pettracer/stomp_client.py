"""Simple STOMP over SockJS client for PetTracer."""
from __future__ import annotations

import asyncio
import json
import logging
import random
import string
import time
from typing import Callable, Any

import aiohttp
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger("custom_components.pettracer")

class StompClient:
    """STOMP over SockJS client."""

    def __init__(
        self,
        hass: HomeAssistant,
        ws_url: str,
        access_token: str,
        device_ids: list[int] | None,  # Properly type hint optional
        callback: Callable[[dict[str, Any]], None],
    ) -> None:
        """Initialize the client."""
        self.hass = hass
        self.ws_url = ws_url
        self.access_token = access_token
        self.device_ids = device_ids or []  # Handle None/Optional
        self.callback = callback
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._running = False
        self._connected = False
        self._reconnect_task: asyncio.Task | None = None

    def update_token(self, access_token: str) -> None:
        """Update the access token."""
        self.access_token = access_token
        # If running, maybe trigger reconnect?
        # For now let the next reconnect cycle pick it up or force it
        if self._running and self._connected:
             # Force reconnect logic here is complex without blocking loop
             pass

    async def start(self) -> None:
        """Start the client."""
        _LOGGER.debug("StompClient.start() called - spawning connection loop")
        self._running = True
        self._reconnect_task = self.hass.loop.create_task(self._connect_loop())

    async def stop(self) -> None:
        """Stop the client."""
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

    def _generate_session_id(self) -> str:
        """Generate a random 8-character string for SockJS session ID."""
        return "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )

    def _generate_server_id(self) -> str:
        """Generate a random 3-digit server ID."""
        return f"{random.randint(0, 999):03d}"

    async def _connect_loop(self) -> None:
        """Maintain the WebSocket connection."""
        _LOGGER.debug("Entering _connect_loop")
        while self._running:
            try:
                session_id = self._generate_session_id()
                server_id = self._generate_server_id()
                # Construct SockJS URL
                # Format: {base_url}/{server_id}/{session_id}/websocket
                url = f"{self.ws_url}/{server_id}/{session_id}/websocket?access_token={self.access_token}"

                _LOGGER.info("Connecting to WebSocket: %s", url)
                
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(url, heartbeat=30) as ws:
                        self._ws = ws
                        self._connected = True
                        _LOGGER.info("WebSocket connected")

                        # Handle messages
                        async for msg in ws:
                            if not self._running:
                                _LOGGER.debug("Unhandled message received after stop signal, ignoring")
                                break

                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self._handle_message(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                _LOGGER.error("WebSocket error: %s", msg.data)
                                break
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                _LOGGER.debug("CLOSED message received")
                                break

            except Exception as err:
                _LOGGER.error("WebSocket connection error: %s", err)

            self._connected = False
            if self._running:
                _LOGGER.debug("Reconnecting WebSocket in 10 seconds...")
                await asyncio.sleep(10)

    async def _handle_message(self, data: str) -> None:
        """Handle incoming WebSocket message."""
        if not data:
            return

        # SockJS protocol
        # o: Open frame
        # h: Heartbeat
        # a: Array of messages
        # c: Close frame

        frame_type = data[0]
        
        if frame_type == "o":
            _LOGGER.debug("SockJS Open Frame received")
            # connection opened, send STOMP CONNECT
            await self._send_stomp_connect()
        elif frame_type == "h":
            # Heartbeat, ignore
            # _LOGGER.debug("SockJS Heartbeat")
            pass
        elif frame_type == "a":
            _LOGGER.debug("SockJS Message Array received: %s", data[:100] + "..." if len(data) > 100 else data)
            # Message array
            try:
                messages = json.loads(data[1:])
                for msg in messages:
                    await self._handle_stomp_message(msg)
            except json.JSONDecodeError:
                _LOGGER.error("Failed to decode SockJS message: %s", data)
        elif frame_type == "c":
            # Close frame
            _LOGGER.info("SockJS close frame received: %s", data)

    async def _heartbeat_sender(self) -> None:
        """Send periodic STOMP heartbeats."""
        try:
            while self._running and self._connected:
                await asyncio.sleep(9)  # Send slightly faster than 10s timeout
                if self._ws and not self._ws.closed:
                     # Send STOMP heartbeat (newline char) wrapped in SockJS frame
                     # Use compact separators to match JS JSON.stringify behavior
                     heartbeat_frame = json.dumps(["\n"], separators=(",", ":"))
                     try:
                        await self._ws.send_str(heartbeat_frame)
                     except Exception as e:
                        _LOGGER.debug("Failed to send heartbeat: %s", e)
                        break
        except asyncio.CancelledError:
            pass

    async def _send_stomp_connect(self) -> None:
        """Send STOMP CONNECT frame."""
        # STOMP CONNECT frame
        connect_frame = (
            "CONNECT\n"
            "accept-version:1.1,1.0\n"
            "heart-beat:10000,10000\n"
            "\n"
            "\u0000"
        )
        await self._send_sockjs_message(connect_frame)

    async def _handle_stomp_message(self, msg: str) -> None:
        """Handle STOMP message content."""
        # STOMP heartbeats are often just a newline character
        if not msg or msg == "\n" or msg == "\r\n":
            # _LOGGER.debug("Received STOMP Heartbeat")
            return

        # Handle multiple STOMP frames in a single message (if they are concatenated)
        # Split by NULL byte
        frames = msg.split("\u0000")
        
        for frame in frames:
            frame = frame.strip()
            if not frame:
                continue
                
            if frame.startswith("CONNECTED"):
                _LOGGER.info("STOMP CONNECTED - Frame received")
                self._connected = True
                # Subscribe after connection
                await self._send_stomp_subscribe()
                # Start heartbeat sender task if negotiated
                self.hass.loop.create_task(self._heartbeat_sender())
            elif frame.startswith("MESSAGE"):
                _LOGGER.debug("Received STOMP MESSAGE frame")
                # Parse MESSAGE frame to extract body
                try:
                    # Find the first occurrence of double newline which separates headers from body
                    body_start = frame.find("\n\n")
                    if body_start != -1:
                        # +2 for the two newlines
                        body = frame[body_start + 2:]
                        
                        if body:
                            _LOGGER.debug("STOMP body found, parsing JSON")
                            try:
                                json_body = json.loads(body)
                                _LOGGER.debug("STOMP message parsed: %s", json_body)
                                
                                # Ensure callback is called on the loop
                                if self.hass and self.hass.loop and self.hass.loop.is_running():
                                     self.hass.loop.call_soon(self.callback, json_body)
                                else:
                                     self.callback(json_body)
                            except json.JSONDecodeError:
                                # Sometimes body is not JSON or is a partial fragment
                                _LOGGER.debug("STOMP body not JSON: %s", body)
                        else:
                            _LOGGER.warning("STOMP message empty body")
                    else:
                        _LOGGER.warning("STOMP message no header separator")
                except Exception as err:
                    _LOGGER.error("Error parsing STOMP frame: %s", err)
            else:
                 _LOGGER.debug("Received other STOMP frame type: %s...", frame[:20])

    async def _send_stomp_subscribe(self) -> None:
        """Send STOMP SUBSCRIBE frame."""
        _LOGGER.debug("Sending STOMP SUBSCRIBE frame")
        
        # Subscribe to message queue
        subscribe_frame_0 = (
            "SUBSCRIBE\n"
            "id:sub-0\n"
            "destination:/user/queue/messages\n"
            "\n"
            "\u0000"
        )
        await self._send_sockjs_message(subscribe_frame_0)

        # Subscribe to portal queue as seen in browser logs
        subscribe_frame_1 = (
            "SUBSCRIBE\n"
            "id:sub-1\n"
            "destination:/user/queue/portal\n"
            "\n"
            "\u0000"
        )
        await self._send_sockjs_message(subscribe_frame_1)
        
        if self.device_ids:
             # Browser sends: {"deviceIds":[12345,67890]}
             # The key is deviceIds string, value is array of ints
             payload = json.dumps({"deviceIds": self.device_ids}, separators=(",", ":"))
             send_frame = (
                 "SEND\n"
                 "destination:/app/subscribe\n"
                 f"content-length:{len(payload)}\n"
                 "\n"
                 f"{payload}"
                 "\u0000"
             )
             _LOGGER.info("Sending device subscription to /app/subscribe with payload: %s", payload)
             await self._send_sockjs_message(send_frame)

    async def _send_sockjs_message(self, message: str) -> None:
        """Wrap message in SockJS array and send."""
        if self._ws and not self._ws.closed:
            _LOGGER.debug("Sending SockJS message: %s", message)
            # Use compact separators to match JS JSON.stringify behavior
            sockjs_frame = json.dumps([message], separators=(",", ":"))
            await self._ws.send_str(sockjs_frame)
