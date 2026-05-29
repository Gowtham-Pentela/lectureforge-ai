# Architecture Report

This report is generated locally from static project analysis. No external API calls are used.

## Executive Summary

- Project root: `/Users/gowtham/Desktop/lectureforge-ai`
- Files scanned: `98`
- Dependency edges: `57`
- Entry points: `3`
- Roles detected: `16`
- Extensions detected: `21`

## Entry Points

- `lectureforge-backend/main.py`
- `lectureforge-frontend/src/App.jsx`
- `lectureforge-frontend/src/main.jsx`

## Architecture Warnings

- 46 non-documentation files appear isolated. Some may be unused, generated, or dynamically loaded.
- Duplicate project/build files detected: index.html. Verify which root Vercel/Docker/local dev actually uses.
- 6 file(s) mention API keys, passwords, or secrets. Confirm secrets are not hardcoded.

## Most Connected Files

| Rank | File | Incoming | Outgoing | Total | Role |
|---:|---|---:|---:|---:|---|
| 1 | `lectureforge-backend/main.py` | 0 | 14 | 14 | Application entry point |
| 2 | `lectureforge-backend/models/__init__.py` | 8 | 0 | 8 | Supporting project file |
| 3 | `lectureforge-backend/models/schemas.py` | 8 | 0 | 8 | Class-based business logic or data model |
| 4 | `lectureforge-frontend/src/components/StudyDashboard.jsx` | 1 | 7 | 8 | Frontend component |
| 5 | `lectureforge-backend/utils/transcript_utils.py` | 5 | 2 | 7 | Utility/helper module |
| 6 | `lectureforge-backend/agents/agent2_analysis.py` | 1 | 6 | 7 | Streamlit user interface module |
| 7 | `lectureforge-backend/agents/agent3_study.py` | 1 | 6 | 7 | AI model integration module |
| 8 | `lectureforge-frontend/src/App.jsx` | 1 | 5 | 6 | Application entry point |
| 9 | `lectureforge-backend/utils/__init__.py` | 5 | 0 | 5 | Utility/helper module |
| 10 | `lectureforge-backend/agents/agent1_ingestion.py` | 1 | 4 | 5 | AI model integration module |
| 11 | `lectureforge-backend/agents/agent4_faculty_audit.py` | 1 | 4 | 5 | Streamlit user interface module |
| 12 | `lectureforge-backend/utils/study_kit_validator.py` | 1 | 4 | 5 | Utility/helper module |
| 13 | `lectureforge-backend/services/__init__.py` | 4 | 0 | 4 | Supporting project file |
| 14 | `lectureforge-backend/services/openai_service.py` | 4 | 0 | 4 | AI model integration module |
| 15 | `lectureforge-backend/utils/faculty_audit_validator.py` | 1 | 2 | 3 | Utility/helper module |

## Environment Variables

### `LECTUREFORGE_CORS_ORIGINS`
- `lectureforge-backend/main.py`

### `LECTUREFORGE_ENABLE_DEBUG_ENDPOINTS`
- `lectureforge-backend/main.py`

### `OPENAI_API_KEY`
- `lectureforge-backend/agents/agent1_ingestion.py`
- `lectureforge-backend/main.py`
- `lectureforge-backend/services/openai_service.py`

### `OPENAI_EMBEDDING_MODEL`
- `lectureforge-backend/main.py`
- `lectureforge-backend/services/openai_service.py`

### `OPENAI_MODEL`
- `lectureforge-backend/main.py`
- `lectureforge-backend/services/openai_service.py`

### `SUPADATA_API_KEY`
- `lectureforge-backend/agents/agent1_ingestion.py`
- `lectureforge-backend/main.py`

### `VITE_API_BASE_URL`
- `lectureforge-frontend/src/lib/api.js`

## Files With Secret/API-Key Risk

- `MOBILE_RELEASE.md`
- `README.md`
- `lectureforge-backend/agents/agent1_ingestion.py`
- `lectureforge-backend/main.py`
- `lectureforge-backend/services/openai_service.py`
- `tools/project_mapper.py`

## Possibly Isolated Files

- `lectureforge-backend/study_kit_82186720.json`
- `lectureforge-frontend/android/app/capacitor.build.gradle`
- `lectureforge-frontend/android/app/proguard-rules.pro`
- `lectureforge-frontend/android/app/src/androidTest/java/com/getcapacitor/myapp/ExampleInstrumentedTest.java`
- `lectureforge-frontend/android/app/src/main/AndroidManifest.xml`
- `lectureforge-frontend/android/app/src/main/assets/capacitor.plugins.json`
- `lectureforge-frontend/android/app/src/main/assets/public/cordova.js`
- `lectureforge-frontend/android/app/src/main/assets/public/cordova_plugins.js`
- `lectureforge-frontend/android/app/src/main/assets/public/index.html`
- `lectureforge-frontend/android/app/src/main/java/com/lectureforge/ai/MainActivity.java`
- `lectureforge-frontend/android/app/src/main/res/drawable-v24/ic_launcher_foreground.xml`
- `lectureforge-frontend/android/app/src/main/res/drawable/ic_launcher_background.xml`
- `lectureforge-frontend/android/app/src/main/res/layout/activity_main.xml`
- `lectureforge-frontend/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
- `lectureforge-frontend/android/app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml`
- `lectureforge-frontend/android/app/src/main/res/values/ic_launcher_background.xml`
- `lectureforge-frontend/android/app/src/main/res/values/strings.xml`
- `lectureforge-frontend/android/app/src/main/res/values/styles.xml`
- `lectureforge-frontend/android/app/src/main/res/xml/file_paths.xml`
- `lectureforge-frontend/android/app/src/test/java/com/getcapacitor/myapp/ExampleUnitTest.java`
- `lectureforge-frontend/android/capacitor-cordova-android-plugins/cordova.variables.gradle`
- `lectureforge-frontend/android/capacitor-cordova-android-plugins/src/main/AndroidManifest.xml`
- `lectureforge-frontend/android/capacitor.settings.gradle`
- `lectureforge-frontend/android/gradle.properties`
- `lectureforge-frontend/android/gradle/wrapper/gradle-wrapper.properties`
- `lectureforge-frontend/android/gradlew`
- `lectureforge-frontend/android/gradlew.bat`
- `lectureforge-frontend/android/settings.gradle`
- `lectureforge-frontend/android/variables.gradle`
- `lectureforge-frontend/index.html`
- ... plus 16 more

## Leaf Files

Files that are imported by other files but do not import local files themselves.

- `lectureforge-backend/agents/__init__.py`
- `lectureforge-backend/models/__init__.py`
- `lectureforge-backend/models/schemas.py`
- `lectureforge-backend/services/__init__.py`
- `lectureforge-backend/services/job_store.py`
- `lectureforge-backend/services/openai_service.py`
- `lectureforge-backend/utils/__init__.py`
- `lectureforge-frontend/src/components/ConceptMapTab.jsx`
- `lectureforge-frontend/src/components/FacultyAuditDashboard.jsx`
- `lectureforge-frontend/src/components/FlashcardsTab.jsx`
- `lectureforge-frontend/src/components/Header.jsx`
- `lectureforge-frontend/src/components/OutlineTab.jsx`
- `lectureforge-frontend/src/components/ProgressCard.jsx`
- `lectureforge-frontend/src/components/SummariesTab.jsx`
- `lectureforge-frontend/src/components/Tabs.jsx`
- `lectureforge-frontend/src/components/TranscriptTab.jsx`
- `lectureforge-frontend/src/components/VideoForm.jsx`
- `lectureforge-frontend/src/lib/api.js`
- `lectureforge-frontend/src/styles/index.css`

## Duplicate Basenames

### `androidmanifest.xml`
- `lectureforge-frontend/android/app/src/main/AndroidManifest.xml`
- `lectureforge-frontend/android/capacitor-cordova-android-plugins/src/main/AndroidManifest.xml`

### `build.gradle`
- `lectureforge-frontend/android/app/build.gradle`
- `lectureforge-frontend/android/build.gradle`
- `lectureforge-frontend/android/capacitor-cordova-android-plugins/build.gradle`

### `capacitor.config.json`
- `lectureforge-frontend/android/app/src/main/assets/capacitor.config.json`
- `lectureforge-frontend/capacitor.config.json`
- `lectureforge-frontend/ios/App/App/capacitor.config.json`

### `config.xml`
- `lectureforge-frontend/android/app/src/main/res/xml/config.xml`
- `lectureforge-frontend/ios/App/App/config.xml`

### `contents.json`
- `lectureforge-frontend/ios/App/App/Assets.xcassets/AppIcon.appiconset/Contents.json`
- `lectureforge-frontend/ios/App/App/Assets.xcassets/Contents.json`
- `lectureforge-frontend/ios/App/App/Assets.xcassets/Splash.imageset/Contents.json`

### `cordova.js`
- `lectureforge-frontend/android/app/src/main/assets/public/cordova.js`
- `lectureforge-frontend/ios/App/App/public/cordova.js`

### `cordova_plugins.js`
- `lectureforge-frontend/android/app/src/main/assets/public/cordova_plugins.js`
- `lectureforge-frontend/ios/App/App/public/cordova_plugins.js`

### `ic_launcher_background.xml`
- `lectureforge-frontend/android/app/src/main/res/drawable/ic_launcher_background.xml`
- `lectureforge-frontend/android/app/src/main/res/values/ic_launcher_background.xml`

### `index-b_kexwk-.css`
- `lectureforge-frontend/android/app/src/main/assets/public/assets/index-B_kExwk-.css`
- `lectureforge-frontend/ios/App/App/public/assets/index-B_kExwk-.css`

### `index.html`
- `lectureforge-frontend/android/app/src/main/assets/public/index.html`
- `lectureforge-frontend/index.html`
- `lectureforge-frontend/ios/App/App/public/index.html`

### `readme.md`
- `README.md`
- `lectureforge-frontend/README.md`
- `lectureforge-frontend/ios/App/CapApp-SPM/README.md`

## Role Distribution

- Supporting project file: `39`
- Frontend component: `12`
- Configuration file: `9`
- Project documentation: `5`
- Dependency or project configuration file: `5`
- Utility/helper module: `4`
- AI model integration module: `3`
- Streamlit user interface module: `3`
- Application entry point: `3`
- API server or backend route module: `3`
- Stylesheet: `3`
- Frontend HTML entry file: `3`
- Class-based business logic or data model: `2`
- Test file: `2`
- Reusable logic module: `1`
- Developer tooling script: `1`

## Extension Distribution

- `.py`: `16`
- `.jsx`: `14`
- `.xml`: `13`
- `.json`: `9`
- `.gradle`: `8`
- `.js`: `8`
- `.md`: `5`
- `.java`: `3`
- `.css`: `3`
- `.html`: `3`
- `.swift`: `3`
- `.properties`: `2`
- `.storyboard`: `2`
- `.plist`: `2`
- `.txt`: `1`
- `.pro`: `1`
- `no extension`: `1`
- `.bat`: `1`
- `.pbxproj`: `1`
- `.podspec`: `1`
- `.xcconfig`: `1`

## Detected Concepts

`lectureforge` (97), `frontend` (92), `android` (40), `supporting` (39), `get` (21), `ios` (21), `backend` (20), `study` (19), `audit` (19), `build` (18), `faculty` (16), `kit` (15), `xml` (15), `transcript` (14), `configuration` (14), `translate` (12), `tab` (12), `api` (11), `section` (11), `gradle` (11), `assets` (11), `video` (10), `openai` (10), `search` (10), `process` (10)

## Suggested Questions For AI Coding Tools

- What files should I read first to understand this project?
- Which files are safest to edit for a UI-only change?
- Which files appear to control the main application flow?
- How does execution flow from the entry points into the rest of the codebase?
- Why is `lectureforge-backend/main.py` the most connected file?
- Which environment variables are required to run this project?

## Recommended AI Workflow

1. Read `ARCHITECTURE_REPORT.md` first.
2. Open `PROJECT_GRAPH.html` to understand relationships visually.
3. Use `PROJECT_MAP.md` for exact file summaries.
4. Inspect the target source files before editing.
5. Regenerate the project map after meaningful structural changes.
