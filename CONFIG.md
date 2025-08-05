# Configuration Management

This project now uses `pydantic-settings` for centralized configuration management. All configuration parameters can be set via environment variables or an `.env` file.

## Configuration Files

- **`config.py`**: Contains all configuration classes and settings
- **`.env.example`**: Example configuration file with all available parameters
- **`.env`**: Your local configuration (not committed to git)

## Configuration Classes

### AIClientSettings
- `PPIO_API_KEY`: API key for PPIO services
- `PPIO_BASE_URL`: Base URL for PPIO API (default: https://api.ppinfra.com/v3/openai)
- `ALIYUN_API_KEY`: API key for Aliyun services
- `ALIYUN_BASE_URL`: Base URL for Aliyun API (default: https://dashscope.aliyuncs.com/compatible-mode/v1)

### ModelSettings
- `TITLE_MODEL`: Model for title generation (default: deepseek/deepseek-v3-0324)
- `SUMMARIZE_MODEL`: Model for summarization (default: deepseek/deepseek-v3-0324)
- `CONDENSE_MODEL`: Model for text condensing (default: qwen-turbo)
- `EMBEDDING_MODEL`: Model for embeddings (default: text-embedding-v4)
- `TITLE_MAX_TOKENS`: Max tokens for title generation (default: 1024)
- `TITLE_TEMPERATURE`: Temperature for title generation (default: 0.0)
- `SUMMARIZE_TEMPERATURE`: Temperature for summarization (default: 0.0)
- `EMBEDDING_DIMENSIONS`: Embedding dimensions (default: 1024)

### ProcessingSettings
- `TITLE_TEXT_LIMIT`: Max text length for title generation (default: 2000)
- `DEFAULT_TOKEN_LIMIT`: Default token limit for fuzzy search (default: 100)
- `FUZZY_SEARCH_CHUNK_SIZE`: Chunk size for fuzzy search (default: 200)
- `SUMMARIZE_PROCESS_LENGTH`: Process length for summarization (default: 10000)
- `CONDENSE_MAX_WORDS`: Max words for text condensing (default: 100)
- `CACHE_DIRECTORY`: Directory for caching chunks (default: cache/chunks)

### AppSettings
- `APP_TITLE`: FastAPI application title (default: Context Manager Extractor API)
- `DEBUG_MODE`: Enable debug mode (default: true)
- `CORS_ENABLED`: Enable CORS in production (default: true)

## Usage

### Setting up configuration:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   PPIO_API_KEY=your_actual_ppio_key
   ALIYUN_API_KEY=your_actual_aliyun_key
   ```

3. The application will automatically load these settings.

### Using in code:

```python
from config import ai_client_settings, model_settings, processing_settings, app_settings

# Access configuration values
api_key = ai_client_settings.ppio_api_key
model_name = model_settings.title_model
token_limit = processing_settings.default_token_limit
```

## Benefits

- **Centralized**: All configuration in one place
- **Validated**: Pydantic validates types and values
- **Flexible**: Easy to override via environment variables
- **Secure**: Sensitive values kept in `.env` (not committed)
- **Documented**: Clear field descriptions and defaults
- **Type-safe**: Full type hints and IDE support

## Testing

Run the configuration tests to verify everything is working:

```bash
python -m pytest tests/test_config.py -v
```