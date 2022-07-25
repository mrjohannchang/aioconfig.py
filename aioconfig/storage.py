import abc
import collections
import datetime
import json
from typing import Any

import dataset

from . import database


KEY = 'key'
VALUE = 'value'
CREATED_AT = 'created_at'
UPDATED_AT = 'updated_at'


class NonExistentError(ValueError):
    pass


class BaseStorage(metaclass=abc.ABCMeta):
    def __init__(self, db_client: database.DatabaseClient):
        self.db_client = db_client
        self.loop = self.db_client.loop

    @abc.abstractmethod
    async def get(self, key: str):
        pass


class Storage(BaseStorage):
    def __init__(self, db_client: database.DatabaseClient):
        super().__init__(db_client)
        self.cache = dict()

    async def get(self, key: str):
        key = dataset.util.normalize_table_name(key)
        if key not in self.cache:
            self.cache[key] = await Section(key, db_client=self.db_client).init()
        return self.cache.get(key)


class Section(BaseStorage):
    def __init__(self, name: str, db_client: database.DatabaseClient):
        super().__init__(db_client)
        self.name = dataset.util.normalize_table_name(name)
        self.cache = dict()

    async def init(self):
        tables = await self.loop.run_in_executor(self.db_client.executor, self._get_tables)
        if self.name not in tables:
            await self.loop.run_in_executor(
                self.db_client.executor, self.db_client.connection.create_table, self.name)

        rows = await self.loop.run_in_executor(
            self.db_client.executor, self.db_client.connection.load_table, self.name)
        for row in rows:
            self.cache[row[KEY]] = row[VALUE]

        return self

    async def get(self, key: str, default=NonExistentError):
        key = dataset.util.normalize_table_name(key)
        value = self.cache.get(key, NonExistentError)

        if value is NonExistentError:
            if default is NonExistentError:
                raise NonExistentError('key "{}" does not exist in {}'.format(key, self.name))
            value = default
        else:
            value = json.loads(value)
        return value

    def _get_tables(self):
        return self.db_client.connection.tables

    def _set(self, key: str, jsonized_value: str):
        now = datetime.datetime.utcnow()

        data = collections.OrderedDict()
        data[KEY] = key
        data[VALUE] = jsonized_value
        if key not in self.cache:
            data[CREATED_AT] = now
        data[UPDATED_AT] = now

        self.cache[key] = jsonized_value

        self.db_client.connection.load_table(self.name).upsert(data, [KEY])

    # This is an awaitable function
    def set(self, key: str, value: Any):
        return self.loop.run_in_executor(self.db_client.executor, self._set, key, json.dumps(value))


def get_storage(db_client: database.DatabaseClient):
    return Storage(db_client)
