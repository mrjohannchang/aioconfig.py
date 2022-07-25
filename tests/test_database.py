import os

import aioconfig
import pytest


@pytest.fixture()
async def db_path():
    path = 'test.db'
    yield path
    if os.path.isfile('{}-shm'.format(path)):
        os.remove('{}-shm'.format(path))
    if os.path.isfile('{}-wal'.format(path)):
        os.remove('{}-wal'.format(path))
    os.remove(path)


@pytest.mark.asyncio
async def test_attach(db_path):
    await aioconfig.attach(db_path=db_path)
    assert os.path.isfile(db_path)
