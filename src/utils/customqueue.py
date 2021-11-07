# -*- coding: utf-8 -*-
'''
Copyright (c) 2021 Oliver Clarke.

This file is part of HermesBot.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import asyncio
import random


class CustomQueue(asyncio.Queue):
    """This class creates an async queue to store music.
    It adds additional features allowing the items to be
    injected at the start of the queue.  Aditionaly, it
    allows the queue to be shuffled.
    """

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
            except Exception:
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
        """Shuffle items in the queue.

        Shuffles items in the queue using a random shuffle.
        """
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
