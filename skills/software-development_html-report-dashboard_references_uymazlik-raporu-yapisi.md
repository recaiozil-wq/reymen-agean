---
name: software-development_html-report-dashboard_references_uymazlik-raporu-yapisi
description: UYMAZLIK Durum Raporu — Dosya Yapısı
title: "Software Development Html Report Dashboard References Uymazlik Raporu Yapisi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | UYMAZLIK Durum Raporu — Dosya Yapısı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# UYMAZLIK Durum Raporu — Dosya Yapısı

## COLS Tanım Merkezi (Sütun Eşleştirmeleri)
`COLS` objesi tüm sütun adlarını tek bir yerde tanımlar. Başlık değişirse sadece COLS güncellenir.

```javascript
var COLS = {
  YIL:       'YIL',
  URETIM:    'ÜRETİM YERİ YURT DIŞI YURT İÇİ',
  IMALAT:    'İMALAT YERİ 2.HBFM',
  ONARIM:    'ONARIM YERİ 2.HBFM',
  INCELEME:  'İNCELEME MERKEZİ',
  DURUM:     'DURUMU IDE (Inc. Devam Ediyor) G/F (İncelendi, Gayri Faal) F (İncelendi, Faal) INCM (İncelenemez) IPT (İptal)',
  SONUC:     'SONUÇ A(AÇIK)/K(KAPALI)',
  UCAK:      'UÇAK OLAYI E(EVET)-/- H(HAYIR)',
  KARKUR:    'KAR/KUR',
  BIRLIK:    'BİRLİK',
  SISTEM:    'SİSTEM',
  ANASISTEM: 'ANA SİLAH SİSTEMİ',
  UNITE:     'ÜNİTE/TEÇHİZAT ADI',
  HATA:      'HATA SEBEP KODU',
  COST:      'INC. MALİYETİS',
  INC_SURE:  'INC. SÜR.',
  MLZ_SURE:  'MLZ. GELİŞ SÜRESİ',
  GEN_SURE:  'GENEL TOP. SÜRE',
  ONL_ADET:  'ÖNL TEDBİR ADEDİ',
  ONCEAN:    'ÖNC.A/N',
};
```

## Kategori Fonksiyonları

### İNCELEME MERKEZİ bazlı (pasta grafikle tutarlı)
```javascript
function incKat(r){
  var v = String(r[COLS.INCELEME]||'').trim().toLocaleUpperCase('tr-TR');
  if(v.includes('HBF')) return 'hbf';
  if(v.includes('DIŞ')||v.includes('DIS')) return 'yd';
  if(v && v!=='-') return 'yi';
  return '';
}
```

### İMALAT/ONARIM bazlı (ESKİ — kullanma)
```javascript
function isHBF2(r) {
  return String(r[COLS.IMALAT]||'').trim()==='2.HBFM'
      || String(r[COLS.ONARIM]||'').trim()==='2.HBFM';
}
```

## Grafik Oluşturma

- `mkBar(id, data, opts)` — Bar grafik (yatay/dikey)
- `mkPie(id, data, isDoughnut)` — Pasta/halka grafik
- `mkLine(id, data)` — Çizgi grafik (aslında bar olarak render edilir)

Tüm grafik fonksiyonları `charts` objesini kullanır ve önce eski chart'ı `destroyChart(id)` ile temizler.

## Dosya Yükleme Mantığı

1. Kullanıcı XLSX/XLS/CSV seçer
2. `XLSX.read()` ile workbook okunur
3. `UR Takip` sayfası aranır (yoksa ilk sayfa)
4. Başlıklar `trim()` ile normalize edilir
5. Dosya adının ilk 4 karakteri yıl anahtarı olarak alınır
6. En fazla 2 dosya karşılaştırılır (en güncel 2 yıl)
7. `onAllLoaded()` tüm grafikleri ve yorumu günceller

## Lexical/İmla Notları

- `2\'nci` — JS string içinde `2'nci` anlamına gelir (concatenation ile)
- `2\'nci` YAZMA: patch aracı bunu `2\\'nci` yapabilir → syntax hatası
- Düzeltmek için binary replace: `b"2\\\\'nci"` → `b"2\\'nci"`
