# PetTracer Home Assistant Integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=djmillsuk&repository=homeassistant-pettracer&category=integration)

A custom component for Home Assistant to integrate the PetTracer GPS cat tracking system.

<img width="498" height="467" alt="image" src="https://github.com/user-attachments/assets/b9029867-5e85-41b0-ae55-fdd9ce54edcc" />

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

## 🤖 Automation Examples

Unlock the full potential of your PetTracer integration with these automation ideas. Copy and paste these YAML examples into your `automations.yaml` or use the visual editor.

### 🔋 Low Battery Power Saver
Automatically switch to **Slow** mode when the battery drops below 10% to ensure you don't lose contact before you can recharge.

```yaml
alias: "Pet: Low Battery Saver"
description: "Switch to Slow mode to save battery when low"
trigger:
  - platform: numeric_state
    entity_id: sensor.fluffy_battery
    below: 10
action:
  - service: select.select_option
    target:
      entity_id: select.fluffy_mode
    data:
      option: "Slow"
  - service: notify.mobile_app_my_phone
    data:
      message: "Fluffy's battery is low! Switched to Slow mode."
```

### 🌙 Night & Day Cycle
Save battery while your pet sleeps at night, and ensure good tracking during the day.

```yaml
alias: "Pet: Night/Day Cycle"
description: "Switch to Slow mode at night and Normal in the morning"
trigger:
  - platform: time
    at: "22:00:00"
    id: "night"
  - platform: time
    at: "07:00:00"
    id: "day"
action:
  - choose:
      - conditions:
          - condition: trigger
            id: "night"
        sequence:
          - service: select.select_option
            target:
              entity_id: select.fluffy_mode
            data:
              option: "Slow"
      - conditions:
          - condition: trigger
            id: "day"
        sequence:
          - service: select.select_option
            target:
              entity_id: select.fluffy_mode
            data:
              option: "Normal"
```

### 🚪 SurePet Smart Flap Integration
Sync your PetTracer mode with your SurePet cat flap. When the flap detects your pet leaving, switch to **Fast** mode. When they return, switch to **Slow** mode to save battery.

```yaml
alias: "Pet: SurePet Flap Sync"
description: "Switch mode based on home/away presence from SurePet flap"
trigger:
  - platform: state
    entity_id: binary_sensor.fluffy
    from: "on"
    to: "off"
    id: "left_home"
  - platform: state
    entity_id: binary_sensor.fluffy
    from: "off"
    to: "on"
    id: "arrived_home"
action:
  - service: select.select_option
    target:
      entity_id: select.fluffy_mode
    data:
      option: >
        {{ 'Fast' if trigger.id == 'left_home' else 'Slow' }}
```

### 🚨 "Lost Pet" Protocol
Create a script to maximize visibility if your pet goes missing. This sets the tracker to **Live** mode and turns on the **LED** and **Buzzer** to help locate them.

```yaml
script:
  find_fluffy:
    alias: "Find Fluffy Protocol"
    sequence:
      - service: select.select_option
        target:
          entity_id: select.fluffy_mode
        data:
          option: "Live"
      - service: switch.turn_on
        target:
          entity_id: switch.fluffy_led
      - service: switch.turn_on
        target:
          entity_id: switch.fluffy_buzzer
      - service: notify.mobile_app_my_phone
        data:
          message: "Emergency tracking activated! LED and Buzzer are ON."
```
