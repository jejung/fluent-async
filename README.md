# fluent-async

## Overview

fluent-async is a Python library that enables fluent-style chaining of asynchronous methods and supports [`@async_property` and `@async_cached_property`](https://pypi.org/project/async-property/) without requiring explicit `await` statements at each step. It simplifies working with asynchronous classes and methods by eliminating deep nesting of `await` expressions.

In other words:

```python
async def example():
    await (await (await (await StyleBuilder().gray()).bold()).underline()).as_posix_style
```

Becomes:

```python
async def example():
    await StyleBuilder().gray().bold().underline().as_posix_style
```

## Features
- **Fluent API for Async Methods**: Chain async methods seamlessly without manually awaiting each step.
- **Automatic Handling of Async Properties**: Access `@async_property` attributes without explicit `await`.
- **Enhanced Debugging**: Provides clear execution traces in `__repr__` for better debugging.

## Installation

```shell
pip install fluent-async
```

```shell
poetry add fluent-async
```

## Usage
### Basic Example

```python
import asyncio
from async_property import async_property
from fluent_async import fluent

from typing import cast, Callable, Self


class Arithmetic:
    def __init__(self, value: int):
        self.value = value

    @fluent
    async def increment(self) -> Self:
        self.value += 1
        return self

    increment = cast(Callable[..., Self], increment)

    @fluent
    async def double(self) -> Self:
        self.value *= 2
        return self

    double = cast(Callable[..., Self], double)

    @async_property
    async def async_value(self) -> int:
        return self.value


async def main():
    result = await Arithmetic(1).increment().double().async_value
    print(result)  # Expected output: (1+1) * 2 = 4


asyncio.run(main())
```

## How It Works
### `@fluent` Decorator
- Wraps an async method to allow fluent chaining.
- Ensures returned values are wrapped in a `Fluent` instance.

### `Fluent` Class
- Implements `__getattr__` to support accessing async properties.
- Implements `__call__` to handle method calls.
- Overrides `__await__` to return awaited values correctly.

## License
MIT License -- [LICENSE](./LICENSE)

## Contributing
Contributions are welcome! Please submit issues or pull requests to improve the project.
