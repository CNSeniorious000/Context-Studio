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
    line_id: int
    line_len: int
    text: str
    tokens: int
    embedding: np.ndarray | None = None


def split_text(input: str | list[str], chunk_size: int = 200) -> list[Chunk]:
    # if text is a list, return a list of dicts
    if isinstance(input, list):
        chunks = [Chunk(line_id=i, line_len=1, text=line, tokens=count_token(line)) for i, line in enumerate(input)]
        return chunks

    if not input.strip():
        return []

    # if input is a string, split it into chunks
    chunks = []
    lines_splited = input.splitlines(keepends=True)
    lines = []
    for line in lines_splited:
        if lines and line == "\n":
            lines[-1] += "\n"
        else:
            lines.append(line)

    current_chunk = ""
    current_tokens = 0
    current_len_id = 0
    current_line_len = 0

    for i, line in enumerate(lines):
        line_tokens = count_token(line)

        # if the current line will exceed the chunk_size, save the current chunk
        if current_tokens + line_tokens > chunk_size and current_chunk.strip():
            chunks.append(Chunk(line_id=current_len_id, line_len=current_line_len, text=current_chunk.strip(), tokens=current_tokens))
            current_chunk = line
            current_tokens = line_tokens
            current_line_len = 1
            current_len_id = i
        else:
            # otherwise, add the line to the current chunk
            current_line_len += 1
            if current_chunk:
                current_chunk += line
                current_tokens += line_tokens
            else:
                current_chunk = line
                current_tokens = line_tokens

    # add the last chunk
    if current_chunk.strip():
        chunks.append(Chunk(line_id=current_len_id, line_len=current_line_len, text=current_chunk.strip(), tokens=current_tokens))

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
            valid_chunks.append(
                Chunk(
                    line_id=chunks[i].line_id,
                    line_len=chunks[i].line_len,
                    text=chunks[i].text,
                    tokens=chunks[i].tokens,
                    embedding=emb,
                )
            )
    return valid_chunks


def rerank_chunk_with_similarity(query_emb: np.ndarray, chunks: list[Chunk]):
    chunk_embs = np.array([chunk.embedding for chunk in chunks])
    scores = cosine_similarity([query_emb], chunk_embs)[0]
    sorted_indices = np.argsort(scores)[::-1]
    reranked_chunks = [chunks[idx] for idx in sorted_indices]

    if not reranked_chunks:
        raise ValueError("failed to get chunk embeddings.")  # noqa: TRY003

    return reranked_chunks


def sorted_chunk_with_id(chunks: list[Chunk]):
    sorted_chunks = sorted(chunks, key=lambda x: x.line_id)
    return sorted_chunks


def merged_chunk_with_id(chunks: list[Chunk]):
    merged_chunks = []
    for chunk in chunks:
        if merged_chunks and merged_chunks[-1].line_id + merged_chunks[-1].line_len == chunk.line_id:
            merged_chunks[-1].text += chunk.text
            merged_chunks[-1].line_len += chunk.line_len
        else:
            merged_chunks.append(chunk)
    return merged_chunks


def select_chunks_by_limit(reranked_chunks: list[Chunk], limit: int) -> list[Chunk]:
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

    return selected_chunks


def join_chunks(chunks: list[Chunk], chunks_len: int) -> str:
    joined_chunks_str = ""
    for i, chunk in enumerate(chunks):
        if i == 0:
            cut_line_len = chunk.line_id
        else:
            pre_chunk = chunks[i - 1]
            cut_line_len = chunk.line_id - pre_chunk.line_id - pre_chunk.line_len
        if cut_line_len > 0:
            joined_chunks_str += f"[... skip {cut_line_len} lines ...]\n\n\n"
        joined_chunks_str += chunk.text
        if i != len(chunks) - 1:
            joined_chunks_str += "\n\n\n"

    cut_line_len = chunks_len - chunks[-1].line_id - chunks[-1].line_len - 1
    if cut_line_len > 0:
        joined_chunks_str += f"\n\n\n[... skip {cut_line_len} lines ...]"

    return joined_chunks_str


async def fuzzy_search(query: str, input: str | list[str], token_limit: int = 500) -> str:
    # if input is a string, split it into chunks
    chunks = split_text(input=input)

    # get the query embedding and chunk embeddings
    query_emb = await get_embedding(query)
    if query_emb is None:
        raise ValueError("failed to get query embedding.")  # noqa: TRY003

    chunks = await update_chunk_embeddings(chunks)

    # rerank the chunks by similarity
    reranked_chunks = rerank_chunk_with_similarity(query_emb, chunks)

    # select the chunks by token limit
    selected_chunks = select_chunks_by_limit(reranked_chunks, token_limit)

    # sorted the chunks by id
    sorted_chunks = sorted_chunk_with_id(selected_chunks)

    # merged the chunks with adjacent id
    merged_chunks = merged_chunk_with_id(sorted_chunks)

    # join the chunks
    result = join_chunks(merged_chunks, chunks[-1].line_id + chunks[-1].line_len - 1)
    return result
