import os

import pytest

import aioconfig


@pytest.fixture()
def db_path():
    path = 'test.db'
    yield path
    os.remove(path)


@pytest.mark.asyncio
async def test_attach(db_path):
    await aioconfig.attach(db_path=db_path)
    assert os.path.isfile(db_path)
