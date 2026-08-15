# Document 151ax — HU Storage Preflight Resilience Correction Contract (TR)

**Tarih:** 2026-08-09, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — LOCAL CONTRACT/CODE/TEST CORRECTION`  
**Kapsam:** yalnızca HU storage preflight ve post-run audit dayanıklılığı

## 1. Amaç ve yetki sınırı

Document 151au/151av wave'i source/footer erişimine başlamadan, yalnızca 30 saniyelik
`du -xsh` timeout'u nedeniyle fail-closed durmuştur. Bu belge, home kullanımını eski bir `14G`
sonucuyla ikame etmeden canlı ve bounded biçimde ölçmek için preflight/audit protokolünü düzeltir.

Bu belge çalıştırılmamıştır ve 151an/151at execution yetkisi vermez. HU/SSH, network, vngrs
source/footer erişimi, corpus-row veya full-shard indirme, sample calibration, materialization,
scoring, evaluation, model/tokenizer erişimi, GPU/Slurm, training, cleanup/deletion ve
Documents 151ay/151az/152--154 bu correction turn'ünün dışındadır.

```text
status                     = FROZEN — UNEXECUTED
execution_authorization   = not granted by this document
source_access              = forbidden
151an/151at execution      = forbidden
primary gate               = blocked_by_operational_access
global gate                = blocked_by_measurement_design
ready_to_measure           = false
ready_to_train             = false
```

## 2. Canlı home kullanımının exact-byte primary ölçümü

Eski raporlanmış `14G` değeri yalnızca tarihsel bağlamdır; canlı execution preflight'ının yerine
kullanılamaz. Primary kontrol her wave'in hemen öncesinde aşağıdaki exact-byte komutuyla yapılır:

```bash
du -x -B1 -s /vol/fob-vol6/mi25/yesildau
```

Bu komutun frozen bounded timeout'u **120 saniyedir**. Başarılı çıktı tam olarak tek bir satırda
unsigned decimal byte sayısı ve hedef path içermelidir; timeout, non-zero exit, boş/çok satırlı
çıktı veya exact-byte parse failure fail-closed `BLOCKED` üretir. Byte değeri
`30 * 1024^3` değerinden küçük olmalıdır; `>= 30 GiB` `BLOCKED`'dır.

Human-readable diagnostic ayrıca çalıştırılabilir:

```bash
du -xsh /vol/fob-vol6/mi25/yesildau
```

Bu diagnostic için bounded timeout 30 saniyedir. Ancak exact-byte kontrolü başarıyla tamamlanmış
ve exact değer 30 GiB altında ise, `du -xsh` timeout'u tek başına execution'ı BLOCKED yapmaz.
Human-readable command sonucu yine command, timeout, exit code, timeout flag, stdout byte ve
stderr byte kanıtıyla kaydedilir.

Preflight sonucu `home_usage_bytes` olarak yalnız exact-byte kontrolden gelen değeri kullanır;
human-readable `14G` veya başka bir eski/stale sonuç kullanılmaz.

## 3. Zorunlu filesystem, path ve yazma sınırları

Exact-byte kontrolüne ek olarak her future execution wave'inde aşağıdaki kontroller bounded ve
read-only olarak çalıştırılır:

```bash
df -h /vol/fob-vol6/mi25/yesildau /vol/tmp /vol/tmp2
df -i /vol/fob-vol6/mi25/yesildau /vol/tmp /vol/tmp2
readlink -f /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

`df -h`, `df -i` veya `readlink -f` timeout/non-zero/failure durumları fail-closed `BLOCKED`'dır.
Frozen output root execution başlamadan önce absent olmalıdır. HU home için açık yazma yasağı
uygulanır:

```text
HU home = /vol/fob-vol6/mi25/yesildau
home_write_allowed = false
new execution writes = only the explicitly frozen scratch root
prior evidence/report/cache/sample roots = immutable/read-only
```

Resolved output root HU home altında olamaz. Hiçbir preflight sonucu HU home'a yazılamaz; command
çıktıları memory'de tutulur veya yalnızca daha sonra yetkili scratch evidence'a alınır.

## 4. Bounded >500 MiB home-file audit

Preflight ve post-run audit bounded bir regular-file manifest üretir. Frozen command:

```bash
find /vol/fob-vol6/mi25/yesildau -xdev -type f -size +500M -printf '%s %p\\n'
```

Bu audit'in timeout'u **120 saniyedir**. Parser her satırı `{path, bytes}` olarak doğrular,
path'in HU home altında olduğunu, byte değerinin `500 * 1024^2` değerinden büyük olduğunu ve
duplicate path bulunmadığını kontrol eder. Sıralanmış manifest'in canonical JSON SHA-256'sı
raporlanır:

```text
large_home_file_audit.status = PASS | BLOCKED | INCOMPLETE
large_home_file_audit.threshold_bytes = 524288000
large_home_file_audit.manifest = [{path, bytes}, ...]
large_home_file_audit.manifest_sha256 = SHA256(canonical manifest bytes)
```

Timeout veya non-zero command sonucu `INCOMPLETE`/`BLOCKED`; parse failure veya inventory
reconciliation failure `INCOMPLETE` olarak kaydedilir ve execution preflight'ı complete sayılmaz.
Bu durumlar “home temiz” veya “0 büyük dosya” şeklinde yorumlanamaz.

Mümkün olduğunda post-run manifest, preflight manifest ile exact path/byte seti olarak karşılaştırılır:

```text
added_paths
removed_paths
changed_paths
before_manifest_sha256
after_manifest_sha256
reconciliation_status = PASS | BLOCKED | INCOMPLETE
```

Herhangi bir yeni/değişmiş >500 MiB home dosyası `BLOCKED`'dır. Pre veya post manifest mevcut
değilse reconciliation `INCOMPLETE` olur; bu, başarılı storage audit iddiasına dönüştürülemez.

## 5. 151an/151at bilimsel ve operasyonel sınırlarının korunması

Bu correction aşağıdaki frozen kimlik ve sınırları değiştirmez:

```text
repository          = vngrs-ai/vngrs-web-corpus
immutable_revision  = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
selected_shards     = exactly the frozen 151an 32-path set
route_kind          = parquet_footer_range
scratch_root        = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

151an'ın etkin bounded profile'ı `128` total HTTP attempts, `24` retries, `64 MiB` total
response, `4 MiB` single response, `7,200` saniye wall-clock, `128` regular files ve `128`
new inodes'tur. 151at'ın redirect overlay'i ayrıca en fazla `121` logical attempts, `242`
physical HTTP hops ve zero-or-one validated HTTPS 302 hop; yalnız official
`xethub.hf.co`/`cdn.hf.co` suffix'leri; secret-safe Location evidence; method/Range koruması
ve cross-host Authorization/Cookie stripping gerektirir. Redirect hop retry değildir.

Bu değerler 151ax tarafından yükseltilmez, gevşetilmez veya response-dependent hale getirilmez.
Yalnız compact metadata/footer/license evidence alınabilir; corpus rows, compressed row groups,
full shards, model weights/tokenizers ve training data bu wave'lerde yasaktır.

## 6. Fail-closed kararları

```text
PASS:
  exact-byte du başarılı ve <30 GiB;
  df -h/df -i/path/root kontrolleri başarılı;
  root execution öncesi absent;
  HU write prohibition geçerli;
  bounded large-file manifest ve mümkünse pre/post reconciliation PASS.

BLOCKED:
  exact-byte du timeout/parse failure/non-zero veya >=30 GiB;
  df/inode/path/root/write-policy failure;
  large-file command failure veya yeni/değişmiş büyük home dosyası;
  151an/151at route, byte, retry, file/inode veya source-identity ihlali.

INCOMPLETE:
  bounded large-file inventory veya pre/post reconciliation kanıtı tamamlanamıyor.
```

Human-readable `du -xsh` timeout'u yalnızca exact-byte kontrolü PASS ve home kullanımı 30 GiB
altında ise tek başına BLOCKED değildir. Diğer zorunlu kontrol failure'ları bu istisnadan
yararlanamaz.

## 7. Sonraki ayrı authorization

151ax'ın başarılı local correction sonucu yalnız preflight implementation'ını düzeltir; 151an
veya 151at çalıştırılmış sayılmaz. Sonraki ayrı yetki aşağıdaki zinciri açıkça kapsamalıdır:

1. yalnız bu dar correction commit'inin ordinary non-force push ile yayımlanması;
2. korunmuş HU dirty-state için yeniden 42-entry/status-digest/path-overlap doğrulaması;
3. yalnız preservation kontrolleri geçerse HU checkout'un `merge --ff-only` ile güncellenmesi;
4. corrected exact-byte primary, filesystem/path/root ve bounded large-file preflight'ının
   çalıştırılması;
5. preflight ve independent-writer self-check geçerse 151an/151at semantiğiyle tam olarak bir
   bounded execution;
6. post-run storage/path/inode audit ve yalnız yetkilendirilmiş result/gate belgeleri.

Bu zincir yeni bir explicit authorization olmadan çalıştırılamaz. Başarılı bir preflight veya
route wave'i corpus selection, sample calibration, measurement design completion,
`ready_to_measure` ya da `ready_to_train` anlamına gelmez.

## 8. Append-only final-audit binding clarification (2026-08-09)

Bu bölüm append-only bir fail-closed correction'dır; önceki frozen içerik değiştirilmemiştir.
Append öncesi Document 151ax SHA-256 değeri
`15bdc5a7ae0e0356254c5d5ffd5ad47b091f459a52689ce4c0cb1ecc9699ed22` olarak korunur.

### 8.1 Source-stage ve top-level status bağlama kuralı

Executor, source aşamasının ham/başarılı sonucunu `source_stage_result` altında aynen korur ve
`source_stage_status` alanını source aşamasının status değeriyle doldurur. Zorunlu post-run
storage audit tamamlanmadan top-level sonuç PASS olarak sonlandırılamaz. Top-level PASS için
gerekli ve yeterli koşul şudur:

```text
source_stage_status == PASS
AND post_run_storage_audit.status == PASS
```

Source aşaması PASS olduktan sonra post-run audit `BLOCKED` veya `INCOMPLETE` dönerse:

```text
top_level_status = BLOCKED
phase = post_run_storage_audit
source_stage_status = PASS
```

Bu durumda source aşamasının ürettiği kanıtlar ve source-stage payload silinmez, source aşaması
başarısızmış gibi yeniden etiketlenmez ve tam `post_run_storage_audit` sonucu top-level rapora
eklenir. Audit implementation'ının kendisi exception/timeout/parse eksikliğiyle sonuçlanırsa
bu sonuç `INCOMPLETE` olarak kanıtlanır ve top-level yine BLOCKED olur.

### 8.2 Post-run audit status ayrımı

`post_run_storage_audit.status` yalnızca şu kurallarla atanır:

```text
PASS:
  zorunlu home/capacity/inode/path kontrolleri ve pre/post large-file reconciliation PASS.

BLOCKED:
  home usage >= 30 GiB;
  yeni, silinmiş veya byte değeri değişmiş >500 MiB home regular file;
  açık filesystem/path/write-policy ihlali;
  kesin command failure olarak sınıflandırılmış non-zero sonuç.

INCOMPLETE:
  timeout;
  parse failure;
  eksik pre veya post large-file manifesti;
  pre/post reconciliation kanıtının tamamlanamaması.
```

Human-readable `du -xsh` diagnostic'inin timeout istisnası Bölüm 2'deki gibi korunur; exact-byte
primary kontrol başarılı ve 30 GiB altında olsa bile bu diagnostic timeout'u tek başına PASS
üretmez, yalnızca execution'ı tek başına BLOCKED da yapmaz. Bu clarification execution yetkisi
vermez; 151an/151at, HU/SSH, network, source/footer, corpus, scoring, evaluation, GPU/Slurm,
training ve Documents 151ay/151az/152--154 kapsam dışı kalır.
