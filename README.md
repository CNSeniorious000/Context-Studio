# Context Studio Backend

Context Studio 的后端服务，提供文件内容提取、智能分析和文本处理的 API 接口。配合 [Context-Studio-FE](https://github.com/CNSeniorious000/Context-Studio-FE) 前端应用，为用户提供完整的 AI 系统消息构建和管理解决方案。

## 功能特性

- **文件内容提取**：基于 MarkItDown 库，支持将多种格式的文件（PDF、图片、音频、Office 文档等）转换为 Markdown 格式的纯文本
- **智能标题生成**：利用 AI 模型为提取的文本内容自动生成简洁准确的标题
- **内容摘要**：通过 AI 模型为长文本生成精炼的摘要
- **模糊搜索**：在文本内容中进行智能搜索，支持语义匹配和关键词查找
- **Token 计算**：精确计算文本内容的 token 数量，便于 AI 模型使用

## 模糊搜索算法原理

Context Studio 的模糊搜索功能采用基于语义相似度的智能文本压缩算法，能够从长文本中提取与查询最相关的片段，有效减少文本长度同时保持语义完整性。

### 核心工作流程

1. **文本分块 (Text Chunking)**
   - 将输入文本按行分割，每个块控制在约 200 个 token 以内
   - 保持文本的逻辑结构，避免在句子中间切断
   - 为每个块记录行号和长度信息，便于后续重组

2. **向量化编码 (Embedding Generation)**
   - 使用阿里云通义千问的 `text-embedding-v4` 模型
   - 为查询词和每个文本块生成 1024 维的语义向量
   - 支持缓存机制，避免重复计算相同文本的向量

3. **相似度计算与排序 (Similarity Ranking)**
   - 计算查询向量与所有文本块向量的余弦相似度
   - 按相似度分数从高到低重新排列文本块
   - 优先选择语义最匹配的内容片段

4. **智能选择与合并 (Smart Selection & Merging)**
   - 根据 token 限制从高分块中选择内容
   - 按原文档顺序重新排列选中的块
   - 合并相邻的文本块，保持内容连贯性
   - 在跳跃的块之间插入省略标记 `[... skip N lines ...]`

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
- **AI 模型**：[OpenAI API](https://platform.openai.com/)（通过 PPIO 基础设施）- 提供标题生成和摘要功能
- **文本处理**：
  - [`tiktoken`](https://github.com/openai/tiktoken) - Token 计算
  - [`scikit-learn`](https://scikit-learn.org/) - 文本向量化和搜索
  - [`numpy`](https://numpy.org/) - 数值计算
- **开发工具**：
  - [`ruff`](https://docs.astral.sh/ruff/) - Python 代码检查和格式化
  - [`pytest`](https://docs.pytest.org/) - 单元测试框架
  - [`uvicorn`](https://www.uvicorn.org/) - ASGI 服务器

## 快速开始

### 环境要求
- Python 3.13+
- 设置环境变量 `PPIO_API_KEY` 用于 AI 功能

### 安装依赖
```bash
uv sync
```
> 关于 uv sync 的详细说明，请参考 [uv 文档](https://docs.astral.sh/uv/concepts/projects/#project-environments)

### 开发模式
```bash
uvicorn-hmr main:app
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
