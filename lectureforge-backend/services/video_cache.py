import os
from typing import Any, Dict, List, Optional

try:
    import psycopg
    from psycopg.types.json import Jsonb
except Exception:  # pragma: no cover - optional production dependency
    psycopg = None
    Jsonb = None


class VideoCache:
    def __init__(self):
        self.database_url = (
            os.getenv("LECTUREFORGE_DATABASE_URL")
            or os.getenv("SUPABASE_DATABASE_URL")
            or os.getenv("DATABASE_URL")
        )

    def is_enabled(self) -> bool:
        return bool(self.database_url and psycopg)

    def get_completed_study_kit(
        self,
        youtube_video_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if not self.is_enabled() or not youtube_video_id:
            return None

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select id, study_kit
                    from lecture_videos
                    where youtube_video_id = %s
                      and status = 'completed'
                      and study_kit is not null
                    limit 1
                    """,
                    (youtube_video_id,),
                )
                row = cur.fetchone()

                if not row:
                    return None

                video_id, study_kit = row

                if user_id:
                    self._link_user_video(cur, user_id, video_id)

                return study_kit

    def save_completed_study_kit(
        self,
        youtube_video_id: str,
        youtube_url: str,
        study_kit: Any,
        user_id: Optional[str] = None,
        transcript_provider: Optional[str] = None,
    ):
        if not self.is_enabled() or not youtube_video_id:
            return

        payload = self._to_plain_data(study_kit)
        title = payload.get("lecture_title") or "Untitled Lecture"
        duration_seconds = payload.get("duration_seconds")

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into lecture_videos (
                        youtube_video_id,
                        youtube_url,
                        title,
                        duration_seconds,
                        transcript_provider,
                        status,
                        study_kit,
                        updated_at
                    )
                    values (%s, %s, %s, %s, %s, 'completed', %s, now())
                    on conflict (youtube_video_id)
                    do update set
                        youtube_url = excluded.youtube_url,
                        title = excluded.title,
                        duration_seconds = excluded.duration_seconds,
                        transcript_provider = excluded.transcript_provider,
                        status = 'completed',
                        study_kit = excluded.study_kit,
                        updated_at = now()
                    returning id
                    """,
                    (
                        youtube_video_id,
                        youtube_url,
                        title,
                        duration_seconds,
                        transcript_provider,
                        Jsonb(payload),
                    ),
                )
                video_id = cur.fetchone()[0]

                if user_id:
                    self._link_user_video(cur, user_id, video_id)

            conn.commit()

    def save_embeddings(
        self,
        youtube_video_id: str,
        embeddings: List[Dict[str, Any]],
    ):
        if not self.is_enabled() or not youtube_video_id or not embeddings:
            return

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select id from lecture_videos where youtube_video_id = %s",
                    (youtube_video_id,),
                )
                row = cur.fetchone()

                if not row:
                    return

                video_id = row[0]

                for index, item in enumerate(embeddings):
                    chunk = self._to_plain_data(item.get("chunk"))
                    embedding = item.get("embedding")

                    if not chunk or not embedding:
                        continue

                    cur.execute(
                        """
                        insert into lecture_transcript_chunks (
                            video_id,
                            chunk_index,
                            start_seconds,
                            end_seconds,
                            text,
                            embedding
                        )
                        values (%s, %s, %s, %s, %s, %s::vector)
                        on conflict (video_id, chunk_index)
                        do update set
                            start_seconds = excluded.start_seconds,
                            end_seconds = excluded.end_seconds,
                            text = excluded.text,
                            embedding = excluded.embedding
                        """,
                        (
                            video_id,
                            index,
                            chunk.get("start"),
                            chunk.get("end"),
                            chunk.get("text"),
                            self._vector_literal(embedding),
                        ),
                    )

            conn.commit()

    def _connect(self):
        return psycopg.connect(self.database_url)

    def _link_user_video(self, cur, user_id: str, video_id: int):
        cur.execute(
            """
            insert into app_users (id)
            values (%s)
            on conflict (id) do nothing
            """,
            (user_id,),
        )
        cur.execute(
            """
            insert into user_lecture_videos (user_id, video_id, last_accessed_at)
            values (%s, %s, now())
            on conflict (user_id, video_id)
            do update set last_accessed_at = now()
            """,
            (user_id, video_id),
        )

    def _to_plain_data(self, value):
        if value is None:
            return None

        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        if hasattr(value, "dict"):
            return value.dict()

        return value

    def _vector_literal(self, embedding: List[float]) -> str:
        return "[" + ",".join(str(float(value)) for value in embedding) + "]"
