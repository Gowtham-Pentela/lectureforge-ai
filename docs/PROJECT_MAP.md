# Project Map

This file was generated automatically by `project_mapper.py`.
Use it to help AI coding tools understand the codebase before making changes.

## Project Summary

- Root: `/Users/gowtham/Desktop/lectureforge-ai`
- Files scanned: `42`
- Dependency edges found: `57`

## Generated Visuals

- Mermaid graph: `PROJECT_DEPENDENCIES.mmd`
- Graphviz DOT graph: `PROJECT_GRAPH.dot`
- Graph image: `PROJECT_GRAPH.png`
- SVG graph: `PROJECT_GRAPH.svg`

## Suggested AI Instruction

> Read this `PROJECT_MAP.md` first. Then inspect the relevant files before editing code. Preserve working behavior and avoid changing unrelated files.

## Entry Points

- `lectureforge-backend/main.py`
- `lectureforge-frontend/src/App.jsx`
- `lectureforge-frontend/src/main.jsx`

## High-Level Dependency Graph

```mermaid
graph TD
    N1["lectureforge-backend/agents/agent1_ingestion.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N1["lectureforge-backend/agents/agent1_ingestion.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N1["lectureforge-backend/agents/agent1_ingestion.py"] --> N4["lectureforge-backend/utils/__init__.py"]
    N1["lectureforge-backend/agents/agent1_ingestion.py"] --> N5["lectureforge-backend/utils/transcript_utils.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N7["lectureforge-backend/services/__init__.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N8["lectureforge-backend/services/openai_service.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N4["lectureforge-backend/utils/__init__.py"]
    N6["lectureforge-backend/agents/agent2_analysis.py"] --> N5["lectureforge-backend/utils/transcript_utils.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N7["lectureforge-backend/services/__init__.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N8["lectureforge-backend/services/openai_service.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N4["lectureforge-backend/utils/__init__.py"]
    N9["lectureforge-backend/agents/agent3_study.py"] --> N5["lectureforge-backend/utils/transcript_utils.py"]
    N10["lectureforge-backend/agents/agent4_faculty_audit.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N10["lectureforge-backend/agents/agent4_faculty_audit.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N10["lectureforge-backend/agents/agent4_faculty_audit.py"] --> N7["lectureforge-backend/services/__init__.py"]
    N10["lectureforge-backend/agents/agent4_faculty_audit.py"] --> N8["lectureforge-backend/services/openai_service.py"]
    N11["lectureforge-backend/main.py"] --> N12["lectureforge-backend/agents/__init__.py"]
    N11["lectureforge-backend/main.py"] --> N1["lectureforge-backend/agents/agent1_ingestion.py"]
    N11["lectureforge-backend/main.py"] --> N6["lectureforge-backend/agents/agent2_analysis.py"]
    N11["lectureforge-backend/main.py"] --> N9["lectureforge-backend/agents/agent3_study.py"]
    N11["lectureforge-backend/main.py"] --> N10["lectureforge-backend/agents/agent4_faculty_audit.py"]
    N11["lectureforge-backend/main.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N11["lectureforge-backend/main.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N11["lectureforge-backend/main.py"] --> N7["lectureforge-backend/services/__init__.py"]
    N11["lectureforge-backend/main.py"] --> N13["lectureforge-backend/services/job_store.py"]
    N11["lectureforge-backend/main.py"] --> N8["lectureforge-backend/services/openai_service.py"]
    N11["lectureforge-backend/main.py"] --> N4["lectureforge-backend/utils/__init__.py"]
    N11["lectureforge-backend/main.py"] --> N14["lectureforge-backend/utils/faculty_audit_validator.py"]
    N11["lectureforge-backend/main.py"] --> N15["lectureforge-backend/utils/study_kit_validator.py"]
    N11["lectureforge-backend/main.py"] --> N5["lectureforge-backend/utils/transcript_utils.py"]
    N14["lectureforge-backend/utils/faculty_audit_validator.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N14["lectureforge-backend/utils/faculty_audit_validator.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N15["lectureforge-backend/utils/study_kit_validator.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N15["lectureforge-backend/utils/study_kit_validator.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N15["lectureforge-backend/utils/study_kit_validator.py"] --> N4["lectureforge-backend/utils/__init__.py"]
    N15["lectureforge-backend/utils/study_kit_validator.py"] --> N5["lectureforge-backend/utils/transcript_utils.py"]
    N5["lectureforge-backend/utils/transcript_utils.py"] --> N2["lectureforge-backend/models/__init__.py"]
    N5["lectureforge-backend/utils/transcript_utils.py"] --> N3["lectureforge-backend/models/schemas.py"]
    N16["lectureforge-frontend/src/App.jsx"] --> N17["lectureforge-frontend/src/components/FacultyAuditDashboard.jsx"]
    N16["lectureforge-frontend/src/App.jsx"] --> N18["lectureforge-frontend/src/components/Header.jsx"]
    N16["lectureforge-frontend/src/App.jsx"] --> N19["lectureforge-frontend/src/components/ProgressCard.jsx"]
    N16["lectureforge-frontend/src/App.jsx"] --> N20["lectureforge-frontend/src/components/StudyDashboard.jsx"]
    N16["lectureforge-frontend/src/App.jsx"] --> N21["lectureforge-frontend/src/components/VideoForm.jsx"]
    N22["lectureforge-frontend/src/components/SearchTab.jsx"] --> N23["lectureforge-frontend/src/lib/api.js"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N24["lectureforge-frontend/src/components/ConceptMapTab.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N25["lectureforge-frontend/src/components/FlashcardsTab.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N26["lectureforge-frontend/src/components/OutlineTab.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N22["lectureforge-frontend/src/components/SearchTab.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N27["lectureforge-frontend/src/components/SummariesTab.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N28["lectureforge-frontend/src/components/Tabs.jsx"]
    N20["lectureforge-frontend/src/components/StudyDashboard.jsx"] --> N29["lectureforge-frontend/src/components/TranscriptTab.jsx"]
    N30["lectureforge-frontend/src/main.jsx"] --> N16["lectureforge-frontend/src/App.jsx"]
    N30["lectureforge-frontend/src/main.jsx"] --> N31["lectureforge-frontend/src/styles/index.css"]
```

## File Summaries

### `README.md`

- Role: Project documentation
- Type: `.md`
- Size: `11280` bytes
- Lines: `560`
- Local dependencies: none detected
- Notes:
  - May handle API keys or secrets. Verify secrets are loaded from environment variables.
  - Reads, writes, or processes JSON-like data.

### `VERSION_NOTES.md`

- Role: Project documentation
- Type: `.md`
- Size: `587` bytes
- Lines: `31`
- Local dependencies: none detected

### `lectureforge-backend/agents/__init__.py`

- Role: Supporting project file
- Type: `.py`
- Size: `0` bytes
- Lines: `0`
- Local dependencies: none detected

### `lectureforge-backend/agents/agent1_ingestion.py`

- Role: AI model integration module
- Type: `.py`
- Size: `13467` bytes
- Lines: `445`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/utils/__init__.py`
  - `lectureforge-backend/utils/transcript_utils.py`
- Functions: _extract_video_id, _find_audio_file, _get_segment_value, _get_supadata_transcript, _get_transcript_api_captions, _get_youtube_captions_with_ytdlp, _parse_json3_captions, _run_command, _safe_get, _select_best_caption_file, _transcribe_with_whisper, get_transcript plus 1 more
- Classes: Agent1Ingestion
- Environment variables: OPENAI_API_KEY, SUPADATA_API_KEY
- Notes:
  - Imports 13 external or internal modules.
  - Defines 13 function(s).
  - Defines 1 class(es).
  - Uses environment variable(s): OPENAI_API_KEY, SUPADATA_API_KEY.
  - May handle API keys or secrets. Verify secrets are loaded from environment variables.
  - Includes exception handling.

### `lectureforge-backend/agents/agent2_analysis.py`

- Role: Streamlit user interface module
- Type: `.py`
- Size: `1850` bytes
- Lines: `70`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/services/__init__.py`
  - `lectureforge-backend/services/openai_service.py`
  - `lectureforge-backend/utils/__init__.py`
  - `lectureforge-backend/utils/transcript_utils.py`
- Functions: analyze
- Classes: Agent2Analysis
- Notes:
  - Imports 4 external or internal modules.
  - Defines 1 function(s).
  - Defines 1 class(es).
  - Reads, writes, or processes JSON-like data.

### `lectureforge-backend/agents/agent3_study.py`

- Role: Prompt or AI instruction logic
- Type: `.py`
- Size: `5841` bytes
- Lines: `230`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/services/__init__.py`
  - `lectureforge-backend/services/openai_service.py`
  - `lectureforge-backend/utils/__init__.py`
  - `lectureforge-backend/utils/transcript_utils.py`
- Functions: _generate_bilingual_output, _generate_concept_map, _generate_flashcards, _generate_summaries, create_search_embeddings, generate_study_kit
- Classes: Agent3Study
- Notes:
  - Imports 4 external or internal modules.
  - Defines 6 function(s).
  - Defines 1 class(es).
  - Reads, writes, or processes JSON-like data.

### `lectureforge-backend/agents/agent4_faculty_audit.py`

- Role: Streamlit user interface module
- Type: `.py`
- Size: `19974` bytes
- Lines: `581`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/services/__init__.py`
  - `lectureforge-backend/services/openai_service.py`
- Functions: _as_list, _as_string, _default_dimension, _normalize_dimension, _normalize_highest_impact_fix, _normalize_priority_fixes, _normalize_rewrites, _safe_chunk_value, _seconds_to_timestamp, build_empty_faculty_audit_report, format_transcript_for_audit, generate_faculty_audit plus 2 more
- Notes:
  - Imports 4 external or internal modules.
  - Defines 14 function(s).
  - Includes exception handling.
  - Reads, writes, or processes JSON-like data.

### `lectureforge-backend/main.py`

- Role: Application entry point
- Type: `.py`
- Size: `34395` bytes
- Lines: `1169`
- Local dependencies:
  - `lectureforge-backend/agents/__init__.py`
  - `lectureforge-backend/agents/agent1_ingestion.py`
  - `lectureforge-backend/agents/agent2_analysis.py`
  - `lectureforge-backend/agents/agent3_study.py`
  - `lectureforge-backend/agents/agent4_faculty_audit.py`
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/services/__init__.py`
  - `lectureforge-backend/services/job_store.py`
  - `lectureforge-backend/services/openai_service.py`
  - `lectureforge-backend/utils/__init__.py`
  - `lectureforge-backend/utils/faculty_audit_validator.py`
  - `lectureforge-backend/utils/study_kit_validator.py`
  - `lectureforge-backend/utils/transcript_utils.py`
- Functions: build_public_error_message, build_translation_section_key, cosine_similarity, debug_env, debug_openai, extract_json_from_text, get_faculty_audit, get_job_status, get_original_section_data, get_study_kit, get_study_kit_dict, process_faculty_audit plus 15 more
- Environment variables: OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_MODEL, SUPADATA_API_KEY
- Notes:
  - Imports 18 external or internal modules.
  - Defines 27 function(s).
  - Uses environment variable(s): OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_MODEL, SUPADATA_API_KEY.
  - May handle API keys or secrets. Verify secrets are loaded from environment variables.
  - Includes exception handling.
  - Reads, writes, or processes JSON-like data.

### `lectureforge-backend/models/__init__.py`

- Role: Supporting project file
- Type: `.py`
- Size: `0` bytes
- Lines: `0`
- Local dependencies: none detected

### `lectureforge-backend/models/schemas.py`

- Role: Class-based business logic or data model
- Type: `.py`
- Size: `3656` bytes
- Lines: `177`
- Local dependencies: none detected
- Classes: AuditDimension, ConceptMap, ConceptMapEdge, ConceptMapNode, FacultyAuditReport, FacultyAuditRequest, Flashcard, HighestImpactFix, KeyConcept, LectureAnalysis, OutlineItem, PriorityFix plus 13 more
- Notes:
  - Imports 2 external or internal modules.
  - Defines 25 class(es).

### `lectureforge-backend/requirements.txt`

- Role: Dependency or project configuration file
- Type: `.txt`
- Size: `163` bytes
- Lines: `10`
- Local dependencies: none detected

### `lectureforge-backend/services/__init__.py`

- Role: Supporting project file
- Type: `.py`
- Size: `0` bytes
- Lines: `0`
- Local dependencies: none detected

### `lectureforge-backend/services/job_store.py`

- Role: Class-based business logic or data model
- Type: `.py`
- Size: `3479` bytes
- Lines: `129`
- Local dependencies: none detected
- Functions: __init__, add_translation, create_job, get_job, get_translation, get_translation_section, set_translation_section, update_job
- Classes: JobStore
- Notes:
  - Imports 1 external or internal modules.
  - Defines 8 function(s).
  - Defines 1 class(es).

### `lectureforge-backend/services/openai_service.py`

- Role: Prompt or AI instruction logic
- Type: `.py`
- Size: `1805` bytes
- Lines: `64`
- Local dependencies: none detected
- Functions: call_openai_json, create_embedding, create_embeddings, generate_json, generate_text
- Environment variables: OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_MODEL
- Notes:
  - Imports 5 external or internal modules.
  - Defines 5 function(s).
  - Uses environment variable(s): OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, OPENAI_MODEL.
  - May handle API keys or secrets. Verify secrets are loaded from environment variables.
  - Reads, writes, or processes JSON-like data.

### `lectureforge-backend/study_kit_82186720.json`

- Role: API server or backend route module
- Type: `.json`
- Size: `35968` bytes
- Lines: `388`
- Local dependencies: none detected

### `lectureforge-backend/utils/__init__.py`

- Role: Utility/helper module
- Type: `.py`
- Size: `0` bytes
- Lines: `0`
- Local dependencies: none detected

### `lectureforge-backend/utils/faculty_audit_validator.py`

- Role: Utility/helper module
- Type: `.py`
- Size: `447` bytes
- Lines: `16`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
- Functions: validate_faculty_audit
- Notes:
  - Imports 1 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-backend/utils/study_kit_validator.py`

- Role: Utility/helper module
- Type: `.py`
- Size: `2646` bytes
- Lines: `84`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
  - `lectureforge-backend/utils/__init__.py`
  - `lectureforge-backend/utils/transcript_utils.py`
- Functions: clamp_timestamp, find_best_timestamp_for_text, validate_study_kit
- Notes:
  - Imports 3 external or internal modules.
  - Defines 3 function(s).
  - Includes exception handling.

### `lectureforge-backend/utils/transcript_utils.py`

- Role: Utility/helper module
- Type: `.py`
- Size: `3659` bytes
- Lines: `142`
- Local dependencies:
  - `lectureforge-backend/models/__init__.py`
  - `lectureforge-backend/models/schemas.py`
- Functions: clean_text, format_timestamp, merge_small_chunks, plain_text_to_chunks, transcript_to_plain_text, youtube_timestamp_url
- Notes:
  - Imports 3 external or internal modules.
  - Defines 6 function(s).
  - Includes exception handling.

### `lectureforge-frontend/README.md`

- Role: Project documentation
- Type: `.md`
- Size: `610` bytes
- Lines: `42`
- Local dependencies: none detected

### `lectureforge-frontend/index.html`

- Role: Supporting project file
- Type: `.html`
- Size: `302` bytes
- Lines: `12`
- Local dependencies: none detected

### `lectureforge-frontend/package.json`

- Role: Dependency or project configuration file
- Type: `.json`
- Size: `561` bytes
- Lines: `24`
- Local dependencies: none detected

### `lectureforge-frontend/postcss.config.js`

- Role: Configuration file
- Type: `.js`
- Size: `81` bytes
- Lines: `6`
- Local dependencies: none detected

### `lectureforge-frontend/src/App.jsx`

- Role: Application entry point
- Type: `.jsx`
- Size: `15344` bytes
- Lines: `548`
- Local dependencies:
  - `lectureforge-frontend/src/components/FacultyAuditDashboard.jsx`
  - `lectureforge-frontend/src/components/Header.jsx`
  - `lectureforge-frontend/src/components/ProgressCard.jsx`
  - `lectureforge-frontend/src/components/StudyDashboard.jsx`
  - `lectureforge-frontend/src/components/VideoForm.jsx`
- Functions: App, handleLanguageChange, handleModeChange, handleProcessVideo, normalizeTranslatedSectionData, pollJobStatus, structuredCloneSafe, translateTranscriptInBatches
- Notes:
  - Imports 6 external or internal modules.
  - Defines 8 function(s).
  - Reads, writes, or processes JSON-like data.

### `lectureforge-frontend/src/components/ConceptMapTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `2043` bytes
- Lines: `85`
- Local dependencies: none detected
- Functions: ConceptMapTab, buildLayout
- Notes:
  - Imports 1 external or internal modules.
  - Defines 2 function(s).

### `lectureforge-frontend/src/components/FacultyAuditDashboard.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `13444` bytes
- Lines: `487`
- Local dependencies: none detected
- Functions: DimensionSection, EmptyState, FacultyAuditDashboard, ListCard, TextBlock, buildMarkdownReport, downloadReport, formatDimensionForMarkdown
- Notes:
  - Imports 1 external or internal modules.
  - Defines 8 function(s).

### `lectureforge-frontend/src/components/FlashcardsTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `4334` bytes
- Lines: `137`
- Local dependencies: none detected
- Functions: FlashcardsTab, buildYouTubeJumpUrl, formatTime, toggleCard
- Notes:
  - Imports 2 external or internal modules.
  - Defines 4 function(s).

### `lectureforge-frontend/src/components/Header.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `1055` bytes
- Lines: `26`
- Local dependencies: none detected
- Functions: Header
- Notes:
  - Imports 2 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-frontend/src/components/OutlineTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `3208` bytes
- Lines: `105`
- Local dependencies: none detected
- Functions: OutlineTab, buildYouTubeJumpUrl, formatTime
- Notes:
  - Imports 2 external or internal modules.
  - Defines 3 function(s).

### `lectureforge-frontend/src/components/ProgressCard.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `2248` bytes
- Lines: `65`
- Local dependencies: none detected
- Functions: ProgressCard
- Notes:
  - Imports 2 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-frontend/src/components/SearchTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `6624` bytes
- Lines: `203`
- Local dependencies:
  - `lectureforge-frontend/src/lib/api.js`
- Functions: SearchTab, buildYouTubeJumpUrl, formatTime, handleSearch
- Notes:
  - Imports 3 external or internal modules.
  - Defines 4 function(s).

### `lectureforge-frontend/src/components/StudyDashboard.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `6718` bytes
- Lines: `220`
- Local dependencies:
  - `lectureforge-frontend/src/components/ConceptMapTab.jsx`
  - `lectureforge-frontend/src/components/FlashcardsTab.jsx`
  - `lectureforge-frontend/src/components/OutlineTab.jsx`
  - `lectureforge-frontend/src/components/SearchTab.jsx`
  - `lectureforge-frontend/src/components/SummariesTab.jsx`
  - `lectureforge-frontend/src/components/Tabs.jsx`
  - `lectureforge-frontend/src/components/TranscriptTab.jsx`
- Functions: StudyDashboard, TranslationProgressList, formatTranslationStatus, getTranslationStatusClass
- Notes:
  - Imports 9 external or internal modules.
  - Defines 4 function(s).

### `lectureforge-frontend/src/components/SummariesTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `1101` bytes
- Lines: `36`
- Local dependencies: none detected
- Functions: SummariesTab
- Notes:
  - Imports 1 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-frontend/src/components/Tabs.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `943` bytes
- Lines: `29`
- Local dependencies: none detected
- Functions: Tabs
- Notes:
  - Imports 1 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-frontend/src/components/TranscriptTab.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `567` bytes
- Lines: `18`
- Local dependencies: none detected
- Functions: TranscriptTab
- Notes:
  - Imports 1 external or internal modules.
  - Defines 1 function(s).

### `lectureforge-frontend/src/components/VideoForm.jsx`

- Role: Frontend component
- Type: `.jsx`
- Size: `1911` bytes
- Lines: `56`
- Local dependencies: none detected
- Functions: VideoForm, handleSubmit
- Notes:
  - Imports 1 external or internal modules.
  - Defines 2 function(s).

### `lectureforge-frontend/src/lib/api.js`

- Role: Reusable logic module
- Type: `.js`
- Size: `3662` bytes
- Lines: `162`
- Local dependencies: none detected
- Functions: getFacultyAudit, getJobStatus, getStudyKit, processFacultyAudit, processVideo, searchStudyKit, translateSection, translateStudyKit
- Environment variables: VITE_API_BASE_URL
- Notes:
  - Defines 8 function(s).
  - Uses environment variable(s): VITE_API_BASE_URL.
  - Reads, writes, or processes JSON-like data.

### `lectureforge-frontend/src/main.jsx`

- Role: Application entry point
- Type: `.jsx`
- Size: `281` bytes
- Lines: `11`
- Local dependencies:
  - `lectureforge-frontend/src/App.jsx`
  - `lectureforge-frontend/src/styles/index.css`
- Notes:
  - Imports 5 external or internal modules.

### `lectureforge-frontend/src/styles/index.css`

- Role: Supporting project file
- Type: `.css`
- Size: `601` bytes
- Lines: `34`
- Local dependencies: none detected

### `lectureforge-frontend/tailwind.config.js`

- Role: Configuration file
- Type: `.js`
- Size: `248` bytes
- Lines: `12`
- Local dependencies: none detected

### `lectureforge-frontend/vite.config.js`

- Role: Configuration file
- Type: `.js`
- Size: `134` bytes
- Lines: `6`
- Local dependencies: none detected
- Notes:
  - Imports 2 external or internal modules.

### `tools/project_mapper.py`

- Role: Developer tooling script
- Type: `.py`
- Size: `35127` bytes
- Lines: `1129`
- Local dependencies: none detected
- Functions: __init__, build_graphviz_graph, build_lookup_tables, collect_files, detect_entry_points, detect_env_vars, detect_python_package_roots, escape_dot, escape_mermaid_label, generate_key_notes, get_node_id, graph_node_attributes plus 22 more
- Classes: FileSummary, ProjectMap, ProjectMapper
- Notes:
  - Imports 10 external or internal modules.
  - Defines 34 function(s).
  - Defines 3 class(es).
  - May handle API keys or secrets. Verify secrets are loaded from environment variables.
  - Contains TODO or FIXME comments.
  - Includes exception handling.

## Dependency Edges

- `lectureforge-backend/agents/agent1_ingestion.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/agents/agent1_ingestion.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/agents/agent1_ingestion.py` uses `lectureforge-backend/utils/__init__.py`
- `lectureforge-backend/agents/agent1_ingestion.py` uses `lectureforge-backend/utils/transcript_utils.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/services/__init__.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/services/openai_service.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/utils/__init__.py`
- `lectureforge-backend/agents/agent2_analysis.py` uses `lectureforge-backend/utils/transcript_utils.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/services/__init__.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/services/openai_service.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/utils/__init__.py`
- `lectureforge-backend/agents/agent3_study.py` uses `lectureforge-backend/utils/transcript_utils.py`
- `lectureforge-backend/agents/agent4_faculty_audit.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/agents/agent4_faculty_audit.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/agents/agent4_faculty_audit.py` uses `lectureforge-backend/services/__init__.py`
- `lectureforge-backend/agents/agent4_faculty_audit.py` uses `lectureforge-backend/services/openai_service.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/agents/__init__.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/agents/agent1_ingestion.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/agents/agent2_analysis.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/agents/agent3_study.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/agents/agent4_faculty_audit.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/services/__init__.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/services/job_store.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/services/openai_service.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/utils/__init__.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/utils/faculty_audit_validator.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/utils/study_kit_validator.py`
- `lectureforge-backend/main.py` uses `lectureforge-backend/utils/transcript_utils.py`
- `lectureforge-backend/utils/faculty_audit_validator.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/utils/faculty_audit_validator.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/utils/study_kit_validator.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/utils/study_kit_validator.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/utils/study_kit_validator.py` uses `lectureforge-backend/utils/__init__.py`
- `lectureforge-backend/utils/study_kit_validator.py` uses `lectureforge-backend/utils/transcript_utils.py`
- `lectureforge-backend/utils/transcript_utils.py` uses `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/utils/transcript_utils.py` uses `lectureforge-backend/models/schemas.py`
- `lectureforge-frontend/src/App.jsx` uses `lectureforge-frontend/src/components/FacultyAuditDashboard.jsx`
- `lectureforge-frontend/src/App.jsx` uses `lectureforge-frontend/src/components/Header.jsx`
- `lectureforge-frontend/src/App.jsx` uses `lectureforge-frontend/src/components/ProgressCard.jsx`
- `lectureforge-frontend/src/App.jsx` uses `lectureforge-frontend/src/components/StudyDashboard.jsx`
- `lectureforge-frontend/src/App.jsx` uses `lectureforge-frontend/src/components/VideoForm.jsx`
- `lectureforge-frontend/src/components/SearchTab.jsx` uses `lectureforge-frontend/src/lib/api.js`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/ConceptMapTab.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/FlashcardsTab.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/OutlineTab.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/SearchTab.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/SummariesTab.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/Tabs.jsx`
- `lectureforge-frontend/src/components/StudyDashboard.jsx` uses `lectureforge-frontend/src/components/TranscriptTab.jsx`
- `lectureforge-frontend/src/main.jsx` uses `lectureforge-frontend/src/App.jsx`
- `lectureforge-frontend/src/main.jsx` uses `lectureforge-frontend/src/styles/index.css`

## Maintenance Notes

Regenerate this file whenever the project structure changes:

```bash
python tools/project_mapper.py
```
