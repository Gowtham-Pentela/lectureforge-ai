import os
import re
import json
import time
import random
import base64
import tempfile
import subprocess
from typing import List, Optional, Iterable, Tuple
from urllib.parse import urlparse, parse_qs

import requests
from openai import OpenAI
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

from models.schemas import TranscriptChunk
from utils.transcript_utils import clean_text, merge_small_chunks

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_AUDIO_UPLOAD_LIMIT_BYTES = int(
    os.getenv("OPENAI_AUDIO_UPLOAD_LIMIT_BYTES", str(24 * 1024 * 1024))
)
OPENAI_TRANSCRIPTION_MAX_RETRIES = int(
    os.getenv("OPENAI_TRANSCRIPTION_MAX_RETRIES", "3")
)
OPENAI_TRANSCRIPTION_RETRY_BASE_SECONDS = float(
    os.getenv("OPENAI_TRANSCRIPTION_RETRY_BASE_SECONDS", "2")
)


class Agent1Ingestion:
    def get_transcript(self, youtube_url: str) -> List[TranscriptChunk]:
        errors = []
        provider = self._get_transcript_provider()

        for strategy in self._get_transcript_strategies(provider):
            try:
                chunks = self._run_transcript_strategy(strategy, youtube_url)

                if chunks and len(chunks) > 3:
                    if strategy == "supadata" and not self._chunks_look_english(chunks):
                        errors.append(
                            "Supadata returned non-English transcript; trying next fallback"
                        )
                        print("Supadata returned non-English transcript; trying next fallback")
                        continue

                    print(f"{strategy} transcript extraction succeeded with {len(chunks)} chunks")
                    return merge_small_chunks(chunks)

                errors.append(f"{strategy} returned too few chunks")
            except Exception as e:
                errors.append(f"{strategy} failed: {str(e)}")
                print(f"{strategy} failed: {str(e)}")

        raise RuntimeError(
            "Could not extract transcript from this YouTube URL. "
            "Errors: "
            + " | ".join(errors)
        )

    def _get_transcript_provider(self) -> str:
        provider = os.getenv("LECTUREFORGE_TRANSCRIPT_PROVIDER", "").strip().lower()

        if provider:
            return provider

        return "auto"

    def _get_transcript_strategies(self, provider: str) -> List[str]:
        configured_strategy = os.getenv("LECTUREFORGE_TRANSCRIPT_STRATEGY", "").strip()

        if configured_strategy:
            return [
                self._normalize_transcript_strategy(item)
                for item in configured_strategy.split(",")
                if self._normalize_transcript_strategy(item)
            ]

        provider_map = {
            "auto": self._default_transcript_strategy(),
            "captions": ["youtube_captions", "ytdlp_captions"],
            "captions_fast": ["youtube_captions"],
            "youtube": ["youtube_captions", "ytdlp_captions"],
            "supadata": ["supadata", "youtube_captions", "ytdlp_captions"],
            "openai": ["youtube_captions", "ytdlp_captions", "supadata", "openai_audio"],
            "whisper": ["youtube_captions", "ytdlp_captions", "supadata", "openai_audio"],
            "openai_only": ["openai_audio"],
            "whisper_only": ["openai_audio"],
        }

        return provider_map.get(provider, self._default_transcript_strategy())

    def _default_transcript_strategy(self) -> List[str]:
        strategies = ["youtube_captions"]

        if os.getenv("SUPADATA_API_KEY"):
            prefer_supadata = os.getenv(
                "LECTUREFORGE_PREFER_SUPADATA",
                "true" if self._is_hosted_runtime() else "false",
            ).strip().lower()

            if prefer_supadata in {"true", "1", "yes"}:
                strategies = ["supadata", "youtube_captions"]
            else:
                strategies.append("supadata")

        strategies.extend(["ytdlp_captions", "openai_audio"])
        return strategies

    def _normalize_transcript_strategy(self, strategy: str) -> str:
        normalized = strategy.strip().lower().replace("-", "_")

        aliases = {
            "youtube": "youtube_captions",
            "captions": "youtube_captions",
            "transcript_api": "youtube_captions",
            "youtube_transcript_api": "youtube_captions",
            "yt_dlp": "ytdlp_captions",
            "ytdlp": "ytdlp_captions",
            "whisper": "openai_audio",
            "openai": "openai_audio",
            "audio": "openai_audio",
        }

        normalized = aliases.get(normalized, normalized)

        allowed = {
            "supadata",
            "youtube_captions",
            "ytdlp_captions",
            "openai_audio",
        }

        return normalized if normalized in allowed else ""

    def _run_transcript_strategy(
        self,
        strategy: str,
        youtube_url: str,
    ) -> List[TranscriptChunk]:
        if strategy == "supadata":
            return self._get_supadata_transcript(youtube_url)

        if strategy == "youtube_captions":
            return self._get_transcript_api_captions(youtube_url)

        if strategy == "ytdlp_captions":
            return self._get_youtube_captions_with_ytdlp(youtube_url)

        if strategy == "openai_audio":
            if self._should_skip_hosted_audio_transcription():
                raise RuntimeError(
                    "Hosted audio transcription is disabled on serverless runtime"
                )

            return self._transcribe_with_whisper(youtube_url)

        raise RuntimeError(f"Unknown transcript strategy: {strategy}")

    def _should_skip_hosted_audio_transcription(self) -> bool:
        allow_audio = os.getenv(
            "LECTUREFORGE_ALLOW_HOSTED_AUDIO_TRANSCRIPTION",
            "",
        ).strip().lower()

        if allow_audio in {"true", "1", "yes"}:
            return False

        if allow_audio in {"false", "0", "no"}:
            return True

        return self._is_serverless_runtime()

    def _is_serverless_runtime(self) -> bool:
        serverless_markers = [
            "VERCEL",
            "AWS_LAMBDA_FUNCTION_NAME",
            "AWS_EXECUTION_ENV",
            "FUNCTION_TARGET",
            "FUNCTIONS_WORKER_RUNTIME",
            "K_SERVICE",
        ]

        return any(os.getenv(marker) for marker in serverless_markers)

    def _is_hosted_runtime(self) -> bool:
        hosted_markers = [
            "VERCEL",
            "RENDER",
            "RAILWAY_ENVIRONMENT",
            "AWS_LAMBDA_FUNCTION_NAME",
            "AWS_EXECUTION_ENV",
            "FUNCTION_TARGET",
            "FUNCTIONS_WORKER_RUNTIME",
            "K_SERVICE",
        ]

        environment_values = [
            os.getenv("LECTUREFORGE_ENV"),
            os.getenv("APP_ENV"),
            os.getenv("ENV"),
            os.getenv("ENVIRONMENT"),
            os.getenv("NODE_ENV"),
            os.getenv("VERCEL_ENV"),
        ]

        return any(os.getenv(marker) for marker in hosted_markers) or any(
            str(value).lower() in {"production", "prod"}
            for value in environment_values
            if value
        )

    def _get_supadata_transcript(self, youtube_url: str) -> List[TranscriptChunk]:
        api_key = os.getenv("SUPADATA_API_KEY")

        if not api_key:
            raise RuntimeError("SUPADATA_API_KEY is not configured")

        endpoint = "https://api.supadata.ai/v1/transcript"

        response = requests.get(
            endpoint,
            params={
                "url": youtube_url,
                "lang": "en",
                "mode": os.getenv("SUPADATA_TRANSCRIPT_MODE", "auto"),
                "chunkSize": int(os.getenv("SUPADATA_CHUNK_SIZE", "1000")),
            },
            headers={"x-api-key": api_key},
            timeout=60,
        )

        if response.status_code == 202:
            data = response.json()
            job_id = data.get("jobId") or data.get("job_id")

            if not job_id:
                raise RuntimeError(f"Supadata returned 202 without a jobId: {data}")

            data = self._poll_supadata_transcript_job(job_id, api_key)
            return self._supadata_data_to_chunks(data)

        if response.status_code != 200:
            raise RuntimeError(
                f"Supadata request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()
        return self._supadata_data_to_chunks(data)

    def _poll_supadata_transcript_job(self, job_id: str, api_key: str) -> dict:
        endpoint = f"https://api.supadata.ai/v1/transcript/{job_id}"
        timeout_seconds = int(os.getenv("SUPADATA_JOB_TIMEOUT_SECONDS", "120"))
        poll_interval = float(os.getenv("SUPADATA_JOB_POLL_INTERVAL_SECONDS", "1"))
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            response = requests.get(
                endpoint,
                headers={"x-api-key": api_key},
                timeout=30,
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Supadata job request failed with status {response.status_code}: {response.text}"
                )

            data = response.json()
            status = str(data.get("status", "")).lower()

            if status == "completed":
                result = data.get("result")
                if isinstance(result, dict):
                    return result

                return data

            if status == "failed":
                raise RuntimeError(f"Supadata transcript job failed: {data}")

            time.sleep(poll_interval)

        raise RuntimeError(
            f"Supadata transcript job timed out after {timeout_seconds} seconds"
        )

    def _supadata_data_to_chunks(self, data: dict) -> List[TranscriptChunk]:
        content = data.get("content")

        if not content:
            raise RuntimeError("Supadata returned no transcript content")

        if isinstance(content, str):
            content = [
                {
                    "text": paragraph.strip(),
                    "offset": index * 15000,
                    "duration": 15000,
                }
                for index, paragraph in enumerate(content.splitlines())
                if paragraph.strip()
            ]

        chunks = []

        for item in content:
            text = clean_text(item.get("text", ""))

            if not text:
                continue

            offset_ms = item.get("offset", 0)
            duration_ms = item.get("duration", 0)

            start = float(offset_ms) / 1000
            end = float(offset_ms + duration_ms) / 1000

            if end <= start:
                end = start + 2

            chunks.append(
                TranscriptChunk(
                    start=start,
                    end=end,
                    text=text,
                )
            )

        if not chunks:
            raise RuntimeError("Supadata transcript content had no usable text")

        return chunks

    def _extract_video_id(self, youtube_url: str) -> str:
        parsed = urlparse(youtube_url)

        if parsed.hostname in ["youtu.be", "www.youtu.be"]:
            return parsed.path.lstrip("/").split("?")[0]

        if parsed.hostname in ["youtube.com", "www.youtube.com", "m.youtube.com"]:
            query = parse_qs(parsed.query)

            if "v" in query:
                return query["v"][0]

            shorts_match = re.search(r"/shorts/([^/?]+)", parsed.path)
            if shorts_match:
                return shorts_match.group(1)

            embed_match = re.search(r"/embed/([^/?]+)", parsed.path)
            if embed_match:
                return embed_match.group(1)

        raise ValueError("Could not extract YouTube video ID from URL")

    def _get_transcript_api_captions(self, youtube_url: str) -> List[TranscriptChunk]:
        video_id = self._extract_video_id(youtube_url)

        api = YouTubeTranscriptApi(proxy_config=self._build_youtube_proxy_config())

        transcript_data = None

        language_attempts = [
            ["en"],
            ["en-US"],
            ["en-GB"],
        ]

        last_error = None

        for languages in language_attempts:
            try:
                transcript_data = api.fetch(video_id, languages=languages)
                break
            except Exception as e:
                last_error = e

        if transcript_data is None:
            transcript_data = self._fetch_translated_transcript_from_list(
                api=api,
                video_id=video_id,
                last_error=last_error,
            )

        chunks = self._transcript_data_to_chunks(transcript_data)

        if chunks and not self._chunks_look_english(chunks):
            translated_transcript_data = self._fetch_translated_transcript_from_list(
                api=api,
                video_id=video_id,
                last_error="Direct caption fetch returned non-English text",
            )
            translated_chunks = self._transcript_data_to_chunks(translated_transcript_data)

            if translated_chunks and self._chunks_look_english(translated_chunks):
                return translated_chunks

        return chunks

    def _fetch_translated_transcript_from_list(self, api, video_id: str, last_error):
        try:
            transcript_list = api.list(video_id)

            selected = None

            for transcript in transcript_list:
                if transcript.language_code.startswith("en"):
                    selected = transcript
                    break

            if selected is None:
                for transcript in transcript_list:
                    if transcript.is_translatable:
                        selected = transcript.translate("en")
                        break

            if selected is None:
                for transcript in transcript_list:
                    selected = transcript
                    break

            if selected is None:
                raise RuntimeError("No transcripts found for this video")

            if (
                not selected.language_code.startswith("en")
                and selected.is_translatable
            ):
                selected = selected.translate("en")

            return selected.fetch()

        except Exception as e:
            raise RuntimeError(
                f"Transcript API could not fetch English captions. "
                f"Last direct fetch error: {last_error}. "
                f"List/fetch error: {e}"
            )

    def _transcript_data_to_chunks(self, transcript_data) -> List[TranscriptChunk]:
        chunks = []

        for item in transcript_data:
            start = self._safe_get(item, "start", 0)
            duration = self._safe_get(item, "duration", 0)
            text = self._safe_get(item, "text", "")

            start = float(start)
            duration = float(duration)
            text = clean_text(str(text))

            if not text:
                continue

            chunks.append(
                TranscriptChunk(
                    start=start,
                    end=start + duration,
                    text=text,
                )
            )

        return chunks

    def _safe_get(self, item, key: str, default):
        if isinstance(item, dict):
            return item.get(key, default)

        return getattr(item, key, default)

    def _chunks_look_english(self, chunks: List[TranscriptChunk]) -> bool:
        sample = " ".join(chunk.text for chunk in chunks[:12])

        if not sample.strip():
            return True

        ascii_letters = sum(1 for char in sample if char.isascii() and char.isalpha())
        non_ascii_letters = sum(1 for char in sample if not char.isascii() and char.isalpha())

        if non_ascii_letters > ascii_letters * 0.2:
            return False

        common_words = {
            "the",
            "and",
            "to",
            "of",
            "in",
            "that",
            "is",
            "for",
            "with",
            "this",
            "you",
            "we",
            "are",
        }
        words = [
            word.strip(".,!?;:()[]{}\"'").lower()
            for word in sample.split()
        ]

        return sum(1 for word in words if word in common_words) >= 3 or non_ascii_letters == 0

    def _run_command(self, command: List[str]):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=int(os.getenv("YTDLP_COMMAND_TIMEOUT_SECONDS", "15")),
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed: {self._redact_command_for_logs(command)}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        return result

    def _redact_command_for_logs(self, command: List[str]) -> str:
        redacted = []
        sensitive_next = False

        for part in command:
            if sensitive_next:
                redacted.append("[redacted]")
                sensitive_next = False
                continue

            redacted.append(part)

            if part in {"--proxy", "--cookies"}:
                sensitive_next = True

        return " ".join(redacted)

    def _get_youtube_captions_with_ytdlp(self, youtube_url: str) -> List[TranscriptChunk]:
        with tempfile.TemporaryDirectory() as temp_dir:
            cookie_file = self._prepare_youtube_cookie_file(temp_dir)

            return self._get_youtube_captions_with_ytdlp_in_temp_dir(
                youtube_url=youtube_url,
                temp_dir=temp_dir,
                cookie_file=cookie_file,
            )

    def _get_youtube_captions_with_ytdlp_in_temp_dir(
        self,
        youtube_url: str,
        temp_dir: str,
        cookie_file: Optional[str],
    ) -> List[TranscriptChunk]:
        try:
            chunks = self._get_youtube_captions_with_ytdlp_api(
                youtube_url=youtube_url,
                cookie_file=cookie_file,
            )

            if chunks:
                return chunks
        except Exception as e:
            print(f"yt-dlp Python caption extraction failed: {str(e)}")

        if self._is_serverless_runtime():
            raise RuntimeError(
                "yt-dlp caption command fallback is unavailable on serverless runtime"
            )

        output_template = os.path.join(temp_dir, "captions.%(ext)s")

        command = [
            "yt-dlp",
            "--write-auto-subs",
            "--write-subs",
            "--sub-lang",
            "en.*,en,all",
            "--sub-format",
            "json3",
            "--skip-download",
            "-o",
            output_template,
        ]

        self._append_ytdlp_network_options(command, cookie_file)
        command.append(youtube_url)

        self._run_command(command)

        caption_files = [
            os.path.join(temp_dir, file)
            for file in os.listdir(temp_dir)
            if file.endswith(".json3")
        ]

        if not caption_files:
            raise ValueError("No captions found through yt-dlp")

        caption_file = self._select_best_caption_file(caption_files)

        with open(caption_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = self._parse_json3_captions(data)

        if not chunks:
            raise ValueError("Caption file was found, but no usable text was parsed")

        return chunks

    def _get_youtube_captions_with_ytdlp_api(
        self,
        youtube_url: str,
        cookie_file: Optional[str],
    ) -> List[TranscriptChunk]:
        ydl_options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["default", "ios", "android"],
                },
            },
        }
        proxy_url = self._get_youtube_proxy_url()

        if proxy_url:
            ydl_options["proxy"] = proxy_url

        if cookie_file:
            ydl_options["cookiefile"] = cookie_file

        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

        for language, track in self._iter_caption_tracks(info):
            try:
                chunks = self._download_caption_track(track)

                if chunks:
                    print(f"yt-dlp found {language} captions through metadata")
                    return chunks
            except Exception as e:
                print(f"Could not parse yt-dlp {language} caption track: {str(e)}")

        raise ValueError("No usable captions found through yt-dlp metadata")

    def _append_ytdlp_network_options(
        self,
        command: List[str],
        cookie_file: Optional[str],
    ):
        proxy_url = self._get_youtube_proxy_url()

        if proxy_url:
            command.extend(["--proxy", proxy_url])

        if cookie_file:
            command.extend(["--cookies", cookie_file])

    def _build_youtube_proxy_config(self):
        proxy_url = self._get_youtube_proxy_url()

        if not proxy_url:
            return None

        return GenericProxyConfig(
            http_url=proxy_url,
            https_url=proxy_url,
        )

    def _get_youtube_proxy_url(self) -> str:
        return (
            os.getenv("LECTUREFORGE_YOUTUBE_PROXY_URL")
            or os.getenv("YOUTUBE_PROXY_URL")
            or ""
        ).strip()

    def _prepare_youtube_cookie_file(self, temp_dir: str) -> Optional[str]:
        existing_path = os.getenv("LECTUREFORGE_YOUTUBE_COOKIES_PATH", "").strip()

        if existing_path:
            if not os.path.exists(existing_path):
                raise RuntimeError("LECTUREFORGE_YOUTUBE_COOKIES_PATH does not exist")

            return existing_path

        cookie_text = self._get_youtube_cookie_text()

        if not cookie_text:
            return None

        cookie_file = os.path.join(temp_dir, "youtube-cookies.txt")

        with open(cookie_file, "w", encoding="utf-8") as f:
            f.write(cookie_text)
            if not cookie_text.endswith("\n"):
                f.write("\n")

        return cookie_file

    def _get_youtube_cookie_text(self) -> str:
        encoded_cookies = os.getenv("LECTUREFORGE_YOUTUBE_COOKIES_B64", "").strip()

        if encoded_cookies:
            try:
                cookie_text = base64.b64decode(encoded_cookies).decode("utf-8")
            except Exception as e:
                raise RuntimeError(
                    "LECTUREFORGE_YOUTUBE_COOKIES_B64 is not valid base64 text"
                ) from e

            return self._normalize_cookie_text(cookie_text)

        cookie_text = os.getenv("LECTUREFORGE_YOUTUBE_COOKIES_TEXT", "").strip()

        if cookie_text:
            return self._normalize_cookie_text(cookie_text)

        return ""

    def _normalize_cookie_text(self, cookie_text: str) -> str:
        cookie_text = cookie_text.replace("\\n", "\n").strip()

        if not cookie_text:
            return ""

        valid_headers = (
            "# Netscape HTTP Cookie File",
            "# HTTP Cookie File",
        )

        if cookie_text.startswith(valid_headers):
            return cookie_text

        return "# Netscape HTTP Cookie File\n" + cookie_text

    def _iter_caption_tracks(self, info: dict) -> Iterable[Tuple[str, dict]]:
        subtitles = info.get("subtitles") or {}
        automatic_captions = info.get("automatic_captions") or {}
        preferred_languages = self._preferred_caption_languages(
            list(subtitles.keys()) + list(automatic_captions.keys())
        )

        for language in preferred_languages:
            for source in (subtitles, automatic_captions):
                tracks = source.get(language) or []
                track = self._select_best_caption_track(tracks)

                if track:
                    yield language, track

    def _preferred_caption_languages(self, languages: List[str]) -> List[str]:
        unique_languages = []

        for language in languages:
            if language and language not in unique_languages:
                unique_languages.append(language)

        preferred = []

        for target in ("en", "en-US", "en-GB", "en-orig"):
            for language in unique_languages:
                if language == target and language not in preferred:
                    preferred.append(language)

        for language in unique_languages:
            if language.startswith("en") and language not in preferred:
                preferred.append(language)

        for language in unique_languages:
            if language not in preferred:
                preferred.append(language)

        return preferred

    def _select_best_caption_track(self, tracks: List[dict]) -> Optional[dict]:
        if not tracks:
            return None

        preferred_extensions = ["json3", "vtt", "srv3", "ttml"]

        for extension in preferred_extensions:
            for track in tracks:
                if track.get("ext") == extension and track.get("url"):
                    return track

        for track in tracks:
            if track.get("url"):
                return track

        return None

    def _download_caption_track(self, track: dict) -> List[TranscriptChunk]:
        response = requests.get(track["url"], timeout=45)
        response.raise_for_status()

        extension = (track.get("ext") or "").lower()
        content_type = response.headers.get("content-type", "").lower()

        if extension == "json3" or "json" in content_type:
            return self._parse_json3_captions(response.json())

        return self._parse_vtt_captions(response.text)

    def _select_best_caption_file(self, caption_files: List[str]) -> str:
        preferred_markers = [
            ".en.",
            ".en-US.",
            ".en-us.",
            ".en-orig.",
        ]

        for marker in preferred_markers:
            for file_path in caption_files:
                if marker in file_path:
                    return file_path

        return caption_files[0]

    def _parse_json3_captions(self, data: dict) -> List[TranscriptChunk]:
        chunks = []

        for event in data.get("events", []):
            if "segs" not in event:
                continue

            start_ms = event.get("tStartMs", 0)
            duration_ms = event.get("dDurationMs", 0)

            text = "".join(seg.get("utf8", "") for seg in event.get("segs", []))
            text = clean_text(text)

            if not text:
                continue

            start = start_ms / 1000
            end = (start_ms + duration_ms) / 1000

            if end <= start:
                end = start + 2

            chunks.append(
                TranscriptChunk(
                    start=start,
                    end=end,
                    text=text,
                )
            )

        return chunks

    def _parse_vtt_captions(self, text: str) -> List[TranscriptChunk]:
        chunks = []
        current_start = None
        current_end = None
        current_text = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line or line.upper() == "WEBVTT" or line.startswith(("Kind:", "Language:")):
                if current_start is not None and current_text:
                    self._append_vtt_chunk(chunks, current_start, current_end, current_text)
                current_start = None
                current_end = None
                current_text = []
                continue

            if "-->" in line:
                if current_start is not None and current_text:
                    self._append_vtt_chunk(chunks, current_start, current_end, current_text)

                start_text, end_text = line.split("-->", 1)
                current_start = self._parse_vtt_timestamp(start_text.strip())
                current_end = self._parse_vtt_timestamp(end_text.strip().split()[0])
                current_text = []
                continue

            if current_start is not None and not line.isdigit():
                cleaned_line = re.sub(r"<[^>]+>", "", line)
                current_text.append(cleaned_line)

        if current_start is not None and current_text:
            self._append_vtt_chunk(chunks, current_start, current_end, current_text)

        return chunks

    def _append_vtt_chunk(
        self,
        chunks: List[TranscriptChunk],
        start: float,
        end: float,
        text_lines: List[str],
    ):
        text = clean_text(" ".join(text_lines))

        if not text:
            return

        if end <= start:
            end = start + 2

        if chunks and chunks[-1].text == text:
            chunks[-1].end = max(chunks[-1].end, end)
            return

        chunks.append(
            TranscriptChunk(
                start=start,
                end=end,
                text=text,
            )
        )

    def _parse_vtt_timestamp(self, value: str) -> float:
        timestamp = value.replace(",", ".")
        parts = timestamp.split(":")

        try:
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

            if len(parts) == 2:
                minutes, seconds = parts
                return int(minutes) * 60 + float(seconds)

            return float(parts[0])
        except Exception:
            return 0.0

    def _transcribe_with_whisper(self, youtube_url: str) -> List[TranscriptChunk]:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._download_audio_for_openai(youtube_url, temp_dir)

            audio_path = self._find_audio_file(temp_dir)

            if not audio_path:
                raise FileNotFoundError("yt-dlp finished but no audio file was found")

            audio_size = os.path.getsize(audio_path)

            if audio_size > OPENAI_AUDIO_UPLOAD_LIMIT_BYTES:
                raise ValueError(
                    "Downloaded audio is too large for OpenAI transcription: "
                    f"{audio_size} bytes. Limit is {OPENAI_AUDIO_UPLOAD_LIMIT_BYTES} bytes."
                )

            transcript = self._create_openai_transcription_with_retry(audio_path)

            segments = getattr(transcript, "segments", None)

            if not segments:
                raise ValueError("Whisper returned no timestamped segments")

            chunks = []

            for segment in segments:
                start = self._get_segment_value(segment, "start", 0)
                end = self._get_segment_value(segment, "end", start + 2)
                text = self._get_segment_value(segment, "text", "")

                text = clean_text(text)

                if not text:
                    continue

                chunks.append(
                    TranscriptChunk(
                        start=float(start),
                        end=float(end),
                        text=text,
                    )
                )

            return chunks

    def _create_openai_transcription_with_retry(self, audio_path: str):
        last_error = None

        for attempt in range(1, OPENAI_TRANSCRIPTION_MAX_RETRIES + 1):
            try:
                with open(audio_path, "rb") as audio_file:
                    return client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                    )
            except Exception as e:
                last_error = e

                if not self._is_openai_rate_limit_error(e):
                    raise

                if attempt >= OPENAI_TRANSCRIPTION_MAX_RETRIES:
                    break

                delay = (
                    OPENAI_TRANSCRIPTION_RETRY_BASE_SECONDS
                    * (2 ** (attempt - 1))
                    + random.uniform(0, 0.75)
                )
                print(
                    "OpenAI audio transcription rate-limited; "
                    f"retrying attempt {attempt + 1}/{OPENAI_TRANSCRIPTION_MAX_RETRIES} "
                    f"in {delay:.1f}s"
                )
                time.sleep(delay)

        raise last_error

    def _is_openai_rate_limit_error(self, error: Exception) -> bool:
        error_text = str(error).lower()
        status_code = getattr(error, "status_code", None)
        code = getattr(error, "code", None)

        return (
            status_code == 429
            or code == "rate_limit_exceeded"
            or "rate_limit" in error_text
            or "rate limit" in error_text
            or "429" in error_text
            or "too many requests" in error_text
        )

    def _download_audio_for_openai(self, youtube_url: str, temp_dir: str):
        output_template = os.path.join(temp_dir, "audio.%(ext)s")

        ydl_options = {
            "format": (
                "bestaudio[filesize<24000000][ext=m4a]/"
                "bestaudio[filesize_approx<24000000][ext=m4a]/"
                "bestaudio[filesize<24000000][ext=webm]/"
                "bestaudio[filesize_approx<24000000][ext=webm]/"
                "worstaudio[ext=m4a]/worstaudio[ext=webm]/worstaudio"
            ),
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["default", "ios", "android"],
                },
            },
        }

        with YoutubeDL(ydl_options) as ydl:
            ydl.download([youtube_url])

    def _find_audio_file(self, temp_dir: str) -> Optional[str]:
        supported_extensions = [
            ".mp3",
            ".mp4",
            ".mpeg",
            ".mpga",
            ".m4a",
            ".wav",
            ".webm",
        ]

        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)

            if not os.path.isfile(file_path):
                continue

            for extension in supported_extensions:
                if file.endswith(extension):
                    return file_path

        return None

    def _get_segment_value(self, segment, key: str, default):
        if isinstance(segment, dict):
            return segment.get(key, default)

        return getattr(segment, key, default)
    
    def get_video_title(self, youtube_url: str) -> str:
        try:
            command = [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",
                youtube_url,
            ]

            result = self._run_command(command)

            data = json.loads(result.stdout)

            title = data.get("title")

            if title:
                return title.strip()

            return "Untitled Lecture"

        except Exception as e:
            print(f"Could not extract YouTube title: {str(e)}")
            return "Untitled Lecture"
