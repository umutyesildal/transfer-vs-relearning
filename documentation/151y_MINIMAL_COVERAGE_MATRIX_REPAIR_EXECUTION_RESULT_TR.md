# Document 151y — MINIMAL COVERAGE-MATRIX REPAIR EXECUTION RESULT (TR)

**Tarih:** 2026-08-08 (Europe/Berlin)  
**Contract:** Document 151x — `EXECUTED_ONCE`  
**Execution sonucu:** `BLOCKED`  
**Global gate:** `blocked_by_measurement_design`  
**`ready_to_train`:** `false`

## 1. Kapsam ve yetki

Bu belge, corrected frozen Document 151x’in kullanıcı tarafından açıkça yetkilendirilen tam
olarak bir bounded execution’ının sonucudur. Contract SHA-256’sı execution öncesinde
`9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b` olarak doğrulandı.

Execution yalnızca immutable HU girdilerinin source-read-only okunmasını ve yeni
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1` root’u altında
frozen dokuz çıktının oluşturulmasını kullandı. Public HTTP/network, scoring, inference,
weights/tokenizers, corpus materialization, GPU/Slurm, training, cleanup veya deletion
yapılmadı. Önceki evidence root’larına yazılmadı; eksik evidence backfill edilmedi.

## 2. HU preflight ve immutable-input reconciliation

Zorunlu storage/path/inode preflight, yeni root’un execution öncesinde mevcut olmadığının
kontrolü ve iki eski root’un read-only reconciliation’ı tamamlandı.

| Kontrol | Sonuç |
|---|---|
| HU home (`/vol/fob-vol6/mi25/yesildau`) | `14G`; inode kullanımı `%53` |
| `/vol/tmp` | `140T` toplam, `122T` kullanılan, `18T` boş; inode `%3` |
| `/vol/tmp2` | `140T` toplam, `27T` kullanılan, `113T` boş; inode `%3` |
| İlk execution root | 91 dosya, 13,063,617 byte; inventory SHA `4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad`; değişmedi |
| Retry root | 16 dosya, 38,315,850 byte; inventory SHA `8cd5d889b4875a95d54241d038dcb12e5cf4a22df9b6fd602823fb3473d2a13a`; değişmedi |
| Yeni repair root | preflight’ta yoktu; `/vol/tmp2/yesildau` altında oluşturuldu |

Immutable input hash ledger’ı aşağıdaki sekiz dosyayı kaydetti:

| Input | Byte | Satır/biçim | SHA-256 |
|---|---:|---:|---|
| `first-wave/registries/coverage_matrix.jsonl` | 55,436 | 132 | `77f1397f03ec3615af000b2917505a5d964ab817285678bbc920e1bb31ae80cc` |
| `first-wave/registries/benchmark_registry.jsonl` | 20,447 | 3 | `06f3f797014ba58382d94605303b42a449623ce22523155ac3ebcc038f989afd` |
| `first-wave/registries/source_model_registry.jsonl` | 5,262 | 3 | `ac98933957e9ec8595453413ebefda0c8409f5d0a0cd3f3e05cf24a581e745fc` |
| `retry/registries/retry_coverage_matrix.jsonl` | 2,940 | 6 | `8787ad5df982c64383883e90a66c65aed15f10a5743e9df025f3b8daddefc951` |
| `retry/registries/retry_benchmark_registry.jsonl` | 3,018 | 3 | `7f7deb55e1340d175ed7cf25e4c16d9b5efd717a72815a9a72d39881f62a1eaa` |
| `retry/registries/retry_source_model_registry.jsonl` | 4,242 | 3 | `d311665829b223e344d69082c3dab4a5126bdaab0a4a8d314c655084cffeb610` |
| `retry/reconciliation/first_wave_reuse_ledger.jsonl` | 40,674 | 91 | `057e1c3d71939ea91ce49e5a2496885c981d1ffc1d2c6f91fb1e1e372787c01a` |
| `retry/reports/retry_registry_completion_report.json` | 8,544 | JSON object | `cdc7dfc04aa3898f155b0195e78291b9f28784496230247e70b3ad903c4ae261` |

Reuse ledger’daki 91 kayıt `read_only_reconciled` olarak işlendi; hiçbir input dosyası
repair root’una kopyalanmadı veya overwrite edilmedi.

## 3. Üretilen repair çıktıları

Contract’ın dokuz sıralı çıktısı yalnızca yeni repair root’u altında üretildi:

| Çıktı | Byte | SHA-256 |
|---|---:|---|
| `input_manifest.json` | 5,665 | `5aa88c03f939f948b1a3769b0efa269fabe0e3dd70aac1c513be63e16b2bbfd1` |
| `input_hash_ledger.jsonl` | 2,835 | `26b9527ae658283b52602cf82c5257141a8c909dd7cf2baf87a6c2cabff7c12e` |
| `coverage_repair_field_matrix.jsonl` | 114,649 | `19c45daa9454d3c13bd55bc3cb3f0b00865b7ddd37b04ea16e9c87393168d29b` |
| `coverage_repair_benchmark_registry.jsonl` | 20,091 | `22ca0fbd1581637a5d9b5590f5ec3763d5603bbb1923d128e245cc640929b04c` |
| `coverage_repair_source_model_registry.jsonl` | 5,307 | `4711d12d2e54d3b795b9e006d16d14a49d4d769f637ef5ec44949167f908d638` |
| `coverage_repair_reconciliation.jsonl` | 47,120 | `f94057d0fb7d8fdd81faa6dee9db6f490ecfd0ad2d2e33bd8b91bebd48dbc60f` |
| `coverage_repair_report.json` | 3,382 | `c70fbbfc6afc1639025a6ec7bbe4fd620cd606af87e5714e805df06385704f1b` |
| `output_artifact_manifest.jsonl` | 1,311 | `dee64588a922cd9be35e5710c00c837616e12aafea11f29bfaa4b9f8b131cdc2` |
| `post_repair_storage_audit.json` | 3,633 | `a61520578cafb290618d521c04d8d211d06afdc559ca250e433e5b7636ec8812` |

Repair root post-run toplamı **9 dosya / 203,993 byte** olup inventory SHA-256’sı
`7bce6b0d70c8069595d9c8ca96801b2eca1faf5a31973b8741e176926ef26e82`’dir.

`output_artifact_manifest.jsonl` yalnızca kendisinden önceki sekiz çıktıyı listeler; kendisini
ve son yazılan `post_repair_storage_audit.json` dosyasını içermez. Manifest self-reference ve
final-audit self-reference yoktur. Final audit manifest’in path/byte/SHA bilgisini, son root
count/byte/inventory bilgisini ve immutable-root inventory kontrollerini kaydeder.

## 4. Coverage ve registry sonucu

Field matrix contract’ın zorunlu cardinality’sini sağladı:

| Kapsam | Beklenen | Üretilen | Durum |
|---|---:|---:|---|
| Benchmark entity-field satırı | 3 × 27 = 81 | 81 | `PASS / schema-complete` |
| Model entity-field satırı | 3 × 23 = 69 | 69 | `PASS / schema-complete` |
| Toplam unique `(entity_id, field_name)` | 150 | 150 | `PASS` |
| Benchmark registry row | 3 | 3 | 27-field schema tamam |
| Source-model registry row | 3 | 3 | 23-field schema tamam |

Zorunlu matrix entity’leri tam olarak `benchmark.turblimp`, `benchmark.turkishmmlu`,
`benchmark.turkish_exams`, `model.olmo_2_0425_1b`, `model.falcon_rw_1b` ve
`model.qwen2_5_1_5b` oldu. CETVEL/TurkBench zorunlu matrix’e eklenmedi.

Coverage status dağılımı:

| Status | Satır |
|---|---:|
| `verified` | 96 |
| `not_reported` | 30 |
| `not_retrieved_in_this_wave` | 18 |
| `blocked` | 6 |
| **Toplam** | **150** |

Şema tamamlanmış olsa da required benchmark evidence ve source-model provenance’ın eksik
olduğu yerlerde status’ler truthful non-PASS bırakıldı. Eksik alanlar uydurulmadı; mevcut
raw model-card satırları complete provenance yerine kanıt olarak tutuldu ve model weights veya
snapshot erişimi yapılmadı.

## 5. Contract kararı

Karar **`BLOCKED`**’dır. Birincil blocker’lar:

- `blocked_by_benchmark_registry`: zorunlu benchmark registry alanları için evidence-complete
  ve contract’a göre doğrulanabilir kaynak kanıtı mevcut değil;
- `blocked_by_source_model_provenance`: üç model için gerekli provenance alanları mevcut
  immutable evidence ile tamamlanamıyor.

Bu nedenle schema-complete repair çıktısı, evidence-complete PASS anlamına gelmez. Global
`blocked_by_measurement_design` gate’i açık kalır; `ready_to_train=false` kalır. Bu execution
Documents 152–154’ü, training’i veya herhangi bir scoring/inference çalışmasını yetkilendirmez.

## 6. Kayıt statüsü

Bu belge 151x’in tek yetkili execution result’ıdır. Document 151z aşağıdaki post-repair gate’i
kaydeder. 151x yeniden çalıştırılamaz; yeni bir deneme için yeni/frozen contract ve ayrı açık
yetki gerekir.
