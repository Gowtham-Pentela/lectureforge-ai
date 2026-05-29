# LectureForge AI Mobile Release

This project can be packaged for iOS and Android with Capacitor. Capacitor wraps the existing Vite/React frontend in native iOS and Android projects while the Python API stays deployed as a separate HTTPS backend.

## 1. Pick Final App IDs

The starter Capacitor config uses:

```text
appId: com.lectureforge.ai
appName: LectureForge AI
```

Change `lectureforge-frontend/capacitor.config.json` before publishing if you want a different bundle ID/package name. Treat this as permanent once the app is live in App Store Connect or Google Play Console.

## 2. Deploy The Backend

Mobile apps cannot call `http://localhost:8000`. Deploy `lectureforge-backend` to a production HTTPS host, set the required API keys there, and confirm:

```text
GET https://lectureforge-ai.onrender.com/
```

returns the LectureForge backend status JSON.

For mobile builds, include Capacitor origins in the backend CORS setting:

```text
LECTUREFORGE_CORS_ORIGINS=https://lectureforge-ai.vercel.app,https://localhost,capacitor://localhost
```

## 3. Configure The Mobile API URL

Create a local mobile env file:

```bash
cp lectureforge-frontend/.env.mobile.example lectureforge-frontend/.env.mobile
```

Then set:

```text
VITE_API_BASE_URL=https://lectureforge-ai.onrender.com
```

Do not commit real secrets. The frontend should only contain the public backend URL.

After changing `.env.mobile`, rerun:

```bash
npm run mobile:sync
```

## 4. Install Mobile Tooling

From `lectureforge-frontend`:

```bash
npm install
```

If the native projects do not exist yet:

```bash
npm run mobile:add:android
npm run mobile:add:ios
```

Then build and sync web assets into both native projects:

```bash
npm run mobile:build
```

## 5. Android Release

Prerequisites:

- Google Play Console developer account
- Android Studio
- Java/Gradle toolchain installed through Android Studio
- Production backend URL configured in `.env.mobile`

Open the Android project:

```bash
npm run mobile:open:android
```

In Android Studio:

1. Set the release version code/name.
2. Configure app signing.
3. Build an Android App Bundle (`.aab`).
4. Upload the `.aab` in Play Console.
5. Complete store listing, content rating, data safety, privacy policy, and testing requirements.

Google Play currently requires new apps and updates to target Android 15 / API level 35 or higher for phone/tablet apps. The generated Android project currently targets API level 36.

## 6. iOS Release

Prerequisites:

- Apple Developer Program membership
- Xcode on macOS
- App Store Connect app record
- Production backend URL configured in `.env.mobile`

Open the iOS project:

```bash
npm run mobile:open:ios
```

In Xcode:

1. Select the Apple team and bundle identifier.
2. Set version/build number.
3. Archive the app.
4. Upload to App Store Connect.
5. Test with TestFlight.
6. Complete app privacy, age rating, screenshots, description, and review notes.

App Store Connect currently requires iOS app builds to be built with Xcode 16 or later for customer distribution or TestFlight upload.

## 7. Store Review Notes

LectureForge processes YouTube lecture URLs and generates AI study/faculty-audit content. Before submitting, prepare:

- A privacy policy URL.
- Clear disclosure that generated study/audit material is AI-assisted.
- Demo credentials or a testable public YouTube lecture URL for reviewers.
- Support URL and contact email.
- Screenshot sets for required device sizes.
- Confirmation that the backend has rate limits and does not expose debug endpoints publicly.
- Final LectureForge app icons and splash screens replacing the default Capacitor assets.

The backend now disables `/debug-env` and `/debug-openai` unless `LECTUREFORGE_ENABLE_DEBUG_ENDPOINTS=true`.
