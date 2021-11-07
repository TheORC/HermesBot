import asyncio
import random


class CustomQueue(asyncio.Queue):

    def __init__(self):
        super().__init__()

    def _put(self, item, index):
        if(index == -1):
            self._queue.append(item)
        else:
            try:
                print('Time to insert instead of append')
                self._queue.insert(index, item)
            except Exception:
                print('There was an error inserting...')
                self._queue.append(item)

    async def put(self, item, index=-1):
        """Put an item into the queue.

        Put an item into the queue. If the queue is full, wait until a free
        slot is available before adding item.
        """
        while self.full():
            putter = self._get_loop().create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()  # Just in case putter is not done yet.
                try:
                    # Clean self._putters from canceled putters.
                    self._putters.remove(putter)
                except ValueError:
                    # The putter could be removed from self._putters by a
                    # previous get_nowait call.
                    pass
                if not self.full() and not putter.cancelled():
                    # We were woken up by get_nowait(), but can't take
                    # the call.  Wake up the next in line.
                    self._wakeup_next(self._putters)
                raise
        return self.put_nowait(item, index)

    def shuffle_queue(self):
        random.shuffle(self._queue)

    def put_nowait(self, item, index):
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """
        if self.full():
            raise asyncio.QueueFull
        self._put(item, index)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)
