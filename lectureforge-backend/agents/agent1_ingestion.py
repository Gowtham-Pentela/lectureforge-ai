import os
import re
import json
import time
import tempfile
import subprocess
from typing import List, Optional
from urllib.parse import urlparse, parse_qs

import requests
from openai import OpenAI
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi

from models.schemas import TranscriptChunk
from utils.transcript_utils import clean_text, merge_small_chunks

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent1Ingestion:
    def get_transcript(self, youtube_url: str) -> List[TranscriptChunk]:
        errors = []
        provider = self._get_transcript_provider()
        use_supadata = provider == "supadata"
        use_captions = provider not in {"openai_only", "whisper_only"}
        use_openai = provider not in {"supadata", "captions", "youtube"}
        use_ytdlp_captions = provider != "captions_fast"

        if use_supadata:
            try:
                chunks = self._get_supadata_transcript(youtube_url)
                if chunks and len(chunks) > 3:
                    if self._chunks_look_english(chunks):
                        print(f"Supadata transcript extraction succeeded with {len(chunks)} chunks")
                        return merge_small_chunks(chunks)

                    errors.append("Supadata returned non-English transcript; trying translatable captions")
                    print("Supadata returned non-English transcript; trying translatable captions")

                errors.append("Supadata returned too few chunks")
            except Exception as e:
                errors.append(f"Supadata failed: {str(e)}")
                print(f"Supadata failed: {str(e)}")

        if use_captions:
            try:
                chunks = self._get_transcript_api_captions(youtube_url)
                if chunks and len(chunks) > 3:
                    print(f"youtube-transcript-api succeeded with {len(chunks)} chunks")
                    return merge_small_chunks(chunks)

                errors.append("youtube-transcript-api returned too few chunks")
            except Exception as e:
                errors.append(f"youtube-transcript-api failed: {str(e)}")
                print(f"youtube-transcript-api failed: {str(e)}")

            if use_ytdlp_captions and not self._is_serverless_runtime():
                try:
                    chunks = self._get_youtube_captions_with_ytdlp(youtube_url)
                    if chunks and len(chunks) > 3:
                        print(f"yt-dlp caption extraction succeeded with {len(chunks)} chunks")
                        return merge_small_chunks(chunks)

                    errors.append("yt-dlp captions returned too few chunks")
                except Exception as e:
                    errors.append(f"yt-dlp captions failed: {str(e)}")
                    print(f"yt-dlp captions failed: {str(e)}")

        if use_openai:
            if self._should_skip_hosted_audio_transcription():
                errors.append(
                    "Hosted audio transcription is disabled on serverless runtime"
                )
            else:
                try:
                    chunks = self._transcribe_with_whisper(youtube_url)
                    if chunks and len(chunks) > 0:
                        print(
                            f"OpenAI Whisper transcription succeeded with {len(chunks)} chunks"
                        )
                        return merge_small_chunks(chunks)

                    errors.append("OpenAI Whisper returned no chunks")
                except Exception as e:
                    errors.append(f"OpenAI Whisper transcription failed: {str(e)}")
                    print(f"OpenAI Whisper transcription failed: {str(e)}")

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

    def _should_skip_hosted_audio_transcription(self) -> bool:
        allow_audio = os.getenv(
            "LECTUREFORGE_ALLOW_HOSTED_AUDIO_TRANSCRIPTION",
            "",
        ).strip().lower()

        if allow_audio in {"true", "1", "yes"}:
            return False

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

    def _should_try_openai_transcription_first(self, provider: str) -> bool:
        if provider in {"openai", "whisper"}:
            return True

        if provider in {"supadata", "captions", "youtube"}:
            return False

        if not os.getenv("OPENAI_API_KEY"):
            return False

        production_markers = [
            "RENDER",
            "VERCEL",
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
            os.getenv("RAILWAY_ENVIRONMENT"),
            os.getenv("RENDER_EXTERNAL_HOSTNAME"),
        ]

        return any(os.getenv(marker) for marker in production_markers) or any(
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

        api = YouTubeTranscriptApi()

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
                f"Command failed: {' '.join(command)}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        return result

    def _get_youtube_captions_with_ytdlp(self, youtube_url: str) -> List[TranscriptChunk]:
        with tempfile.TemporaryDirectory() as temp_dir:
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
                youtube_url,
            ]

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

    def _transcribe_with_whisper(self, youtube_url: str) -> List[TranscriptChunk]:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._download_audio_for_openai(youtube_url, temp_dir)

            audio_path = self._find_audio_file(temp_dir)

            if not audio_path:
                raise FileNotFoundError("yt-dlp finished but no audio file was found")

            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )

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

    def _download_audio_for_openai(self, youtube_url: str, temp_dir: str):
        output_template = os.path.join(temp_dir, "audio.%(ext)s")

        ydl_options = {
            "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
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
