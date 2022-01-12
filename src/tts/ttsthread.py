from ..utils import CustomQueue
from .ttserror import TTSError

from ..database import DatabaseManager

from async_timeout import timeout

import threading
import asyncio


class TTSThread(threading.Thread):

    def __init__(self):

        # Initialize internal elements
        super().__init__()

        self.queue = CustomQueue()
        self.is_running = True
        self.daemon = True

        self._target = self.initialize_loop

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Create a new database connection manager
        self.database = DatabaseManager(self.loop)

        # Start the thread
        self.start()

    def __del__(self):
        self.is_running = False

    def add_job(self, job):
        asyncio.run_coroutine_threadsafe(self.queue.put(job), self.loop)

    async def _run_task(self):
        print('This was called!')

        while self.is_running:

            # Wait for a new job
            try:
                async with timeout(.1):
                    job = await self.queue.get()
            except asyncio.TimeoutError:
                continue

            # Perform the job
            try:
                await job.task(self.database)
            except TTSError as e:
                print(f'Task failed: {e}')

    def initialize_loop(self):

        self.loop.run_until_complete(self._run_task())
        self.loop.close()

        print('Thread finished.')
