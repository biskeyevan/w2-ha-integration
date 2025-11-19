# Energy Meter Home Assistant Integration

This is a custom Home Assistant integration for monitoring an energy meter
device accessible over LAN.

## Installation

### HACS Installation (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant
   instance.
2. In Home Assistant, go to HACS > Integrations.
3. Click the three dots in the top right corner and select "Custom
   repositories".
4. Add this repository URL: `https://github.com/yourusername/w2-ha-integration`
5. Select "Integration" as the category.
6. Click "Add".
7. Search for "Energy Meter" in HACS and install it.
8. Restart Home Assistant.
9. Go to Settings > Devices & Services > Add Integration.
10. Search for "Energy Meter" and select it.
11. Enter the IP address of your energy meter device (e.g., 192.168.1.66).
12. The integration will test the connection and create sensors.

### Manual Installation

1. Copy the `custom_components/energy_meter` directory to your Home Assistant
   `custom_components` folder.
2. Restart Home Assistant.
3. Go to Settings > Devices & Services > Add Integration.
4. Search for "Energy Meter" and select it.
5. Enter the IP address of your energy meter device (e.g., 192.168.1.66).
6. The integration will test the connection and create sensors.

## Sensors Created

The integration creates the following sensors for each channel in the energy
meter:

- **Power** (W) - Real-time power consumption
- **Energy Import** (kWh) - Cumulative energy imported
- **Energy Export** (kWh) - Cumulative energy exported
- **Voltage** (V) - Current voltage

For each CT (Current Transformer):

- **Power** (W) - Power through the CT
- **Current** (A) - Current through the CT
- **Voltage** (V) - Voltage at the CT

## Configuration

- **Host**: IP address of the energy meter device
- **Update Interval**: 30 seconds (fixed)

## API Endpoint

The integration polls `http://[IP]/current-sample` which should return JSON data
in the format:

```json
{
    "sensorId": "0x000004714B062945",
    "timestamp": "2025-11-19T17:56:53Z",
    "channels": [
        {
            "type": "PHASE_A_CONSUMPTION",
            "ch": 1,
            "eImp_Ws": 90966084701,
            "eExp_Ws": 514122,
            "p_W": 622,
            "q_VAR": -337,
            "v_V": 121.173
        }
    ],
    "cts": [
        {
            "ct": 1,
            "p_W": 622,
            "q_VAR": -337,
            "v_V": 121.173,
            "i_A": 5.931
        }
    ]
}
```

## Troubleshooting

- Ensure the energy meter is connected to the same network as Home Assistant
- Verify the IP address is correct and the device is responding
- Check Home Assistant logs for connection errors
- The integration will retry failed requests automatically
