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
    text = text[:2000]
    messages = [
        ChatCompletionUserMessageParam(
            role="user",
            content=(
                "Based on the following text, please generate a title for it:\n"
                f"{text}\n\n"
                "Requirements:\n"
                "1. The title must be in the SAME LANGUAGE as the original text\n"
                "2. Maximum 10 words\n"
                "3. Only text, no special characters or formatting\n"
                "4. IMPORTANT: If the text is in Chinese, respond in Chinese; if English, respond in English; maintain the original language exactly\n"
                "5. Do NOT include any prefixes like 'Title:', 'Summary:', or similar - just return the title directly\n"
                "6. If the provided information is insufficient to generate a meaningful title, return exactly 'no title'"
            ),
        )
    ]

    response = await client.chat.completions.create(
        model="qwen-max",
        messages=messages,
        max_tokens=1024,
        temperature=0,
    )
    title = response.choices[0].message.content

    if not title:
        logger.error("no title in response.")
        return "title"

    return title
