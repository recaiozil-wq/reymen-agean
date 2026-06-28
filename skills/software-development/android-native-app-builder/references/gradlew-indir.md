---
skill_id: 6c6ad83974cd
usage_count: 1
last_used: 2026-06-16
---
# gradlew indir
curl -sL "https://raw.githubusercontent.com/gradle/gradle/v8.11.1/gradlew" -o gradlew
curl -sL "https://raw.githubusercontent.com/gradle/gradle/v8.11.1/gradlew.bat" -o gradlew.bat
chmod +x gradlew gradlew.bat
```

### 3. Build
```bash
export ANDROID_HOME="/c/Users/<user>/AppData/Local/Android/Sdk"
export ANDROID_SDK_ROOT="/c/Users/<user>/AppData/Local/Android/Sdk"
./gradlew assembleDebug --no-daemon
```

### 4. APK konumu
`app/build/outputs/apk/debug/app-debug.apk`