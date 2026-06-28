---
title: Kanban ile Görev Yönetimi
description: ReYMeN Kanban tahtasını kullanarak görev takibi
tags: [kanban, gorev, planlama, takip]
---

## Görev ekle
KANBAN_EKLE "Proje raporu hazırla" "Müşteri için Q3 raporu" 2

## Görevleri listele
KANBAN_LISTE

## Görevi tamamlandı olarak işaretle
KANBAN_TAMAMLA "1"

## Durumu güncelle
KANBAN_GUNCELLE "1" "running"

## Özet al
KANBAN_OZET

## Çoklu görev ekleme iş akışı
1. KANBAN_EKLE her alt görev için
2. KANBAN_OZET ile ilerlemeyi kontrol et
3. Her tamamlananda KANBAN_TAMAMLA çağır
