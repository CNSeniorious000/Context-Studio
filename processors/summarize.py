import logging
import os

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


async def summarize(text: str, limit: int) -> str | None:
    if not text or not text.strip():
        raise ValueError("input text is empty.")  # noqa: TRY003

    if limit <= 0:
        raise ValueError("limit must be greater than 0.")  # noqa: TRY003

    if limit > 10000:
        logger.warning(f"limit {limit} is too large, it should be less than 10000.")

    if len(text) <= limit:
        return text

    try:
        messages = [
            ChatCompletionUserMessageParam(
                role="user",
                content=(f"Based on the following text, please summarize it and ensure the length of the summary is less than {limit} characters:\n{text}"),
            )
        ]

        response = await client.chat.completions.create(
            model="deepseek-v3",
            messages=messages,
            max_tokens=min(limit * 2, 4000),
            temperature=0,
        )

        if not response.choices:
            logger.error("no choices in response.")
            return None

        content = response.choices[0].message.content
        if not content:
            logger.error("response content is empty.")
            return None

        if len(content) > limit * 1.2:
            logger.warning(f"summary length {len(content)} exceeds limit {limit}")

        return content.strip()

    except Exception:
        logger.exception("failed to summarize text.")
        return None
