import pytest

from processors.fuzzy_search import fuzzy_search


@pytest.fixture
def text():
    with open("data/file6.txt") as f:
        text = f.read()
    return text


@pytest.mark.asyncio
async def test_fuzzy_search(text: str):
    result = await fuzzy_search("what is this book about", text, token_limit=2000)
    print(result)
    assert result is not None
