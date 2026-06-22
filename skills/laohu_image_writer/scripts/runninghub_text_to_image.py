#!/usr/bin/env python3
"""老胡音乐项目专用 RunningHub 文生图脚本。

只调用 RunningHub text-to-image，不调用 Codex 内置生图，也不依赖其他项目脚本。
默认 1:1、2k，用于音乐封面。
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import struct
from typing import Dict, Optional


DEFAULT_BASE_URL = "https://www.runninghub.cn/openapi/v2"
DEFAULT_UPSCALE_BASE_URL = "https://www.runninghub.ai/openapi/v2"
DEFAULT_SUBMIT_PATH = "/rhart-image-g-2/text-to-image"
QUERY_PATH = "/query"
UPLOAD_PATH = "/media/upload/binary"
UPSCALE_AI_APP_PATH = "/run/ai-app/2067476912817131522"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_RESOLUTION = "2k"
DEFAULT_QUALITY = ""
DEFAULT_UPSCALE = True
UPSCALE_IMAGE_NODE_ID = "2"
UPSCALE_SIZE_NODE_ID = "6"
UPSCALE_SIZE_FIELD_NAME = "value"
MIN_SIDE_BY_RESOLUTION = {
    "1k": 1000,
    "2k": 2000,
    "4k": 4000,
}
POLL_INTERVAL = 5.0
TIMEOUT_SECONDS = 600.0
ENV_FILES = (
    ".env",
    "~/.laohu-image.env",
)
SUPPORTED_RATIOS = {
    "1:1",
    "3:2",
    "2:3",
    "5:4",
    "4:5",
    "16:9",
    "9:16",
    "21:9",
    "3:4",
    "4:3",
    "9:21",
    "1:2",
    "2:1",
    "1:3",
    "3:1",
}
SUPPORTED_RESOLUTIONS = {"1k", "2k", "4k"}


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and not os.getenv(key):
            os.environ[key] = value


def load_env() -> None:
    cwd = Path.cwd()
    for env_file in ENV_FILES:
        path = Path(env_file).expanduser()
        if not path.is_absolute():
            path = cwd / path
        load_env_file(path)


def read_prompt(prompt: Optional[str], prompt_file: Optional[str]) -> str:
    if prompt and prompt_file:
        die("Use --prompt or --prompt-file, not both.")
    if prompt_file:
        if prompt_file == "-":
            text = sys.stdin.read()
        else:
            path = Path(prompt_file)
            if not path.exists():
                die(f"Prompt file not found: {path}")
            text = path.read_text(encoding="utf-8")
        text = extract_prompt_block(text).strip()
        if not text:
            die("Prompt file is empty.")
        return text
    if prompt:
        text = prompt.strip()
        if not text:
            die("Prompt is empty.")
        return text
    die("Missing prompt. Use --prompt or --prompt-file.")
    return ""


def extract_prompt_block(text: str) -> str:
    """Allow project markdown prompt records while sending only the prompt body."""
    marker = "## Prompt"
    marker_index = text.find(marker)
    if marker_index < 0:
        return text
    after_marker = text[marker_index + len(marker) :]
    fence_start = after_marker.find("```")
    if fence_start < 0:
        return after_marker
    block = after_marker[fence_start + 3 :]
    first_newline = block.find("\n")
    if first_newline >= 0:
        block = block[first_newline + 1 :]
    fence_end = block.find("```")
    if fence_end >= 0:
        block = block[:fence_end]
    return block


def curl_json(url: str, *, api_key: str, payload: Dict[str, object]) -> Dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="laohu-runninghub-") as tmp:
        payload_path = Path(tmp) / "payload.json"
        response_path = Path(tmp) / "response.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        cmd = [
            "curl",
            "--http1.1",
            "-sS",
            url,
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Authorization: Bearer {api_key}",
            "-d",
            f"@{payload_path}",
        ]
        with response_path.open("wb") as response_file:
            subprocess.run(cmd, stdout=response_file, check=True)
        raw = response_path.read_text(encoding="utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            die(f"Response is not JSON: {exc}\n{raw[:500]}")
        if not isinstance(parsed, dict):
            die(f"Response is not an object: {raw[:500]}")
        return parsed


def curl_upload(url: str, *, api_key: str, path: Path) -> Dict[str, object]:
    cmd = [
        "curl",
        "--http1.1",
        "-sS",
        url,
        "-H",
        f"Authorization: Bearer {api_key}",
        "-F",
        f"file=@{path}",
    ]
    raw = subprocess.check_output(cmd).decode("utf-8", errors="replace")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"Upload response is not JSON: {exc}\n{raw[:500]}")
    if not isinstance(parsed, dict):
        die(f"Upload response is not an object: {raw[:500]}")
    return parsed


def download_image(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "--http1.1", "-fL", "-sS", url, "-o", str(out)]
    subprocess.run(cmd, check=True)


def read_image_size(path: Path) -> Optional[tuple[int, int]]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)
    if data.startswith(b"\xff\xd8"):
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            i += 2
            if marker in {0xD8, 0xD9}:
                continue
            if i + 2 > len(data):
                return None
            length = struct.unpack(">H", data[i : i + 2])[0]
            if length < 2 or i + length > len(data):
                return None
            if 0xC0 <= marker <= 0xC3:
                height, width = struct.unpack(">HH", data[i + 3 : i + 7])
                return int(width), int(height)
            i += length
    return None


def generate(args: argparse.Namespace) -> None:
    load_env()
    api_key = os.getenv("RUNNINGHUB_API_KEY") or os.getenv("OPENAI_API_KEY")
    upscale_api_key = (
        args.upscale_api_key
        or os.getenv("RUNNINGHUB_UPSCALE_API_KEY")
        or os.getenv("RUNNINGHUB_AI_APP_API_KEY")
        or api_key
    )
    if not api_key:
        die("Missing RUNNINGHUB_API_KEY or OPENAI_API_KEY. Configure project .env or environment variables.")

    aspect_ratio = args.aspect_ratio
    resolution = args.resolution
    if aspect_ratio not in SUPPORTED_RATIOS:
        die(f"Unsupported aspect ratio: {aspect_ratio}")
    if resolution not in SUPPORTED_RESOLUTIONS:
        die(f"Unsupported resolution: {resolution}")

    out = Path(args.out)
    if out.exists() and not args.force:
        die(f"Output already exists: {out} (use --force to overwrite).")

    prompt = "" if args.input_image else read_prompt(args.prompt, args.prompt_file)
    base_url = (args.base_url or os.getenv("RUNNINGHUB_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    upscale_base_url = (
        args.upscale_base_url
        or os.getenv("RUNNINGHUB_UPSCALE_BASE_URL")
        or DEFAULT_UPSCALE_BASE_URL
    ).rstrip("/")
    submit_path = (args.submit_path or os.getenv("RUNNINGHUB_SUBMIT_PATH") or DEFAULT_SUBMIT_PATH).strip()
    if not submit_path.startswith("/"):
        submit_path = "/" + submit_path
    submit_url = base_url + submit_path
    query_url = base_url + QUERY_PATH
    upload_url = upscale_base_url + UPLOAD_PATH
    upscale_url = base_url + UPSCALE_AI_APP_PATH
    upscale_query_url = upscale_base_url + QUERY_PATH
    upscale_run_url = upscale_base_url + UPSCALE_AI_APP_PATH
    payload: Dict[str, object] = {
        "prompt": prompt,
        "aspectRatio": aspect_ratio,
        "resolution": resolution,
    }
    if args.quality:
        payload["quality"] = args.quality

    if args.input_image:
        input_image_path = Path(args.input_image)
        if not input_image_path.exists():
            die(f"Input image not found: {input_image_path}")
        download_image_task_id = ""
        task_id = "input-image"
        out.parent.mkdir(parents=True, exist_ok=True)
        low_out = input_image_path
        if not args.upscale:
            if input_image_path.resolve() != out.resolve():
                out.write_bytes(input_image_path.read_bytes())
            image_size = read_image_size(out)
            meta = {
                "taskId": task_id,
                "textToImageTaskId": download_image_task_id,
                "imageUrl": "",
                "out": str(out),
                "aspectRatio": aspect_ratio,
                "resolution": resolution,
                "submitPath": "input-image",
                "quality": args.quality,
                "upscaled": False,
                "upscale": None,
                "actualWidth": image_size[0] if image_size else None,
                "actualHeight": image_size[1] if image_size else None,
                "pixelStatus": "unknown",
            }
            print(json.dumps(meta, ensure_ascii=False, indent=2))
            return
    else:
        print(f"Calling RunningHub: {submit_url}", file=sys.stderr)
        submit_response = curl_json(submit_url, api_key=api_key, payload=payload)
        if submit_response.get("errorMessage"):
            die(
                f"RunningHub submit failed: {submit_response.get('errorMessage')} "
                f"| {submit_response.get('errorCode', 'unknown')}"
            )
        task_id = str(submit_response.get("taskId") or "").strip()
        if not task_id:
            die(f"RunningHub response did not contain taskId: {submit_response}")

    started = time.time()
    while True:
        if args.input_image:
            image_url = ""
            if args.upscale:
                final_task_id = task_id
                final_image_url = image_url
                upscale_meta = None
                upscale_out = out
                upload_response = curl_upload(upload_url, api_key=upscale_api_key, path=low_out)
                if upload_response.get("code") not in (0, "0", None) and upload_response.get("message") != "success":
                    die(f"RunningHub upload failed: {upload_response}")
                upload_data = upload_response.get("data") or {}
                uploaded_file_name = str(upload_data.get("fileName") or upload_data.get("download_url") or "").strip()
                if not uploaded_file_name:
                    die(f"RunningHub upload returned no fileName/download_url: {upload_response}")
                upscale_payload: Dict[str, object] = {
                    "nodeInfoList": [
                        {
                            "nodeId": UPSCALE_IMAGE_NODE_ID,
                            "fieldName": "image",
                            "fieldValue": uploaded_file_name,
                            "description": "image",
                        },
                        {
                            "nodeId": UPSCALE_SIZE_NODE_ID,
                            "fieldName": UPSCALE_SIZE_FIELD_NAME,
                            "fieldValue": str(MIN_SIDE_BY_RESOLUTION.get(resolution, 2048)),
                            "description": "longest edge size",
                        }
                    ],
                    "instanceType": args.instance_type,
                    "usePersonalQueue": "true" if args.use_personal_queue else "false",
                }
                print(f"Calling RunningHub upscale app: {upscale_run_url}", file=sys.stderr)
                upscale_submit_response = curl_json(upscale_run_url, api_key=upscale_api_key, payload=upscale_payload)
                if upscale_submit_response.get("errorMessage"):
                    die(
                        f"RunningHub upscale submit failed: {upscale_submit_response.get('errorMessage')} "
                        f"| {upscale_submit_response.get('errorCode', 'unknown')}"
                    )
                upscale_task_id = str(upscale_submit_response.get("taskId") or "").strip()
                if not upscale_task_id:
                    die(f"RunningHub upscale response did not contain taskId: {upscale_submit_response}")
                upscale_started = time.time()
                while True:
                    if time.time() - upscale_started > TIMEOUT_SECONDS:
                        die(f"RunningHub upscale task timed out after {TIMEOUT_SECONDS:.0f}s: {upscale_task_id}")
                    upscale_status_response = curl_json(
                        upscale_query_url,
                        api_key=upscale_api_key,
                        payload={"taskId": upscale_task_id},
                    )
                    upscale_status = str(upscale_status_response.get("status") or "").upper()
                    if upscale_status == "SUCCESS":
                        upscale_results = upscale_status_response.get("results") or []
                        if (
                            not isinstance(upscale_results, list)
                            or not upscale_results
                            or not upscale_results[0].get("url")
                        ):
                            die(f"RunningHub upscale succeeded but returned no image URL: {upscale_status_response}")
                        final_task_id = upscale_task_id
                        final_image_url = str(upscale_results[0]["url"])
                        download_image(final_image_url, upscale_out)
                        upscale_meta = {
                            "lowTaskId": task_id,
                            "lowOut": str(low_out),
                            "uploadFileName": uploaded_file_name,
                            "upscaleTaskId": upscale_task_id,
                            "upscaleAppPath": UPSCALE_AI_APP_PATH,
                            "upscaleBaseUrl": upscale_base_url,
                        }
                        break
                    if upscale_status == "FAILED":
                        die(
                            f"RunningHub upscale task failed: "
                            f"{upscale_status_response.get('errorMessage') or upscale_status_response.get('failedReason') or 'unknown'} "
                            f"| {upscale_status_response.get('errorCode', 'unknown')}"
                        )
                    print(
                        f"RunningHub upscale task {upscale_task_id} status: {upscale_status or 'UNKNOWN'}",
                        file=sys.stderr,
                    )
                    time.sleep(POLL_INTERVAL)

                image_size = read_image_size(out)
                actual_width = image_size[0] if image_size else None
                actual_height = image_size[1] if image_size else None
                min_side = min(image_size) if image_size else None
                expected_min_side = MIN_SIDE_BY_RESOLUTION.get(resolution)
                pixel_status = "unknown"
                if min_side is not None and expected_min_side is not None:
                    pixel_status = "ok" if min_side >= expected_min_side else "below_requested_resolution"
                meta = {
                    "taskId": final_task_id,
                    "textToImageTaskId": task_id,
                    "imageUrl": final_image_url,
                    "out": str(out),
                    "aspectRatio": aspect_ratio,
                    "resolution": resolution,
                    "submitPath": "input-image",
                    "quality": args.quality,
                    "upscaled": True,
                    "upscale": upscale_meta,
                    "actualWidth": actual_width,
                    "actualHeight": actual_height,
                    "pixelStatus": pixel_status,
                }
                print(json.dumps(meta, ensure_ascii=False, indent=2))
                return

        if time.time() - started > TIMEOUT_SECONDS:
            die(f"RunningHub task timed out after {TIMEOUT_SECONDS:.0f}s: {task_id}")
        status_response = curl_json(query_url, api_key=api_key, payload={"taskId": task_id})
        status = str(status_response.get("status") or "").upper()
        if status == "SUCCESS":
            results = status_response.get("results") or []
            if not isinstance(results, list) or not results or not results[0].get("url"):
                die(f"RunningHub task succeeded but returned no image URL: {status_response}")
            image_url = str(results[0]["url"])
            download_image(image_url, out)
            final_task_id = task_id
            final_image_url = image_url
            upscale_meta = None
            if args.upscale:
                upscale_out = out
                low_out = out.with_name(out.stem + "_low" + out.suffix)
                out.replace(low_out)
                upload_response = curl_upload(upload_url, api_key=upscale_api_key, path=low_out)
                if upload_response.get("code") not in (0, "0", None) and upload_response.get("message") != "success":
                    die(f"RunningHub upload failed: {upload_response}")
                upload_data = upload_response.get("data") or {}
                uploaded_file_name = str(upload_data.get("fileName") or upload_data.get("download_url") or "").strip()
                if not uploaded_file_name:
                    die(f"RunningHub upload returned no fileName/download_url: {upload_response}")
                upscale_payload: Dict[str, object] = {
                    "nodeInfoList": [
                        {
                            "nodeId": UPSCALE_IMAGE_NODE_ID,
                            "fieldName": "image",
                            "fieldValue": uploaded_file_name,
                            "description": "image",
                        },
                        {
                            "nodeId": UPSCALE_SIZE_NODE_ID,
                            "fieldName": UPSCALE_SIZE_FIELD_NAME,
                            "fieldValue": str(MIN_SIDE_BY_RESOLUTION.get(resolution, 2048)),
                            "description": "longest edge size",
                        }
                    ],
                    "instanceType": args.instance_type,
                    "usePersonalQueue": "true" if args.use_personal_queue else "false",
                }
                print(f"Calling RunningHub upscale app: {upscale_run_url}", file=sys.stderr)
                upscale_submit_response = curl_json(upscale_run_url, api_key=upscale_api_key, payload=upscale_payload)
                if upscale_submit_response.get("errorMessage"):
                    die(
                        f"RunningHub upscale submit failed: {upscale_submit_response.get('errorMessage')} "
                        f"| {upscale_submit_response.get('errorCode', 'unknown')}"
                    )
                upscale_task_id = str(upscale_submit_response.get("taskId") or "").strip()
                if not upscale_task_id:
                    die(f"RunningHub upscale response did not contain taskId: {upscale_submit_response}")
                upscale_started = time.time()
                while True:
                    if time.time() - upscale_started > TIMEOUT_SECONDS:
                        die(f"RunningHub upscale task timed out after {TIMEOUT_SECONDS:.0f}s: {upscale_task_id}")
                    upscale_status_response = curl_json(
                        upscale_query_url,
                        api_key=upscale_api_key,
                        payload={"taskId": upscale_task_id},
                    )
                    upscale_status = str(upscale_status_response.get("status") or "").upper()
                    if upscale_status == "SUCCESS":
                        upscale_results = upscale_status_response.get("results") or []
                        if (
                            not isinstance(upscale_results, list)
                            or not upscale_results
                            or not upscale_results[0].get("url")
                        ):
                            die(f"RunningHub upscale succeeded but returned no image URL: {upscale_status_response}")
                        final_task_id = upscale_task_id
                        final_image_url = str(upscale_results[0]["url"])
                        download_image(final_image_url, upscale_out)
                        upscale_meta = {
                            "lowTaskId": task_id,
                            "lowOut": str(low_out),
                            "uploadFileName": uploaded_file_name,
                            "upscaleTaskId": upscale_task_id,
                            "upscaleAppPath": UPSCALE_AI_APP_PATH,
                            "upscaleBaseUrl": upscale_base_url,
                        }
                        break
                    if upscale_status == "FAILED":
                        die(
                            f"RunningHub upscale task failed: "
                            f"{upscale_status_response.get('errorMessage') or upscale_status_response.get('failedReason') or 'unknown'} "
                            f"| {upscale_status_response.get('errorCode', 'unknown')}"
                        )
                    print(
                        f"RunningHub upscale task {upscale_task_id} status: {upscale_status or 'UNKNOWN'}",
                        file=sys.stderr,
                    )
                    time.sleep(POLL_INTERVAL)

            image_size = read_image_size(out)
            actual_width = image_size[0] if image_size else None
            actual_height = image_size[1] if image_size else None
            min_side = min(image_size) if image_size else None
            expected_min_side = MIN_SIDE_BY_RESOLUTION.get(resolution)
            pixel_status = "unknown"
            if min_side is not None and expected_min_side is not None:
                pixel_status = "ok" if min_side >= expected_min_side else "below_requested_resolution"
                if pixel_status != "ok":
                    print(
                        "Warning: requested "
                        f"{resolution} but downloaded image is {actual_width}x{actual_height}; "
                        f"minimum side is below {expected_min_side}px.",
                        file=sys.stderr,
                    )
            meta = {
                "taskId": final_task_id,
                "textToImageTaskId": task_id,
                "imageUrl": final_image_url,
                "out": str(out),
                "aspectRatio": aspect_ratio,
                "resolution": resolution,
                "submitPath": submit_path,
                "quality": args.quality,
                "upscaled": bool(args.upscale),
                "upscale": upscale_meta,
                "actualWidth": actual_width,
                "actualHeight": actual_height,
                "pixelStatus": pixel_status,
            }
            print(json.dumps(meta, ensure_ascii=False, indent=2))
            return
        if status == "FAILED":
            die(
                f"RunningHub task failed: "
                f"{status_response.get('errorMessage') or status_response.get('failedReason') or 'unknown'} "
                f"| {status_response.get('errorCode', 'unknown')}"
            )
        print(f"RunningHub task {task_id} status: {status or 'UNKNOWN'}", file=sys.stderr)
        time.sleep(POLL_INTERVAL)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Laohu Music cover image via RunningHub text-to-image.")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--out", required=True)
    parser.add_argument("--input-image")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO)
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    parser.add_argument("--quality", default=DEFAULT_QUALITY)
    parser.add_argument("--upscale", dest="upscale", action="store_true", default=DEFAULT_UPSCALE)
    parser.add_argument("--no-upscale", dest="upscale", action="store_false")
    parser.add_argument("--instance-type", default="default")
    parser.add_argument("--use-personal-queue", action="store_true")
    parser.add_argument("--upscale-api-key")
    parser.add_argument("--base-url")
    parser.add_argument("--upscale-base-url")
    parser.add_argument("--submit-path")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    generate(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
