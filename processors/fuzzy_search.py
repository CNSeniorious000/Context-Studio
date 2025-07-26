import asyncio
import os
from dataclasses import dataclass

import numpy as np
from openai import AsyncOpenAI
from promptools.openai import count_token
from sklearn.metrics.pairwise import cosine_similarity

client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


@dataclass
class Chunk:
    text: str
    tokens: int
    embedding: np.ndarray | None = None


def split_text(input: str | list[str], chunk_size: int = 200) -> list[Chunk]:
    # if text is a list, return a list of dicts
    if isinstance(input, list):
        chunks = [Chunk(text=line, tokens=count_token(line)) for line in input]
        return chunks

    if not input.strip():
        return []

    # if input is a string, split it into chunks
    chunks = []
    lines = input.splitlines(keepends=True)
    current_chunk = ""
    current_tokens = 0

    for line in lines:
        line_tokens = count_token(line)

        # if the current line will exceed the chunk_size, save the current chunk
        if current_tokens + line_tokens > chunk_size and current_chunk.strip():
            chunks.append(Chunk(text=current_chunk.strip(), tokens=current_tokens))
            current_chunk = line
            current_tokens = line_tokens
        else:
            # otherwise, add the line to the current chunk
            if current_chunk:
                current_chunk += line
                current_tokens += line_tokens
            else:
                current_chunk = line
                current_tokens = line_tokens

    # add the last chunk
    if current_chunk.strip():
        chunks.append(Chunk(text=current_chunk.strip(), tokens=current_tokens))

    if not chunks:
        raise ValueError("input is empty.")  # noqa: TRY003

    return chunks


async def get_embedding(text: str) -> np.ndarray | None:
    try:
        completion = await client.embeddings.create(
            model="text-embedding-v4",
            input=text,
            dimensions=1024,
            encoding_format="float",
        )
        return np.array(completion.data[0].embedding)
    except Exception:
        return None


async def update_chunk_embeddings(chunks: list[Chunk], timeout: float = 6.0):
    valid_chunks = []
    tasks = [asyncio.wait_for(get_embedding(chunk.text), timeout=timeout) for chunk in chunks]
    emb_results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, emb in enumerate(emb_results):
        if isinstance(emb, np.ndarray):
            valid_chunks.append(Chunk(text=chunks[i].text, tokens=chunks[i].tokens, embedding=emb))
    return valid_chunks


def rerank_chunk(query_emb: np.ndarray, chunks: list[Chunk]):
    chunk_embs = np.array([chunk.embedding for chunk in chunks])
    scores = cosine_similarity([query_emb], chunk_embs)[0]
    sorted_indices = np.argsort(scores)[::-1]
    reranked_chunks = [chunks[idx] for idx in sorted_indices]

    if not reranked_chunks:
        raise ValueError("failed to get chunk embeddings.")  # noqa: TRY003

    return reranked_chunks


def select_chunks_by_limit(reranked_chunks: list[Chunk], limit: int) -> str:
    total_tokens = 0
    selected_chunks = []

    for chunk in reranked_chunks:
        chunk_tokens = chunk.tokens

        # if adding this chunk will not exceed the limit, add it
        if total_tokens + chunk_tokens <= limit:
            selected_chunks.append(chunk)
            total_tokens += chunk_tokens
        else:
            break

    if not selected_chunks:
        selected_chunks = [reranked_chunks[0]]

    result = "\n".join([chunk.text for chunk in selected_chunks])
    return result


async def fuzzy_search(query: str, input: str | list[str], limit: int = 50) -> str:
    # if input is a string, split it into chunks
    chunks = split_text(input=input)

    # get the query embedding and chunk embeddings
    query_emb = await get_embedding(query)
    if query_emb is None:
        raise ValueError("failed to get query embedding.")  # noqa: TRY003

    chunks = await update_chunk_embeddings(chunks)

    # rerank the chunks
    reranked_chunks = rerank_chunk(query_emb, chunks)

    # select the chunks based on the limit
    result = select_chunks_by_limit(reranked_chunks, limit)
    return result
