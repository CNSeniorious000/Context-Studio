import asyncio
import os

import numpy as np

# from promptools.openai import count_token
import tiktoken
from openai import AsyncOpenAI
from sklearn.metrics.pairwise import cosine_similarity

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼服务的base_url
)


def count_token(text: str):
    if not text:
        return 0

    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = encoding.encode(text)
    return len(tokens)


def split_text(text: str, chunk_size: int = 100) -> list[str]:
    """
    按照chunk_size将文本拆分成chunks，并保证句子完整性
    使用\n作为句子分隔符
    """
    if not text.strip():
        return []

    # 按行分割文本
    lines = text.split("\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for line in lines:
        line_tokens = count_token(line)

        # 如果当前行加入后会超过chunk_size，先保存当前chunk
        if current_tokens + line_tokens > chunk_size and current_chunk.strip():
            chunks.append(current_chunk.strip())
            current_chunk = line
            current_tokens = line_tokens
        else:
            # 否则将行添加到当前chunk
            if current_chunk:
                current_chunk += "\n" + line
                current_tokens += line_tokens + count_token("\n")  # 加上换行符的token
            else:
                current_chunk = line
                current_tokens = line_tokens

    # 添加最后一个chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # 如果单行就超过了chunk_size，需要进一步分割
    final_chunks = []
    for chunk in chunks:
        if count_token(chunk) <= chunk_size:
            final_chunks.append(chunk)
        else:
            # 对于超长的chunk，按字符分割
            words = chunk.split()
            temp_chunk = ""
            for word in words:
                temp_tokens = count_token(temp_chunk + " " + word if temp_chunk else word)
                if temp_tokens <= chunk_size:
                    temp_chunk = temp_chunk + " " + word if temp_chunk else word
                else:
                    if temp_chunk:
                        final_chunks.append(temp_chunk)
                    temp_chunk = word

            if temp_chunk:
                final_chunks.append(temp_chunk)

    return final_chunks


async def get_embedding(text, model="text-embedding-v4"):
    try:
        completion = await client.embeddings.create(
            model=model,
            input=text,
            dimensions=1024,
            encoding_format="float",
        )
        return np.array(completion.data[0].embedding)
    except Exception:
        return None


async def fuzzy_search(query: str, input: str | list[str], limit: int = 100) -> str:
    # 如果input是字符串，先进行分割
    chunks = split_text(text=input) if isinstance(input, str) else input

    if not chunks:
        raise ValueError("input is empty.")  # noqa: TRY003

    tasks = []

    # 获取查询的embedding
    query_task = get_embedding(query)
    tasks.append(query_task)

    # 获取所有chunk的embeddings
    chunk_tasks = [get_embedding(chunk) for chunk in chunks]
    tasks.extend(chunk_tasks)

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        raise ValueError(f"failed to get embeddings: {e!s}") from e  # noqa: TRY003

    # 分离查询embedding和chunk embeddings
    query_emb = results[0]
    chunk_results = results[1:]

    if query_emb is None or isinstance(query_emb, Exception):
        raise ValueError("failed to get query embedding.")  # noqa: TRY003

    # 收集成功的chunk embeddings
    chunk_embs = []
    valid_chunks = []

    for i, emb in enumerate(chunk_results):
        if emb is not None and not isinstance(emb, Exception):
            chunk_embs.append(emb)
            valid_chunks.append(chunks[i])

    if not chunk_embs:
        raise ValueError("failed to get chunk embeddings.")  # noqa: TRY003

    # 计算相似度
    chunk_embs = np.array(chunk_embs)
    scores = cosine_similarity([query_emb], chunk_embs)[0]

    # 按相似度排序
    sorted_indices = np.argsort(scores)[::-1]

    # 根据token限制选择chunks
    selected_chunks = []
    total_tokens = 0

    for idx in sorted_indices:
        chunk = valid_chunks[idx]
        chunk_tokens = count_token(chunk)

        # 如果加入这个chunk后不会超过限制，就加入
        if total_tokens + chunk_tokens <= limit:
            selected_chunks.append(chunk)
            total_tokens += chunk_tokens
        else:
            # 如果超过限制但还没有选择任何chunk，至少选择一个
            if not selected_chunks:
                selected_chunks.append(chunk)
            break

    # 如果没有选择到任何chunk，返回相似度最高的一个
    if not selected_chunks:
        best_idx = sorted_indices[0]
        selected_chunks = [valid_chunks[best_idx]]

    result = "\n".join(selected_chunks)
    return result
