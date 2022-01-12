from .ttserror import TTSError
from .ttsjob import TTSJob
from ..database import DatabaseManager

import threading
import asyncio
import queue


class TTSThread(threading.Thread):

    def __init__(self):

        # Initialize internal elements
        super().__init__()

        self.queue = queue.Queue()
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
        try:
            self.queue.put(job, timeout=2)
        except TimeoutError:
            print('Adding job to the queue has timedout.')

    async def _run_task(self):

        missing_tts = await self.database.get_missing_tts()

        if len(missing_tts) > 0:
            for missing in missing_tts:
                temp_job = TTSJob(
                    missing[0],
                    missing[3],
                    f'{missing[0]}_{missing[2]}_{missing[1]}'
                    )
                self.add_job(temp_job)

        while self.is_running:

            # Wait for a new job
            try:
                job = self.queue.get(timeout=1)
            except Exception:
                continue

            print(temp_job)

            # Perform the job
            try:
                await job.task(self.database)
            except TTSError as e:
                print(f'Task failed: {e}')

    def initialize_loop(self):

        self.loop.run_until_complete(self._run_task())
        self.loop.close()

        print('Thread finished.')
