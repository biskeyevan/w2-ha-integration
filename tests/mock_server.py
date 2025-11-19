#!/usr/bin/env python3
"""Mock Energy Meter HTTP server for testing."""
import asyncio
import json
from datetime import datetime, timezone
from aiohttp import web


class MockEnergyMeterServer:
    """Mock server that simulates an energy meter API."""

    def __init__(self, port=8080):
        """Initialize the mock server."""
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/current-sample', self.handle_current_sample)
        
    async def handle_current_sample(self, request):
        """Handle /current-sample endpoint."""
        # Simulate realistic energy meter data
        data = {
            "sensorId": "0x000004714B062945",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "channels": [
                {
                    "type": "PHASE_A_CONSUMPTION",
                    "ch": 1,
                    "eImp_Ws": 90966084701,
                    "eExp_Ws": 514122,
                    "p_W": 622,
                    "q_VAR": -337,
                    "v_V": 121.173
                },
                {
                    "type": "PHASE_B_CONSUMPTION",
                    "ch": 2,
                    "eImp_Ws": 85234567890,
                    "eExp_Ws": 423456,
                    "p_W": 478,
                    "q_VAR": -289,
                    "v_V": 120.845
                }
            ],
            "cts": [
                {
                    "ct": 1,
                    "p_W": 622,
                    "q_VAR": -337,
                    "v_V": 121.173,
                    "i_A": 5.931
                },
                {
                    "ct": 2,
                    "p_W": 478,
                    "q_VAR": -289,
                    "v_V": 120.845,
                    "i_A": 4.582
                }
            ]
        }
        return web.json_response(data)

    async def start(self):
        """Start the mock server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        print(f"Mock Energy Meter server running on http://localhost:{self.port}")
        print("Press Ctrl+C to stop")
        
        try:
            # Keep server running
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            await runner.cleanup()


if __name__ == '__main__':
    server = MockEnergyMeterServer(port=8080)
    asyncio.run(server.start())