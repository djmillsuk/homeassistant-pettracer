# PetTracer Home Assistant Integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=djmillsuk&repository=homeassistant-pettracer&category=integration)

A custom component for Home Assistant to integrate the PetTracer GPS cat tracking system.

<img width="498" height="339" alt="image" src="https://github.com/user-attachments/assets/e85b1178-0a0b-456b-8abd-3bbf8e9d0885" />

## Features

📍 **Device Tracker**: Real-time GPS location updates for your pets.

🔋 **Battery Monitoring**: Accurate battery level (%) and voltage sensors.

🎛️ **Mode Selection**: Easily switch between all 7 tracking modes (Fast, Slow, Live, etc.) using a Select entity.

💡 **Remote Control**: Toggle the collar's LED and Buzzer on/off directly from Home Assistant switches.

🔔 **Status Monitoring**: Binary sensors for Home presence, Charging status, LED state, and Buzzer state.

🐾 **Device Integration**: All entities are grouped under a single Device for each pet, allowing easy access to controls and status on one screen.

## Installation via HACS

1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS > Integrations**.
3. Click the **3 dots** in the top right corner and select **Custom repositories**.
4. Add the URL of this GitHub repository (https://github.com/djmillsuk/homeassistant-pettracer).
5. Select **Integration** as the category.
6. Click **Add**.
7. Close the modal, find **PetTracer** in the list, and click **Download**.
8. Restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & Services**.
2. Click **Add Integration**.
3. Search for **PetTracer**.
4. Enter your **PetTracer Username** and **Password**.

<img width="1007" height="971" alt="image" src="https://github.com/user-attachments/assets/e94e6c7d-611a-4048-a597-93600a48d01e" />
<img width="499" height="776" alt="image" src="https://github.com/user-attachments/assets/65077dee-e708-4056-ab2c-d4ac503ca655" />

## Recommended Automations

The largest advantage i have seen from automating using petTracer is by also having a SurePet cat flap with the connect hub. Once you integrate this to homeassistant along with pettracer you can switch your cat's collar to slow mode when they are inside and fast when they are out. This means you get the battery saving benefit most of the time from the slow mode and the accuracy of territory mapping in fast mode when your cat it outside...

<img width="498" height="659" alt="image" src="https://github.com/user-attachments/assets/f91a2647-ca55-43aa-be25-bc56d8f027d5" />
<img width="496" height="658" alt="image" src="https://github.com/user-attachments/assets/41c20e64-609a-439a-9ea2-a04e7327ef4a" />
