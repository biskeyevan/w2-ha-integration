# Testing Guide for Energy Meter Integration

## Quick Start Testing

### 1. Start the Mock Server

```bash
cd tests
python3 mock_server.py
```

This will start a mock energy meter API server on `http://localhost:8080` that
returns realistic test data.

### 2. Test the API Client

In a new terminal:

```bash
python3 tests/test_api.py
```

This tests:

- API client connection
- Data retrieval
- Session management
- Error handling
- Resource cleanup

### 3. Test in Home Assistant

#### Option A: Manual Installation Test

1. Copy the integration to your Home Assistant instance:
   ```bash
   # From the project root
   cp -r custom_components/energy_meter /config/custom_components/
   ```

2. Restart Home Assistant

3. Add the integration:
   - Go to Settings > Devices & Services
   - Click "+ Add Integration"
   - Search for "Energy Meter"
   - Enter `localhost:8080` as the host (with mock server running)

4. Verify sensors are created:
   - Check Developer Tools > States
   - Look for sensors like:
     - `sensor.phase_a_consumption_power`
     - `sensor.phase_a_consumption_energy_import`
     - `sensor.ct_1_power`
     - etc.

#### Option B: HACS Installation Test

1. Ensure HACS is installed
2. Add custom repository
3. Install and configure as above

## Testing Checklist

### ✅ Basic Functionality

- [ ] Integration loads without errors
- [ ] All expected sensors are created
- [ ] Sensors show correct initial values
- [ ] Sensors update every 30 seconds
- [ ] Device info displays correctly

### ✅ Data Validation

- [ ] Handles missing `channels` key gracefully
- [ ] Handles missing `cts` key gracefully
- [ ] Sensors show "Unknown" when data unavailable
- [ ] Energy sensors convert Ws to kWh correctly

### ✅ Resource Management

- [ ] No memory leaks over 10+ minutes
- [ ] Integration unloads cleanly
- [ ] Reload works without errors
- [ ] Config flow validates connection

### ✅ Error Handling

- [ ] Gracefully handles network errors
- [ ] Recovers when device goes offline
- [ ] Shows meaningful errors in config flow
- [ ] Logs errors appropriately

## Monitoring During Testing

### Check Logs

```bash
# Watch live logs
tail -f /config/home-assistant.log | grep energy_meter

# Or in Home Assistant UI
# Settings > System > Logs
# Filter by "energy_meter"
```

### Monitor Memory Usage

```bash
# On the Home Assistant host
ps aux | grep hass
```

Watch the memory (RSS) column over time - it should remain stable.

### Check Sensor Updates

1. Go to Developer Tools > States
2. Filter for `energy_meter`
3. Watch the "Last Updated" timestamp - should update every 30 seconds
4. Verify values change when mock server data changes

## Advanced Testing

### Test with Real Device

1. Stop the mock server
2. Update integration configuration with real device IP
3. Verify real data flows correctly

### Load Testing

```python
# Create test_load.py
import asyncio
from custom_components.energy_meter.api import EnergyMeterApiClient

async def load_test():
    client = EnergyMeterApiClient("localhost:8080")
    for i in range(1000):
        data = await client.async_get_data()
        if i % 100 == 0:
            print(f"Completed {i} requests")
    await client.async_close()

asyncio.run(load_test())
```

### Test Edge Cases

Modify `mock_server.py` to return:

- Empty channels list
- Missing data fields
- Invalid JSON
- HTTP errors (500, 503, etc.)

## Troubleshooting

### Integration Won't Load

- Check Home Assistant logs for import errors
- Verify all files are in correct locations
- Ensure no syntax errors after modifications

### Sensors Not Updating

- Check coordinator logs for update failures
- Verify network connectivity to device/mock server
- Check update interval in code (default 30s)

### Memory Leaks

- Ensure `async_close()` is called on API client
- Check for unclosed aiohttp sessions
- Monitor over longer periods (hours)

### Config Flow Errors

- Ensure mock server is running (for tests)
- Check host format (IP:port or just IP)
- Verify device is accessible on network

## Common Issues

### "Cannot connect" error during setup

- Mock server not running
- Wrong host/port
- Firewall blocking connection

### Sensors show "Unknown"

- API not returning expected data format
- Check logs for validation errors
- Verify mock server is returning correct JSON

### Integration won't unload

- Resource cleanup issue
- Check logs for errors in `async_unload_entry`
- May need Home Assistant restart

## Automation Testing (Optional)

Create automations to verify sensor behavior:

```yaml
automation:
    - alias: "Test Energy Meter Updates"
      trigger:
          - platform: state
            entity_id: sensor.phase_a_consumption_power
      action:
          - service: notify.persistent_notification
            data:
                message: "Power changed to {{ trigger.to_state.state }}W"
```

## Performance Benchmarks

Expected performance with mock server:

- Initial setup: < 5 seconds
- Sensor updates: < 1 second per cycle
- Memory usage: Stable at ~5-10MB
- CPU usage: < 1% between updates

## Reporting Issues

When reporting issues, include:

1. Home Assistant version
2. Integration version
3. Relevant log excerpts
4. Steps to reproduce
5. Expected vs actual behavior
