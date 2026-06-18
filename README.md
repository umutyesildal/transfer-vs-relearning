# Synthetic Fact Generation Pipeline

This project contains a deterministic, template-based pipeline for generating synthetic training and probing data for a thesis on cross-lingual transfer in language models. The generator does not use an LLM.

## Input Format

The default input file is `data/canonical_subject_profiles_10.csv`. Each CSV row represents one synthetic subject profile with four facts:

- `profession`
- `born_in`
- `studied_at`
- `works_at`

Required columns:

- `row_id`
- `subject_id`
- `subject`
- `profession_en`, `profession_tr`
- `birthplace_en`, `birthplace_tr`
- `university_en`, `university_tr`
- `employer_en`, `employer_tr`
- `name_type`
- `name_rarity_bucket`
- `popularity_rank`
- `popularity_bucket`
- `profession_frequency_bucket`
- `birthplace_frequency_bucket`
- `university_frequency_bucket`
- `employer_frequency_bucket`
- `branch_group`

Example input row:

```csv
row_id,subject_id,subject,profession_en,profession_tr,birthplace_en,birthplace_tr,university_en,university_tr,employer_en,employer_tr,name_type,name_rarity_bucket,popularity_rank,popularity_bucket,profession_frequency_bucket,birthplace_frequency_bucket,university_frequency_bucket,employer_frequency_bucket,branch_group
R0001,S0001,Leran Dovik,football player,futbolcu,London,Londra,Westbridge University,Westbridge Üniversitesi,Westbridge FC,Westbridge FC,english_like,rare,1,high,high,medium,low,high,A
```

## Internal Expansion

Each subject profile expands into four internal fact records. `row_id` identifies the source row, while `fact_id` is generated from `subject_id` and relation.

For the example above, the generated facts are:

| fact_id | relation | object_en | object_tr | frequency_bucket |
|---|---|---|---|---|
| `S0001_profession` | `profession` | football player | futbolcu | high |
| `S0001_born_in` | `born_in` | London | Londra | medium |
| `S0001_studied_at` | `studied_at` | Westbridge University | Westbridge Üniversitesi | low |
| `S0001_works_at` | `works_at` | Westbridge FC | Westbridge FC | high |

## Experimental Logic

Branch assignment is subject-level:

- Branch A: all four facts appear in English training and are excluded from Turkish repetition.
- Branch B: all four facts appear in both English training and Turkish repetition.

Relation-level branch assignment is not used.

Frequency is relation-specific. The current exposure mapping is:

- `low`: 3 exposures
- `medium`: 8 exposures
- `high`: 15 exposures

Changing the profession frequency for a subject does not change the birthplace, university, or employer frequency for that subject.

The metadata columns `name_type`, `name_rarity_bucket`, `popularity_rank`, and `popularity_bucket` are preserved in all generated outputs.

## Templates

The generator supports four fixed relations:

- `profession`
- `born_in`
- `studied_at`
- `works_at`

Each relation has 10 English training templates, 10 Turkish repetition templates, and at least 3 probe templates per language. Templates use the fullname heuristic: every generated sentence and question includes the full subject name and avoids pronouns.

## Outputs

The pipeline writes four files to `output/`:

- `english_training.jsonl`: English training exposures for all facts.
- `turkish_repetition.jsonl`: Turkish repetition exposures for Branch B facts only.
- `probes_en.csv`: English probe questions for all facts.
- `probes_tr.csv`: Turkish probe questions for all facts.

Training and repetition records contain:

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

Probe files contain the same metadata, with `question` and `expected_answer` instead of `split`, `text`, and `answer`.

## Validation

The loader validates:

- required columns
- unique `row_id`
- unique `subject_id`
- unique full `subject`
- allowed categorical values
- non-empty English and Turkish object values
- valid relation-specific frequency values
- valid branch values

Shared object values across subjects are allowed.

## Running

Install dependencies:

```bash
pip install pandas
```

Run the full pipeline:

```bash
python3 main.py
```

Run tests:

```bash
python3 -m unittest discover -s tests
```
