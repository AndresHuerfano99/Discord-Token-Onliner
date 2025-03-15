#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import random

try:
    import aiohttp
    import asyncio
    from pystyle import Colors, Colorate, Center
except Exception as e:
    print(e)

# Global options for status selection
STATUS_OPTIONS = ["online", "idle"]

class Stats:
    """
    A simple class to track global statistics.
    """
    online = 0
    total = 0

class Onliner:
    """
    Connects to Discord's WebSocket gateway and sends presence data using the provided token.
    """
    def __init__(self, token: str) -> None:
        self.token = token

    async def start(self) -> None:
        """
        Starts the WebSocket connection and handles events.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect("wss://gateway.discord.gg/?encoding=json&v=10") as ws:
                    await self._send_initial_presence(ws)
                    await self._handle_events(ws)
        except Exception as e:
            print(f"Error starting connection: {e}")

    async def _send_initial_presence(self, ws) -> None:
        """
        Sends the initial presence payload to Discord.
        """
        try:
            payload = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": sys.platform,
                        "$browser": "Discord iOS",
                        "$device": f"{sys.platform} Device",
                    },
                    "presence": {
                        "game": {
                            "name": "discord.gg/discord-developers",
                            "type": 0,
                            "details": "discord.gg/discord-developers",
                            "state": "discord.gg/discord-developers",
                        },
                        "status": random.choice(STATUS_OPTIONS),
                        "since": 0,
                        "activities": [],
                        "afk": False,
                    },
                },
                "s": None,
                "t": None,
            }
            await ws.send_json(payload)
            Stats.online += 1
        except Exception as e:
            print(f"Error sending initial presence: {e}")

    async def _handle_events(self, ws) -> None:
        """
        Listens for events on the WebSocket connection.
        Starts a heartbeat task when the 'hello' event is received.
        """
        try:
            async for msg in ws:
                event = json.loads(msg.data)
                if event.get("op") == 10:
                    heartbeat_interval = int(event["d"]["heartbeat_interval"]) / 1000
                    asyncio.create_task(self._send_heartbeat(ws, heartbeat_interval))
        except Exception as e:
            print(f"Error during event handling: {e}")

    async def _send_heartbeat(self, ws, interval: float) -> None:
        """
        Sends a heartbeat message to Discord at regular intervals.

        Args:
            ws: The active WebSocket connection.
            interval: Time interval (in seconds) between heartbeats.
        """
        try:
            while True:
                heartbeat_payload = {"op": 1, "d": None}
                await ws.send_json(heartbeat_payload)
                await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error sending heartbeat: {e}")


async def banner_thread() -> None:
    """
    Continuously updates and displays a banner with current statistics.
    """
    while True:
        os.system("cls")
        banner = f"""
          ╭───────────────────────────────────────╮
                         Online: {Stats.online:<5}
                         Total: {Stats.total:<5}
          ╰───────────────────────────────────────╯
        """
        print(Center.XCenter(Colorate.Vertical(Colors.purple_to_blue, banner)))
        await asyncio.sleep(0.1)


async def main() -> None:
    """
    Main function to load tokens, create Onliner instances for each token,
    and start the banner thread.
    """
    os.system("cls")
    tasks = []

    try:
        # Read tokens from file and update total count
        with open("./tokens.txt", "r") as tokens_file:
            tokens = [line.strip() for line in tokens_file if line.strip()]
        Stats.total = len(tokens)

        # Start the banner display task
        asyncio.create_task(banner_thread())

        # Create a connection task for each token
        for token in tokens:
            onliner = Onliner(token)
            task = asyncio.create_task(onliner.start())
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    # Install requirements.
    if not os.getenv('requirements'):
        subprocess.Popen(['start', 'start.bat'], shell=True)
        sys.exit()

    os.system('cls' if os.name == 'nt' else 'clear')
    asyncio.run(main())
