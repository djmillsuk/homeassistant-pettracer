# PetTracer Home Assistant Integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=djmillsuk&repository=homeassistant-pettracer&category=integration)

A custom component for Home Assistant to integrate the PetTracer GPS cat tracking system.

## Features
* **Device Tracker**: GPS location updates for your pets.
* **Battery Sensors**: Monitor battery level (%) and voltage.
* **Mode Selection**: Change tracking modes (Fast, Slow, Live, etc.) directly from Home Assistant.
* **Status**: Home presence, Charging status, LED, and Buzzer status.

## Installation via HACS

1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS > Integrations**.
3. Click the **3 dots** in the top right corner and select **Custom repositories**.
4. Add the URL of your GitHub repository.
5. Select **Integration** as the category.
6. Click **Add**.
7. Close the modal, find **PetTracer** in the list, and click **Download**.
8. Restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & Services**.
2. Click **Add Integration**.
3. Search for **PetTracer**.
4. Enter your **PetTracer Username** and **Password**.
