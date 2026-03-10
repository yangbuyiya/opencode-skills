---
name: video-parse-transcribe
author: 杨不易呀(yangbuyiya)
description: 此技能用于解析短视频链接，支持解析抖音、快手、B站等多个主流平台的短视频和图文链接，并能自动提取语音内容转录为文字。适用于需要批量获取视频元数据或将视频内容转为文本的场景。
---

# 视频解析与转录技能

此技能通过自动化流程，从短视频分享链接中提取元数据，并将其语音内容转录为结构化的文字报告。

## 使用场景

- 当用户提供短视频分享链接，并希望了解其详细内容或摘要时
- 需要将视频内容转换为文字，用于笔记创作、内容二次加工或翻译时
- 自动化批量获取视频元数据（标题、封面、作者）及原始视频地址时

## 工作流程

### 第一步：解析视频元数据
调用特定的 API 解析短视频链接，获取标题、封面图、作者信息以及原始视频下载链接。

### 第二步：提取视频音频
如果解析结果包含视频文件，系统会自动下载视频，并利用 `ffmpeg` 工具从视频中提取高质量音频轨道。

### 第三步：语音转录文字
调用 SiliconFlow 的 ASR（语音识别）服务（默认模型：`FunAudioLLM/SenseVoiceSmall`），将提取的音频全文转录为文字。

## 如何使用

### 1. 安装依赖
首先，确保您的系统中已安装 `ffmpeg` 并将其添加至系统环境变量，然后安装 Python 依赖：

```bash
pip install -r requirements.txt
```

### 2. 环境配置
在技能根目录下创建 `.env` 文件，并配置相关 API 密钥：

```env
# SiliconFlow API Key
api_key=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 视频转录模型 (默认: FunAudioLLM/SenseVoiceSmall)
model=FunAudioLLM/SenseVoiceSmall
# 视频解析 API 地址
parse_api_url=http://110.40.172.157:8000/video/share/url/parse?url=
# SiliconFlow ASR API 地址
siliconflow_api_url=https://api.siliconflow.cn/v1/audio/transcriptions
```

### 3. 运行脚本
使用核心脚本执行解析和转录任务：

```bash
python scripts/video_processor.py --url <VIDEO_URL> [options]
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--url` | 无 | **必需**。要解析的视频分享链接（建议用引号包裹） | 无 |
| `--api_key` | 无 | 可选。SiliconFlow API 密钥。默认从 `.env` 读取 | 从 .env 读取 |
| `--model` | 无 | 可选。语音识别模型名称 | `FunAudioLLM/SenseVoiceSmall` |

## 常用示例

```bash
# 1) 基础解析与转录
python scripts/video_processor.py --url "https://v.douyin.com/xxx/"

# 2) 指定模型进行转录
python scripts/video_processor.py --url "https://www.xiaohongshu.com/discovery/item/xxx" --model FunAudioLLM/SenseVoiceSmall

# 3) 临时指定 API Key
python scripts/video_processor.py --url "https://www.bilibili.com/video/xxx" --api_key sk-your-key
```

## 技能资源

### 脚本文件
- `scripts/video_processor.py` - 核心自动化处理脚本
- `references/api_info.md` - 详细的 API 接口文档说明

### 结果输出
- 命令行实时打印 JSON 格式结果
- 自动在 `demos/` 目录下生成结构化的 Markdown 报告

## 注意事项

1. **环境依赖**：必须预先在系统中安装 `ffmpeg`，否则音频提取步骤将失败
2. **网络要求**：脚本需要访问解析 API 及 SiliconFlow API，请确保网络环境畅通
3. **API 限制**：语音转录受 SiliconFlow 额度限制，解析 API 受第三方服务稳定性影响
4. **输出路径**：默认生成的报告会保存在 `demos` 文件夹下，请确保该文件夹存在或有写入权限

# 支持平台

## 视频/图集/LivePhoto
| 平台 | 状态 | 平台 | 状态 |
|----|----|----|----|
| 抖音 | ✔ | 快手 | ✔ |
| 小红书 | ✔ | 哔哩哔哩 | ✔ |
| 皮皮虾 | ✔ | 微博 | ✔ |
| 西瓜视频 | ✔ | 火山视频 | ✔ |
| AcFun | ✔ | 美拍 | ✔ |
| 梨视频 | ✔ | 好看视频 | ✔ |
| 更多... | ✔ | | |

> 完整支持列表请参考 [GitHub 项目](https://github.com/yangbuyiya/parse-video-py2)
