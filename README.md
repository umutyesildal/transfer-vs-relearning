# Synthetic Fact Generation Pipeline

This project contains a deterministic, template-based pipeline for generating synthetic training and evaluation data for a thesis on cross-lingual transfer in language models. The goal is to create a controlled dataset to study how facts learned in English are represented and accessed in Turkish.

## Project Goal

The pipeline takes a canonical fact table as input and generates four distinct datasets:
1.  **English-side training data**: Sentences that teach facts in English.
2.  **Turkish-side repetition data**: Sentences that repeat a subset of facts in Turkish.
3.  **English probing questions**: Questions to test the model's knowledge of the facts in English.
4.  **Turkish probing questions**: Questions to test the model's knowledge of the facts in Turkish.

The generation process is **fully heuristic and does not use an LLM**, ensuring deterministic and easily debuggable outputs.

## How to Run the Pipeline

### 1. Prerequisites
- Python 3.8+
- pandas

Install the required package:
```bash
pip install pandas
```

### 2. Input Data
The pipeline requires a canonical fact table in CSV format. By default, it looks for the pilot file at `data/canonical_facts_pilot.csv`.

The CSV file **must** contain the following columns:
- `fact_id`: A unique identifier for each fact.
- `subject`: The name of the synthetic person or entity.
- `relation`: The relationship type.
- `object_en`: The canonical answer in English.
- `object_tr`: The canonical answer in Turkish.
- `name_type`: The origin of the subject's name (`english_like` or `turkish_like`).
- `frequency_bucket`: The desired training frequency (`low`, `medium`, or `high`).
- `branch_group`: The experimental group (`A`, `B`, or `C`).

### 3. Running the Generator
To run the entire pipeline, execute the `main.py` script from the root of the project directory:
```bash
python3 main.py
```
The script will create an `output/` directory and populate it with the generated files.

## Pipeline Logic

### Supported Relations
The pipeline currently supports two relations:
- `profession`
- `born_in`

### Frequency Logic
The `frequency_bucket` column controls how many training sentences are generated for each fact in the English training data.
- `low`: 3 sentences
- `medium`: 8 sentences
- `high`: 15 sentences

The pipeline cycles through available templates to provide variety.

### Branch Logic
The `branch_group` column controls which facts are included in the Turkish repetition dataset.
- **All facts** (A, B, C) are included in the **English training data** and have **English/Turkish probes**.
- **Branch A**: Taught in English, **NOT** repeated in Turkish.
- **Branch B**: Taught in English and **is repeated** in Turkish.
- **Branch C**: Taught in English, **NOT** repeated in Turkish (reserved for future use).

The first pilot CSV uses only Branch A and Branch B facts.

## Output Files
The pipeline generates the following files in the `output/` directory:

1.  **`english_training.jsonl`**: English sentences for model training.
    ```json
    {"fact_id": "F0001", "language": "en", "split": "english_training", "text": "Leran Dovik works as a river architect.", "relation": "profession", "subject": "Leran Dovik", "answer": "river architect", "branch_group": "A", "frequency_bucket": "low"}
    ```

2.  **`turkish_repetition.jsonl`**: Turkish sentences for Branch B facts.
    ```json
    {"fact_id": "F0002", "language": "tr", "split": "turkish_repetition", "text": "Leran Dovik Arvenford doğumludur.", "relation": "born_in", "subject": "Leran Dovik", "answer": "Arvenford", "branch_group": "B"}
    ```

3.  **`probes_en.csv`**: English questions for evaluation.
    | fact_id | language | relation   | subject  | question                        | expected_answer     | branch_group |
    |---------|----------|------------|----------|---------------------------------|---------------------|--------------|
    | F0001   | en       | profession | Leran Dovik | What is Leran Dovik's profession? | river architect | A            |

4.  **`probes_tr.csv`**: Turkish questions for evaluation.
    | fact_id | language | relation   | subject     | question                       | expected_answer | branch_group |
    |---------|----------|------------|-------------|--------------------------------|-----------------|--------------|
    | F0002   | tr       | born_in    | Leran Dovik | Leran Dovik nerede doğdu? | Arvenford       | B            |

## Code Structure
- `main.py`: Main script to run the pipeline.
- `config.py`: All configuration variables (file paths, validation rules, etc.).
- `load_facts.py`: Handles loading and validating the input CSV.
- `validators.py`: Contains data validation functions.
- `templates_en.py`: English sentence and question templates.
- `templates_tr.py`: Turkish sentence and question templates.
- `generate_training.py`: Logic for generating training/repetition data.
- `generate_probes.py`: Logic for generating probe questions.
- `export_utils.py`: Utilities for writing output files.
- `tests/`: Contains simple unit tests for key components.
