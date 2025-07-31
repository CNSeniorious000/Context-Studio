import pytest

from processors.summarize import summarize


@pytest.mark.asyncio
async def test_summarize(summarize_parameters: dict):
    summary = await summarize(summarize_parameters["text"])
    print(summary)
    assert summary is not None
