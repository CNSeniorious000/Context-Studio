import pytest

from processors.summarize import summarize


@pytest.fixture
def text():
    with open("data/file4.txt") as f:
        text = f.read()
    return text


@pytest.mark.asyncio
async def test_summarize(text: str):
    summary = await summarize(text, 200)
    print(summary)
    assert summary is not None
