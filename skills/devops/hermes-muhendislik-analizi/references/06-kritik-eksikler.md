---
skill_id: 84e81c38d833
usage_count: 1
last_used: 2026-06-16
---
# Bölüm 6: Kritik Eksikler

## "Yazıldı Ama Kullanılmıyor" Modüller

| Modül | Sorun | Etki |
|---|---|---|
| PriorityTaskQueue | Daemon ThreadPoolExecutor kullanıyor, bu sınıf bağlı değil | #oncelik-yuksek etiketinin etkisi yok |
| TaskStateMachine | __init__'de tanımlı ama _process_job'da çağrılmıyor | Çökme sonrası görevler kurtarılamıyor |
| SpacedRepetition | _post_skill_hooks'ta register() çağrılmıyor | Aralıklı tekrar sistemi hiç çalışmıyor |

## Veri Tutarsızlıkları

- Çift vektör deposu: _vectors.json + ChromaDB hermes_vault paralel ama senkronize değil
- Tag sorgulama O(N): ChromaDB WHERE filtresi çalışmıyor (tags CSV string)
- GraphMemory RAG'a entegre değil: 2-hop kavram komşuları kullanılmıyor

## Güvenlik Açığı

GitHelper.push(): Token URL'e gömülüyor https://x-access-token:{token}@github.com/...
Çözüm: GIT_ASKPASS veya git credential-helper

## Öncelik Sırası

ÖNCELİK 1 — Hemen Düzeltilmeli:
- hermes_v7.py -> _post_skill_hooks() içine: self.spaced_rep.register(skill_name)
- hermes_v7.py -> _process_job() içine: self.state_machine.transition(task_id, RUNNING)

ÖNCELİK 2 — PriorityTaskQueue Entegrasyonu:
- _submit_job(): priority = 0 if "#oncelik-yuksek" in tags else 5
