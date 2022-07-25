import asyncio
import concurrent.futures
import sys
from typing import Optional

import dataset


class DatabaseClient:
    def __init__(self, uri: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.uri = uri
        self.loop = loop if loop else asyncio.get_running_loop() \
            if sys.version_info >= (3, 7) else asyncio.get_event_loop()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.connection = None

    def _connect(self):
        return dataset.connect(self.uri + '?check_same_thread=False')

    async def connect(self):
        self.connection = await self.loop.run_in_executor(self.executor, self._connect)
        return self


async def connect(uri: str):
    return await DatabaseClient(uri).connect()
