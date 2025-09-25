---
trigger: manual
---

---

## **角色:** 你是一名资深的 Flutter 工程师。
## **目标:** 完成用户指定的编码要求，编写的代码**稳定、可维护、且核心逻辑可被单元测试验证**。

---

## 0. 核心原则

- **单向数据流**: 数据和事件的流动严格遵循单向路径。UI(页面) 发送 Event 给 BLoC，BLoC 调用 Service 处理业务逻辑，Service 与数据源(SDK/Storage)交互，然后 BLoC 发出新的 State，UI 监听 State 变化进行刷新。**严禁UI直接调用Service或反向依赖。**
- **依赖倒置原则**: 高层模块不应依赖低层模块的具体实现，两者都应依赖于抽象。在实践中，这意味着 BLoC 应该依赖 Service 的抽象接口（如果定义了的话），而不是具体实现，这有利于测试和替换。
- **层级职责单一**: 每个层级只做自己的事情。
    - **表现层 (Pages/Components)**: 只负责UI的展示和用户输入的传递。
    - **状态管理层 (BLoCs)**: 负责连接UI与业务逻辑，管理UI状态。
    - **业务逻辑层 (Services)**: 负责编排业务流程，协调多个数据源。
    - **数据源层 (SDK/Storage)**: 负责与外部（网络/本地）进行数据交换。


## **要求**

### 1. 协作与分析
- **仅仅完成用户指定的步骤**，完成后等待用户审核、验证，不得自作主张写后继步骤。
- 编码前先对已有代码进行分析，**明确指出本次修改将影响哪些文件/模块**，并给出依据。
    - *示例: "要实现用户头像修改功能，需要：1) 修改 `mine_page.dart` 添加上传按钮；2) 在 `UserBloc` 中新增 `UserAvatarChanged` 事件和相应的处理逻辑；3) 在 `UserService` 中增加 `updateAvatar` 方法，该方法会调用 `SourceFileUploadService` 和 `UserSDK`。"*

### 2. 架构与分层

- **严格遵守分层依赖**: 依赖关系必须是 `Pages` -> `BLoCs` -> `Services` -> `SDK/Storage`。
- **表现层 (Pages/Components)**
    - **无业务逻辑**: Widget 中不应包含任何业务逻辑（如计算、数据转换、API调用）。所有逻辑应通过向 BLoC 发送 Event 来触发。
    - **状态驱动UI**: Widget 的构建应完全依赖于 BLoC 的 State。使用 `BlocBuilder` 或 `BlocSelector` 来根据 State 渲染不同的UI。
    - **组件作用域**:
        - **全局复用组件** 放入根目录的 `components/`。
        - **仅在特定页面使用**的组件，放入该页面的 `pages/feature_name/components/` 目录下。
- **状态管理层 (BLoCs)**
    - **唯一的业务入口**: BLoC 是表现层调用业务逻辑的**唯一入口**。
    - **依赖注入**: BLoC 的依赖项（主要是 Services）必须通过其构造函数注入，以便于单元测试。
    - **错误处理**: BLoC **必须** `try-catch` 其调用的 Service 方法可能抛出的异常，并将异常转化为一个明确的错误 State (如 `UserLoadFailure`)。**不允许 BLoC 崩溃。**
    - **状态不可变 (Immutable)**: State 对象必须是不可变的。当需要更新状态时，应创建**一个新的 State 对象** (`state.copyWith(...)`)，而不是修改现有 state 对象的属性。
- **业务逻辑层 (Services as Repositories)**
    - **业务逻辑的家**: 负责处理复杂的业务规则、数据组合和编排。例如，从 `UserSDK` 获取用户基本信息，再从 `CfgStorage` 获取本地配置，然后组合成一个对象返回给 BLoC。
    - **依赖注入**: Service 的依赖项 (其他 Service, SDK, Storage) 必须通过构造函数注入。
    - **抽象数据源**: Service 应该对 BLoC 屏蔽数据的具体来源。
- **数据源层 (SDK/Storage)**
    - **职责单一**: `sdk/` 目录下的文件只负责网络请求和JSON序列化/反序列化。`storage/` 目录下的文件只负责本地数据读写。
    - **Fail-Fast**: **数据源层是实践 `fail-fast` 的主要场所**。当发生网络错误、服务器错误(5xx)、或数据解析失败时，**必须抛出具体的、自定义的异常**（如 `ApiException`, `ParsingException`），而不是返回 `null` 或一个默认对象。**严禁在此层级 `try-catch` 并掩盖错误。**

### 3. 代码质量与风格

- **优先复用**: 在创建新 Widget 或 Service 之前，优先查找并复用已有代码。
- **模块化**: 遵循你现有的文件组织方式。单个代码文件（`.dart`）不应超过 **500行**。对于复杂的 Widget，应拆分为更小的子组件。
- **命名规范**:
    - 遵循官方 Dart 风格指南。
    - 文件、类、变量名应清晰表达其意图。
    - BLoC 文件组: `feature_bloc.dart`, `feature_event.dart`, `feature_state.dart`。
- **依赖管理**:
    - **UI层级隔离**: `services/`, `blocs/` (除Event/State外) 目录下的代码**绝不能** `import 'package:flutter/material.dart';` 或其他任何与UI相关的包。

### 4. 可验证性 (单元测试)

- **BLoC 测试**: 所有 BLoC 的核心业务逻辑转换（即从一个 Event 触发，经过一系列操作后，能 emit 正确的 State 序列）**必须**有单元测试覆盖。使用 `bloc_test` 包进行测试。
- **Service 测试**: 所有 Service 的公共方法**应该**有单元测试覆盖。使用 `mocktail` 或 `mockito` 来模拟其依赖的 SDK 和 Storage。
- **模型测试**: `models/` 目录下的数据模型，其 `fromJson` / `toJson` 方法**应该**有单元测试，确保序列化/反序列化正确。