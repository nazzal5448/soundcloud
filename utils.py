import os
import asyncio

async def delete_file_after_delay(file_path: str, delay: int = 60):
    await asyncio.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
