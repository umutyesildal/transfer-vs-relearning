# Synthetic Fact Generation Pipeline

This project contains a deterministic, template-based pipeline for generating synthetic training and probing data for a thesis on cross-lingual transfer in language models. The generator does not use an LLM or internet lookup.

## Source Lists

Canonical subject profiles are generated from UTF-8 text files in `data/source_lists/`:

- `cities_en.txt`, `cities_tr.txt`
- `company_en.txt`, `company_tr.txt`
- `jobs_en.txt`, `jobs_tr.txt`
- `names_en.txt`, `names_tr.txt`
- `surnames_en.txt`, `surnames_tr.txt`
- `university_en.txt`, `university_tr.txt`

Each file has one item per line. Loading trims whitespace, ignores empty lines, and removes exact duplicate lines while preserving order. A cleaning report is written to `output/source_validation_report.json`.

Profession files use aligned English/Turkish rows in this format:

```text
Footballer — 100
Warehouse worker — 29
```

The separator may be `—`, `–`, or ` - `. Scores must be numeric integers from 0 to 100, and aligned English/Turkish scores must match.

Source-list order is treated as a frequency-rank proxy for names, cities, universities, and companies.

## Canonical Generation

Run:

```bash
python3 generate_canonical.py
```

This creates `data/canonical_subject_profiles_5000.csv` with exactly 5,000 one-row-per-subject profiles:

- 2,500 `english_like` subjects
- 2,500 `turkish_like` subjects
- 2,500 Branch A subjects
- 2,500 Branch B subjects

Use this end-to-end command to generate the canonical CSV, run the existing pipeline, and validate outputs:

```bash
python3 generate_canonical.py --run-pipeline
```

The canonical generation summary is written to `output/canonical_generation_summary.json`.

## Subject And Object Assignment

Names are generated without mixing language components:

- `english_like`: `names_en.txt` + `surnames_en.txt`
- `turkish_like`: `names_tr.txt` + `surnames_tr.txt`

Only single-component first names and surnames are used. Multi-component source entries are excluded, hyphenated single components are preserved, and generated subjects are natural-cased two-part names.

Name rarity uses first-name and surname source ranks:

- `common`: both components mainly from the first third
- `medium`: middle-third names or common/rare mixes
- `rare`: at least one final-third component with high combined rarity

The target rarity distribution is 40% common, 35% medium, and 25% rare within each name type.

Professions are assigned coverage-first, then with deterministic weighted sampling based on profession popularity score. Subject popularity uses:

```text
fame_score = 0.75 * profession_popularity_score + 0.25 * deterministic_random_score
```

Subjects are ranked by fame score. Popularity buckets are fixed:

- top 10%: `high`
- next 30%: `medium`
- bottom 60%: `low`

Cities, universities, and companies are assigned through six deterministic profile patterns:

- English-region domestic: English birthplace, residence, university, and employer
- Turkish-region domestic: Turkish birthplace, residence, university, and employer
- English-region study in Turkish region
- Turkish-region study in English region
- English-region work in Turkish region
- Turkish-region work in English region

The target distribution is 35%, 35%, 7.5%, 7.5%, 7.5%, and 7.5%. Pattern assignment is stratified across `name_type`, Branch A/B, popularity bucket, and name rarity so name language does not determine biography region. Residence follows the current employer region. Object sampling within the required regional pool uses coverage first, then inverse-square-root-rank weighting.

`born_in` and `lives_in` share the same city vocabulary from `cities_en.txt` and `cities_tr.txt`. Each subject receives different birthplace and residence values, compared by normalized city identity, so the dataset can test relation-specific knowledge rather than only subject-city association. Example:

```text
Leran Dovik -> born_in -> Bristol
Leran Dovik -> lives_in -> Manchester
```

Proper-name pairs are built safely:

- English-origin object: `object_en = object_tr = original item`
- Turkish-origin object: `object_tr = original item`, `object_en = Turkish-character-normalized item`

No organization, city, or university names are translated or invented.

## Compatibility And Frequencies

Employer assignment uses a small keyword-based profession/employer compatibility layer within the employer region required by the profile pattern. It tries direct category matches, university employers for academic/research professions, general employers, broad compatible categories, and only then final fallback. The summary reports compatibility matches, general-employer fallback, and final fallback separately.

The exposure mapping is unchanged:

- `low`: 3 exposures
- `medium`: 8 exposures
- `high`: 15 exposures

Relation-specific frequency rules:

- `profession`: subject popularity bucket
- `works_at`: subject popularity bucket, lowered one level if employer fallback was required
- `born_in`: subject popularity bucket lowered one level
- `lives_in`: same frequency bucket as `born_in`
- `studied_at`: subject popularity bucket lowered one level, except education professions keep the base bucket

Branch assignment remains subject-level. Branch A facts appear only in English training; Branch B facts appear in English training and Turkish repetition.

## Canonical CSV Schema

`data/canonical_subject_profiles_5000.csv` uses exactly these columns:

- `row_id`
- `subject_id`
- `subject`
- `profession_en`, `profession_tr`
- `birthplace_en`, `birthplace_tr`
- `residence_en`, `residence_tr`
- `university_en`, `university_tr`
- `employer_en`, `employer_tr`
- `name_type`
- `name_rarity_bucket`
- `popularity_rank`
- `popularity_bucket`
- `profession_frequency_bucket`
- `birthplace_frequency_bucket`
- `residence_frequency_bucket`
- `university_frequency_bucket`
- `employer_frequency_bucket`
- `branch_group`

Each subject expands into five internal facts:

- `profession`
- `born_in`
- `lives_in`
- `studied_at`
- `works_at`

For example, `S00001` expands to:

- `S00001_profession`
- `S00001_born_in`
- `S00001_lives_in`
- `S00001_studied_at`
- `S00001_works_at`

The full canonical dataset expands to 25,000 facts.

## Pipeline Outputs

Run the existing pipeline:

```bash
python3 main.py
```

It reads `data/canonical_subject_profiles_5000.csv` and writes:

- `output/english_training.jsonl`
- `output/turkish_repetition.jsonl`
- `output/probes_en.csv`
- `output/probes_tr.csv`

Training and repetition rows contain:

- `fact_id`
- `row_id`
- `subject_id`
- `language`
- `split`
- `text`
- `relation`
- `subject`
- `answer`
- `name_type`
- `name_rarity_bucket`
- `popularity_rank`
- `popularity_bucket`
- `frequency_bucket`
- `branch_group`
- `template_id`

Probe files contain the same metadata with `question` and `expected_answer`.

## Validation

The canonical stage validates source files, profession alignment, exact 5,000-row canonical shape, unique IDs and names, exact popularity and branch distributions, valid categorical values, non-empty objects, and frequency values.

The pipeline validation checks that every subject expands into five facts, every fact appears in English training, only Branch B facts appear in Turkish repetition, every fact has one probe per language, metadata is consistent, `born_in` and `lives_in` remain distinct with matched frequencies, and row totals match frequency-derived expectations.

Run tests:

```bash
python3 -m unittest discover -s tests
```
