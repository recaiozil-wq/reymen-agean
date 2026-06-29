
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References__Work Smali Com Package Keepaliveservice Smali |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# _work/smali/com/package/KeepAliveService.smali
.class public Lcom/package/KeepAliveService;
.super Landroid/app/Service;
.source "KeepAliveService.smali"

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
```

**Foreground Service şablonu (mikrofon + bildirim):**

foregroundServiceType="microphone" olan service'lerde notification channel + startForeground zorunlu:

```smali
.class public Lcom/package/BgRecordService;
.super Landroid/app/Service;
.source "BgRecordService"

.method public onCreate()V
    .locals 5
    invoke-super {p0}, Landroid/app/Service;->onCreate()V
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I
    const/16 v1, 0x1a
    if-lt v0, v1, :cond_0
    const-string v0, "bg_channel"
    const-string v1, "Recording"
    const/4 v2, 0x2
    new-instance v3, Landroid/app/NotificationChannel;
    invoke-direct {v3, v0, v1, v2}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V
    const-class v1, Landroid/app/NotificationManager;
    invoke-virtual {p0, v1}, Lcom/package/BgRecordService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Landroid/app/NotificationManager;
    invoke-virtual {v1, v3}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V
    :cond_0
    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 3
    invoke-virtual {p0}, Lcom/package/BgRecordService;->getApplicationContext()Landroid/content/Context;
    move-result-object v0
    new-instance v1, Landroid/app/Notification$Builder;
    const-string v2, "bg_channel"
    invoke-direct {v1, v0, v2}, Landroid/app/Notification$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V
    const v2, 0x7f080689
    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setSmallIcon(I)Landroid/app/Notification$Builder;
    const-string v2, "App Name"
    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;
    const-string v2, "Recording active"
    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setContentText(Ljava/lang/CharSequence;)Landroid/app/Notification$Builder;
    const/4 v2, 0x1
    invoke-virtual {v1, v2}, Landroid/app/Notification$Builder;->setOngoing(Z)Landroid/app/Notification$Builder;
    invoke-virtual {v1}, Landroid/app/Notification$Builder;->build()Landroid/app/Notification;
    move-result-object v1
    const/16 v2, 0x3e8
    invoke-virtual {p0, v2, v1}, Lcom/package/BgRecordService;->startForeground(ILandroid/app/Notification;)V
    const/4 v0, 0x1
    return v0
.end method
```

İcon ID: `grep "icon\\|logo" _work/res/values/public.xml` ile bul → `const v2, 0x7f08XXXX`.

Application.onCreate()'a enjeksiyonda `startForegroundService()` kullan (startService değil) — manifest'te foregroundServiceType varsa startService crash üretebilir. Dönüş tipi void olduğu için smali'de `move-result` kullanma.

**OnCreate'e enjeksiyon:**

Application subclass'ının onCreate'ini bul (`.method public final onCreate()V` ara, invoke-super'dan sonra ekle):

```smali
    new-instance v1, Landroid/content/Intent;
    const-class v0, Lcom/package/KeepAliveService;
    invoke-direct {v1, p0, v0}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {p0, v1}, Lcom/package/ApplicationClass;->startForegroundService(Landroid/content/Intent;)V
```

**ÖNEMLİ:** `startForegroundService` void döner — smali'de `move-result` kullanma. Manifest'te `foregroundServiceType` tanımlı service'ler için `startService()` yerine `startForegroundService()` zorunludur. Aksi halde `RuntimeException: Context.startForegroundService()` hata alınır.

**.locals kontrolü:** Enjeksiyon yaptığın metodda `.locals X` varsa, kullandığın register sayısını karşıla. X >= kullandığın en yüksek register+1 olmalı. Yoksa local sayısını artır.

**GATE 2S:** Yeni smali dosyası _work/smali/**/ altında mı? `find _work/smali -name "*.smali" | wc -l` arttı mı?

---

### Adım 3 — REBUILD

```bash
$APKTOOL b -o _build_unsigned.apk _work/
```

**GATE 3:**
```bash
[ -f _build_unsigned.apk ] && echo "APK_OLUSTU: $(stat -c%s _build_unsigned.apk) bytes" || (echo "REBUILD_FAILED"; exit 1)
```

Hata varsa apktool log'unu oku:
- `brut.androlib.AndrolibException` → genelde kaynak XML hatası
- `Resource ID 0x7f0xxxxx not found` → eksik resource
- `Unknown resource type` → public.xml bozulmuş

**Hata varsa DUR.** Aynı hatayı 3 kez fix'lemeden dene — başarısızsa farklı strateji (binary-level patch, Bölüm 13).

---

### Adım 4 — ZIPALIGN (Atlanamaz)

```bash
"$ZIPALIGN" -p 4 _build_unsigned.apk _build_aligned.apk
```

**GATE 4:**
```bash
"$ZIPALIGN" -c 4 _build_aligned.apk