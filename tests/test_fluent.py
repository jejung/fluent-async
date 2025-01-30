from typing import cast, Callable, Self

import pytest
from async_property import async_property, async_cached_property

from fluent_async import fluent


async def test_fluent_directly_awaited() -> None:
    class SimpleCase:
        @fluent
        async def bogus(self) -> int:
            return 1

        bogus = cast(Callable[..., int], bogus)

        @fluent
        async def with_args(self, a: int, b: int = 10) -> int:
            return a + b

        with_args = cast(Callable[..., int], with_args)

    subject = SimpleCase()
    assert 1 == await subject.bogus()
    assert 10 == await subject.with_args(0)
    assert 11 == await subject.with_args(1)
    assert 2 == await subject.with_args(1, 1)
    assert 3 == await subject.with_args(1, b=2)
    assert 7 == await subject.with_args(a=5, b=2)


async def test_fluent_accessing_properties():
    class DataHolding:
        def __init__(self, data: str = 'see this?'):
            self.field = data

        def sync_method(self) -> Self:
            return self

        async def async_method(self) -> Self:
            return self

        @property
        def sync_prop(self) -> Self:
            return DataHolding('see that?')

        @async_property
        async def async_prop(self) -> Self:
            return DataHolding('see what?')

        async_prop = cast(Self, async_prop)

        @async_cached_property
        async def async_cached_prop(self) -> Self:
            return DataHolding('see what?')

        async_cached_prop = cast(Self, async_cached_prop)

        @fluent
        async def another_fluent(self) -> Self:
            return self

        another_fluent = cast(Callable[..., Self], another_fluent)

    class Proxy:
        @fluent
        async def data(self) -> DataHolding:
            return DataHolding()

        data = cast(Callable[..., DataHolding], data)

    subject = Proxy()
    assert await subject.data().field == 'see this?'
    assert await subject.data().sync_method().field == 'see this?'
    assert await subject.data().async_method().field == 'see this?'
    assert await subject.data().sync_prop.field == 'see that?'
    assert await subject.data().async_prop.field == 'see what?'
    assert await subject.data().async_cached_prop.field == 'see what?'
    assert await subject.data().another_fluent().field == 'see this?'
    assert await subject.data().another_fluent().sync_method().field == 'see this?'
    assert await subject.data().another_fluent().async_method().field == 'see this?'
    assert await subject.data().another_fluent().sync_prop.field == 'see that?'
    assert await subject.data().another_fluent().async_prop.field == 'see what?'
    assert await subject.data().another_fluent().async_cached_prop.field == 'see what?'
    assert await subject.data().another_fluent().async_cached_prop.field == 'see what?'


async def test_fluent_raising_exception() -> None:
    class HeavyFluentBuilder:
        @fluent
        async def start(self) -> Self:
            return self

        start = cast(Callable[..., Self], start)

        @fluent
        async def do_something(self) -> Self:
            return self

        do_something = cast(Callable[..., Self], do_something)

        @fluent
        async def do_other_thing(self) -> Self:
            return self

        do_other_thing = cast(Callable[..., Self], do_other_thing)

        @fluent
        async def fluent_breaks(self) -> Self:
            raise Exception('broke here')

        fluent_breaks = cast(Callable[..., Self], fluent_breaks)

        @fluent
        def sync_fluent_breaks(self) -> Self:
            raise Exception('broke here')

        def regular_breaks(self) -> Self:
            raise Exception('broke here')

    with pytest.raises(Exception, match='broke here'):
        await HeavyFluentBuilder().start().do_something().do_other_thing().fluent_breaks()

    with pytest.raises(Exception, match='broke here'):
        await HeavyFluentBuilder().start().do_something().do_other_thing().sync_fluent_breaks()

    with pytest.raises(Exception, match='broke here'):
        await HeavyFluentBuilder().start().do_something().do_other_thing().regular_breaks()
