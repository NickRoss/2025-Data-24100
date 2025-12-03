"""Demonstrate async vs sync execution patterns.

This module shows the difference between synchronous (blocking) and
asynchronous (non-blocking) execution by simulating multiple processes.
"""

import argparse
import asyncio
import random
import time


# SYNC VERSION
def process_sync(name):
    """Simulate a synchronous process that blocks execution.

    Args:
        name: Name identifier for the process
    """
    wait_time = int(random.uniform(3, 6))
    print(f"Started process {name} (will take {wait_time}s)")
    for i in range(1, wait_time + 1):
        time.sleep(1)
        print(f"  {name}: {i} second(s)")
    print(f"Finished {name}")

def run_sync():
    """Run three synchronous processes sequentially."""
    print("\n=== SYNC VERSION ===")
    start = time.time()

    process_sync("A")
    process_sync("B")
    process_sync("C")

    print(f"\nTotal time: {time.time() - start:.1f} seconds\n")


# ASYNC VERSION
async def process_async(name):
    """Simulate an asynchronous process that doesn't block.

    Args:
        name: Name identifier for the process
    """
    wait_time = int(random.uniform(3, 6))
    print(f"Started process {name} (will take {wait_time}s)")
    for i in range(1, wait_time + 1):
        await asyncio.sleep(1)
        print(f"  {name}: {i} second(s)")
    print(f"Finished {name}")


async def run_async():
    """Run three asynchronous processes concurrently."""
    print("\n=== ASYNC VERSION ===")
    start = time.time()

    await asyncio.gather(
        process_async("A"), process_async("B"), process_async("C")
    )
    print(f"\nTotal time: {time.time() - start:.1f} seconds\n")


def main():
    """Main entry point for the async example script."""
    parser = argparse.ArgumentParser(
        description="Demonstrate async vs sync execution"
    )
    parser.add_argument(
        "mode", choices=["sync", "async"], help="Run sync or async versions"
    )

    args = parser.parse_args()

    if args.mode == "sync":
        run_sync()

    else:
        asyncio.run(run_async())


if __name__ == "__main__":
    main()
