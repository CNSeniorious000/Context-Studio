"""Test configuration settings."""

import pytest

from config import ai_client_settings, app_settings, model_settings, processing_settings


def test_ai_client_settings():
    """Test that AI client settings are properly loaded."""
    assert ai_client_settings.ppio_api_key == "dummy_ppio_key_for_testing"
    assert ai_client_settings.aliyun_api_key == "dummy_aliyun_key_for_testing"
    assert ai_client_settings.ppio_base_url == "https://api.ppinfra.com/v3/openai"
    assert ai_client_settings.aliyun_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"


def test_model_settings():
    """Test that model settings are properly loaded."""
    assert model_settings.title_model == "deepseek/deepseek-v3-0324"
    assert model_settings.summarize_model == "deepseek/deepseek-v3-0324"
    assert model_settings.condense_model == "qwen-turbo"
    assert model_settings.embedding_model == "text-embedding-v4"
    assert model_settings.title_max_tokens == 1024
    assert model_settings.title_temperature == 0.0
    assert model_settings.summarize_temperature == 0.0
    assert model_settings.embedding_dimensions == 1024


def test_processing_settings():
    """Test that processing settings are properly loaded."""
    assert processing_settings.title_text_limit == 2000
    assert processing_settings.default_token_limit == 100
    assert processing_settings.fuzzy_search_chunk_size == 200
    assert processing_settings.summarize_process_length == 10000
    assert processing_settings.condense_max_words == 100
    assert processing_settings.cache_directory == "cache/chunks"


def test_app_settings():
    """Test that app settings are properly loaded."""
    assert app_settings.app_title == "Context Manager Extractor API"
    assert app_settings.debug_mode is True
    assert app_settings.cors_enabled is True


def test_client_instantiation():
    """Test that clients can be instantiated with configuration settings."""
    from processors.title import client as title_client
    from processors.summarize import aclient, pclient
    from processors.fuzzy_search import client as search_client

    # Test that clients have the correct API keys and base URLs
    # Note: OpenAI client normalizes URLs by adding trailing slash
    assert title_client.api_key == ai_client_settings.ppio_api_key
    assert str(title_client.base_url).rstrip('/') == ai_client_settings.ppio_base_url

    assert pclient.api_key == ai_client_settings.ppio_api_key
    assert str(pclient.base_url).rstrip('/') == ai_client_settings.ppio_base_url

    assert aclient.api_key == ai_client_settings.aliyun_api_key
    assert str(aclient.base_url).rstrip('/') == ai_client_settings.aliyun_base_url

    assert search_client.api_key == ai_client_settings.aliyun_api_key
    assert str(search_client.base_url).rstrip('/') == ai_client_settings.aliyun_base_url


def test_main_app_integration():
    """Test that main app uses configuration settings."""
    from main import app

    assert app.title == app_settings.app_title


def test_fuzzy_search_request_defaults():
    """Test that FuzzySearchRequest uses configuration defaults."""
    from main import FuzzySearchRequest

    # Create a request without specifying token_limit
    request = FuzzySearchRequest(query="test", input="test input")
    assert request.token_limit == processing_settings.default_token_limit