---
trigger: always_on
---

# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个基于 Flutter 的文档翻译应用程序，支持文档、图片和文本翻译，并提供订阅和支付服务。应用程序采用清晰的架构模式，使用 BLoC 状态管理，支持 Android 和 iOS 平台。

## 开发命令

### Flutter 命令
```bash
# 在开发模式下运行应用
flutter run

# 构建发布版本
flutter build apk --release
flutter build ios --release

# 运行测试
flutter test

# 运行代码检查
flutter analyze

# 生成代码（用于 JSON 序列化、Hive 适配器等）
flutter pub run build_runner build

# 清理构建缓存
flutter clean

# 获取依赖
flutter pub get

# 安装 iOS 依赖（如需要）
cd ios && pod install
```

### 代码生成
```bash
# 生成 JSON 序列化代码
flutter pub run build_runner build --delete-conflicting-outputs

# 监听更改并自动生成
flutter pub run build_runner watch --delete-conflicting-outputs
```

## 架构

### 核心架构模式
应用程序采用分层架构，具有清晰的职责分离：

```
┌─────────────┐
│     UI      │ 页面和组件（使用 BLoC 进行状态管理）
├─────────────┤
│    BLoC     │ 状态管理（事件/状态模式）
├─────────────┤
│  Services   │ 业务逻辑（协调 SDK 调用）
├─────────────┤
│  SDK/API    │ 网络层（直接 API 调用，带有请求/响应模型）
└─────────────┘
```

### 关键目录结构

- **`lib/blocs/`** - BLoC 状态管理，按功能模块组织
  - 每个功能都有自己对应的 BLoC、事件和状态
  - BLoC 是独立的

- **`lib/services/`** - 业务逻辑层
  - **`services/`** - 在应用模型和 SDK 数据之间转换的业务服务
  - **`services/sdk/`** - 带有请求/响应模型的直接 API 包装器
  - **`service_locator.dart`** - 使用 GetIt 的依赖注入设置

- **`lib/models/`** - 应用数据模型
  - 使用 JSON 注解进行序列化
  - 模型表示应用特定的数据结构

- **`lib/pages/`** - 按功能组织的 UI 页面
  - 每个页面都是自包含的，有自己的组件
  - 页面使用 BLoC 进行状态管理

- **`lib/components/`** - 可重用的 UI 组件
  - 在整个应用中使用的通用组件
  - 语言选择器、订阅包等

- **`lib/config/`** - 配置管理
  - 应用配置和设置处理

- **`lib/storage/`** - 本地数据持久化
  - Hive 用于加密本地存储
  - 安全存储敏感数据

- **`lib/utils/`** - 实用函数和辅助工具

### 状态管理（BLoC）
- 使用 BLoC 模式进行状态管理
- 每个功能模块都有自己的 BLoC
- BLoC 发出事件并将其转换为状态
- UI 组件对状态变化做出反应

### 服务层架构
服务层分为两个不同的部分：

1. **SDK 层（`services/sdk/`）**：直接 API 包装器
   - 处理网络通信
   - 定义请求/响应数据结构
   - 返回原始服务器数据

2. **业务服务（`services/`）**：业务逻辑编排
   - 调用 SDK 层
   - 将数据转换为应用模型
   - 处理业务规则和验证

### 数据流
```
UI → BLoC 事件 → 服务 → SDK → API → SDK 响应 → 服务 → 应用模型 → BLoC 状态 → UI 更新
```

### 核心功能
- **文档翻译**：上传和翻译文档
- **图片翻译**：拍照或选择图片进行翻译
- **文本翻译**：直接文本输入翻译
- **用户管理**：登录、身份验证、用户档案
- **订阅系统**：VIP 计划和支付处理
- **历史记录**：翻译历史和使用跟踪
- **客户服务**：应用内支持和反馈

### 重要文件
- **`lib/main.dart`** - 应用入口点和初始化
- **`lib/app.dart`** - 根小部件，包含 BLoC 提供者和路由
- **`lib/routers/routers.dart`** - GoRouter 配置和身份验证重定向
- **`lib/services/service_locator.dart`** - 依赖注入设置
- **`lib/simple_bloc_observer.dart`** - 用于调试的 BLoC 状态观察器

### 依赖项
- **状态管理**：flutter_bloc, bloc
- **路由**：go_router
- **网络**：http, dio
- **存储**：hive, flutter_secure_storage
- **UI**：flutter_easyloading, carousel_slider, card_swiper
- **文件处理**：file_picker, image_picker, camera
- **代码生成**：json_annotation, json_serializable, build_runner

### 开发注意事项
- 为新功能使用现有的 BLoC 模式
- 遵循服务层分离（SDK 与业务服务）
- 修改模型或添加新的 JSON 注解后生成代码
- 使用现有的路由系统和 AppRoute 枚举
- 遵循模块化页面结构，组件放在子目录中