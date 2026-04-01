# Specs - 规格驱动开发技能

## 概述

**Specs (Specifications)** 是一个结构化开发流程的技能，用于将高层想法转化为具有清晰跟踪和问责制的详细实施计划。

本技能遵循 **三阶段工作流程**：
1. **需求分析** → 定义需要构建的内容
2. **设计** → 创建技术架构和实施方法
3. **任务** → 生成离散的、可执行的实施任务

## 何时使用

| 场景 | 建议使用 |
| :--- | :--- |
| 构建需要结构化规划的复杂功能 | ✅ Specs |
| 修复回归成本高昂的 Bug | ✅ Specs |
| 需要团队协作文档 | ✅ Specs |
| 需求或设计需要迭代 | ✅ Specs |
| 快速探索性编码 | ❌ 直接使用 Vibe |
| 目标不明确的原型制作 | ❌ 直接使用 Vibe |

## Specs 类型

### 1. Feature Spec (功能规格)
用于构建应用程序的新功能和能力。

**工作流变体**：
- **需求优先 (Requirements-First)**: `requirements.md` → `design.md` → `tasks.md`
- **设计优先 (Design-First)**: `design.md` → `tasks.md`

### 2. Bugfix Spec (Bug 修复规格)
用于系统地诊断和修复 Bug，防止回归。

**工作流**: `bugfix.md` → `design.md` → `tasks.md`

## 核心文件结构

```
specs/
├── requirements.md    # 功能需求文档（用户故事、验收标准）
├── bugfix.md          # Bug 分析文档（当前行为/预期行为/不变行为）
├── design.md          # 技术设计文档（架构、序列图、实施计划）
└── tasks.md           # 任务清单（离散、可跟踪的实施任务）
```

## 三阶段工作流程详解

### 阶段一：需求或 Bug 分析

#### Feature Spec - requirements.md
捕获用户故事和验收准则：
- **用户故事**: 作为 [角色]，我想要 [功能]，以便 [价值]
- **验收标准**: 明确的功能完成条件
- **边界条件**: 功能的范围和限制

#### Bugfix Spec - bugfix.md
分析 Bug 的结构化符号：
- **当前行为**: Bug 的实际表现
- **预期行为**: 应该的正确表现
- **不变行为**: 不应受影响的部分
- **复现步骤**: 如何触发 Bug

### 阶段二：设计 (design.md)

创建技术架构和实施方法：
- **系统架构**: 整体组件结构
- **组件设计**: 各模块职责
- **序列图**: 交互流程
- **数据流**: 数据流转和处理
- **错误处理**: 异常场景处理
- **测试策略**: 验证方法

### 阶段三：任务 (tasks.md)

生成离散的、可执行的实施任务：
- 每个任务有明确的完成标准
- 任务可跟踪、状态可更新
- 支持单独或批量执行

## 使用方法

### 启动新的 Feature Spec

```
请帮我创建一个新功能：[功能描述]

我将使用 Specs 工作流来：
1. 编写 requirements.md 定义用户故事和验收标准
2. 编写 design.md 设计技术架构
3. 编写 tasks.md 生成可执行任务清单
```

### 启动新的 Bugfix Spec

```
请帮我修复一个 Bug：[Bug 描述]

我将使用 Specs 工作流来：
1. 编写 bugfix.md 分析 Bug
2. 编写 design.md 设计修复方案
3. 编写 tasks.md 生成修复任务清单
```

### 继续现有 Spec

```
继续 specs/[requirements|bugfix|design|tasks].md 的编写
```

## 任务执行规范

每个任务应包含：
- [ ] **任务描述**: 清晰的动作说明
- [ ] **完成标准**: 如何确认任务完成
- [ ] **相关文件**: 涉及的文件路径
- [ ] **依赖关系**: 前置任务（如有）

任务状态：
- `[ ]` - 待处理
- `[~]` - 进行中
- `[x]` - 已完成
- `[-]` - 跳过/不适用

## 最佳实践

1. **原子性**: 每个任务应该足够小，可以独立验证
2. **可测试**: 每个任务应该有明确的验收标准
3. **可追溯**: 任务应该能追溯到需求和设计
4. **增量式**: 优先实现核心功能，再逐步扩展
5. **文档同步**: 保持 specs 文档与代码同步更新

## 相关文件

- [requirements.md.template](./templates/requirements.md.template) - 功能需求模板
- [bugfix.md.template](./templates/bugfix.md.template) - Bug 分析模板
- [design.md.template](./templates/design.md.template) - 技术设计模板
- [tasks.md.template](./templates/tasks.md.template) - 任务清单模板

## 示例输出

执行 Spec 后，将生成以下 artifacts：
- ✅ 结构化的需求/bug 分析文档
- ✅ 包含架构图和序列图的设计文档
- ✅ 可跟踪执行的任务清单
- ✅ 完整的开发过程记录
