import asyncio

import aioconfig


async def example():
    default_section = await aioconfig.get_storage(await aioconfig.attach('example.db')).get('default')

    await default_section.set('foo', 'bar')
    print('foo: {}'.format(await default_section.get('foo')))
    await default_section.set('baz', 12.3)
    print('baz: {}'.format(await default_section.get('baz')))

    default_section.set('qux', 'quux')
    default_section.set('quuz', 'corge')
    default_section.set('grault', 'garply')
    default_section.set('waldo', 'fred')
    default_section.set('plugh', 'xyzzy')
    print('qux: {}'.format(await default_section.get('qux')))
    print('quuz: {}'.format(await default_section.get('quuz')))
    print('grault: {}'.format(await default_section.get('grault')))
    print('waldo: {}'.format(await default_section.get('waldo')))
    print('plugh: {}'.format(await default_section.get('plugh')))


asyncio.run(example())
