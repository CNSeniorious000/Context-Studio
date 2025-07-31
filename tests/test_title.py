import pytest

from processors.title import generate_title


@pytest.mark.asyncio
async def test_generate_title(title_parameters: dict):
    title = await generate_title(title_parameters["text"])
    print(title)
    assert title is not None
