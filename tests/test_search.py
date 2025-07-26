import pytest

from processors.fuzzy_search import fuzzy_search


@pytest.fixture
def text():
    with open("data/file2.txt") as f:
        text = f.read()
    return text


@pytest.mark.asyncio
async def test_fuzzy_search(text: str):
    result = await fuzzy_search("how to download the llm info", text, token_limit=500)
    print(result)
    assert result is not None
