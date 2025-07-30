import asyncio
import hashlib
import os
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from openai import AsyncOpenAI
from promptools.openai import count_token
from sklearn.metrics.pairwise import cosine_similarity

client = AsyncOpenAI(
    api_key=os.getenv("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


@dataclass
class Chunk:
    line_id: int
    line_len: int
    text: str
    tokens: int
    embedding: np.ndarray | None = None


def create_file_name(text: str | list[str], algorithm: str = "sha256") -> Path:
    if isinstance(text, list):
        text = "".join(text)
    hash = hashlib.new(algorithm)
    hash.update(text.encode("utf-8"))
    return Path(f"{hash.hexdigest()}.pkl")


def get_cached_chunks(text: str | list[str]) -> list[Chunk]:
    if isinstance(text, list):
        text = "".join(text)
    file_name = create_file_name(text)
    cache_dir = Path("cache/chunks")
    if (cache_dir / file_name).exists():
        with Path(cache_dir / file_name).open("rb") as cache_file:
            return pickle.load(cache_file)
    return []


def cache_chunks(text: str | list[str], chunks: list[Chunk]):
    if isinstance(text, list):
        text = "".join(text)
    file_name = create_file_name(text)
    cache_dir = Path("cache/chunks")
    cache_dir.mkdir(parents=True, exist_ok=True)

    if (cache_dir / file_name).exists():
        return

    with Path(cache_dir / file_name).open("wb") as cache_file:
        pickle.dump(chunks, cache_file)


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


async def get_embedding(text: str) -> np.ndarray:
    try:
        completion = await client.embeddings.create(
            model="text-embedding-v4",
            input=text,
            dimensions=1024,
            encoding_format="float",
            # timeout=timeout,
        )
        return np.array(completion.data[0].embedding)
    except Exception:
        raise ValueError("failed to get embedding.")  # noqa: TRY003


async def update_chunk_embeddings(chunks: list[Chunk], timeout: float = 6.0):
    valid_chunks = []
    tasks = [get_embedding(chunk.text) for chunk in chunks]
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


async def get_chunks(text: str | list[str]) -> list[Chunk]:
    cached_chunks = get_cached_chunks(text)
    if cached_chunks:
        return cached_chunks

    chunks = split_text(text)
    chunks = await update_chunk_embeddings(chunks)
    cache_chunks(text, chunks)
    return chunks


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
    chunks = await get_chunks(input)

    # get the query embedding and chunk embeddings
    query_emb = await get_embedding(query)

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
