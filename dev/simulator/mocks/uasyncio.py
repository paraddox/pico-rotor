# Mock uasyncio module for MicroPython
# =====================================
# Wraps standard asyncio with MicroPython-specific additions

import asyncio
from asyncio import *  # Re-export everything from asyncio

# MicroPython-specific sleep functions
async def sleep_ms(ms: int):
    """Sleep for the given number of milliseconds."""
    await asyncio.sleep(ms / 1000.0)


async def sleep_us(us: int):
    """Sleep for the given number of microseconds."""
    await asyncio.sleep(us / 1000000.0)


# MicroPython uses create_task, which is the same in standard asyncio
# Just ensure it's exported
create_task = asyncio.create_task

# Ensure run is available
run = asyncio.run

# Event class (same in both)
Event = asyncio.Event

# Lock class (same in both)
Lock = asyncio.Lock

# MicroPython's gather
gather = asyncio.gather

# MicroPython's wait_for
wait_for = asyncio.wait_for

# MicroPython's wait_for_ms
async def wait_for_ms(awaitable, timeout_ms: int):
    """Wait for an awaitable with timeout in milliseconds."""
    return await asyncio.wait_for(awaitable, timeout=timeout_ms / 1000.0)


# StreamReader and StreamWriter for TCP servers
StreamReader = asyncio.StreamReader
StreamWriter = asyncio.StreamWriter

# Start server function
start_server = asyncio.start_server

# Open connection function
open_connection = asyncio.open_connection

# Current task
current_task = asyncio.current_task

# MicroPython's ThreadSafeFlag (simplified version)
class ThreadSafeFlag:
    """Thread-safe flag for signaling between threads and async code."""

    def __init__(self):
        self._event = asyncio.Event()

    def set(self):
        """Set the flag."""
        self._event.set()

    def clear(self):
        """Clear the flag."""
        self._event.clear()

    async def wait(self):
        """Wait for the flag to be set."""
        await self._event.wait()
