# MCP Doubao Seedream 4.0 - 豆包图片生成 MCP 服务器

一个基于 Model Context Protocol (MCP) 的豆包 Seedream 4.0 模型的文生图服务器，可以直接集成到 Claude Code 中使用。

## 功能特性

- 🎨 **AI 图片生成**：基于豆包 Seedream 模型的文生图功能
- 📁 **自动下载**：生成的图片自动下载到指定目录
- 🔧 **灵活配置**：支持多种尺寸、水印控制、批量生成
- 🚀 **即插即用**：通过 MCP 协议无缝集成到 Claude Code
- 💾 **本地存储**：图片保存到本地，便于后续使用

## 快速开始

### 1. 环境要求

- Python 3.11+
- uv (推荐) 或 pip
- Claude Code

### 2. 安装

```bash
# 克隆项目
git clone <your-repo-url>
cd seedream_mcp

# 方法一：使用 uv（推荐）
uv sync

# 方法二：使用 pip
pip install -r requirements.txt
```

**注意**：`requirements.txt` 通过以下命令生成：
```bash
uv export --format requirements.txt --output-file requirements.txt
```

### 3. 配置

设置豆包 API 密钥环境变量：

```bash
export ARK_API_KEY="your-api-key-here"
```

或在 Claude Code 配置中设置：

```json
{
  "mcpServers": {
    "mcp-doubao": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_doubao.server"],
      "cwd": "/path/to/your/seedream_mcp",
      "env": {
        "ARK_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 4. 测试运行

```bash
# 测试服务器
uv run python -m mcp_doubao.server

# 测试图片生成（可选）
uv run python -c "
import asyncio
import sys
sys.path.append('src')
from mcp_doubao.tools import handle_generate_images

async def test():
    result = await handle_generate_images({
        'prompt': '一只可爱的小猫',
        'output_dir': './test_images'
    })
    print(result[0].text)

asyncio.run(test())
"
```

### 5. 接入 Claude Code

详细接入步骤请查看 [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

#### 方法一：使用启动脚本（推荐）

使用项目提供的启动脚本，自动设置虚拟环境和 Python 路径：

```json
{
  "mcpServers": {
    "mcp-doubao": {
      "type": "stdio",
      "command": "/path/to/your/seedream_mcp/start_mcp_server.sh",
      "env": {
        "ARK_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### 方法二：使用 uv 命令

```bash
claude mcp add-json mcp-doubao '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "python", "-m", "mcp_doubao.server"],
  "cwd": "/path/to/your/seedream_mcp",
  "env": {
    "ARK_API_KEY": "your-api-key-here"
  }
}'
```

## 使用方法

### 基本使用

在 Claude Code 中直接用自然语言请求：

```
请生成一张樱花飞舞的图片
```

### 高级参数

```
生成3张不同风格的山水画，4K分辨率，保存到artwork文件夹，不要水印
```

### 工具参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | string | 必填 | 图片描述文本 |
| `num_images` | int | 1 | 生成数量 (1-3) |
| `size` | string | "2K" | 尺寸 ("1K"/"2K"/"4K" 或具体像素如 "2048x2048") |
| `watermark` | bool | false | 是否添加水印 |
| `output_dir` | string | "." | 保存目录 |
| `image_paths` | array | [] | 可选的参考图片路径列表 (1-10张) |
| `sequential_image_generation` | string | "disabled" | 组图模式 ("auto"/"disabled") |
| `max_images` | int | 3 | 组图模式下最大生成数量 (1-15) |

## 项目结构

```
seedream_mcp/
├── src/mcp_doubao/
│   ├── __init__.py          # 模块初始化
│   ├── server.py            # MCP 服务器入口
│   ├── tools.py             # 工具定义和处理
│   ├── doubao_client.py     # 豆包 API 客户端
│   ├── downloader.py        # 图片下载器
│   ├── config.py            # 配置常量
│   └── types.py             # 数据类型定义
├── start_mcp_server.sh      # Claude Code 启动脚本（推荐使用）
├── scripts/
│   └── run_stdio.sh         # 备用启动脚本
├── examples/
│   └── prompts.txt          # 示例提示词
├── tests/                   # 测试文件
├── .venv/                   # Python 虚拟环境
├── pyproject.toml          # 项目配置
├── README.md               # 项目说明
└── INTEGRATION_GUIDE.md    # 接入指南
```

## 技术实现

### MCP 协议

基于 Model Context Protocol 1.14.1+ 实现，提供标准化的工具接口。

### API 集成

- **SDK**: volcengine-python-sdk[ark] 4.0.21+
- **模型**: doubao-seedream-4-0-250828
- **端点**: https://ark.cn-beijing.volces.com/api/v3

### 图片下载

- **HTTP 客户端**: httpx 0.28.1+
- **文件命名**: image_001.jpeg, image_002.jpeg...（自动避免覆盖）
- **格式支持**: JPEG, PNG, WebP 等
- **防覆盖**: 如果文件已存在，自动添加数字后缀

## 开发说明

### 启动脚本功能

`start_mcp_server.sh` 脚本的特性：

- **自动环境设置**：自动使用项目的 `.venv` 虚拟环境
- **路径配置**：自动设置 `PYTHONPATH` 到项目的 `src` 目录
- **工作目录**：自动切换到项目根目录
- **环境变量**：可通过 Claude Code 配置传入 `ARK_API_KEY`

### 本地开发

```bash
# 使用启动脚本（推荐）
./start_mcp_server.sh

# 或使用 uv 命令
uv run python -m mcp_doubao.server

# 运行测试
uv run python -m pytest tests/

# 代码格式化
uv run ruff format src/

# 更新 requirements.txt（添加新依赖后）
uv export --format requirements.txt --output-file requirements.txt
```

### 扩展功能

现有架构支持轻松扩展：

- 添加新的图片参数（引导参数、种子等）
- 支持图生图功能
- 增加数据库记录
- 添加配额管理

## 故障排除

### 常见问题

1. **导入错误**：确保所有依赖已正确安装
2. **API 错误**：检查 `ARK_API_KEY` 环境变量是否正确设置
3. **权限错误**：确保输出目录有写入权限
4. **图片覆盖**：系统会自动避免覆盖现有图片，生成唯一文件名

### 调试模式

```bash
# 启用详细日志
PYTHONPATH=src uv run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# ... 你的测试代码
"
```

## 依赖项

核心依赖：
- `mcp>=1.14.1` - Model Context Protocol
- `volcengine-python-sdk[ark]>=4.0.21` - 豆包 API SDK
- `httpx>=0.28.1` - HTTP 客户端

## 许可证

本项目基于 MIT 许可证开源。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.1.0 (2024-09-23)
- ✨ 初始版本发布
- 🎨 支持基础图片生成功能
- 📁 自动图片下载
- 🔧 MCP 协议集成
- 💾 本地文件存储