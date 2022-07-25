# aioconfig

## Demo

### Init

```py
import aioconfig
storage = aioconfig.get_storage(connection=aioconfig.connect('sqlite'))
```

### Get value

```py
value1 = storage.get(key='foo', section='default')
value2 = storage.get(key='baz', section='default')
```

### Set value

```py
storage.set(key='foo', value='bar', section='default')
storage.set(key='baz', value='qux', section='default')
```

#### Blocking write through

```py
await storage.set(key='foo', value='bar', section='default')
await storage.set(key='baz', value='qux', section='default')
```

### Batch set value (TBD)

```py
with storage.transation():
    storage.set(
        key='foo', value='bar',
        section='default_section')
    storage.set(
        key='baz', value='qux',
        section='default_section')
```

#### Blocking write through (TBD)

```py
async with storage.transation():
    storage.set(
        key='foo', value='bar',
        section='default_section')
    storage.set(
        key='baz', value='qux',
        section='default_section')
```
