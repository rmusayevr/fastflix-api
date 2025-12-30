import pytest
import asyncio


def test_math_works():
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_async_sleep():
    """
    If pytest-asyncio is working, this will wait 0.1s and pass.
    If not, it will crash or warn.
    """
    await asyncio.sleep(0.1)
    assert True
