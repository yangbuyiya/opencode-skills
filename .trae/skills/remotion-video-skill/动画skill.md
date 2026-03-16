# Remotion Skills 安装指南

## 概述

本文档详细记录了使用 `npx skills add remotion-dev/skills` 命令安装 Remotion 相关技能的完整过程。Remotion 是一个用于在 React 中创建视频的强大工具，通过安装其官方技能包，可以获得最佳实践指导和代码建议。

## 安装环境

- **操作系统**: Windows
- **Node.js 版本**: node v22

## 安装步骤

### 第一步：执行安装命令

在终端中执行以下命令：

```bash
npx skills add remotion-dev/skills
```

执行后，系统会提示需要安装以下包：

```
Need to install the following packages:
skills@1.4.4
Ok to proceed? (y) y
```

输入 `y` 确认安装。

### 第二步：Skills CLI 启动

安装程序会启动 Skills CLI，显示欢迎界面：

```
███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝
```

### 第三步：克隆技能仓库

系统自动从 GitHub 克隆 Remotion 官方技能仓库：

```
┌   skills 
│
◇  Source: https://github.com/remotion-dev/skills.git
│
◇  Repository cloned
```

### 第四步：发现技能

系统在克隆的仓库中找到了 1 个技能：

```
◇  Found 1 skill
│
●  Skill: remotion-best-practices
│
│  Best practices for Remotion - Video creation in React
```

该技能提供了 41 个 AI 助手（agents）的配置。

### 第五步：选择安装目标

系统会多次询问要将技能安装到哪些 AI 助手：

```
◆  Which agents do you want to install to?
│
│  ── Universal (.agents/skills) ── always included ────────────
│    • Amp
```

经过多次选择后，最终选择了以下 AI 助手：

- Amp
- Cline
- Codex
- Cursor
- Gemini CLI
- GitHub Copilot
- Kimi Code CLI
- OpenCode

### 第六步：配置安装参数

系统要求配置安装范围和安装方法：

```
◇  Installation scope
│  Project
│
◇  Installation method
│  Symlink (Recommended)
```

- **Installation scope（安装范围）**: Project（项目级别）
- **Installation method（安装方法）**: Symlink（符号链接，推荐方式）

### 第七步：确认安装摘要

系统显示安装摘要，包括安装路径和兼容的 AI 助手列表：

```
│  Installation Summary ───────────────────────────────────────╮
│                                                              │
│  .\.agents\skills\remotion-best-practices                    │
│    universal: Amp, Cline, Codex, Cursor, Gemini CLI +3 more  │
│                                                              │
├──────────────────────────────────────────────────────────────╯
```

### 第八步：安全风险评估

系统对技能进行了安全风险评估：

```
│  Security Risk Assessments ─────────────────────────────────────────────╮
│                                                                         │
│                           Gen               Socket            Snyk      │
│  remotion-best-practices  Safe              0 alerts          Med Risk  │
│                                                                         │
│  Details: https://skills.sh/remotion-dev/skills                         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────╯
```

**评估结果**:
- **Gen（通用安全）**: Safe（安全）
- **Socket**: 0 alerts（无安全警报）
- **Snyk**: Med Risk（中等风险）

### 第九步：确认安装

系统询问是否继续安装：

```
◇  Proceed with installation?
│  Yes
```

输入 `Yes` 确认安装。

### 第十步：安装完成

系统提示安装完成，并显示已安装的技能信息：

```
◇  Installation complete

│
◇  Installed 1 skill ──────────────────────────────────────────╮
│                                                              │
│  ✓ .\.agents\skills\remotion-best-practices                  │
│    universal: Amp, Cline, Codex, Cursor, Gemini CLI +3 more  │
│                                                              │
├──────────────────────────────────────────────────────────────╯

│
└  Done!  Review skills before use; they run with full agent permissions.
```

**重要提示**: 技能拥有完整的代理权限，使用前请仔细审查。

## 额外安装：find-skills

### 第一步：安装提示

系统弹出一次性提示，询问是否安装 find-skills 技能：

```
│  One-time prompt - you won't be asked again if you dismiss.
│
◇  Install the find-skills skill? It helps your agent discover and suggest skills.                                                                                                                                                                                    
│  Yes
```

find-skills 技能可以帮助 AI 助手发现和推荐其他技能。

### 第二步：安装 find-skills

输入 `Yes` 确认安装，系统开始安装：

```
◇  Installing find-skills skill...

┌   skills 
│
◇  Source: https://github.com/vercel-labs/skills.git
│
◇  Repository cloned
│
◇  Found 1 skill
│
●  Selected 1 skill: find-skills
```

### 第三步：安装摘要和安全评估

系统显示 find-skills 的安装摘要：

```
│  Installation Summary ───────────────────────────────────────╮
│                                                              │
│  ~\.agents\skills\find-skills                                │
│    universal: Amp, Cline, Codex, Cursor, Gemini CLI +3 more  │
│                                                              │
├──────────────────────────────────────────────────────────────╯
```

安全评估结果：

```
│  Security Risk Assessments ─────────────────────────────────╮
│                                                             │
│               Gen               Socket            Snyk      │
│  find-skills  Safe              0 alerts          Med Risk  │
│                                                             │
│  Details: https://skills.sh/vercel-labs/skills              │
│                                                             │
├─────────────────────────────────────────────────────────────╯
```

### 第四步：安装完成

```
◇  Installation complete

│
◇  Installed 1 skill ──────────────────────────────────────────╮
│                                                              │
│  ✓ ~\.agents\skills\find-skills                              │
│    universal: Amp, Cline, Codex, Cursor, Gemini CLI +3 more  │
│                                                              │
├──────────────────────────────────────────────────────────────╯

│
└  Done!  Review skills before use; they run with full agent permissions.
```

## NPM 版本提示

安装完成后，npm 提示有新版本可用：

```
npm notice
npm notice New major version of npm available! 10.9.4 -> 11.11.1
npm notice Changelog: https://github.com/npm/cli/releases/tag/v11.11.1
npm notice To update run: npm install -g npm@11.11.1
npm notice
```

**建议**: 可以运行 `npm install -g npm@11.11.1` 更新到最新版本。

## 安装总结

本次安装过程成功完成了以下内容：

1. **主要技能安装**: remotion-best-practices
   - 提供了 Remotion 视频创建的最佳实践
   - 支持多个主流 AI 助手
   - 安装路径: `.agents\skills\remotion-best-practices`

2. **辅助技能安装**: find-skills
   - 帮助发现和推荐其他技能
   - 支持多个主流 AI 助手
   - 安装路径: `~\.agents\skills\find-skills`

## 安全提醒

两个技能的安全评估都显示：
- 通用安全性：安全
- Socket 检测：无安全警报
- Snyk 评估：中等风险

**重要**: 技能拥有完整的代理权限，使用前请务必审查其功能和安全性。

## 后续建议

1. **更新 npm**: 运行 `npm install -g npm@11.11.1` 更新到最新版本
2. **审查技能**: 仔细阅读技能的文档和功能说明
3. **测试技能**: 在实际项目中测试技能是否正常工作
4. **查看文档**: 访问 Remotion 官方文档了解更多使用方法
   - https://www.remotion.dev/docs

## 参考资料

- Remotion 官方网站: https://www.remotion.dev/
- Remotion GitHub: https://github.com/remotion-dev/remotion
- Skills CLI: https://skills.sh/
- 技能详情页: https://skills.sh/remotion-dev/skills
