import logging
import os

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam

# 设置日志
logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


async def summarize(text: str, limit: int) -> str | None:
    """
    使用AI对文本进行摘要

    Args:
        text: 需要摘要的文本
        limit: 摘要文本的最大字符数限制

    Returns:
        摘要文本，如果出现错误则返回None

    Raises:
        ValueError: 当输入参数无效时
    """
    # 输入验证
    if not text or not text.strip():
        raise ValueError("输入文本不能为空")

    if limit <= 0:
        raise ValueError("字符限制必须大于0")

    if limit > 10000:
        logger.warning(f"字符限制{limit}过大，建议不超过10000")

    # 检查API密钥
    if not os.getenv("API_KEY"):
        raise ValueError("未设置API_KEY环境变量")

    try:
        messages = [ChatCompletionUserMessageParam(role="user", content=f"请总结以下文本，并保证总结后的文本长度不超过{limit}个字符：\n{text}")]

        response = await client.chat.completions.create(
            model="deepseek-v3",
            messages=messages,
            max_tokens=min(limit * 2, 4000),  # 设置合理的token限制
            temperature=0.3,  # 降低随机性，提高稳定性
        )

        # 检查响应有效性
        if not response.choices:
            logger.error("API响应中没有选择项")
            return None

        content = response.choices[0].message.content
        if not content:
            logger.error("API响应内容为空")
            return None

        # 检查摘要长度是否符合要求
        if len(content) > limit * 1.2:  # 允许20%的误差
            logger.warning(f"摘要长度{len(content)}超过限制{limit}")

        return content.strip()

    except Exception:
        logger.exception("摘要生成失败")
        return None
