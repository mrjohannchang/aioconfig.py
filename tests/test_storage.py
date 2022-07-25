import json
import os

import aioconfig
import pytest


@pytest.fixture()
async def db_client():
    db_path = 'test.db'
    client = await aioconfig.attach(db_path)
    yield client
    if os.path.isfile('{}-shm'.format(db_path)):
        os.remove('{}-shm'.format(db_path))
    if os.path.isfile('{}-wal'.format(db_path)):
        os.remove('{}-wal'.format(db_path))
    os.remove(db_path)


def test_get_storage(db_client):
    assert isinstance(aioconfig.get_storage(db_client), aioconfig.Storage)


@pytest.mark.asyncio
async def test_storage_get(db_client):
    section = await aioconfig.get_storage(db_client).get('test')
    assert isinstance(section, aioconfig.Section)


@pytest.mark.asyncio
async def test_storage_delete(db_client):
    storage = aioconfig.get_storage(db_client)
    await ((await storage.get('test')).set('foo', 'bar'))
    assert 'test' in storage.db_client.connection.tables
    await storage.delete('test')
    assert 'test' not in storage.db_client.connection.tables


@pytest.mark.asyncio
async def test_section_set(db_client):
    section = await aioconfig.get_storage(db_client).get('test')
    await section.set('foo', 'bar')
    assert 'bar' == json.loads(section.db_client.connection.executable.execute(
        "SELECT key, value FROM test WHERE key='foo'").fetchone()[1])


@pytest.mark.asyncio
async def test_section_get(db_client):
    section = await aioconfig.get_storage(db_client).get('test')
    await section.set('foo', 'bar')
    assert await section.get('foo') == json.loads(section.db_client.connection.executable.execute(
        "SELECT key, value FROM test WHERE key='foo'").fetchone()[1])


@pytest.mark.asyncio
async def test_section_get_all(db_client):
    section = await aioconfig.get_storage(db_client).get('test')
    await section.set('foo', 'bar')
    await section.set('baz', 123)
    assert await section.get_all() == {'foo': 'bar', 'baz': 123}


@pytest.mark.asyncio
async def test_section_delete(db_client):
    section = await aioconfig.get_storage(db_client).get('test')
    await section.set('foo', 'bar')
    await section.set('baz', 123)
    await section.delete('foo')
    await section.delete('baz')
    assert await section.get_all() == {}
