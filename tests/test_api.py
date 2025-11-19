#!/usr/bin/env python3
"""Test script for Energy Meter API client."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import the custom component
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.energy_meter.api import EnergyMeterApiClient


async def test_api_client():
    """Test the API client."""
    print("=" * 60)
    print("Energy Meter API Client Test")
    print("=" * 60)
    
    # Test with localhost (assumes mock server is running)
    host = "localhost:8080"
    print(f"\nTesting connection to: {host}")
    print("-" * 60)
    
    client = EnergyMeterApiClient(host)
    
    try:
        # Test data retrieval
        print("\n1. Testing async_get_data()...")
        data = await client.async_get_data()
        
        print(f"   ✓ Successfully retrieved data")
        print(f"   - Sensor ID: {data.get('sensorId', 'N/A')}")
        print(f"   - Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"   - Channels: {len(data.get('channels', []))}")
        print(f"   - CTs: {len(data.get('cts', []))}")
        
        # Display channel data
        if data.get('channels'):
            print("\n   Channel Details:")
            for ch in data['channels']:
                print(f"     • CH{ch['ch']}: {ch.get('p_W', 0)}W, {ch.get('v_V', 0)}V")
        
        # Display CT data
        if data.get('cts'):
            print("\n   CT Details:")
            for ct in data['cts']:
                print(f"     • CT{ct['ct']}: {ct.get('p_W', 0)}W, {ct.get('i_A', 0)}A")
        
        # Test multiple requests to ensure session reuse
        print("\n2. Testing session reuse (5 requests)...")
        for i in range(5):
            await client.async_get_data()
            print(f"   ✓ Request {i+1} completed")
        
        print("\n3. Testing cleanup...")
        await client.async_close()
        print("   ✓ Client session closed successfully")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nMake sure the mock server is running:")
        print("  python3 tests/mock_server.py")
        return False
    finally:
        # Ensure cleanup
        await client.async_close()


async def test_error_handling():
    """Test error handling with invalid host."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    # Test with invalid host
    host = "invalid-host-that-does-not-exist:9999"
    print(f"\nTesting with invalid host: {host}")
    
    client = EnergyMeterApiClient(host)
    
    try:
        await client.async_get_data()
        print("   ✗ Should have raised an exception")
        return False
    except Exception as e:
        print(f"   ✓ Correctly raised exception: {type(e).__name__}")
        return True
    finally:
        await client.async_close()


if __name__ == '__main__':
    print("\nEnsure mock server is running first:")
    print("  python3 tests/mock_server.py\n")
    
    async def main():
        success = await test_api_client()
        if success:
            await test_error_handling()
    
    asyncio.run(main())