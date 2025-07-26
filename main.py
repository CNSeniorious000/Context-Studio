from io import BytesIO
from json import dumps

from fastapi import Body, FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI(title="Context Manager Extractor API")


class FuzzySearchRequest(BaseModel):
    query: str
    input: str | list[str]
    token_limit: int = 100


@app.post("/markitdown", response_model=str)
def convert_to_markdown(data: bytes = Body(media_type="application/octet-stream")):
    from promptools.openai import count_token

    from extractors.fallback import md

    result = md.convert(BytesIO(data))

    text = result.markdown

    token_count = count_token(text)

    res = PlainTextResponse(text, media_type="text/markdown")

    res.headers["title"] = dumps(result.title)
    res.headers["token-count"] = dumps(token_count)

    return res


@app.post("/generate_title", response_class=PlainTextResponse)
async def generate_title(text: str = Body(media_type="text/plain")) -> str:
    from processors.title import generate_title as title_generator

    return await title_generator(text)


@app.post("/fuzzy_search", response_class=PlainTextResponse)
async def search_text(request: FuzzySearchRequest) -> str:
    from processors.fuzzy_search import fuzzy_search

    return await fuzzy_search(request.query, request.input, request.token_limit)


if not __debug__:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(CORSMiddleware, allow_origins="*", allow_headers="*", allow_methods="*")
