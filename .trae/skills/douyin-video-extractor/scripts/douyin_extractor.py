#!/usr/bin/env python3
"""
抖音视频内容提取脚本（Node.js 版本移植）

功能:
1. 从抖音分享链接获取无水印视频下载链接
2. 下载视频并提取音频
3. 使用硅基流动 API 从音频中提取文本
4. 提取视频首帧作为封面
5. 返回完整的视频数据

环境变量:
- DOUYIN_API_KEY: 硅基流动 API 密钥 (用于文案提取功能)

依赖:
- ffmpeg: 音视频处理
- ffprobe: 媒体信息获取
"""

import os
import sys
import time
import json
import argparse
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any


def load_env_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    从.env文件加载配置

    Args:
        env_file: .env文件路径，如果为None则查找默认位置

    Returns:
        配置字典
    """
    config = {}

    # 查找.env文件
    if env_file is None:
        # 从脚本所在目录开始查找
        script_dir = Path(__file__).parent.parent
        env_file = script_dir / ".env"

    if env_file and Path(env_file).exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    return config


# 加载.env配置
ENV_CONFIG = load_env_config()

# 配置 - 优先使用环境变量，其次使用.env配置，最后使用默认值
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT") or ENV_CONFIG.get("USER_AGENT") or "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1"
}

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL") or ENV_CONFIG.get("API_BASE_URL") or "https://api.siliconflow.cn/v1/audio/transcriptions"
DEFAULT_MODEL = os.getenv("TRANSCRIPTION_MODEL") or ENV_CONFIG.get("TRANSCRIPTION_MODEL") or "FunAudioLLM/SenseVoiceSmall"

# 获取API密钥的优先级：环境变量 > .env文件
def get_api_key() -> str:
    """
    获取API密钥

    Returns:
        API密钥字符串
    """
    api_key = os.getenv("DOUYIN_API_KEY") or os.getenv("API_KEY") or ENV_CONFIG.get("DOUYIN_API_KEY") or ENV_CONFIG.get("API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise Exception("未设置有效的 API 密钥，请在 .env 文件中配置 DOUYIN_API_KEY 或设置环境变量")
    return api_key


def http_request(url, method="GET", headers=None, data=None, stream=False):
    """
    HTTP 请求工具函数

    Args:
        url: 请求URL
        method: 请求方法
        headers: 请求头
        data: 请求数据
        stream: 是否流式传输

    Returns:
        响应数据或响应对象
    """
    if headers is None:
        headers = HEADERS.copy()
    else:
        headers = {**HEADERS, **headers}

    response = requests.request(method, url, headers=headers, data=data, stream=stream, timeout=30)

    if stream:
        return response

    try:
        return response.json()
    except:
        return response.text


def download_file(url, filepath, show_progress=True):
    """
    下载文件

    Args:
        url: 下载URL
        filepath: 保存路径
        show_progress: 是否显示进度

    Returns:
        保存的文件路径
    """
    # 从配置获取超时时间
    timeout = int(ENV_CONFIG.get("DOWNLOAD_TIMEOUT", "60"))
    response = requests.get(url, headers=HEADERS, stream=True, timeout=timeout)

    # 处理重定向
    if response.status_code >= 300 and response.status_code < 400:
        return download_file(response.headers["location"], filepath, show_progress)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if show_progress and total_size > 0:
                progress = (downloaded / total_size * 100)
                sys.stdout.write(f"\r下载进度: {progress:.1f}%")
                sys.stdout.flush()

    if show_progress:
        print(f"\n文件已保存: {filepath}")

    return filepath


def run_ffmpeg(args):
    """
    运行 ffmpeg 命令

    Args:
        args: ffmpeg 参数列表

    Raises:
        Exception: ffmpeg 执行失败
    """
    try:
        subprocess.run(
            ["ffmpeg"] + args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"ffmpeg 执行失败: {e.stderr}")
    except FileNotFoundError:
        raise Exception("ffmpeg 未安装，请先安装 ffmpeg")


def get_media_info(filepath):
    """
    获取媒体信息

    Args:
        filepath: 媒体文件路径

    Returns:
        dict: 媒体信息（时长、大小）
    """
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", filepath],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        info = json.loads(result.stdout)
        format_info = info.get("format", {})
        return {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0))
        }
    except:
        # 如果 ffprobe 失败，返回基本文件信息
        stat = os.stat(filepath)
        return {"duration": 0, "size": stat.st_size}


def follow_redirect(url):
    """
    跟踪重定向获取真实 URL

    Args:
        url: 可能重定向的 URL

    Returns:
        str: 真实 URL
    """
    response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=False)
    if response.status_code >= 300 and response.status_code < 400:
        location = response.headers.get("location", "")
        if location.startswith("http"):
            return location
        # 相对路径处理
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{location}"
    return url


def parse_share_url(share_text):
    """
    解析抖音分享链接

    Args:
        share_text: 分享链接文本

    Returns:
        dict: 视频信息（url, title, video_id）
    """
    # 提取 URL
    import re
    url_match = re.search(r"https?://[^\s]+", share_text)
    if not url_match:
        raise Exception("未找到有效的分享链接")

    share_url = url_match.group(0)

    # 如果是短链，先跟踪重定向获取真实 URL
    if "v.douyin.com" in share_url:
        share_url = follow_redirect(share_url)

    # 从真实 URL 中提取数字视频 ID
    video_id_match = re.search(r"/video/(\d+)", share_url)
    aweme_id = video_id_match.group(1) if video_id_match else share_url.split("/")[-1].split("?")[0]

    # 获取视频详情
    api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}"

    try:
        # 尝试直接调用 API
        api_response = http_request(api_url)

        # 检查响应是否为 JSON
        if isinstance(api_response, str):
            # 如果返回字符串，尝试从页面 HTML 中提取数据
            page_url = share_url if share_url.startswith("http") else f"https://www.douyin.com{share_url}"
            page_content = http_request(page_url)

            if isinstance(page_content, str):
                # 尝试从页面中提取视频数据
                data_match = re.search(r'window\._ROUTER_DATA\s*=\s*(.*?)</script>', page_content)
                if data_match:
                    import json
                    json_data = json.loads(data_match.group(1))
                    loader_data = json_data.get("loaderData", json_data)

                    # 尝试多种可能的路径
                    video_data = (
                        loader_data.get("video_(id)/page", {}).get("videoInfoRes", {}).get("item_list", [{}])[0]
                        or loader_data.get("note_(id)/page", {}).get("videoInfoRes", {}).get("item_list", [{}])[0]
                    )

                    if not video_data or not video_data.get("video"):
                        # 尝试直接从页面搜索视频信息
                        aweme_match = re.search(r'"aweme_id":\s*"(\d+)"', page_content)
                        if aweme_match:
                            aweme_id = aweme_match.group(1)
                            raise Exception("需要重新解析视频ID")
                        else:
                            raise Exception("无法从页面中提取视频信息")
        else:
            video_data = api_response.get("aweme_detail", api_response)

        if not video_data or not video_data.get("video"):
            raise Exception("无法解析视频信息：video 数据为空")

        # 获取无水印视频链接
        video_info = video_data.get("video", {})
        play_addr = video_info.get("play_addr", {})
        url_list = play_addr.get("url_list", [])
        video_url = url_list[0].replace("playwm", "play") if url_list else None

        if not video_url:
            download_addr = video_info.get("download_addr", {})
            url_list = download_addr.get("url_list", [])
            video_url = url_list[0] if url_list else None

        desc = video_data.get("desc", f"douyin_{video_info.get('id', 'unknown')}")
        video_id = video_info.get("id", video_data.get("aweme_id", aweme_id))

        # 清理标题中的非法字符
        title = re.sub(r'[\\/:*?"<>|]', '_', desc)

        return {
            "url": video_url,
            "title": title,
            "video_id": str(video_id)
        }
    except Exception as e:
        raise Exception(f"解析视频信息失败: {str(e)}")


def extract_audio(video_path, show_progress=True):
    """
    从视频中提取音频

    Args:
        video_path: 视频文件路径
        show_progress: 是否显示进度

    Returns:
        str: 音频文件路径
    """
    audio_path = video_path.replace(".mp4", ".mp3")

    if show_progress:
        print("正在提取音频...")

    run_ffmpeg([
        "-i", video_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "0",
        "-y",
        audio_path
    ])

    if show_progress:
        print(f"音频已保存: {audio_path}")

    return audio_path


def extract_cover(video_path, show_progress=True):
    """
    从视频中提取首帧作为封面

    Args:
        video_path: 视频文件路径
        show_progress: 是否显示进度

    Returns:
        str: 封面图片路径
    """
    cover_path = video_path.replace(".mp4", ".jpg")

    if show_progress:
        print("正在提取封面...")

    run_ffmpeg([
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        "-y",
        cover_path
    ])

    if show_progress:
        print(f"封面已保存: {cover_path}")

    return cover_path


def transcribe_audio(audio_path, api_key, show_progress=True):
    """
    语音转文字

    Args:
        audio_path: 音频文件路径
        api_key: API 密钥
        show_progress: 是否显示进度

    Returns:
        str: 识别的文本
    """
    if show_progress:
        print("正在识别语音...")

    # 读取音频文件
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    # 创建 multipart/form-data
    import io
    boundary = "----FormBoundary" + "".join([str(ord(c)) for c in str(time.time())])
    body = io.BytesIO()

    body.write(f"--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(audio_path)}"\r\n'.encode())
    body.write("Content-Type: audio/mpeg\r\n\r\n".encode())
    body.write(audio_data)
    body.write(f"\r\n--{boundary}\r\n".encode())
    body.write(f'Content-Disposition: form-data; name="model"\r\n\r\n{DEFAULT_MODEL}\r\n'.encode())
    body.write(f"--{boundary}--\r\n".encode())

    body.seek(0)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }

    response = requests.post(DEFAULT_API_BASE_URL, data=body.getvalue(), headers=headers, timeout=60)

    if response.status_code != 200:
        raise Exception(f"语音识别失败: {response.text}")

    result = response.json()
    text = result.get("text", "")
    if not text:
        text = json.dumps(result, ensure_ascii=False)

    return text


def extract_video_data(share_link, output_dir=None, save_video=None, save_audio=None, show_progress=None):
    """
    提取视频数据的主函数

    Args:
        share_link: 抖音分享链接
        output_dir: 输出目录（可选，默认使用配置文件中的值）
        save_video: 是否保存视频文件（可选，默认使用配置文件中的值）
        save_audio: 是否保存音频文件（可选，默认使用配置文件中的值）
        show_progress: 是否显示进度（可选，默认使用配置文件中的值）

    Returns:
        dict: 包含完整视频数据的字典
    """
    # 从配置获取默认值
    if output_dir is None:
        output_dir = ENV_CONFIG.get("OUTPUT_DIR", "../output")
        # 转换为绝对路径
        if not os.path.isabs(output_dir):
            script_dir = Path(__file__).parent.parent
            output_dir = str(script_dir / output_dir)

    if save_video is None:
        save_video = ENV_CONFIG.get("SAVE_VIDEO", "false").lower() == "true"

    if save_audio is None:
        save_audio = ENV_CONFIG.get("SAVE_AUDIO", "false").lower() == "true"

    if show_progress is None:
        show_progress = ENV_CONFIG.get("SHOW_PROGRESS", "true").lower() == "true"

    # 获取 API 密钥
    api_key = get_api_key()

    if show_progress:
        print("正在解析抖音分享链接...")

    # 解析视频信息
    video_info = parse_share_url(share_link)

    # 使用标题作为文件夹名（避免重复）
    folder_name = video_info["title"]
    # 检查文件夹是否已存在，如果存在则添加序号
    base_folder_path = os.path.join(output_dir, folder_name)
    output_folder = base_folder_path
    counter = 1

    while os.path.exists(output_folder):
        output_folder = f"{base_folder_path}_{counter}"
        counter += 1

    # 创建输出目录
    os.makedirs(output_folder, exist_ok=True)

    # 下载视频
    if show_progress:
        print("正在下载视频...")

    # 使用标题作为文件名（保持与文件夹名一致）
    video_filename = f"{folder_name}.mp4"
    video_path = os.path.join(output_folder, video_filename)
    video_path = download_file(video_info["url"], video_path, show_progress)

    # 获取媒体信息
    media_info = get_media_info(video_path)

    # 提取音频
    audio_path = extract_audio(video_path, show_progress)

    # 提取封面
    cover_path = extract_cover(video_path, show_progress)

    # 语音转文字
    text_content = transcribe_audio(audio_path, api_key, show_progress)

    # 清理临时文件
    if not save_video:
        try:
            os.remove(video_path)
        except:
            pass

    if not save_audio:
        try:
            os.remove(audio_path)
        except:
            pass

    return {
        "video_info": video_info,
        "media_info": media_info,
        "text_content": text_content,
        "cover_path": cover_path,
        "video_path": video_path if save_video else None,
        "audio_path": audio_path if save_audio else None,
        "output_folder": output_folder
    }


def main():
    parser = argparse.ArgumentParser(description="抖音视频内容提取工具")
    parser.add_argument("command", help="命令: info, download, extract")
    parser.add_argument("share_link", help="抖音分享链接")
    parser.add_argument("-o", "--output", help="输出目录（默认使用配置文件中的值）")
    parser.add_argument("-v", "--save-video", action="store_true", help="保存视频文件")
    parser.add_argument("-a", "--save-audio", action="store_true", help="保存音频文件")
    parser.add_argument("--no-progress", action="store_true", help="不显示进度")

    args = parser.parse_args()

    if not args.command or not args.share_link:
        print("""
抖音视频内容提取工具

用法:
  python douyin_extractor.py info <分享链接>              - 获取视频信息
  python douyin_extractor.py download <链接> -o <目录>   - 下载视频
  python douyin_extractor.py extract <链接> [选项]       - 提取文案（推荐）

选项:
  -o, --output <目录>      - 指定输出目录
  -v, --save-video         - 保存视频文件
  -a, --save-audio         - 保存音频文件
  --no-progress            - 不显示进度信息

配置文件:
  .env 文件（位于技能目录）用于配置 API 密钥和其他参数
  详情请参考 .env 文件中的注释
""")
        sys.exit(1)

    show_progress = not args.no_progress

    try:
        if args.command == "info":
            info = parse_share_url(args.share_link)
            print("\n" + "=" * 50)
            print("视频信息:")
            print("=" * 50)
            print(f"视频ID: {info['video_id']}")
            print(f"标题: {info['title']}")
            print(f"下载链接: {info['url']}")
            print("=" * 50)

        elif args.command == "download":
            info = parse_share_url(args.share_link)

            # 获取输出目录
            output_dir = args.output
            if output_dir is None:
                output_dir = ENV_CONFIG.get("OUTPUT_DIR", "../output")
                if not os.path.isabs(output_dir):
                    script_dir = Path(__file__).parent.parent
                    output_dir = str(script_dir / output_dir)

            # 使用标题作为文件名
            video_filename = f"{info['title']}.mp4"
            video_path = os.path.join(output_dir, video_filename)

            os.makedirs(output_dir, exist_ok=True)
            download_file(info["url"], video_path, show_progress)
            print(f"\n视频已保存到: {video_path}")

        elif args.command == "extract":
            result = extract_video_data(
                args.share_link,
                output_dir=args.output,
                save_video=args.save_video,
                save_audio=args.save_audio,
                show_progress=show_progress
            )
            print("\n" + "=" * 50)
            print("提取完成!")
            print("=" * 50)
            print(f"视频ID: {result['video_info']['video_id']}")
            print(f"标题: {result['video_info']['title']}")
            print(f"时长: {result['media_info']['duration']:.2f}秒")
            print(f"输出目录: {result['output_folder']}")
            print(f"封面: {result['cover_path']}")
            if result.get('video_path'):
                print(f"视频: {result['video_path']}")
            if result.get('audio_path'):
                print(f"音频: {result['audio_path']}")
            print("=" * 50)
            print("\n识别的文字内容:\n")
            print(result["text_content"][:500] + "..." if len(result["text_content"]) > 500 else result["text_content"])
            print("\n" + "=" * 50)
        else:
            print(f"未知命令: {args.command}")
            sys.exit(1)

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
