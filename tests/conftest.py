import json
from pathlib import Path

import pytest


def pytest_addoption(parser):
    """pytest options"""
    parser.addoption(
        "--search",
        action="store",
        default="tests/data/search/1.json",
        help="The search parameters",
    )
    parser.addoption(
        "--summarize",
        action="store",
        default="tests/data/summarize/1.json",
        help="The summarize parameters",
    )
    parser.addoption(
        "--title",
        action="store",
        default="tests/data/title/1.json",
        help="The title parameters",
    )


def read_text(file: Path):
    if not file.exists():
        pytest.fail(f"File {file} does not exist")
    return file.read_text()


def read_json(file: Path):
    if not file.exists():
        pytest.fail(f"File {file} does not exist")
    return json.loads(file.read_text())


@pytest.fixture
def search_parameters(request):
    search_parameters = read_json(
        file=Path(request.config.getoption("--search")),
    )
    search_parameters["text"] = read_text(
        file=Path(search_parameters["text_path"]),
    )
    assert search_parameters["query"] is not None
    assert search_parameters["token_limit"] is not None
    assert search_parameters["text"] is not None
    return search_parameters


@pytest.fixture
def summarize_parameters(request):
    summarize_parameters = read_json(
        file=Path(request.config.getoption("--summarize")),
    )
    summarize_parameters["text"] = read_text(
        file=Path(summarize_parameters["text_path"]),
    )
    assert summarize_parameters["text"] is not None
    return summarize_parameters


@pytest.fixture
def title_parameters(request):
    title_parameters = read_json(
        file=Path(request.config.getoption("--title")),
    )
    title_parameters["text"] = read_text(
        file=Path(title_parameters["text_path"]),
    )
    assert title_parameters["text"] is not None
    return title_parameters
