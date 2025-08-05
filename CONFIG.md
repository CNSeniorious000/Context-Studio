# 配置管理

本项目使用 `pydantic-settings` 进行集中式配置管理。所有配置参数都可以通过环境变量或 `.env` 文件进行设置。

## 配置文件

- **`config.py`**: 包含所有配置类和设置
- **`.env.example`**: 配置示例文件，包含所有可用参数
- **`.env`**: 您的本地配置文件（不会提交到 git）

## 配置参数

### API 客户端设置
- `PPIO_API_KEY`: PPIO 服务的 API 密钥
- `PPIO_BASE_URL`: PPIO API 基础 URL（默认值：https://api.ppinfra.com/v3/openai）
- `ALIYUN_API_KEY`: 阿里云服务的 API 密钥
- `ALIYUN_BASE_URL`: 阿里云 API 基础 URL（默认值：https://dashscope.aliyuncs.com/compatible-mode/v1）

### 模型设置
- `TITLE_MODEL`: 标题生成模型（默认值：deepseek/deepseek-v3-0324）
- `SUMMARIZE_MODEL`: 文本摘要模型（默认值：deepseek/deepseek-v3-0324）
- `CONDENSE_MODEL`: 文本压缩模型（默认值：qwen-turbo）
- `EMBEDDING_MODEL`: 嵌入向量模型（默认值：text-embedding-v4）
- `TITLE_MAX_TOKENS`: 标题生成最大 token 数（默认值：1024）
- `TITLE_TEMPERATURE`: 标题生成温度参数（默认值：0.0）
- `SUMMARIZE_TEMPERATURE`: 摘要生成温度参数（默认值：0.0）
- `EMBEDDING_DIMENSIONS`: 嵌入向量维度（默认值：1024）

### 文本处理设置
- `TITLE_TEXT_LIMIT`: 标题生成的最大文本长度（默认值：2000）
- `DEFAULT_TOKEN_LIMIT`: 模糊搜索的默认 token 限制（默认值：100）
- `FUZZY_SEARCH_CHUNK_SIZE`: 模糊搜索的块大小（默认值：200）
- `SUMMARIZE_PROCESS_LENGTH`: 摘要处理长度（默认值：10000）
- `CONDENSE_MAX_WORDS`: 文本压缩最大词数（默认值：100）
- `CACHE_DIRECTORY`: 块缓存目录（默认值：cache/chunks）

### 应用程序设置
- `APP_TITLE`: FastAPI 应用程序标题（默认值：Context Manager Extractor API）
- `DEBUG_MODE`: 启用调试模式（默认值：true）
- `CORS_ENABLED`: 在生产环境启用 CORS（默认值：true）

## 使用方法

### 设置配置：

1. 复制示例环境文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置您的实际值：
   ```bash
   PPIO_API_KEY=your_actual_ppio_key
   ALIYUN_API_KEY=your_actual_aliyun_key
   ```

3. 应用程序将自动加载这些设置。

### 在代码中使用：

```python
from config import settings

# 访问配置值
api_key = settings.ppio_api_key
model_name = settings.title_model
token_limit = settings.default_token_limit
```

## 优势

- **集中化**: 所有配置都在一个地方
- **验证**: Pydantic 自动验证类型和值
- **灵活**: 可以通过环境变量轻松覆盖
- **安全**: 敏感值保存在 `.env` 中（不提交到 git）
- **文档化**: 清晰的字段描述和默认值
- **类型安全**: 完整的类型提示和 IDE 支持

## 测试

运行配置测试以验证一切正常工作：

```bash
python -m pytest tests/test_config.py -v
```

## 相关链接

- [Pydantic Settings 官方文档](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI 配置和环境变量](https://fastapi.tiangolo.com/advanced/settings/)
- [环境变量最佳实践](https://12factor.net/config)
- [PPIO API 文档](https://api.ppinfra.com/docs)
- [阿里云大模型服务](https://help.aliyun.com/zh/dashscope/)
- [DeepSeek API 文档](https://api-docs.deepseek.com/)
- [通义千问模型文档](https://help.aliyun.com/zh/dashscope/developer-reference/model-introduction)
- [Python dotenv 使用指南](https://github.com/theskumar/python-dotenv)

## 配置示例

### 开发环境配置
```bash
# .env 开发环境示例
PPIO_API_KEY=sk-your-development-key
ALIYUN_API_KEY=sk-your-aliyun-dev-key
DEBUG_MODE=true
TITLE_TEMPERATURE=0.1
```

### 生产环境配置
```bash
# .env 生产环境示例
PPIO_API_KEY=sk-your-production-key
ALIYUN_API_KEY=sk-your-aliyun-prod-key
DEBUG_MODE=false
CORS_ENABLED=true
TITLE_TEMPERATURE=0.0
```