from io import BytesIO
from json import dumps
from typing import Literal

from fastapi import Body, FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI(title="Context Manager Extractor API")


class FuzzySearchRequest(BaseModel):
    query: str
    input: str | list[str]
    limit: int = 100


@app.post("/markitdown/{type}", response_model=str)
def convert_to_markdown(type: Literal["markdown", "text"], data: bytes = Body(media_type="application/octet-stream")):
    from extractors.fallback import md

    result = md.convert(BytesIO(data))

    res = PlainTextResponse(result.markdown, media_type="text/markdown") if type == "markdown" else PlainTextResponse(result.text_content)

    res.headers["title"] = dumps(result.title)

    return res


@app.post("/fuzzy_search", response_class=PlainTextResponse)
async def search_text(request: FuzzySearchRequest):
    from processors.fuzzy_search import fuzzy_search

    result = await fuzzy_search(request.query, request.input, request.limit)

    res = PlainTextResponse(result, media_type="text/plain")

    res.headers["title"] = dumps(result.title)

    return res
