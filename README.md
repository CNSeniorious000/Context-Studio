# Context Studio Backend

Context Studio 的后端服务，提供文件内容提取、智能分析和文本处理的 API 接口。配合 [Context-Studio-FE](https://github.com/CNSeniorious000/Context-Studio-FE) 前端应用，为用户提供完整的 AI 系统消息构建和管理解决方案。

## 功能特性

- **文件内容提取**：基于 MarkItDown 库，支持将多种格式的文件（PDF、图片、音频、Office 文档等）转换为 Markdown 格式的纯文本
- **智能标题生成**：利用 AI 模型为提取的文本内容自动生成简洁准确的标题
- **内容摘要**：通过 AI 模型为长文本生成精炼的摘要
- **模糊搜索**：在文本内容中进行智能搜索，支持语义匹配和关键词查找
- **Token 计算**：精确计算文本内容的 token 数量，便于 AI 模型使用
- **跨域支持**：内置 CORS 中间件，支持前端应用的跨域请求

## API 接口

### `POST /markitdown`
将上传的文件转换为 Markdown 格式
- **请求**：`application/octet-stream` 格式的文件数据
- **响应**：`text/markdown` 格式的文本内容
- **响应头**：包含 `title`（文件标题）和 `token-count`（token 数量）

### `POST /generate_title`
为文本内容生成标题
- **请求**：`text/plain` 格式的文本内容
- **响应**：生成的标题文本

### `POST /summarize`
生成文本摘要
- **请求**：`text/plain` 格式的文本内容
- **响应**：文本摘要

### `POST /fuzzy_search`
在文本中进行模糊搜索
- **请求**：JSON 格式，包含 `query`（搜索词）、`input`（搜索内容）、`token_limit`（结果限制）
- **响应**：搜索结果文本

## 技术栈

- **Web 框架**：[FastAPI](https://fastapi.tiangolo.com/) - 高性能异步 Python Web 框架
- **文件处理**：[MarkItDown](https://github.com/microsoft/markitdown) - 多格式文件到 Markdown 的转换工具
- **AI 模型**：OpenAI API（通过 PPIO 基础设施）- 提供标题生成和摘要功能
- **文本处理**：
  - `tiktoken` - Token 计算
  - `scikit-learn` - 文本向量化和搜索
  - `numpy` - 数值计算
- **开发工具**：
  - `ruff` - Python 代码检查和格式化
  - `pytest` - 单元测试框架
  - `uvicorn` - ASGI 服务器

## 快速开始

### 环境要求
- Python 3.13+
- 设置环境变量 `PPIO_API_KEY` 用于 AI 功能

### 安装依赖
```bash
pip install -e .
```

### 开发模式
```bash
python -m uvicorn main:app --reload
```

### 生产部署
```bash
# 使用 Docker
docker build -t context-studio-backend .
docker run -p 8000:8000 -e PPIO_API_KEY=your_api_key context-studio-backend

# 或直接运行
python -Om uvicorn main:app --host 0.0.0.0
```

### 运行测试
```bash
pytest
```

## 项目结构

```
├── main.py              # FastAPI 应用入口
├── extractors/          # 文件内容提取器
│   └── fallback.py      # 基于 MarkItDown 的通用提取器
├── processors/          # 文本处理器
│   ├── title.py         # 标题生成
│   ├── summarize.py     # 内容摘要
│   └── fuzzy_search.py  # 模糊搜索
├── tests/               # 单元测试
└── Dockerfile           # Docker 构建文件
```

## 相关项目

- [Context-Studio-FE](https://github.com/CNSeniorious000/Context-Studio-FE) - 前端用户界面，基于 Svelte 构建的现代化 Web 应用
