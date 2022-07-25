import asyncio
import concurrent.futures
import sys
from typing import Optional

import dataset


# Should inherit a base class or implement an interface so that we don't have to expose DatabaseClient outside for
# letting users refer its type.
class DatabaseClient:
    def __init__(self, db_path: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.db_path = db_path
        self.loop = loop if loop else asyncio.get_running_loop() \
            if sys.version_info >= (3, 7) else asyncio.get_event_loop()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.connection = None

    def _connect(self):
        connection = dataset.connect('sqlite:///{}?check_same_thread=False'.format(self.db_path))
        connection.executable.execute('PRAGMA journal_mode=WAL')
        return connection

    async def connect(self):
        self.connection = await self.loop.run_in_executor(self.executor, self._connect)
        return self


async def attach(db_path: str, loop: Optional[asyncio.AbstractEventLoop] = None):
    return await DatabaseClient(db_path, loop=loop).connect()
