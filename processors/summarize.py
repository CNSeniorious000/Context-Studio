import asyncio
import logging
import os
import re

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def filter_text(text: str) -> str:
    """
    通过字符匹配的形式对文本进行过滤
    """
    if not text:
        return text

    # 移除多余的空白字符和换行符
    filtered_text = re.sub(r"\s+", " ", text.strip())

    # 移除特殊字符和符号（保留基本标点符号）
    filtered_text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', "", filtered_text)

    # 移除过短的单词或片段（长度小于2的非中文字符）
    words = filtered_text.split()
    filtered_words = []
    for word in words:
        # 保留中文字符、长度>=2的单词、或常见标点符号
        if re.search(r"[\u4e00-\u9fff]", word) or len(word) >= 2 or word in ".,!?;:()[]{}\"'-":
            filtered_words.append(word)

    filtered_text = " ".join(filtered_words)

    # 移除重复的标点符号
    filtered_text = re.sub(r"([.,!?;:])\1+", r"\1", filtered_text)

    return filtered_text.strip()


async def condense_text(text: str) -> str:
    try:
        messages = [
            ChatCompletionUserMessageParam(
                role="user",
                content=(f"Based on the following text:\n{text}\nplease condense the above text (no more than 100 words)\n"),
            )
        ]

        response = await client.chat.completions.create(
            model="qwen-turbo",
            messages=messages,
            temperature=0,
        )

        content = response.choices[0].message.content

        return content.strip() if content else ""

    except Exception:
        return ""


async def summarize_text(text: str) -> str:
    try:
        messages = [
            ChatCompletionUserMessageParam(
                role="user",
                content=(f"Based on the following text:\n{text}\nplease summarize the above text in one sentence (no more than 100 words)\n"),
            )
        ]

        response = await client.chat.completions.create(
            model="qwen-turbo",
            messages=messages,
            temperature=0,
        )

        content = response.choices[0].message.content

        return content.strip() if content else ""

    except Exception:
        return ""


def split_text(text: str, split_len: int) -> list[str]:
    return [text[i : i + split_len] for i in range(0, len(text), split_len)]


async def summarize(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("input text is empty.")  # noqa: TRY003

    # 先对文本进行过滤
    text = filter_text(text)

    if not text:
        raise ValueError("text is empty after filtering.")  # noqa: TRY003

    process_len = 10000

    # 对文本进行分段
    while len(text) >= process_len:
        texts = split_text(text, process_len)
        task = [condense_text(text) for text in texts]
        result = await asyncio.gather(*task)
        text = "".join(result)

    text = await summarize_text(text)

    return text
