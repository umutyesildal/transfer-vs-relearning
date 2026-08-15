# Document 151ba — Bounded vngrs Metadata/Footer Redirect Revised-Base Execution Result (TR)

**Tarih:** 2026-08-10  
**Çalışma birimi:** LUNA-Worker 2  
**Sonuç:** `BLOCKED` — corrected mandatory preflight tamamlanamadı  
**Kapsam:** yalnızca tek, bounded 151an/151at metadata/footer-feasibility wave’i

## 1. Yetki ve değişmez kayıtlar

Bu belge, kullanıcının revised-base üzerinden verdiği tek execution yetkisi kapsamında
oluşturuldu. Documents 151ay ve 151az değiştirilmedi. 151an, 151at ve 151ax frozen
kuralları korunmuştur. Wave corpus row/full-shard indirmedi; sample calibration,
materialization, scoring, evaluation, model/tokenizer erişimi, GPU/Slurm, training,
cleanup veya Documents 153–154 işlemi yapmadı.

## 2. Publication ve local ancestry guard

- Canlı başlangıç remote base: `2ff1cacdffd55820fdf9a8f633c2bc20bffac807`.
- `merge-base(local HEAD, origin/corpus-update)`: `2ff1cacdffd55820fdf9a8f633c2bc20bffac807`.
- Remote ahead: `0`; local ahead: `2`; force push gerekmiyordu.
- Yalnızca `6ff9ceb13bbf2b9a4de19ba1db7788f11d239570` ve
  `92460a00ec136dd885b4940184bee9d954da9106` zincirinin sonu ordinary non-force push ile
  yayınlandı: `2ff1cac...92460a0`.
- Remote sonrası hedef commit: `92460a00ec136dd885b4940184bee9d954da9106`.
- Başka commit yayınlanmadı; force push, amend ve rebase yapılmadı.

## 3. HU preservation-checked synchronization

HU checkout yolu `/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning` olarak korundu.

Merge öncesi HU HEAD:
`2ff1cacdffd55820fdf9a8f633c2bc20bffac807`.

Bu HEAD, hedef `92460a00ec136dd885b4940184bee9d954da9106` commit’inin ancestor’ıydı.
Canonical status blob `git status --porcelain=v2` (NUL’suz form) için:

| Kontrol | Merge öncesi | Merge sonrası |
|---|---:|---:|
| status entry | 42 | 42 |
| tracked `.D` | 39 | 39 |
| untracked | 3 | 3 |
| status byte sayısı | 6,989 | 6,989 |
| status SHA-256 | `71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9` | aynı |

Incoming path seti HU HEAD’e göre iki path içeriyordu:

```text
src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
tests/test_vngrs_preparation.py
```

42 dirty entry ile overlap `0` oldu. Yalnız `origin corpus-update` fetch edildi ve tam
olarak bir `git merge --ff-only origin/corpus-update` çalıştırıldı. HU final HEAD:
`92460a00ec136dd885b4940184bee9d954da9106`. Dirty/untracked owner state byte-for-byte
değişmeden korundu.

## 4. Corrected 151ax preflight

Target root:
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`.

Preflight, source/footer erişiminden önce çalıştırıldı. Primary exact-byte command:

```text
du -x -B1 -s /vol/fob-vol6/mi25/yesildau
```

Frozen bound `120 s` idi. Bu preflight çağrısında command timeout oldu; `returncode=null`,
stdout `0` bytes, stderr `0` bytes ve parse edilebilir home-usage değeri yoktu. Human-readable
diagnostic `du -xsh /vol/fob-vol6/mi25/yesildau` da `30 s` bound içinde tamamlanamadı;
`returncode=null`, stdout `0` bytes, stderr `0` bytes.

Bu nedenle home usage’ın o anda canlı olarak `<30 GiB` olduğu kanıtlanamadı ve 151ax gereği
preflight fail-closed `BLOCKED` oldu. `df -h`, `df -i`, scratch path resolution, root absence
ve HU-home write prohibition kontrolleri başarılıydı. Root execution öncesinde yoktu ve
preflight nedeniyle oluşturulmadı.

Bazı bounded kontroller yine kanıtlandı:

- `df -h`: HU filesystem `1.3T/669G/608G/53%`; `/vol/tmp` `140T/122T/18T/88%`;
  `/vol/tmp2` `140T/27T/113T/19%`.
- `df -i`: HU `53%`, `/vol/tmp` `3%`, `/vol/tmp2` `3%` inode kullanımı.
- `>500 MiB` regular-file manifest: `PASS`, 5 dosya; manifest SHA-256
  `02ecc5c4c95191e91e531b3bba22e195a57c7783b1036b9a657b1b32dc2f2e59`.
- Root altında HU-home write izni: `false`; output root absence: `PASS`.

## 5. Execution ve post-run audit

Preflight failure nedeniyle:

- independent PyArrow writer/parser self-check: `NOT_RUN_PRE_FLIGHT_BLOCKED`;
- executor invocations: `0`;
- logical requests / physical hops / retries: `0 / 0 / 0`;
- response bytes: `0`;
- output files/inodes: `0`;
- source/footer HTTP erişimi: `0`;
- output root: absent, `0` files, `0` bytes.

Zorunlu post-run storage audit yine çalıştırıldı. Hiçbir source sonucu olmadığı için yalnız
storage/path/inode ve reconciliation kapsamındadır. Audit tamamlandı ve `PASS` verdi:

- exact-byte post-run `du`: `14689083392` bytes, command return `0`;
- post-run `du -xsh`: `14G`, command return `0`;
- large-home-file before/after manifest: aynı SHA-256,
  `02ecc5c4c95191e91e531b3bba22e195a57c7783b1036b9a657b1b32dc2f2e59`;
- added/removed/changed büyük home dosyası: yok;
- root inventory: `0` files / `0` bytes;
- post-run path, `df -h`, `df -i` ve write-policy kontrolleri: `PASS`.

Post-run audit’in PASS olması başlangıç preflight timeout’unu geriye dönük olarak geçerli
kılmaz. Top-level sonuç bu nedenle `BLOCKED`, phase `preflight`, source-stage status
`NOT_REACHED` olarak korunmuştur.

## 6. Gate sonucu

- 151an/151at route/footer execution: `NOT_EXECUTED`.
- Operational gate: `blocked_by_operational_access` — corrected exact-byte preflight bounded
  timeout verdi; source access’e geçilmedi.
- Global gate: `blocked_by_measurement_design`.
- `ready_to_measure`: `false`.
- `ready_to_train`: `false`.
- Bu belge corpus seçimi, kalite geçişi, scientific measurement completion veya training
  yetkisi vermez.

## 7. Preservation and exclusions

151ay ve 151az unchanged kaldı. HU’daki mevcut 39 tracked `.D` ve 3 untracked owner entry
değiştirilmedi; hiçbir restore, reset, checkout, stash, clean, deletion veya overwrite
yapılmadı. İkinci executor invocation, retry wave, corpus/full-shard/row erişimi,
calibration/materialization, model/tokenizer indirme, scoring/evaluation, GPU/Slurm,
training ve Documents 153–154 işlemleri yapılmadı.

## 8. Append-only post-wave remote observation

Wave’in yetkilendirilmiş publication adımı tamamlandıktan sonra local branch ve
`origin/corpus-update` read-only kontrolde `210e47256a499d098da9879d7ade990527cdbe35`
commit’ine ilerlemiş olarak gözlendi. Bu commit wave’in yetkilendirilmiş push zincirinin
parçası değildi; LUNA-Worker 2 tarafından push edilmedi, wave sırasında yalnızca
`2ff1cac...92460a0` ordinary non-force yayını gerçekleştirildi. Bu yeni remote hareketi
üzerine ek push, fetch, merge veya HU işlemi yapılmadı. 151ba’nın bu gözlem öncesi SHA-256’sı
`8b1a7349a3177291e6ba37d41fc97aea4cd2227c33501d68afab9ade6e39b940` idi.
