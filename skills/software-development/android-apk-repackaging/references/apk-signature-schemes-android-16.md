---
skill_id: 7f3af666a11f
usage_count: 1
last_used: 2026-06-16
---
# APK Signature Schemes on Android 16 (API 36)

## Verified Behavior

Tested with: Samsung Galaxy S22 Ultra (SM-S908E), One UI 8.0, Android 16, May 2026 security patch.

| Scheme | Supported? | Notes |
|--------|-----------|-------|
| V1 (JAR) | ✅ | Not required for API 24+, but accepted |
| V2 (APK Sig v2) | ✅ | Not required for API 24+, but accepted |
| V3 (APK Sig v3) | ✅ | **Sufficient alone for install** |
| V3.1 | ✅ | |
| V3.2 | ✅ | |
| V4 | ✅ | For incremental updates only |

## Key Finding

**V3 signature alone is sufficient** for installing side-loaded APKs on Android 16. The `apksigner` from build-tools 35+ may default to V3-only when minSdkVersion >= 28. This is NOT the cause of "Package invalid" errors.

## Actual Causes of "Package invalid" Parse Error

1. **Native lib compression** — `.so` files stored with DEFLATE (compressed) when manifest has `extractNativeLibs="false"`. Fix: store as STORED (uncompressed).
2. **Split APK references** — Manifests from split bundles contain `isSplitRequired="true"`, `requiredSplitTypes`, and `com.android.vending.splits` meta-data. These must be removed for standalone install.
3. **Corrupted zip** — Python zipfile can produce valid APKs but compression per file type must be correct.

## apksigner version info

- Build-tools 34/35/36/37 all produce V3-only signatures by default on modern APKs
- Explicit `--v1-signing-enabled true --v2-signing-enabled true` flags did NOT force V1/V2 in testing
- This appears to be expected behavior, not a bug
