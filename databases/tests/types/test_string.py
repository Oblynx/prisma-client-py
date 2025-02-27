import pytest
from dirty_equals import IsPartialDict

from prisma import Prisma
from prisma.models import Types


@pytest.mark.asyncio
async def test_filtering(client: Prisma) -> None:
    """Finding records by a String value"""
    start = ord('a')
    async with client.batch_() as batcher:
        for i in range(10):
            batcher.types.create({'string': chr(start + i)})

    total = await client.types.count(where={'string': {'gte': 'e'}})
    assert total == 6

    found = await client.types.find_first(
        where={
            'string': {
                'equals': 'a',
            },
        },
    )
    assert found is not None
    assert found.string == 'a'

    results = await client.types.find_many(
        where={
            'string': {
                'in': ['a', 'd', 'f', 'z'],
            },
        },
        order={
            'string': 'asc',
        },
    )
    assert len(results) == 3
    assert results[0].string == 'a'
    assert results[1].string == 'd'
    assert results[2].string == 'f'

    results = await client.types.find_many(
        where={
            'string': {
                'not_in': ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'i'],
            },
        },
        order={
            'string': 'asc',
        },
    )
    assert len(results) == 2
    assert results[0].string == 'e'
    assert results[1].string == 'j'

    found = await client.types.find_first(
        where={
            'string': {
                'lt': 'g',
            },
        },
        order={
            'string': 'desc',
        },
    )
    assert found is not None
    assert found.string == 'f'

    found = await client.types.find_first(
        where={
            'string': {
                'lte': 'f',
            },
        },
        order={
            'string': 'desc',
        },
    )
    assert found is not None
    assert found.string == 'f'

    found = await client.types.find_first(
        where={
            'string': {
                'gt': 'f',
            },
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'g'

    found = await client.types.find_first(
        where={
            'string': {
                'gte': 'g',
            },
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'g'

    found = await client.types.find_first(
        where={
            'string': {
                'not': 'a',
            },
        },
        order={'string': 'asc'},
    )
    assert found is not None
    assert found.string == 'b'


@pytest.mark.asyncio
async def test_filtering_nulls(client: Prisma) -> None:
    """None is a valid filter for nullable String fields"""
    await client.types.create(
        {
            'string': 'a',
            'optional_string': None,
        },
    )
    await client.types.create(
        {
            'string': 'b',
            'optional_string': 'null',
        },
    )
    await client.types.create(
        {
            'string': 'c',
            'optional_string': 'robert@craigie.dev',
        },
    )

    found = await client.types.find_first(
        where={
            'NOT': [
                {
                    'optional_string': None,
                },
            ],
        },
        order={
            'string': 'asc',
        },
    )
    assert found is not None
    assert found.string == 'b'
    assert found.optional_string == 'null'

    count = await client.types.count(
        where={
            'optional_string': None,
        },
    )
    assert count == 1

    count = await client.types.count(
        where={
            'NOT': [
                {
                    'optional_string': None,
                },
            ],
        },
    )
    assert count == 2

    # TODO: test passing 'null'


def test_json_schema() -> None:
    """Ensure a JSON Schema definition can be created"""
    assert Types.schema() == IsPartialDict(
        properties=IsPartialDict(
            {
                'string': {
                    'title': 'String',
                    'type': 'string',
                },
                'optional_string': {
                    'title': 'Optional String',
                    'type': 'string',
                },
            }
        )
    )
