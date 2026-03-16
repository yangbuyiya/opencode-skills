---
name: douyin-video-extractor
description: 抖音视频内容提取与讲解工具；支持从抖音链接提取视频数据（无水印下载、封面、音频、文案），自动提取金句、生成数据说明，并生成包含内容分析的Markdown文档
dependency:
  python:
    - requests>=2.31.0
  system:
    - ffmpeg
    - ffprobe
---

# 抖音视频内容提取器

## 任务目标
- 本 Skill 用于：从抖音链接提取视频完整数据并生成内容讲解文档
- 能力包含：
  - 自动解析抖音分享链接，获取无水印视频
  - 下载视频并提取封面（首帧）和音频
  - 使用语音识别技术提取视频文案
  - 智能提取视频内的金句（精华观点、经典语录）
  - 生成数据说明（数据来源、字段含义、使用方式）
  - 智能分析视频内容并生成讲解
  - 生成结构化的 Markdown 文档
- 触发条件：用户需要分析或整理抖音视频内容时

## 前置准备

### 配置文件设置
本 Skill 使用 `.env` 配置文件管理所有配置项，位于技能根目录。

**必需配置项**：
- `DOUYIN_API_KEY`：硅基流动 API 密钥（必需）
  - 获取方式：访问 https://cloud.siliconflow.cn/ 注册并获取 API Key
  - 在 `.env` 文件中设置：`DOUYIN_API_KEY=your-api-key-here`

**可选配置项**：
- `OUTPUT_DIR`：输出目录（默认 `../output`，即 skill 目录下的 output 文件夹）
- `SAVE_VIDEO`：是否保存视频文件（默认 `false`）
- `SAVE_AUDIO`：是否保存音频文件（默认 `false`）
- `API_BASE_URL`：API 基础 URL（默认使用硅基流动）
- `TRANSCRIPTION_MODEL`：语音识别模型（默认 `FunAudioLLM/SenseVoiceSmall`）
- `SHOW_PROGRESS`：是否显示进度信息（默认 `true`）

**配置优先级**：
命令行参数 > 环境变量 > .env 配置文件 > 默认值

### 系统依赖
需要安装以下工具：
- `ffmpeg`：音视频处理（用于提取音频和封面）
- `ffprobe`：媒体信息获取

安装方式：
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载
```

## 操作步骤

### 标准流程

1. **获取视频数据**
   - 调用 `scripts/douyin_extractor.py` 提取视频信息
   - 传入参数：抖音链接（如 `https://v.douyin.com/xxx`）
   - 脚本将自动：
     - 解析抖音分享链接，获取无水印视频
     - 下载视频文件到以视频标题命名的文件夹
     - 提取音频（使用 ffmpeg）到同一文件夹
     - 提取封面（使用 ffmpeg 截取首帧）到同一文件夹
     - 调用硅基流动 API 进行语音识别
     - 返回完整的视频数据（JSON格式）

2. **文件组织结构**
   - 输出目录：默认为 `skill/output/`（可在 `.env` 中配置）
   - 每个视频的所有文件都放在独立的文件夹中，文件夹名为视频标题
   - 如果标题重复，会自动添加序号（如 `标题_1`, `标题_2`）
   - 文件命名规则：
     - 文件夹：`{视频标题}`
     - 视频文件：`{视频标题}.mp4`（如果保存）
     - 音频文件：`{视频标题}.mp3`（如果保存）
     - 封面图片：`{视频标题}.jpg`
     - Markdown 文档：`{视频标题}.md`（如果生成）

3. **生成讲解文档**
   - 基于返回的数据，智能体将生成 Markdown 文档，包含以下章节：
     - **视频基本信息**：标题、视频ID、时长、视频链接
     - **视频金句**：从识别的文案中提取精华观点、经典语录（3-5条）
     - **原始文案**：语音识别的完整文本内容
     - **内容讲解**：根据文案内容分析核心观点和关键信息
     - **数据说明**：解释数据来源、字段含义、使用方式
     - **媒体资源**：视频链接、封面图片、音频文件
     - **完整数据**：原始API返回的所有数据

   - **格式要求**：
     - 视频/音频链接：使用代码块格式展示，添加提示"复制链接到浏览器地址栏访问"
     - 封面图片：使用Markdown图片语法正常显示
     - 标题：使用二级标题
     - 列表：使用无序列表
     - 完整数据：使用代码块展示JSON格式
     - 金句提取：每条金句独立一行，使用引用格式（>）
     - 数据说明：使用表格或列表格式，清晰说明各字段含义

4. **输出结果**
   - 将生成的 Markdown 文档保存到视频文件夹中
   - 用户可直接复制使用或保存为文件

## 资源索引

- **必要脚本**：见 [scripts/douyin_extractor.py](scripts/douyin_extractor.py)
  - 用途：调用视频提取流程，获取完整的视频数据
  - 参数：
    - `command`: 命令类型（info/download/extract）
    - `share_link`: 抖音分享链接
    - `-o/--output`: 输出目录（可选，默认使用 .env 中的配置）
    - `-v/--save-video`: 是否保存视频文件（可选，默认使用 .env 中的配置）
    - `-a/--save-audio`: 是否保存音频文件（可选，默认使用 .env 中的配置）
    - `--no-progress`: 不显示进度信息

- **配置文件**：见 [.env](.env)
  - 用途：配置 API 密钥、输出目录等参数
  - 必需配置项：`DOUYIN_API_KEY`
  - 可选配置项：`OUTPUT_DIR`、`SAVE_VIDEO`、`SAVE_AUDIO`、`API_BASE_URL`、`TRANSCRIPTION_MODEL`、`SHOW_PROGRESS`

- **技术参考**：见 [references/implementation.md](references/implementation.md)
  - 何时读取：需要了解技术实现细节时

## 注意事项

- **API轮询**：脚本会自动处理视频下载和语音识别，可能需要1-3分钟
- **语音识别**：使用硅基流动 API 的 FunAudioLLM/SenseVoiceSmall 模型，需要有效的 API Key
- **内容讲解**：智能体将基于识别的文本内容（textContent）进行客观分析，提取核心观点
- **金句提取**：从识别的文本内容中提取有价值的观点、经典语句，通常3-5条，保持原意，不加个人主观评价
- **数据说明**：解释各数据字段的含义、来源和使用方式，帮助用户理解数据的用途
- **数据保留**：文档中会保留完整的原始数据，方便用户二次使用
- **视频链接访问**：视频链接有防盗链保护，**不要直接点击**。请复制链接到浏览器地址栏访问
- **封面显示**：封面图片可以正常显示，可直接查看

## 使用示例

### 示例1：提取单个视频并生成讲解（推荐）

```bash
python scripts/douyin_extractor.py extract "https://v.douyin.com/xxx"
```

**文件输出结构**：
```
output/
└── 小个子女生如何逆袭第一眼大美女/
    ├── 小个子女生如何逆袭第一眼大美女.jpg        # 封面图片
    ├── 小个子女生如何逆袭第一眼大美女.mp4        # 视频文件（如果保存）
    ├── 小个子女生如何逆袭第一眼大美女.mp3        # 音频文件（如果保存）
    └── 小个子女生如何逆袭第一眼大美女.md         # Markdown 文档
```

**输出示例**（Markdown 文档内容）：
```markdown
# 视频内容分析

## 视频基本信息
- **标题**：小个子女生如何逆袭第一眼大美女
- **视频ID**：7342918392748299524
- **时长**：156.36秒
- **视频链接**：
  ```
  https://sns-video-bd.xhscdn.com/f0370019b934b9b6e_258.mp4
  ```
  💡 提示：复制链接到浏览器地址栏访问

## 视频金句

> 小个子女生真的不要再和别人卷身高上的天赋，这是天生注定的。

> 找到自己的风格比盲目模仿更重要。

> 适合自己的才是最好的，不要被世俗眼光束缚。

## 原始文案
小个子女生真的不要再和别人卷身高上的天赋，这是天生注定的...

## 内容讲解
本视频主要讲述了...

## 数据说明

| 数据字段 | 含义 | 用途 |
|---------|------|------|
| video_id | 视频唯一标识 | 识别和引用特定视频 |
| title | 视频标题 | 了解视频主题 |
| text_content | 语音识别的文本内容 | 获取视频完整的文字内容 |
| video_url | 视频文件地址 | 下载或嵌入视频 |
| cover_path | 封面图片路径 | 获取视频封面 |
| duration | 视频时长（秒） | 了解视频长度 |
| media_info | 媒体信息（大小、时长等） | 了解视频技术参数 |

**数据来源**：
- 视频信息：通过抖音公开 API 接口解析
- 文案内容：使用硅基流动语音识别 API 提取（模型：FunAudioLLM/SenseVoiceSmall）
- 封面：使用 ffmpeg 从视频中截取首帧
- 音频：使用 ffmpeg 从视频中提取

## 媒体资源
- **封面**：
  ![封面](./小个子女生如何逆袭第一眼大美女.jpg)

- **音频链接**：
  ```
  https://sns-video-bd.xhscdn.com/audio.mp3
  ```
  💡 提示：复制链接到浏览器地址栏访问

## 完整数据
```json
{
  "video_info": {
    "video_id": "7342918392748299524",
    "title": "小个子女生如何逆袭第一眼大美女",
    "url": "https://sns-video-bd.xhscdn.com/f0370019b934b9b6e_258.mp4"
  },
  "media_info": {
    "duration": 156.36,
    "size": 15728640
  },
  "text_content": "小个子女生真的不要再和别人卷身高上的天赋...",
  "cover_path": "小个子女生如何逆袭第一眼大美女.jpg"
}
```
```

### 示例2：提取视频并保存音频和视频

```bash
python scripts/douyin_extractor.py extract "https://v.douyin.com/xxx" -v -a
```

### 示例3：仅获取视频信息

```bash
python scripts/douyin_extractor.py info "https://v.douyin.com/xxx"
```

### 示例4：下载视频文件到指定目录

```bash
python scripts/douyin_extractor.py download "https://v.douyin.com/xxx" -o ./videos
```

### 示例5：批量处理视频链接

智能体可依次处理多个视频链接，为每个视频生成独立的分析文档和文件夹。
