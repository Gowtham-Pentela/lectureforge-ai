create extension if not exists vector;

create table if not exists app_users (
    id text primary key,
    created_at timestamptz not null default now()
);

create table if not exists lecture_videos (
    id bigserial primary key,
    youtube_video_id text not null unique,
    youtube_url text not null,
    title text,
    duration_seconds double precision,
    transcript_provider text,
    status text not null default 'processing',
    study_kit jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists user_lecture_videos (
    user_id text not null references app_users(id) on delete cascade,
    video_id bigint not null references lecture_videos(id) on delete cascade,
    created_at timestamptz not null default now(),
    last_accessed_at timestamptz not null default now(),
    primary key (user_id, video_id)
);

create table if not exists lecture_transcript_chunks (
    id bigserial primary key,
    video_id bigint not null references lecture_videos(id) on delete cascade,
    chunk_index integer not null,
    start_seconds double precision,
    end_seconds double precision,
    text text not null,
    embedding vector(1536),
    created_at timestamptz not null default now(),
    unique (video_id, chunk_index)
);

create index if not exists lecture_videos_youtube_video_id_idx
    on lecture_videos (youtube_video_id);

create index if not exists user_lecture_videos_user_id_idx
    on user_lecture_videos (user_id);

create index if not exists lecture_chunks_video_id_idx
    on lecture_transcript_chunks (video_id);

create index if not exists lecture_chunks_embedding_hnsw_idx
    on lecture_transcript_chunks
    using hnsw (embedding vector_cosine_ops)
    where embedding is not null;
