import pytest

from processors.fuzzy_search import fuzzy_search


@pytest.mark.asyncio
async def test_fuzzy_search(search_parameters: dict):
    result = await fuzzy_search(
        query=search_parameters["query"],
        input=search_parameters["text"],
        token_limit=search_parameters["token_limit"],
    )
    print(result)
    assert result is not None
