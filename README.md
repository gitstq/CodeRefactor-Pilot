<p align="center">
  <a href="README.md">简体中文</a> |
  <a href="README_zh-TW.md">繁體中文</a> |
  <a href="README_en.md">English</a>
</p>

---

<h1 align="center">🛩️ CodeRefactor Pilot</h1>

<p align="center">
  <strong>零依赖终端 AI 代码审查与智能重构建议引擎</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/版本-v1.0.0-blue.svg" alt="Version"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE"><img src="https://img.shields.io/badge/许可证-MIT-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8%2B-yellow.svg" alt="Python 3.8+"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/actions"><img src="https://img.shields.io/badge/测试-47%20passed-success.svg" alt="Tests"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/依赖-零依赖-brightgreen.svg" alt="Zero Dependencies"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/语言-Python%20%7C%20JS%20%7C%20TS%20%7C%20Go-orange.svg" alt="Languages"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/静态规则-27条规则-purple.svg" alt="27 Rules">
  <img src="https://img.shields.io/badge/AI后端-OpenAI%20%7C%20Claude%20%7C%20Gemini%20%7C%20Ollama-9cf.svg" alt="AI Backends">
  <img src="https://img.shields.io/badge/报告格式-Terminal%20%7C%20JSON%20%7C%20HTML%20%7C%20MD-informational.svg" alt="Report Formats">
</p>

---

## 🎉 项目介绍

**CodeRefactor Pilot** 是一款专为开发者打造的零依赖终端 AI 代码审查与智能重构建议引擎。它内置了 **27 条静态分析规则**，覆盖复杂度、命名规范、安全隐患、代码风格、性能优化和重复代码检测六大维度，支持 **Python、JavaScript、TypeScript、Go** 四种主流编程语言。

无论你是个人开发者还是团队协作，CodeRefactor Pilot 都能帮你快速发现代码中的「坏味道」，并通过可选的 AI 后端（OpenAI、Claude、Gemini、Ollama）生成精准的重构建议。无需安装任何第三方依赖，一个 `pip install` 即可开始使用！

> 💡 **核心理念**：轻量、快速、智能 —— 让代码审查像呼吸一样自然。

---

## ✨ 核心特性

| 特性 | 说明 |
|:---|:---|
| 🔍 **27 条静态分析规则** | 覆盖复杂度、命名、安全、风格、性能、重复代码六大类 |
| 🌐 **多语言支持** | Python、JavaScript、TypeScript、Go 四种语言 |
| 🤖 **AI 驱动重构建议** | 支持 OpenAI、Claude、Gemini、Ollama 四大 AI 后端 |
| 🔀 **Git 深度集成** | 一键审查暂存区/已提交的变更文件，支持 diff 模式 |
| 📊 **多格式报告输出** | 终端彩色输出、JSON、HTML、Markdown 四种格式 |
| 🖥️ **交互式 TUI 仪表盘** | 终端内交互式浏览所有问题，高效定位代码缺陷 |
| 📦 **零运行时依赖** | 仅使用 Python 标准库，安装即用，无任何第三方依赖 |
| ✅ **47 个单元测试** | 全部通过，代码质量有保障 |

---

## 🚀 快速开始

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# 安装（零依赖，秒级完成）
pip install -e .
```

### ⚡ 三步上手

```bash
# 1️⃣ 扫描你的项目
coderefactor-pilot scan ./my_project

# 2️⃣ 只看 git 变更的文件
coderefactor-pilot scan --diff

# 3️⃣ 开启 AI 智能建议（需配置 AI 后端）
coderefactor-pilot scan ./my_project --ai --ai-backend openai
```

就这么简单！🎉

---

## 📖 详细使用指南

### 🔧 CLI 命令全览

```bash
# 基础扫描
coderefactor-pilot scan <path>              # 扫描指定路径下的代码
coderefactor-pilot scan ./src               # 扫描 src 目录
coderefactor-pilot scan .                   # 扫描当前目录

# Git 集成
coderefactor-pilot scan --diff              # 仅扫描 git 变更的文件

# 语言筛选
coderefactor-pilot scan --lang python       # 仅扫描 Python 文件
coderefactor-pilot scan --lang javascript   # 仅扫描 JavaScript 文件
coderefactor-pilot scan --lang typescript   # 仅扫描 TypeScript 文件
coderefactor-pilot scan --lang go           # 仅扫描 Go 文件

# 严重级别过滤
coderefactor-pilot scan --severity high     # 仅显示高级别问题
coderefactor-pilot scan --severity medium   # 显示中高级别问题
coderefactor-pilot scan --severity low      # 显示所有级别问题

# AI 智能建议
coderefactor-pilot scan --ai                # 启用 AI 重构建议
coderefactor-pilot scan --ai --ai-backend openai    # 使用 OpenAI
coderefactor-pilot scan --ai --ai-backend claude    # 使用 Claude
coderefactor-pilot scan --ai --ai-backend gemini    # 使用 Gemini
coderefactor-pilot scan --ai --ai-backend ollama    # 使用本地 Ollama

# 报告输出
coderefactor-pilot scan --report json       # JSON 格式报告
coderefactor-pilot scan --report html       # HTML 格式报告
coderefactor-pilot scan --report markdown   # Markdown 格式报告
coderefactor-pilot scan --output report.json --report json  # 输出到文件

# 其他命令
coderefactor-pilot config                   # 配置管理
coderefactor-pilot rules                    # 列出所有 27 条规则
coderefactor-pilot version                  # 查看版本信息
```

### 📋 27 条规则详解

#### 🔴 复杂度规则（3 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| CC001 | 圈复杂度 | 检测函数/方法的圈复杂度是否过高 |
| CC002 | 认知复杂度 | 检测代码的认知复杂度是否超出阈值 |
| CC003 | 深层嵌套 | 检测是否存在过深的代码嵌套层级 |

#### 🏷️ 命名规范规则（5 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| NM001 | snake_case | Python 变量/函数应使用 snake_case 命名 |
| NM002 | PascalCase 类名 | 类名应使用 PascalCase 命名 |
| NM003 | camelCase | JS/TS 变量/函数应使用 camelCase 命名 |
| NM004 | Go 命名规范 | Go 代码应遵循 Go 官方命名约定 |
| NM005 | 短标识符 | 检测过短的变量/函数名（如单字母） |

#### 🔁 重复代码规则（2 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| DP001 | 重复代码块 | 检测项目中完全重复的代码块 |
| DP002 | 相似函数 | 检测结构相似的函数，提示可抽取公共逻辑 |

#### 🔒 安全规则（5 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| SEC001 | 硬编码密码 | 检测代码中硬编码的密码和密钥 |
| SEC002 | SQL 注入 | 检测潜在的 SQL 注入风险 |
| SEC003 | 危险函数 | 检测使用 `eval()`、`exec()` 等危险函数 |
| SEC004 | 不安全随机 | 检测使用不安全的随机数生成方式 |
| SEC005 | 硬编码 URL | 检测硬编码的内部 URL 和敏感地址 |

#### 🎨 代码风格规则（6 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| STY001 | 行长度 | 检测超过限制的行长度 |
| STY002 | 函数长度 | 检测过长的函数，建议拆分 |
| STY003 | 文件长度 | 检测过大的文件，建议模块化 |
| STY004 | 参数过多 | 检测函数参数数量是否过多 |
| STY005 | 尾随空白 | 检测行尾多余空白字符 |
| STY006 | 缺少文档字符串 | 检测公共函数/类缺少 docstring |

#### ⚡ 性能规则（6 条）

| 规则编号 | 规则名称 | 说明 |
|:---|:---|:---|
| PERF001 | 循环内字符串拼接 | 检测循环中的低效字符串拼接 |
| PERF002 | 不必要的列表复制 | 检测不必要的列表/数组复制操作 |
| PERF003 | 全局变量查找 | 检测频繁的全局变量查找影响性能 |
| PERF004 | 低效数据类型 | 检测可优化的数据类型选择 |
| PERF005 | 重型模块导入 | 检测在函数内导入重型模块 |
| PERF006 | 未使用导入 | 检测未使用的 import 语句 |

### 🤖 AI 后端配置

CodeRefactor Pilot 支持多种 AI 后端，你可以根据需要选择：

```bash
# 使用 OpenAI（需要 OPENAI_API_KEY 环境变量）
export OPENAI_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend openai

# 使用 Claude（需要 ANTHROPIC_API_KEY 环境变量）
export ANTHROPIC_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend claude

# 使用 Gemini（需要 GOOGLE_API_KEY 环境变量）
export GOOGLE_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend gemini

# 使用本地 Ollama（无需 API Key，需本地运行 Ollama）
coderefactor-pilot scan ./src --ai --ai-backend ollama
```

> 💡 **提示**：AI 功能完全可选，不配置 AI 后端也能使用全部 27 条静态分析规则。

### 📊 报告输出示例

```bash
# 终端彩色输出（默认）
coderefactor-pilot scan ./src

# JSON 报告
coderefactor-pilot scan ./src --report json --output report.json

# HTML 报告
coderefactor-pilot scan ./src --report html --output report.html

# Markdown 报告
coderefactor-pilot scan ./src --report markdown --output report.md
```

---

## 💡 设计思路与迭代规划

### 🏗️ 设计哲学

CodeRefactor Pilot 的设计遵循以下核心原则：

- **零依赖原则**：仅使用 Python 标准库，安装零负担，运行环境零冲突
- **渐进增强**：基础静态分析开箱即用，AI 功能按需开启
- **多语言统一**：一套工具覆盖 Python、JS、TS、Go 四种语言
- **Git 原生集成**：与开发工作流深度结合，diff 模式让审查更聚焦
- **可扩展架构**：规则引擎和 AI 后端均采用插件化设计，便于扩展

### 🗺️ 迭代规划

#### v1.0.0（当前版本）✅
- ✅ 27 条内置静态分析规则
- ✅ 四种语言支持（Python、JavaScript、TypeScript、Go）
- ✅ 四种 AI 后端集成（OpenAI、Claude、Gemini、Ollama）
- ✅ Git diff 模式
- ✅ 多格式报告输出
- ✅ 交互式 TUI 仪表盘
- ✅ 47 个单元测试全部通过

#### v1.1.0（规划中）📋
- 🔲 自定义规则配置文件支持（`.coderefactor.yaml`）
- 🔲 CI/CD 集成指南（GitHub Actions、GitLab CI）
- 🔲 SARIF 格式输出（兼容 GitHub Code Scanning）
- 🔲 增量扫描与缓存机制

#### v1.2.0（远期规划）🔭
- 🔲 VS Code / JetBrains IDE 插件
- 🔲 更多语言支持（Rust、Java、C++）
- 🔲 代码异味趋势分析与可视化
- 🔲 团队协作与规则共享

---

## 📦 安装与部署

### 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- Git（用于 diff 模式，可选）
- AI 后端（用于 AI 建议，可选）

### 安装方式

```bash
# 方式一：从源码安装（推荐）
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot
pip install -e .

# 方式二：直接通过 pip 安装
pip install coderefactor-pilot
```

### 验证安装

```bash
coderefactor-pilot version
# 输出：CodeRefactor Pilot v1.0.0
```

### 配置文件

```bash
# 初始化配置
coderefactor-pilot config

# 查看当前配置
coderefactor-pilot config --show
```

### 卸载

```bash
pip uninstall coderefactor-pilot
```

---

## 🤝 贡献指南

我们欢迎并感谢每一位贡献者！🎉 以下是如何参与贡献的步骤：

### 🛠️ 开发环境搭建

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/<your-username>/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# 2. 安装开发模式
pip install -e .

# 3. 运行测试
python -m pytest tests/ -v
```

### 📝 贡献流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交改动：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 📋 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
feat: 新增功能
fix: 修复 Bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

### 🧪 测试要求

- 所有新功能必须附带单元测试
- 提交 PR 前请确保所有 47 个测试全部通过
- 测试覆盖率不应因新代码而降低

---

## 📄 开源协议

本项目基于 [MIT License](https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE) 开源。

```
MIT License

Copyright (c) 2024 CodeRefactor Pilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  用 ❤️ 打造 | <a href="https://github.com/gitstq/CodeRefactor-Pilot">CodeRefactor Pilot</a>
</p>

---

## English Version

<h1 align="center">🛩️ CodeRefactor Pilot</h1>

<p align="center">
  <strong>Zero-Dependency Terminal AI Code Review & Intelligent Refactoring Engine</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/Version-v1.0.0-blue.svg" alt="Version"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8%2B-yellow.svg" alt="Python 3.8+"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/actions"><img src="https://img.shields.io/badge/Tests-47%20passed-success.svg" alt="Tests"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg" alt="Zero Dependencies"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/Languages-Python%20%7C%20JS%20%7C%20TS%20%7C%20Go-orange.svg" alt="Languages"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Static%20Rules-27%20Rules-purple.svg" alt="27 Rules">
  <img src="https://img.shields.io/badge/AI%20Backends-OpenAI%20%7C%20Claude%20%7C%20Gemini%20%7C%20Ollama-9cf.svg" alt="AI Backends">
  <img src="https://img.shields.io/badge/Report%20Formats-Terminal%20%7C%20JSON%20%7C%20HTML%20%7C%20MD-informational.svg" alt="Report Formats">
</p>

---

## 🎉 Introduction

**CodeRefactor Pilot** is a zero-dependency terminal tool for AI-powered code review and intelligent refactoring suggestions. It comes with **27 built-in static analysis rules** spanning six dimensions: complexity, naming conventions, security vulnerabilities, code style, performance anti-patterns, and code duplication detection. It supports **Python, JavaScript, TypeScript, and Go**.

Whether you're a solo developer or part of a team, CodeRefactor Pilot helps you quickly detect code smells and generate precise refactoring suggestions through optional AI backends (OpenAI, Claude, Gemini, Ollama). No third-party dependencies required — just one `pip install` and you're good to go!

> 💡 **Core Philosophy**: Lightweight, fast, and intelligent — making code review as natural as breathing.

---

## ✨ Key Features

| Feature | Description |
|:---|:---|
| 🔍 **27 Static Analysis Rules** | Covers complexity, naming, security, style, performance, and duplication |
| 🌐 **Multi-Language Support** | Python, JavaScript, TypeScript, Go |
| 🤖 **AI-Powered Refactoring** | OpenAI, Claude, Gemini, and Ollama backends |
| 🔀 **Deep Git Integration** | Review staged/committed changes with diff mode |
| 📊 **Multiple Report Formats** | Terminal (colored), JSON, HTML, Markdown |
| 🖥️ **Interactive TUI Dashboard** | Browse issues interactively right in your terminal |
| 📦 **Zero Runtime Dependencies** | Built entirely on Python standard library |
| ✅ **47 Unit Tests** | All passing, quality guaranteed |

---

## 🚀 Quick Start

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# Install (zero dependencies, instant setup)
pip install -e .
```

### ⚡ Three Steps to Get Started

```bash
# 1️⃣ Scan your project
coderefactor-pilot scan ./my_project

# 2️⃣ Review only git changes
coderefactor-pilot scan --diff

# 3️⃣ Enable AI-powered suggestions (requires AI backend configuration)
coderefactor-pilot scan ./my_project --ai --ai-backend openai
```

That's it! 🎉

---

## 📖 Detailed Usage Guide

### 🔧 CLI Commands

```bash
# Basic scanning
coderefactor-pilot scan <path>              # Scan a specific path
coderefactor-pilot scan ./src               # Scan the src directory
coderefactor-pilot scan .                   # Scan the current directory

# Git integration
coderefactor-pilot scan --diff              # Scan only git-changed files

# Language filtering
coderefactor-pilot scan --lang python       # Python files only
coderefactor-pilot scan --lang javascript   # JavaScript files only
coderefactor-pilot scan --lang typescript   # TypeScript files only
coderefactor-pilot scan --lang go           # Go files only

# Severity filtering
coderefactor-pilot scan --severity high     # High severity issues only
coderefactor-pilot scan --severity medium   # Medium and above
coderefactor-pilot scan --severity low      # All severity levels

# AI-powered suggestions
coderefactor-pilot scan --ai                # Enable AI suggestions
coderefactor-pilot scan --ai --ai-backend openai    # Use OpenAI
coderefactor-pilot scan --ai --ai-backend claude    # Use Claude
coderefactor-pilot scan --ai --ai-backend gemini    # Use Gemini
coderefactor-pilot scan --ai --ai-backend ollama    # Use local Ollama

# Report output
coderefactor-pilot scan --report json       # JSON format
coderefactor-pilot scan --report html       # HTML format
coderefactor-pilot scan --report markdown   # Markdown format
coderefactor-pilot scan --output report.json --report json  # Output to file

# Other commands
coderefactor-pilot config                   # Configuration management
coderefactor-pilot rules                    # List all 27 rules
coderefactor-pilot version                  # Version info
```

### 📋 All 27 Rules

#### 🔴 Complexity Rules (3)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| CC001 | Cyclomatic Complexity | Detects functions/methods with excessive cyclomatic complexity |
| CC002 | Cognitive Complexity | Detects code with high cognitive complexity |
| CC003 | Deep Nesting | Detects excessively nested code structures |

#### 🏷️ Naming Convention Rules (5)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| NM001 | snake_case | Python variables/functions should use snake_case |
| NM002 | PascalCase Classes | Class names should use PascalCase |
| NM003 | camelCase | JS/TS variables/functions should use camelCase |
| NM004 | Go Naming | Go code should follow official Go naming conventions |
| NM005 | Short Identifiers | Detects overly short variable/function names (e.g., single letters) |

#### 🔁 Duplication Rules (2)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| DP001 | Duplicate Code Blocks | Detects identical code blocks across the project |
| DP002 | Similar Functions | Detects structurally similar functions that could share common logic |

#### 🔒 Security Rules (5)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| SEC001 | Hardcoded Passwords | Detects hardcoded passwords and secret keys |
| SEC002 | SQL Injection | Detects potential SQL injection vulnerabilities |
| SEC003 | Dangerous Functions | Detects usage of `eval()`, `exec()`, and similar dangerous functions |
| SEC004 | Insecure Random | Detects insecure random number generation |
| SEC005 | Hardcoded URLs | Detects hardcoded internal URLs and sensitive addresses |

#### 🎨 Style Rules (6)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| STY001 | Line Length | Detects lines exceeding the length limit |
| STY002 | Function Length | Detects overly long functions that should be split |
| STY003 | File Length | Detects oversized files that should be modularized |
| STY004 | Too Many Parameters | Detects functions with excessive parameter counts |
| STY005 | Trailing Whitespace | Detects trailing whitespace characters |
| STY006 | Missing Docstrings | Detects public functions/classes missing docstrings |

#### ⚡ Performance Rules (6)

| Rule ID | Rule Name | Description |
|:---|:---|:---|
| PERF001 | String Concatenation in Loops | Detects inefficient string concatenation inside loops |
| PERF002 | Unnecessary List Copy | Detects unnecessary list/array copy operations |
| PERF003 | Global Variable Lookup | Detects frequent global variable lookups impacting performance |
| PERF004 | Inefficient Data Types | Detects suboptimal data type choices |
| PERF005 | Heavy Module Imports | Detects heavy module imports inside functions |
| PERF006 | Unused Imports | Detects unused import statements |

### 🤖 AI Backend Configuration

CodeRefactor Pilot supports multiple AI backends — pick the one that works best for you:

```bash
# OpenAI (requires OPENAI_API_KEY environment variable)
export OPENAI_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend openai

# Claude (requires ANTHROPIC_API_KEY environment variable)
export ANTHROPIC_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend claude

# Gemini (requires GOOGLE_API_KEY environment variable)
export GOOGLE_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend gemini

# Local Ollama (no API key needed, requires Ollama running locally)
coderefactor-pilot scan ./src --ai --ai-backend ollama
```

> 💡 **Tip**: AI features are entirely optional. All 27 static analysis rules work perfectly without any AI backend configured.

### 📊 Report Output Examples

```bash
# Colored terminal output (default)
coderefactor-pilot scan ./src

# JSON report
coderefactor-pilot scan ./src --report json --output report.json

# HTML report
coderefactor-pilot scan ./src --report html --output report.html

# Markdown report
coderefactor-pilot scan ./src --report markdown --output report.md
```

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Design Principles

CodeRefactor Pilot is built on these core principles:

- **Zero Dependencies**: Built entirely on the Python standard library — zero installation burden, zero runtime conflicts
- **Progressive Enhancement**: Static analysis works out of the box; AI features activate on demand
- **Multi-Language Unity**: One tool covering Python, JS, TS, and Go
- **Git-Native Integration**: Deeply integrated with developer workflows; diff mode keeps reviews focused
- **Extensible Architecture**: Both the rule engine and AI backends use a pluggable design for easy extension

### 🗺️ Roadmap

#### v1.0.0 (Current) ✅
- ✅ 27 built-in static analysis rules
- ✅ Four language support (Python, JavaScript, TypeScript, Go)
- ✅ Four AI backend integrations (OpenAI, Claude, Gemini, Ollama)
- ✅ Git diff mode
- ✅ Multiple report format output
- ✅ Interactive TUI dashboard
- ✅ 47 unit tests all passing

#### v1.1.0 (Planned) 📋
- 🔲 Custom rule configuration file support (`.coderefactor.yaml`)
- 🔲 CI/CD integration guides (GitHub Actions, GitLab CI)
- 🔲 SARIF format output (compatible with GitHub Code Scanning)
- 🔲 Incremental scanning and caching mechanism

#### v1.2.0 (Long-term) 🔭
- 🔲 VS Code / JetBrains IDE plugins
- 🔲 Additional language support (Rust, Java, C++)
- 🔲 Code smell trend analysis and visualization
- 🔲 Team collaboration and rule sharing

---

## 📦 Installation & Deployment

### System Requirements

- Python 3.8 or later
- pip package manager
- Git (for diff mode, optional)
- AI backend (for AI suggestions, optional)

### Installation Methods

```bash
# Method 1: Install from source (recommended)
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot
pip install -e .

# Method 2: Install via pip
pip install coderefactor-pilot
```

### Verify Installation

```bash
coderefactor-pilot version
# Output: CodeRefactor Pilot v1.0.0
```

### Configuration

```bash
# Initialize configuration
coderefactor-pilot config

# Show current configuration
coderefactor-pilot config --show
```

### Uninstall

```bash
pip uninstall coderefactor-pilot
```

---

## 🤝 Contributing

We welcome and appreciate every contributor! 🎉 Here's how you can get involved:

### 🛠️ Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# 2. Install in development mode
pip install -e .

# 3. Run tests
python -m pytest tests/ -v
```

### 📝 Contribution Workflow

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Submit a **Pull Request**

### 📋 Commit Convention

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
feat:     New features
fix:      Bug fixes
docs:     Documentation updates
style:    Code formatting
refactor: Code refactoring
test:     Test-related changes
chore:    Build/toolchain changes
```

### 🧪 Testing Requirements

- All new features must include unit tests
- Ensure all 47 tests pass before submitting a PR
- Test coverage should not decrease with new code

---

## 📄 License

This project is licensed under the [MIT License](https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE).

```
MIT License

Copyright (c) 2024 CodeRefactor Pilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Built with ❤️ | <a href="https://github.com/gitstq/CodeRefactor-Pilot">CodeRefactor Pilot</a>
</p>

---

## 繁體中文版本

<h1 align="center">🛩️ CodeRefactor Pilot</h1>

<p align="center">
  <strong>零依賴終端 AI 程式碼審查與智慧重構建議引擎</strong>
</p>

<p align="center">
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/版本-v1.0.0-blue.svg" alt="Version"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE"><img src="https://img.shields.io/badge/授權條款-MIT-green.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8%2B-yellow.svg" alt="Python 3.8+"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot/actions"><img src="https://img.shields.io/badge/測試-47%20passed-success.svg" alt="Tests"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/依賴-零依賴-brightgreen.svg" alt="Zero Dependencies"></a>
  <a href="https://github.com/gitstq/CodeRefactor-Pilot"><img src="https://img.shields.io/badge/語言-Python%20%7C%20JS%20%7C%20TS%20%7C%20Go-orange.svg" alt="Languages"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/靜態規則-27條規則-purple.svg" alt="27 Rules">
  <img src="https://img.shields.io/badge/AI後端-OpenAI%20%7C%20Claude%20%7C%20Gemini%20%7C%20Ollama-9cf.svg" alt="AI Backends">
  <img src="https://img.shields.io/badge/報告格式-Terminal%20%7C%20JSON%20%7C%20HTML%20%7C%20MD-informational.svg" alt="Report Formats">
</p>

---

## 🎉 專案介紹

**CodeRefactor Pilot** 是一款專為開發者打造的零依賴終端 AI 程式碼審查與智慧重構建議引擎。它內建了 **27 條靜態分析規則**，涵蓋複雜度、命名規範、安全隱患、程式碼風格、效能最佳化與重複程式碼偵測六大面向，支援 **Python、JavaScript、TypeScript、Go** 四種主流程式語言。

無論你是獨立開發者還是團隊協作，CodeRefactor Pilot 都能幫你快速發現程式碼中的「壞味道」，並透過可選的 AI 後端（OpenAI、Claude、Gemini、Ollama）產生精準的重構建議。無需安裝任何第三方依賴，一個 `pip install` 即可開始使用！

> 💡 **核心理念**：輕量、快速、智慧 —— 讓程式碼審查像呼吸一樣自然。

---

## ✨ 核心特性

| 特性 | 說明 |
|:---|:---|
| 🔍 **27 條靜態分析規則** | 涵蓋複雜度、命名、安全、風格、效能、重複程式碼六大類 |
| 🌐 **多語言支援** | Python、JavaScript、TypeScript、Go 四種語言 |
| 🤖 **AI 驅動重構建議** | 支援 OpenAI、Claude、Gemini、Ollama 四大 AI 後端 |
| 🔀 **Git 深度整合** | 一鍵審查暫存區/已提交的變更檔案，支援 diff 模式 |
| 📊 **多格式報告輸出** | 終端彩色輸出、JSON、HTML、Markdown 四種格式 |
| 🖥️ **互動式 TUI 儀表板** | 終端內互動式瀏覽所有問題，高效定位程式碼缺陷 |
| 📦 **零執行期依賴** | 僅使用 Python 標準函式庫，安裝即用，無任何第三方依賴 |
| ✅ **47 個單元測試** | 全部通過，程式碼品質有保障 |

---

## 🚀 快速開始

### 📦 安裝

```bash
# 複製倉庫
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# 安裝（零依賴，秒級完成）
pip install -e .
```

### ⚡ 三步上手

```bash
# 1️⃣ 掃描你的專案
coderefactor-pilot scan ./my_project

# 2️⃣ 只看 git 變更的檔案
coderefactor-pilot scan --diff

# 3️⃣ 開啟 AI 智慧建議（需設定 AI 後端）
coderefactor-pilot scan ./my_project --ai --ai-backend openai
```

就這麼簡單！🎉

---

## 📖 詳細使用指南

### 🔧 CLI 指令全覽

```bash
# 基礎掃描
coderefactor-pilot scan <path>              # 掃描指定路徑下的程式碼
coderefactor-pilot scan ./src               # 掃描 src 目錄
coderefactor-pilot scan .                   # 掃描當前目錄

# Git 整合
coderefactor-pilot scan --diff              # 僅掃描 git 變更的檔案

# 語言篩選
coderefactor-pilot scan --lang python       # 僅掃描 Python 檔案
coderefactor-pilot scan --lang javascript   # 僅掃描 JavaScript 檔案
coderefactor-pilot scan --lang typescript   # 僅掃描 TypeScript 檔案
coderefactor-pilot scan --lang go           # 僅掃描 Go 檔案

# 嚴重等級篩選
coderefactor-pilot scan --severity high     # 僅顯示高等級問題
coderefactor-pilot scan --severity medium   # 顯示中高等級問題
coderefactor-pilot scan --severity low      # 顯示所有等級問題

# AI 智慧建議
coderefactor-pilot scan --ai                # 啟用 AI 重構建議
coderefactor-pilot scan --ai --ai-backend openai    # 使用 OpenAI
coderefactor-pilot scan --ai --ai-backend claude    # 使用 Claude
coderefactor-pilot scan --ai --ai-backend gemini    # 使用 Gemini
coderefactor-pilot scan --ai --ai-backend ollama    # 使用本地 Ollama

# 報告輸出
coderefactor-pilot scan --report json       # JSON 格式報告
coderefactor-pilot scan --report html       # HTML 格式報告
coderefactor-pilot scan --report markdown   # Markdown 格式報告
coderefactor-pilot scan --output report.json --report json  # 輸出至檔案

# 其他指令
coderefactor-pilot config                   # 設定管理
coderefactor-pilot rules                    # 列出所有 27 條規則
coderefactor-pilot version                  # 查看版本資訊
```

### 📋 27 條規則詳解

#### 🔴 複雜度規則（3 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| CC001 | 圈複雜度 | 偵測函式/方法的圈複雜度是否過高 |
| CC002 | 認知複雜度 | 偵測程式碼的認知複雜度是否超出閾值 |
| CC003 | 深層巢狀 | 偵測是否存在過深的程式碼巢狀層級 |

#### 🏷️ 命名規範規則（5 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| NM001 | snake_case | Python 變數/函式應使用 snake_case 命名 |
| NM002 | PascalCase 類別名 | 類別名應使用 PascalCase 命名 |
| NM003 | camelCase | JS/TS 變數/函式應使用 camelCase 命名 |
| NM004 | Go 命名規範 | Go 程式碼應遵循 Go 官方命名慣例 |
| NM005 | 短識別碼 | 偵測過短的變數/函式名（如單字母） |

#### 🔁 重複程式碼規則（2 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| DP001 | 重複程式碼區塊 | 偵測專案中完全重複的程式碼區塊 |
| DP002 | 相似函式 | 偵測結構相似的函式，提示可抽取共用邏輯 |

#### 🔒 安全規則（5 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| SEC001 | 硬編碼密碼 | 偵測程式碼中硬編碼的密碼和金鑰 |
| SEC002 | SQL 注入 | 偵測潛在的 SQL 注入風險 |
| SEC003 | 危險函式 | 偵測使用 `eval()`、`exec()` 等危險函式 |
| SEC004 | 不安全隨機 | 偵測使用不安全的隨機數生成方式 |
| SEC005 | 硬編碼 URL | 偵測硬編碼的內部 URL 和敏感位址 |

#### 🎨 程式碼風格規則（6 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| STY001 | 行長度 | 偵測超過限制的行長度 |
| STY002 | 函式長度 | 偵測過長的函式，建議拆分 |
| STY003 | 檔案長度 | 偵測過大的檔案，建議模組化 |
| STY004 | 參數過多 | 偵測函式參數數量是否過多 |
| STY005 | 尾隨空白 | 偵測行尾多餘空白字元 |
| STY006 | 缺少文件字串 | 偵測公用函式/類別缺少 docstring |

#### ⚡ 效能規則（6 條）

| 規則編號 | 規則名稱 | 說明 |
|:---|:---|:---|
| PERF001 | 迴圈內字串拼接 | 偵測迴圈中的低效字串拼接 |
| PERF002 | 不必要的列表複製 | 偵測不必要的列表/陣列複製操作 |
| PERF003 | 全域變數查找 | 偵測頻繁的全域變數查找影響效能 |
| PERF004 | 低效資料型態 | 偵測可最佳化的資料型態選擇 |
| PERF005 | 重型模組匯入 | 偵測在函式內匯入重型模組 |
| PERF006 | 未使用匯入 | 偵測未使用的 import 陳述式 |

### 🤖 AI 後端設定

CodeRefactor Pilot 支援多種 AI 後端，你可以根據需要選擇：

```bash
# 使用 OpenAI（需要 OPENAI_API_KEY 環境變數）
export OPENAI_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend openai

# 使用 Claude（需要 ANTHROPIC_API_KEY 環境變數）
export ANTHROPIC_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend claude

# 使用 Gemini（需要 GOOGLE_API_KEY 環境變數）
export GOOGLE_API_KEY="your-api-key"
coderefactor-pilot scan ./src --ai --ai-backend gemini

# 使用本地 Ollama（無需 API Key，需本地執行 Ollama）
coderefactor-pilot scan ./src --ai --ai-backend ollama
```

> 💡 **提示**：AI 功能完全可選，不設定 AI 後端也能使用全部 27 條靜態分析規則。

### 📊 報告輸出範例

```bash
# 終端彩色輸出（預設）
coderefactor-pilot scan ./src

# JSON 報告
coderefactor-pilot scan ./src --report json --output report.json

# HTML 報告
coderefactor-pilot scan ./src --report html --output report.html

# Markdown 報告
coderefactor-pilot scan ./src --report markdown --output report.md
```

---

## 💡 設計思路與迭代規劃

### 🏗️ 設計哲學

CodeRefactor Pilot 的設計遵循以下核心原則：

- **零依賴原則**：僅使用 Python 標準函式庫，安裝零負擔，執行環境零衝突
- **漸進增強**：基礎靜態分析開箱即用，AI 功能按需開啟
- **多語言統一**：一套工具涵蓋 Python、JS、TS、Go 四種語言
- **Git 原生整合**：與開發工作流程深度結合，diff 模式讓審查更聚焦
- **可擴展架構**：規則引擎和 AI 後端均採用外掛化設計，便於擴展

### 🗺️ 迭代規劃

#### v1.0.0（當前版本）✅
- ✅ 27 條內建靜態分析規則
- ✅ 四種語言支援（Python、JavaScript、TypeScript、Go）
- ✅ 四種 AI 後端整合（OpenAI、Claude、Gemini、Ollama）
- ✅ Git diff 模式
- ✅ 多格式報告輸出
- ✅ 互動式 TUI 儀表板
- ✅ 47 個單元測試全部通過

#### v1.1.0（規劃中）📋
- 🔲 自訂規則設定檔支援（`.coderefactor.yaml`）
- 🔲 CI/CD 整合指南（GitHub Actions、GitLab CI）
- 🔲 SARIF 格式輸出（相容 GitHub Code Scanning）
- 🔲 增量掃描與快取機制

#### v1.2.0（遠期規劃）🔭
- 🔲 VS Code / JetBrains IDE 外掛
- 🔲 更多語言支援（Rust、Java、C++）
- 🔲 程式碼異味趨勢分析與視覺化
- 🔲 團隊協作與規則共享

---

## 📦 安裝與部署

### 系統需求

- Python 3.8 或更高版本
- pip 套件管理器
- Git（用於 diff 模式，可選）
- AI 後端（用於 AI 建議，可選）

### 安裝方式

```bash
# 方式一：從原始碼安裝（推薦）
git clone https://github.com/gitstq/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot
pip install -e .

# 方式二：透過 pip 直接安裝
pip install coderefactor-pilot
```

### 驗證安裝

```bash
coderefactor-pilot version
# 輸出：CodeRefactor Pilot v1.0.0
```

### 設定檔

```bash
# 初始化設定
coderefactor-pilot config

# 查看當前設定
coderefactor-pilot config --show
```

### 解除安裝

```bash
pip uninstall coderefactor-pilot
```

---

## 🤝 貢獻指南

我們歡迎並感謝每一位貢獻者！🎉 以下是如何參與貢獻的步驟：

### 🛠️ 開發環境建置

```bash
# 1. Fork 並複製倉庫
git clone https://github.com/<your-username>/CodeRefactor-Pilot.git
cd CodeRefactor-Pilot

# 2. 安裝開發模式
pip install -e .

# 3. 執行測試
python -m pytest tests/ -v
```

### 📝 貢獻流程

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/amazing-feature`
3. 提交變更：`git commit -m 'feat: add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 📋 提交規範

請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

```
feat: 新增功能
fix: 修復 Bug
docs: 文件更新
style: 程式碼格式調整
refactor: 程式碼重構
test: 測試相關
chore: 建置/工具鏈相關
```

### 🧪 測試要求

- 所有新功能必須附帶單元測試
- 提交 PR 前請確保所有 47 個測試全部通過
- 測試覆蓋率不應因新程式碼而降低

---

## 📄 開源授權條款

本專案基於 [MIT License](https://github.com/gitstq/CodeRefactor-Pilot/blob/main/LICENSE) 開源。

```
MIT License

Copyright (c) 2024 CodeRefactor Pilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  用 ❤️ 打造 | <a href="https://github.com/gitstq/CodeRefactor-Pilot">CodeRefactor Pilot</a>
</p>
