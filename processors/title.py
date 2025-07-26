import logging
import os

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


async def generate_title(text: str) -> str:
    messages = [
        ChatCompletionUserMessageParam(
            role="user",
            content=(f"Based on the following text, please generate a title for it:\n{text}\nThe title should be no more than 10 words and should only be text with no other characters,\nthe language of title should be the same as the language of the text.\n"),
        )
    ]

    response = await client.chat.completions.create(
        model="qwen-turbo",
        messages=messages,
        temperature=0.3,
    )
    title = response.choices[0].message.content

    if not title:
        logger.error("no title in response.")
        return "title"

    return title
