# MCP Doubao 接入 Claude Code 使用指南

## 概述

本指南说明如何将 MCP Doubao 服务器接入到 Claude Code 中，实现在 Claude Code 内直接调用豆包图片生成功能。

## 前置条件

1. ✅ **Claude Code** 已安装并运行
2. ✅ **MCP Doubao 项目** 已完成设置（当前项目）
3. ✅ **API Key** 已配置（已设置在 config.py 中）

## 接入步骤

### 方法一：命令行快速注册

```bash
# 进入项目目录
cd /Users/jeffzhuo/Documents/Project/cycle_desk/seedream_mcp

# 注册 MCP 服务器
claude mcp add mcp-doubao -- uv run python -m mcp_doubao.server
```

### 方法二：JSON 配置（推荐）

```bash
# 使用 JSON 配置方式注册
claude mcp add-json mcp-doubao '{
  "type": "stdio",
  "command": "uv",
  "args": ["run", "python", "-m", "mcp_doubao.server"],
  "cwd": "/Users/jeffzhuo/Documents/Project/cycle_desk/seedream_mcp"
}'
```

### 方法三：手动编辑配置文件

1. **找到配置文件位置**：
   ```bash
   # 配置文件通常位于
   ~/.claude.json
   ```

2. **编辑配置文件**：
   ```json
   {
     "mcpServers": {
       "mcp-doubao": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "python", "-m", "mcp_doubao.server"],
         "cwd": "/Users/jeffzhuo/Documents/Project/cycle_desk/seedream_mcp"
       }
     }
   }
   ```

3. **重启 Claude Code** 以加载新配置

## 验证接入

### 1. 检查服务器状态

```bash
# 列出已注册的 MCP 服务器
claude mcp list
```

应该看到 `mcp-doubao` 服务器已列出。

### 2. 在 Claude Code 中验证

在 Claude Code 中运行：
```
/mcp
```

应该看到 `mcp-doubao` 服务器状态为 "connected"。

## 使用方法

### 基本图片生成

在 Claude Code 中，你可以直接要求 Claude 生成图片：

```
请帮我生成一张可爱小猫的图片
```

Claude 会自动调用 `generate_images` 工具。

### 高级参数控制

你也可以指定详细参数：

```
请生成3张不同风格的山水画，保存到 ./artwork 目录，不要水印
```

对应的工具调用参数：
- `prompt`: "三张不同风格的山水画"
- `num_images`: 3
- `output_dir`: "./artwork"
- `watermark`: false
- `size`: "2K" (默认)

## 工具参数说明

### `generate_images` 工具参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `prompt` | string | ✅ | - | 图片生成的文本描述 |
| `num_images` | integer | ❌ | 1 | 生成图片数量 (1-3) |
| `size` | string | ❌ | "2K" | 图片尺寸 ("1K", "2K", "4K") |
| `watermark` | boolean | ❌ | false | 是否添加水印 |
| `output_dir` | string | ❌ | "." | 图片保存目录 |

### 尺寸说明

- **1K**: 1024x1024 像素
- **2K**: 2048x2048 像素
- **4K**: 4096x4096 像素

## 使用示例

### 示例 1：简单生成
```
用户：生成一张日落海滩的图片
Claude：[调用 generate_images 工具生成并下载图片]
```

### 示例 2：批量生成
```
用户：生成3张不同季节的风景图，保存到 seasons 文件夹
Claude：[使用参数 num_images=3, output_dir="seasons"]
```

### 示例 3：高质量生成
```
用户：生成一张4K分辨率的抽象艺术作品，带水印
Claude：[使用参数 size="4K", watermark=true]
```

## 故障排除

### 服务器连接失败

1. **检查项目路径**：确保 `cwd` 指向正确的项目目录
2. **检查依赖**：确保 `uv` 可用且项目依赖已安装
3. **检查 API Key**：确认 config.py 中的 API Key 有效

### 图片生成失败

1. **网络连接**：确保可以访问豆包 API 服务
2. **API 配额**：检查 API Key 是否有足够配额
3. **参数验证**：确认传入参数符合要求

### 图片下载失败

1. **目录权限**：确保输出目录有写入权限
2. **磁盘空间**：确保有足够的存储空间
3. **网络稳定**：图片下载需要稳定的网络连接

## 日志调试

如需查看详细日志，可以：

1. **启用详细日志**：
   ```bash
   # 在项目目录下手动运行服务器查看日志
   uv run python -m mcp_doubao.server
   ```

2. **Claude Code 调试模式**：
   ```bash
   # 启动 Claude Code 时启用 MCP 调试
   claude --debug-mcp
   ```

## 注意事项

1. **API Key 安全**：不要将包含真实 API Key 的代码提交到公共仓库
2. **文件管理**：生成的图片会保存到指定目录，注意定期清理
3. **网络依赖**：图片生成和下载都需要网络连接
4. **并发限制**：避免同时进行大量图片生成请求

## 更新和维护

当需要更新 MCP 服务器时：

1. **停止服务**：重启 Claude Code
2. **更新代码**：拉取最新代码并安装依赖
3. **重新启动**：重启 Claude Code 重新加载服务器

---

现在你可以在 Claude Code 中直接使用自然语言请求生成图片，Claude 会自动调用我们的 MCP Doubao 工具来完成任务！