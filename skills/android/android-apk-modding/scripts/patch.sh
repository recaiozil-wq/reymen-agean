#!/usr/bin/env bash
#
# patch.sh — APK modding pipeline (tek yön, geri dönüşsüz)
#
# Kullanım:
#   ./patch.sh <target.apk> [tip] [argümanlar...]
#
# Tipler:
#   full        — tüm pipeline (önbelge→doğrula)
#   manifest    — targetSdk, debuggable, networkSecurity, split-clean
#   resource    — renk, string, logo değişikliği
#   smali       — yeni service sınıfı ekle + manifest bildirimi
#
# Çıkış kodları:
#   0 başarılı  1 önbelge  2 decompile  3 yama  4 rebuild  5 zipalign  6 imza  7 doğrula
#
# Ortam değişkenleri:
#   KEYSTORE, KEYALIAS, KSPASS (ZORUNLU), PACKAGE_NAME
#
set -euo pipefail

APK="${1:-}"
PATCH_TYPE="${2:-full}"
WORK_DIR="${WORK_DIR:-$(mktemp -d /tmp/apkmod.XXXXXX)}"
ANDROID_SDK="/c/Users/marko/AppData/Local/Android/Sdk/build-tools/35.0.0"
KEYSTORE="${KEYSTORE:-/c/Users/marko/Desktop/LiveTranscriber/release.keystore}"
KEYALIAS="${KEYALIAS:-livetranscriber}"
KSPASS="${KSPASS:-}"

[[ -f "$APK" ]] || { echo "Kullanım: $0 <target.apk> [tip]"; exit 1; }
[[ -n "$KSPASS" ]] || { echo "KSPASS zorunlu"; exit 1; }

APKTOOL="java -jar /c/Users/marko/re-hermes/apktool.jar"
ZIPALIGN="${ANDROID_SDK}/zipalign.exe"
APKSIGNER="${ANDROID_SDK}/apksigner.bat"

gate() { local n="$1" msg="$2"; shift 2; if "$@"; then echo "  GECTI [$n] $msg"; else echo "  KALDI [$n] $msg"; exit "$n"; fi; }

# Adım 0 — Önbelge
echo "[0/6] Önbelge"
$APKTOOL d -f -o "${WORK_DIR}/_preview" "$APK" >/dev/null 2>&1 || true
TARGET_SDK=$(grep -E "targetSdkVersion:" "${WORK_DIR}/_preview/apktool.yml" 2>/dev/null | awk '{print $2}' || echo "?")
PKG_NAME=$(grep 'package=' "${WORK_DIR}/_preview/AndroidManifest.xml" 2>/dev/null | sed 's/.*package="\([^"]*\)".*/\1/' || echo "?")
NATIVE_COUNT=$(find "${WORK_DIR}/_preview/lib" -name "*.so" 2>/dev/null | wc -l)
echo "  Package: $PKG_NAME  targetSdk: $TARGET_SDK  native: $NATIVE_COUNT"
rm -rf "${WORK_DIR}/_preview"

# Adım 1 — Decompile
echo "[1/6] Decompile"
cp "$APK" "${WORK_DIR}/original.apk"
$APKTOOL d -f -o "${WORK_DIR}/_work" "$APK" >/dev/null
gate 1 "manifest" test -f "${WORK_DIR}/_work/AndroidManifest.xml"

# Adım 2 — Yama
echo "[2/6] Yama: $PATCH_TYPE"
case "$PATCH_TYPE" in
    manifest)
        for arg in "${@:3}"; do
            case "$arg" in
                targetSdk=*) sed -i "s/targetSdkVersion:.*/targetSdkVersion: ${arg#targetSdk=}/" "${WORK_DIR}/_work/apktool.yml" ;;
                debuggable=true) sed -i 's|<application |<application android:debuggable="true" |' "${WORK_DIR}/_work/AndroidManifest.xml" ;;
                networkSecurity=true)
                    mkdir -p "${WORK_DIR}/_work/res/xml"
                    cat > "${WORK_DIR}/_work/res/xml/network_security_config.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors><certificates src="system"/></trust-anchors>
    </base-config>
</network-security-config>
EOF
                    sed -i 's|<application |<application android:networkSecurityConfig="@xml/network_security_config" |' "${WORK_DIR}/_work/AndroidManifest.xml"
                    ;;
                split-clean)
                    sed -i 's/android:isSplitRequired="[^"]*"//' "${WORK_DIR}/_work/AndroidManifest.xml"
                    sed -i 's/android:requiredSplitTypes="[^"]*"//' "${WORK_DIR}/_work/AndroidManifest.xml"
                    sed -i '/splits\.required/d; /com\.android\.vending\.splits/d; /stamp\./d' "${WORK_DIR}/_work/AndroidManifest.xml"
                    ;;
            esac
        done
        ;;
    resource)
        TYPE="$3" NAME="$4" NEWVAL="$5"
        case "$TYPE" in
            color) sed -i "s/name=\"${NAME}\">[^<]*</name=\"${NAME}\">${NEWVAL}</" "${WORK_DIR}/_work/res/values/colors.xml" ;;
            string) sed -i "s|name=\"${NAME}\">[^<]*<|name=\"${NAME}\">${NEWVAL}<|" "${WORK_DIR}/_work/res/values/strings.xml" ;;
            logo) cp "$NEWVAL" "${WORK_DIR}/_work/res/drawable/${NAME}" ;;
        esac
        ;;
    smali)
        CLASS="$3" PKG_PATH=$(echo "$PKG_NAME" | tr '.' '/')
        mkdir -p "${WORK_DIR}/_work/smali/${PKG_PATH}"
        cat > "${WORK_DIR}/_work/smali/${PKG_PATH}/${CLASS}.smali" << EOF
.class public L${PKG_PATH}/${CLASS};
.super Landroid/app/Service;
.source "${CLASS}.smali"
.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 1
    const/4 v0, 0x1
    return v0
.end method
.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 1
    const/4 v0, 0x0
    return-object v0
.end method
EOF
        sed -i "s|</application>|    <service android:name=\".${CLASS}\" android:exported=\"false\"/>\\n    </application>|" "${WORK_DIR}/_work/AndroidManifest.xml"
        ;;
esac

# Adım 3 — Rebuild
echo "[3/6] Rebuild"
$APKTOOL b -o "${WORK_DIR}/_build_unsigned.apk" "${WORK_DIR}/_work" >/dev/null
SIZE=$(stat -c%s "${WORK_DIR}/_build_unsigned.apk" 2>/dev/null || echo 0)
gate 4 "apk boyut" test "$SIZE" -gt 0

# Adım 4 — zipalign
echo "[4/6] zipalign"
"$ZIPALIGN" -f -p 4 "${WORK_DIR}/_build_unsigned.apk" "${WORK_DIR}/_build_aligned.apk" >/dev/null 2>&1
gate 5 "hizalama" "$ZIPALIGN" -c 4 "${WORK_DIR}/_build_aligned.apk" >/dev/null 2>&1

# Adım 5 — İmzala
echo "[5/6] apksigner"
"$APKSIGNER" sign --ks "$KEYSTORE" --ks-key-alias "$KEYALIAS" --ks-pass pass:"$KSPASS" "${WORK_DIR}/_build_aligned.apk" >/dev/null 2>&1
gate 6 "imza" "$APKSIGNER" verify "${WORK_DIR}/_build_aligned.apk" >/dev/null 2>&1

# Adım 6 — Doğrula
echo "[6/6] Doğrula"
OUT_APK="./$(basename "$APK" .apk)_mod.apk"
cp "${WORK_DIR}/_build_aligned.apk" "$OUT_APK"
echo "  Çıktı: $OUT_APK"

if command -v adb &>/dev/null; then
    adb install "${WORK_DIR}/_build_aligned.apk" 2>/dev/null && echo "  Kurulum: OK" || echo "  Kurulum: FAIL"
    if [[ -n "${PACKAGE_NAME:-}" ]]; then
        adb logcat -c 2>/dev/null || true
        adb shell monkey -p "$PACKAGE_NAME" 1 2>/dev/null || true
        sleep 2
        CRASH=$(adb logcat -d | grep -ci "FATAL\|ANR.*$PACKAGE_NAME" || true)
        echo "  Crash: $CRASH"
    fi
fi

rm -rf "$WORK_DIR"
echo "Pipeline: OK"
exit 0
