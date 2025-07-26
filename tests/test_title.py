import pytest

from processors.title import generate_title


@pytest.fixture
def text():
    with open("data/file.txt") as f:
        text = f.read()
    return text


@pytest.mark.asyncio
async def test_generate_title(text):
    title = await generate_title(text)

    print(title)
    assert title is not None
