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
    def delete(self, key: str):
        pass

    @abc.abstractmethod
    async def get(self, key: str):
        pass


class Storage(BaseStorage):
    def __init__(self, db_client: database.DatabaseClient):
        super().__init__(db_client)
        self.cache = dict()

    def _delete(self, key):
        self.cache.pop(key, None)
        tables = self._get_tables()
        if key in tables:
            self.db_client.connection.load_table(key).drop()

    def delete(self, key):
        key = dataset.util.normalize_table_name(key)
        return self.loop.run_in_executor(self.db_client.executor, self._delete, key)

    def _get_tables(self):
        return self.db_client.connection.tables

    async def get(self, key: str):
        key = dataset.util.normalize_table_name(key)

        tables = await self.loop.run_in_executor(self.db_client.executor, self._get_tables)
        if key not in tables:
            await self.loop.run_in_executor(
                self.db_client.executor, self.db_client.connection.create_table, key)

        if key not in self.cache:
            self.cache[key] = await Section(key, db_client=self.db_client).load()

        return self.cache.get(key)


class Section(BaseStorage):
    def __init__(self, name: str, db_client: database.DatabaseClient):
        super().__init__(db_client)
        self.name = dataset.util.normalize_table_name(name)
        self.cache = dict()
        self.table = None

    def _delete(self, key):
        self.cache.pop(key, None)
        self.table.delete(key=key)

    def delete(self, key):
        return self.loop.run_in_executor(self.db_client.executor, self._delete, key)

    async def load(self):
        self.table = await self.loop.run_in_executor(
            self.db_client.executor, self.db_client.connection.load_table, self.name)
        for row in self.table:
            self.cache[row[KEY]] = row[VALUE]

        return self

    def _get(self, key: str):
        return self.cache.get(key, NonExistentError)

    async def get(self, key: str, default=NonExistentError):
        key = dataset.util.normalize_table_name(key)
        value = await self.loop.run_in_executor(self.db_client.executor, self._get, key)

        if value is NonExistentError:
            if default is NonExistentError:
                raise NonExistentError('key "{}" does not exist in {}'.format(key, self.name))
            value = default
        else:
            value = json.loads(value)

        return value

    def _get_all(self):
        return {key: json.loads(value) for key, value in self.cache.items()}

    async def get_all(self):
        return await self.loop.run_in_executor(self.db_client.executor, self._get_all)

    def _set(self, key: str, jsonized_value: str):
        now = datetime.datetime.utcnow()

        data = collections.OrderedDict()
        data[KEY] = key
        data[VALUE] = jsonized_value
        if key not in self.cache:
            data[CREATED_AT] = now
        data[UPDATED_AT] = now

        self.cache[key] = jsonized_value
        self.table.upsert(data, [KEY])

    # This is an awaitable function
    def set(self, key: str, value: Any):
        return self.loop.run_in_executor(self.db_client.executor, self._set, key, json.dumps(value))


def get_storage(db_client: database.DatabaseClient):
    return Storage(db_client)
