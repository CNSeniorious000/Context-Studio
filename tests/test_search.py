import pytest

from processors.fuzzy_search import fuzzy_search


@pytest.fixture
def text():
    with open("data/file3.txt") as f:
        text = f.read()
    return text


@pytest.mark.asyncio
async def test_fuzzy_search(text: str):
    result = await fuzzy_search("what is ai scientist", text, token_limit=500)
    print(result)
    assert result is not None
