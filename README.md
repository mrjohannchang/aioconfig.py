# aioconfig

`aioconfig` **efficiently** and **thread-safely** stores configurations in the
background (**asynchronously**).

## Installation

```sh
pip install aioconfig
```

## Usage

The interface of `aioconfig` is dramatically easy to use.
For example, both `set(key, value)` and `await set(key, value)` store a pair of
key/value, which the former one is a fire-and-forget asynchronous function call
while the latter one blocks until the data written onto the disk.

### Init

```py
import aioconfig
storage = aioconfig.get_storage(await aioconfig.attach('example.db'))
section = await aioconfig.get('default')
```

### Delete value

```py
section.delete(key='foo')
```

#### Blocking delete value (wait until it's done)

```py
await section.delete(key='foo')
```

### Get value

```py
value1 = await section.get(key='foo', default='bar')
value2 = await section.get(key='baz', default=12.3)
```

### Set value (fire-and-forget)

```py
section.set(key='foo', value='bar')
section.set(key='baz', value=12.3)
```

#### Blocking set value (wait until it's done)

```py
await section.set(key='foo', value='bar')
await section.set(key='baz', value=12.3)
```

### Batch set value (fire-and-forget) (TBD)

```py
with storage.transation():
    storage.set(
        key='foo', value='bar',
        section='default_section')
    storage.set(
        key='baz', value=12.3,
        section='default_section')
```

#### Blocking batch set value (wait until it's done) (TBD)

```py
async with storage.transation():
    storage.set(
        key='foo', value='bar',
        section='default_section')
    storage.set(
        key='baz', value=12.3,
        section='default_section')
```
