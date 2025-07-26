from io import BytesIO
from json import dumps
from typing import Literal

from fastapi import Body, FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="Context Manager Extractor API")


@app.post("/markitdown/{type}", response_model=str)
def convert_to_markdown(type: Literal["markdown", "text"], data: bytes = Body(media_type="application/octet-stream")):
    from extractors.fallback import md

    result = md.convert(BytesIO(data))

    res = PlainTextResponse(result.markdown, media_type="text/markdown") if type == "markdown" else PlainTextResponse(result.text_content)

    res.headers["title"] = dumps(result.title)

    return res
