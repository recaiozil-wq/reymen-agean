#!/usr/bin/env bash
#
# apk-audit.sh — Faz 1: Kendi APK'nı saldırgan gözüyle oku (READ-ONLY)
#
# Yama YAPMAZ. Sadece decompile eder, lisans/premium mantığını arar,
# gömülü sırları tarar ve bir kırılganlık haritası raporu üretir.
#
# Kullanım:
#   ./apk-audit.sh /yol/uygulama.apk
#   ./apk-audit.sh /yol/uygulama.apk ./cikti-dizini
#
# Gereksinimler: apktool, jadx (jadx-cli), aapt veya aapt2, grep, awk
#
set -euo pipefail

# ---------------------------------------------------------------------------
# 0. Argüman ve ortam kontrolü
# ---------------------------------------------------------------------------
APK="${1:-}"
OUTDIR="${2:-./audit-$(date +%Y%m%d-%H%M%S)}"

if [[ -z "$APK" || ! -f "$APK" ]]; then
  echo "Kullanım: $0 <apk-dosyasi> [cikti-dizini]" >&2
  exit 1
fi

need() { command -v "$1" >/dev/null 2>&1 || { echo "Eksik araç: $1" >&2; MISSING=1; }; }
MISSING=0
need apktool
need jadx
command -v aapt >/dev/null 2>&1 || command -v aapt2 >/dev/null 2>&1 || {
  echo "Uyarı: aapt/aapt2 yok — manifest özeti atlanacak." >&2; }
[[ "$MISSING" == "1" ]] && { echo "Önce eksik araçları kur." >&2; exit 1; }

mkdir -p "$OUTDIR"
SMALI_DIR="$OUTDIR/apktool"
JAVA_DIR="$OUTDIR/jadx"
REPORT="$OUTDIR/REPORT.md"

# Lisans / premium / bütünlük mantığına işaret eden anahtar kelimeler.
# Kendi kod tabanına göre genişlet (örn. ürün isimlerin, custom metot adların).
KEYWORDS='isPremium|isPro|isPaid|isLicensed|checkLicense|verifyLicense|licenseValid|isSubscribed|isActive|isUnlocked|hasPurchase|premiumEnabled|isTrial|trialExpired|entitlement|checkPurchase|verifyPurchase|integrity|attestation|safetyNet|isRooted|isEmulator|isDebuggable|signatureCheck|verifySignature'

# Gömülü sır göstergeleri
SECRETS='api[_-]?key|secret|password|passwd|token|bearer|authorization|client[_-]?secret|private[_-]?key|BEGIN (RSA|EC|PRIVATE)|AIza[0-9A-Za-z_-]{35}|https?://[A-Za-z0-9./_-]+'

echo "==> APK: $APK"
echo "==> Çıktı: $OUTDIR"
echo

# ---------------------------------------------------------------------------
# Rapor başlığı
# ---------------------------------------------------------------------------
{
  echo "# APK Self-Audit Raporu (Faz 1 — READ ONLY)"
  echo
  echo "- **APK:** \`$(basename "$APK")\`"
  echo "- **SHA-256:** \`$(sha256sum "$APK" | awk '{print $1}')\`"
  echo "- **Boyut:** $(du -h "$APK" | awk '{print $1}')"
  echo "- **Tarih:** $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "> Bu rapor yama içermez. Amaç: lisans/premium kararının ne kadar"
  echo "> görünür ve tek-noktaya bağlı olduğunu görmek."
  echo
} > "$REPORT"

# ---------------------------------------------------------------------------
# 1. apktool — smali + resource + manifest
# ---------------------------------------------------------------------------
echo "==> [1/6] apktool decompile..."
apktool d -f -o "$SMALI_DIR" "$APK" >/dev/null 2>&1 || {
  echo "apktool başarısız." >&2; exit 1; }

# ---------------------------------------------------------------------------
# 2. jadx — okunabilir Java
# ---------------------------------------------------------------------------
echo "==> [2/6] jadx decompile (Java)..."
# --no-res hızlandırır; kaynakları apktool zaten verdi.
jadx -d "$JAVA_DIR" --no-res "$APK" >/dev/null 2>&1 || \
  echo "Uyarı: jadx bazı sınıfları çözemedi (kısmi çıktı normal)."

# ---------------------------------------------------------------------------
# 3. Manifest özeti
# ---------------------------------------------------------------------------
echo "==> [3/6] Manifest özeti..."
{
  echo "## 1. Manifest"
  echo
  MAN="$SMALI_DIR/AndroidManifest.xml"
  if [[ -f "$MAN" ]]; then
    DEBUGGABLE=$(grep -o 'android:debuggable="[^"]*"' "$MAN" || true)
    echo "- **debuggable:** ${DEBUGGABLE:-bulunamadı (iyi — varsayılan false)}"
    echo "- **İzin sayısı:** $(grep -c 'uses-permission' "$MAN" || echo 0)"
    echo "- **networkSecurityConfig:** $(grep -o 'networkSecurityConfig="[^"]*"' "$MAN" || echo 'tanımlı değil')"
    echo
    echo "İlk 15 izin:"
    echo '```'
    grep -o 'android:name="[^"]*"' "$MAN" | grep -i permission | head -15 || echo "(yok)"
    echo '```'
  else
    echo "_Manifest çözülemedi._"
  fi
  echo
} >> "$REPORT"

# ---------------------------------------------------------------------------
# 4. Lisans / premium / bütünlük mantığı — KALP
# ---------------------------------------------------------------------------
echo "==> [4/6] Lisans/premium/bütünlük mantığı taranıyor..."
{
  echo "## 2. Lisans / Premium / Bütünlük Mantığı"
  echo
  echo "Aranan anahtar kelimeler smali içinde tarandı. Her satır bir karar"
  echo "noktası adayıdır — kaç tane var ve nerede toplanmış, kritik soru bu."
  echo
  echo '### Smali isabetleri'
  echo '```'
  grep -rInE "$KEYWORDS" "$SMALI_DIR" --include='*.smali' 2>/dev/null \
    | head -60 || echo "(isabet yok)"
  echo '```'
  HITS=$(grep -rIlE "$KEYWORDS" "$SMALI_DIR" --include='*.smali' 2>/dev/null | wc -l | tr -d ' ')
  echo
  echo "- **Etkilenen smali dosyası sayısı:** $HITS"
  echo
  echo "### Java karşılığı (jadx — okuması kolay)"
  echo '```'
  grep -rInE "$KEYWORDS" "$JAVA_DIR" --include='*.java' 2>/dev/null \
    | head -40 || echo "(isabet yok / jadx çözemedi)"
  echo '```'
  echo
  echo "> **Yorum:** İsabetler 1–2 dosyada toplanmış ve karar tek bir boolean"
  echo "> dönüşüyse → tek satır yamayla kırılabilir tasarım. Karar dağıtılmış"
  echo "> veya sunucudan geliyorsa → çıta yüksek."
  echo
} >> "$REPORT"

# ---------------------------------------------------------------------------
# 5. Karar yapısını işaretle (if-eqz / return-bool desenleri)
# ---------------------------------------------------------------------------
echo "==> [5/6] Yamaya açık dallanma desenleri..."
{
  echo "## 3. Tek Satır Yamaya Açık Desenler"
  echo
  echo "Lisans metotlarının hemen yakınındaki \`if-eqz\`/\`if-nez\` dalları ve"
  echo "\`return v0\` (boolean dönüş) noktaları, klasik 'tek satır flip' hedefidir."
  echo
  echo '```'
  # Anahtar kelime içeren smali dosyalarında boolean dönüş + koşullu dal say
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    cnt=$(grep -cE '^\s*(if-eqz|if-nez|return v[0-9]+)' "$f" 2>/dev/null || echo 0)
    rel="${f#"$SMALI_DIR"/}"
    echo "$cnt  $rel"
  done < <(grep -rIlE "$KEYWORDS" "$SMALI_DIR" --include='*.smali' 2>/dev/null) \
    | sort -rn | head -20
  echo '```'
  echo
  echo "> Yüksek sayı = o dosyada çok karar dalı = saldırgana çok hedef ama"
  echo "> aynı zamanda obfuscation/dağıtım varsa okuması da zor demek."
  echo
} >> "$REPORT"

# ---------------------------------------------------------------------------
# 6. Gömülü sırlar / endpoint / hardcode string
# ---------------------------------------------------------------------------
echo "==> [6/6] Gömülü sır ve endpoint taraması..."
{
  echo "## 4. Gömülü Sırlar ve Endpoint'ler"
  echo
  echo "Kaynak kodda açıkça duran API anahtarı, URL, token gibi değerler hem"
  echo "saldırgana harita verir hem de sırların sızması demektir."
  echo
  echo '### strings.xml ve kaynaklar'
  echo '```'
  grep -rInE "$SECRETS" "$SMALI_DIR/res" 2>/dev/null | head -30 || echo "(temiz görünüyor)"
  echo '```'
  echo
  echo '### Smali/Java gömülü string'
  echo '```'
  grep -rInE "$SECRETS" "$SMALI_DIR" --include='*.smali' 2>/dev/null \
    | grep -vi 'android\.\|androidx\.' | head -30 || echo "(temiz görünüyor)"
  echo '```'
  echo
} >> "$REPORT"

# ---------------------------------------------------------------------------
# Obfuscation / native sinyalleri + özet
# ---------------------------------------------------------------------------
{
  echo "## 5. Sertleştirme Sinyalleri"
  echo
  # R8/ProGuard belirtisi: çok sayıda tek harfli sınıf adı
  SHORT=$(find "$SMALI_DIR" -name '*.smali' 2>/dev/null \
    | grep -E '/[a-z]\.smali$' | wc -l | tr -d ' ')
  echo "- **Tek-harfli sınıf dosyası (obfuscation belirtisi):** $SHORT"
  [[ "$SHORT" -gt 20 ]] \
    && echo "  → R8/ProGuard aktif görünüyor (iyi)." \
    || echo "  → Obfuscation zayıf/yok — jadx çıktın muhtemelen okunaklı (zaaf)."
  echo
  # Native lib
  if ls "$SMALI_DIR"/lib/*/*.so >/dev/null 2>&1; then
    echo "- **Native (.so) kütüphane:** VAR — kritik mantığı buraya taşıma seçeneğin var."
    ls "$SMALI_DIR"/lib/*/*.so 2>/dev/null | sed 's/^/    /' | head -10
  else
    echo "- **Native (.so) kütüphane:** yok — tüm mantık smali'de, yani tamamen okunabilir."
  fi
  echo
  echo "---"
  echo
  echo "## Kırılganlık Haritası — Şu Cümleyi Kurabiliyor musun?"
  echo
  echo '> "Premium kararım [client / server] tarafında, [tek / N] karar'
  echo '> noktasında, [SharedPreferences / sunucu doğrulaması] ile saklanıyor,'
  echo '> obfuscation [var / yok], native koruma [var / yok]."'
  echo
  echo "Bu cümleyi raporun yukarısındaki verilerle doldur. \"client / tek /"
  echo "SharedPreferences / yok / yok\" çıkıyorsa Faz 2 sertleştirmesi şart."
  echo
} >> "$REPORT"

echo
echo "==> Bitti. Rapor: $REPORT"
echo "==> Smali: $SMALI_DIR   Java: $JAVA_DIR"
