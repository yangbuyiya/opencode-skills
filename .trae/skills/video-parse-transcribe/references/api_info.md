# 视频解析与转录 API 信息

## 工作流程

1.  **环境配置加载**: 脚本首先会从项目根目录下的 `.env` 文件中加载 API 密钥和相关配置。
2.  **参数解析**: 通过命令行接收用户传入的视频 URL、API 密钥（可选）和模型名称（可选）。命令行参数的优先级高于 `.env` 文件中的配置。
3.  **API 请求**: 向视频解析服务发送请求。
4.  **媒体处理**:
    - **视频**: 下载视频 -> `ffmpeg` 提取音频 -> 调用 ASR API 转录。
    - **图文**: 若链接为图文笔记，则跳过媒体处理，仅输出元数据。
5.  **报告生成**: 将所有信息汇总，生成 `.md` 文件。

## 视频解析 API

- **URL**: `http://110.40.172.157:8000/video/share/url/parse?url=`
- **Method**: GET
- **参数**: `url` (需要解析的短视频链接)
- **响应格式**: JSON, 包含 `video_url`, `cover_url`, `title`, `images` 等字段。

## 语音转录 API (SiliconFlow)

- **URL**: `https://api.siliconflow.cn/v1/audio/transcriptions`
- **Method**: POST (Multipart/form-data)
- **Header**: `Authorization: Bearer <API_KEY>`
- **参数**:
  - `file`: 音频文件 (.mp3, .wav 等)
  - `model`: 语音识别模型，默认 `FunAudioLLM/SenseVoiceSmall`
- **响应格式**: JSON, 包含 `text` 字段。

## 处理逻辑说明

1. 接收用户传递的短视频链接。
2. 调用 **视频解析 API** 获取视频元数据。
3. 若 `video_url` 存在：
   - 下载视频文件。
   - 使用 `ffmpeg` 提取音频 (采样率 16000Hz, 单声道)。
   - 调用 **语音转录 API** 获取视频文本内容。
4. 若 `video_url` 不存在但 `images` 存在：
   - 表明是图文笔记，仅返回解析出的元数据。
5. 最终返回完整的解析结果与转录文本。
