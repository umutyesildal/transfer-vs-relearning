# Document 151bc — Prewarmed HU-Only 151an/151at Retry Result (TR)

**Tarih:** 2026-08-10  
**Sonuç:** `BLOCKED` — HU read-only connectivity/prewarm evidence tamamlanamadı  
**Kapsam:** yalnızca tek HU-only bounded retry; source erişimi başlamadı

## 1. Yetki ve korunan sınırlar

Bu belge, kullanıcının push/fetch/merge yapmadan, HU checkout’unu
`92460a00ec136dd885b4940184bee9d954da9106` commit’inde tutarak verdiği tek retry yetkisi
kapsamında oluşturuldu. 151ba ve 151bb değiştirilmedi. `210e47256a499d098da9879d7ade990527cdbe35`
bu wave’in dışında bırakıldı; HU’yu o commit’e ilerletmek için hiçbir işlem yapılmadı.

No push, fetch, merge, reset, checkout, cleanup, deletion veya HU-home write yapıldı. Corpus
row/full-shard erişimi, sample calibration/materialization, model/tokenizer indirme,
scoring/evaluation, GPU/Slurm, training ve Documents 153–154 işlemleri yapılmadı.

## 2. HU precondition doğrulaması

Retry’ın ilk birleşik prewarm komutu HU üzerinde HEAD, canonical status, root absence, bounded
large-file manifest ve exact-byte `du` kontrollerini çalıştırmak üzere başlatıldı; ancak SSH
helper yalnız `spawn ssh ...` çıktısı verdi ve remote JSON sonucu dönmedi. Bu nedenle aşağıdaki
değerler bu retry için yeniden doğrulanmış sayılmamıştır:

| Alan | Beklenen/son korunmuş kayıt | Bu retry doğrulaması |
|---|---|---|
| HU HEAD | `92460a00ec136dd885b4940184bee9d954da9106` | `NOT_OBTAINED` |
| status entries | 42 | `NOT_OBTAINED` |
| tracked `.D` | 39 | `NOT_OBTAINED` |
| untracked | 3 | `NOT_OBTAINED` |
| status bytes | 6,989 | `NOT_OBTAINED` |
| status SHA-256 | `71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9` | `NOT_OBTAINED` |
| frozen root | absent in last accepted 151ba record | current absence `NOT_OBTAINED` |

Önceki kayıtlar beklenen commit ve dirty-state’i gösterse de bu retry’ın canlı precondition
kanıtı yerine geçirilmedi.

## 3. Prewarming sonucu

### 3.1 Bounded SSH/read-only connectivity evidence

Kısa read-only probe:

```text
./scripts/hu_ssh_expect "printf HU_READONLY_OK"
```

Bu helper, dışarıdan 30 saniyelik bounded wrapper ile çalıştırıldı. Sonuç:

```text
timed_out=true
returncode=null
duration_seconds=30.004
stdout_bytes=226
stderr_bytes=0
remote_result=absent
```

stdout yalnızca SSH `spawn` satırını içeriyordu; `HU_READONLY_OK` dönmedi.

### 3.2 Large-file manifest priming

İstenen command şu kimlikle başlatıldı:

```text
find /vol/fob-vol6/mi25/yesildau -xdev -type f -size +500M -printf '%s %p\n'
```

Bound `120 s` idi. Remote JSON sonucu alınamadığı için command exit code’u, gerçek çalışma
süresi, parse sonucu, dosya sayısı ve canonical manifest SHA-256 elde edilemedi:

```text
status=NOT_OBTAINED
parse=NOT_OBTAINED
manifest_sha256=NOT_OBTAINED
```

HU home’a manifest veya başka çıktı yazılmadı. Önceki kabul edilmiş beş dosyalı manifest SHA’sı
`02ecc5c4c95191e91e531b3bba22e195a57c7783b1036b9a657b1b32dc2f2e59` bu canlı priming’in
yerine kullanılmadı.

### 3.3 Exact-byte diagnostic priming

İstenen command şu kimlikle aynı prewarm akışında başlatıldı:

```text
du -x -B1 -s /vol/fob-vol6/mi25/yesildau
```

Bound `120 s` idi. Remote JSON dönmediği için exit code, command duration, stdout/stderr byte
sayısı, parse edilmiş byte değeri ve `<30 GiB` sonucu elde edilemedi:

```text
status=NOT_OBTAINED
parsed_home_usage_bytes=NOT_OBTAINED
below_30_GiB=NOT_OBTAINED
```

Bu nedenle priming PASS olarak kabul edilmedi ve fail-closed duruldu.

## 4. Execution gate ve post-run audit

Priming kanıtı tamamlanmadığından:

- internal 151ax preflight: `NOT_RUN`;
- independent PyArrow writer/parser self-check: `NOT_RUN`;
- executor invocation count: `0`;
- source-stage status: `NOT_REACHED`;
- logical requests / HTTP hops / redirects / retries: `0 / 0 / 0 / 0`;
- response bytes: `0`;
- artifact/file/inode counts: `0 / 0 / 0` yeni artifact kanıtı; root inventory doğrulanamadı;
- source/footer HTTP: `0`.

Mandatory post-run audit için HU üzerinde read-only audit çağrısı da bounded wrapper ile
denendi. Remote audit sonucu dönmeden wrapper timeout oldu:

```text
timed_out=true
returncode=null
duration_seconds=30.005
stdout_bytes=680
stderr_bytes=0
remote_audit_result=absent
```

Bu nedenle post-run storage audit status’u `INCOMPLETE / NOT_OBTAINED` olarak kaydedildi; PASS
veya BLOCKED şeklinde uydurulmadı. Top-level karar:

```text
status = BLOCKED
phase = hu_read_only_connectivity_and_prewarm
source_stage_status = NOT_REACHED
post_run_storage_audit.status = INCOMPLETE
```

## 5. Gate ve sonraki yetki

- Operational gate: `blocked_by_operational_access`.
- Global gate: `blocked_by_measurement_design`.
- `ready_to_measure`: `false`.
- `ready_to_train`: `false`.
- 151an/151at route feasibility execution sonucu üretilmedi.
- Yeni retry otomatik olarak yetkilendirilmedi; sonraki yetki öncelikle bounded HU bağlantısı,
  canlı HEAD/status/root kanıtı ve iki priming sonucunun alınmasını gerektirir.

No scientific/source result was fabricated. Documents 151ba and 151bb ile önceki result/gate
belgeleri korunmuştur.
