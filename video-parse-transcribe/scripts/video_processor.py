import os
import sys
import requests
import subprocess
import json
import uuid
import re
from urllib.parse import quote
from pathlib import Path

# 配置信息
DEFAULT_API_BASE_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"
DEFAULT_MODEL = "FunAudioLLM/SenseVoiceSmall"
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1"
PARSE_API_URL = "http://110.40.172.157:8000/video/share/url/parse?url="

def load_env(env_path):
    """
    手动读取 .env 文件（避免引入额外的 python-dotenv 依赖）
    """
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def save_to_markdown(result, original_url, output_dir=None):
    """
    将处理结果保存为 Markdown 文件
    """
    # 如果未指定目录，默认为脚本所在目录的父级 demos 目录
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(os.path.dirname(script_dir), "demos")

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parse_data = result.get("parse_info", {})
    if not parse_data or parse_data.get("code") != 200:
        return None

    data = parse_data.get("data", {})
    title = data.get("title", "未命名视频")
    author = data.get("author", {}).get("name", "未知作者")
    cover_url = data.get("cover_url", "")
    transcription = result.get("transcription", "无转录内容")

    # 清理文件名中的非法字符
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    filename = f"{safe_title}.md"
    file_path = os.path.join(output_dir, filename)

    md_content = f"""# {title}

## 基本信息
- **作者**: {author}
- **原始链接**: [{original_url}]({original_url})
- **封面**: 
![封面图]({cover_url})

## 🎙️ 语音转录内容
{transcription}

---
*生成时间: {Path(file_path).stat().st_mtime if os.path.exists(file_path) else "刚刚"}*
"""
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return file_path

def download_video(video_url, output_path):
    """
    下载视频文件到本地
    """
    print(f"正在下载视频: {video_url} -> {output_path}")
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(video_url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("视频下载完成")
        return True
    except Exception as e:
        print(f"下载视频失败: {e}")
        return False

def extract_audio(video_path, audio_path):
    """
    使用 ffmpeg 从视频中提取音频 (mp3)
    """
    print(f"正在提取音频: {video_path} -> {audio_path}")
    try:
        # ffmpeg 参数: -i 输入文件 -vn 不处理视频 -acodec libmp3lame 音频编码 -ar 16000 采样率 -ac 1 声道 -y 覆盖输出
        cmd = [
            "ffmpeg", "-i", str(video_path),
            "-vn", "-acodec", "libmp3lame",
            "-ar", "16000", "-ac", "1",
            "-y", str(audio_path)
        ]
        # 运行 ffmpeg 命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ffmpeg 提取音频失败: {result.stderr}")
            return False
        print("音频提取完成")
        return True
    except Exception as e:
        print(f"提取音频异常: {e}")
        return False

def transcribe_audio(audio_path, api_key, model=DEFAULT_MODEL):
    """
    调用 SiliconFlow API 转录音频为文本
    """
    print(f"正在调用语音识别 API 提取文本 (模型: {model})...")
    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        files = {
            "file": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/mpeg")
        }
        data = {
            "model": model
        }
        response = requests.post(DEFAULT_API_BASE_URL, headers=headers, files=files, data=data, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        if "text" in result:
            print("文本提取成功")
            return result["text"]
        else:
            print(f"API 响应中没有找到 text 字段: {result}")
            return str(result)
    except Exception as e:
        print(f"语音转录失败: {e}")
        return None

def process_video_url(parse_api_url, video_url_to_parse, api_key, model=DEFAULT_MODEL):
    """
    核心流程: 解析URL -> 下载视频 -> 提取音频 -> 转录文本
    """
    # 1. 解析 URL
    print(f"正在解析视频 URL: {video_url_to_parse}")
    full_parse_url = f"{parse_api_url}{quote(video_url_to_parse)}"
    try:
        response = requests.get(full_parse_url, timeout=30)
        response.raise_for_status()
        parse_data = response.json()
        
        if parse_data.get("code") != 200:
            print(f"解析失败: {parse_data.get('msg')}")
            return parse_data

        data = parse_data.get("data", {})
        video_url = data.get("video_url")
        
        # 结果字典
        final_result = {
            "parse_info": parse_data,
            "transcription": None
        }

        # 2. 如果存在视频 URL, 则进行转录
        if video_url:
            # 创建临时文件
            temp_id = uuid.uuid4().hex
            temp_dir = Path("temp_video_process")
            temp_dir.mkdir(exist_ok=True)
            
            video_file = temp_dir / f"video_{temp_id}.mp4"
            audio_file = temp_dir / f"audio_{temp_id}.mp3"
            
            try:
                # 下载
                if download_video(video_url, video_file):
                    # 提取音频
                    if extract_audio(video_file, audio_file):
                        # 转录
                        text = transcribe_audio(audio_file, api_key, model)
                        final_result["transcription"] = text
            finally:
                # 清理临时文件
                if video_file.exists():
                    os.remove(video_file)
                if audio_file.exists():
                    os.remove(audio_file)
                # 如果目录为空，也删除
                try:
                    os.rmdir(temp_dir)
                except OSError:
                    pass
        else:
            print("未找到 video_url，跳过转录流程 (可能是图文笔记)")
            
        return final_result

    except Exception as e:
        print(f"处理视频过程中发生错误: {e}")
        return {"error": str(e)}

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="解析视频链接并转录音频。")
    parser.add_argument("--url", required=True, help="要解析的视频分享链接。")
    parser.add_argument("--api_key", help="SiliconFlow API 密钥。如果未提供，将从 .env 文件中读取。")
    parser.add_argument("--model", help="要使用的语音识别模型。")

    args = parser.parse_args()

    # 尝试从 .env 加载配置
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(script_dir, ".env")
    if not os.path.exists(env_file):
        env_file = os.path.join(os.path.dirname(script_dir), ".env")

    env_config = load_env(env_file)

    # 优先级：命令行参数 > .env 文件 > 默认值
    video_url = args.url
    api_key = args.api_key or env_config.get("api_key")
    model = args.model or env_config.get("model", DEFAULT_MODEL)
    parse_api = env_config.get("parse_api_url", PARSE_API_URL)

    if not api_key:
        print("错误: 未提供 api_key。请通过命令行参数传递或在 .env 文件中设置。")
        sys.exit(1)

    result = process_video_url(parse_api, video_url, api_key, model)
    print("\n--- 处理结果 ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 自动保存为 Markdown
    md_file = save_to_markdown(result, video_url)
    if md_file:
        print(f"\n✅ 已生成 Markdown 文档: {os.path.abspath(md_file)}")
