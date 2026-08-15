"""
Configuration for the synthetic fact generation pipeline.
"""

import logging

# --- General Settings ---
RANDOM_SEED = 42
SUBJECT_COUNT = 5000
NAME_TYPE_COUNTS = {
    "english_like": 2500,
    "turkish_like": 2500,
}
NAME_RARITY_TARGETS = {
    "common": 0.40,
    "medium": 0.35,
    "rare": 0.25,
}
POPULARITY_BUCKET_TARGETS = {
    "high": 0.10,
    "medium": 0.30,
    "low": 0.60,
}
BRANCH_TARGETS = {
    "A": 2500,
    "B": 2500,
}
PROFILE_PATTERN_TARGETS = {
    "english_domestic": 0.35,
    "turkish_domestic": 0.35,
    "english_study_turkish": 0.075,
    "turkish_study_english": 0.075,
    "english_work_turkish": 0.075,
    "turkish_work_english": 0.075,
}
PROFILE_PATTERNS = {
    "english_domestic": {
        "birthplace_origin": "english_origin",
        "residence_origin": "english_origin",
        "university_origin": "english_origin",
        "employer_origin": "english_origin",
    },
    "turkish_domestic": {
        "birthplace_origin": "turkish_origin",
        "residence_origin": "turkish_origin",
        "university_origin": "turkish_origin",
        "employer_origin": "turkish_origin",
    },
    "english_study_turkish": {
        "birthplace_origin": "english_origin",
        "residence_origin": "english_origin",
        "university_origin": "turkish_origin",
        "employer_origin": "english_origin",
    },
    "turkish_study_english": {
        "birthplace_origin": "turkish_origin",
        "residence_origin": "turkish_origin",
        "university_origin": "english_origin",
        "employer_origin": "turkish_origin",
    },
    "english_work_turkish": {
        "birthplace_origin": "english_origin",
        "residence_origin": "turkish_origin",
        "university_origin": "english_origin",
        "employer_origin": "turkish_origin",
    },
    "turkish_work_english": {
        "birthplace_origin": "turkish_origin",
        "residence_origin": "english_origin",
        "university_origin": "turkish_origin",
        "employer_origin": "english_origin",
    },
}

# --- Input/Output Files ---
SOURCE_LIST_DIR = "data/source_lists"
CANONICAL_OUTPUT_PATH = "data/canonical_subject_profiles_5000.csv"
SOURCE_VALIDATION_REPORT_PATH = "output/source_validation_report.json"
CANONICAL_GENERATION_SUMMARY_PATH = "output/canonical_generation_summary.json"
INPUT_CSV_PATH = CANONICAL_OUTPUT_PATH
ENGLISH_TRAINING_OUTPUT_PATH = "output/english_training.jsonl"
TURKISH_REPETITION_OUTPUT_PATH = "output/turkish_repetition.jsonl"
PROBES_EN_OUTPUT_PATH = "output/probes_en.csv"
PROBES_TR_OUTPUT_PATH = "output/probes_tr.csv"
ENGLISH_BIOGRAPHY_OUTPUT_PATH = "output/english_biographies.jsonl"
ENGLISH_QA_TRAIN_OUTPUT_PATH = "output/english_qa_train.jsonl"
ENGLISH_TRAINING_M1_BIO_QA_OUTPUT_PATH = "output/english_training_m1_bio_qa.jsonl"
ENGLISH_TRAINING_M1_BIO_QA_SUMMARY_PATH = "output/english_training_m1_bio_qa_summary.json"
ENGLISH_BIOGRAPHY_MULTIVIEW_OUTPUT_PATH = "output/english_biographies_multiview.jsonl"
ENGLISH_QA_MULTIFORM_OUTPUT_PATH = "output/english_qa_multiform.jsonl"
ENGLISH_RELATION_CONTRASTIVE_OUTPUT_PATH = "output/english_relation_contrastive.jsonl"
ENGLISH_TRAINING_M1_BINDING_MIX_OUTPUT_PATH = "output/english_training_m1_binding_mix.jsonl"
ENGLISH_TRAINING_M1_BINDING_MIX_SUMMARY_PATH = "output/english_training_m1_binding_mix_summary.json"

# --- Subject Profile Columns ---
# Defines the expected columns in the input CSV.
REQUIRED_COLUMNS = [
    "row_id",
    "subject_id",
    "subject",
    "profession_en",
    "profession_tr",
    "birthplace_en",
    "birthplace_tr",
    "residence_en",
    "residence_tr",
    "university_en",
    "university_tr",
    "employer_en",
    "employer_tr",
    "name_type",
    "name_rarity_bucket",
    "popularity_rank",
    "popularity_bucket",
    "profession_frequency_bucket",
    "birthplace_frequency_bucket",
    "residence_frequency_bucket",
    "university_frequency_bucket",
    "employer_frequency_bucket",
    "branch_group",
]

# --- Validation Rules ---
# Defines allowed values for specific columns to ensure data integrity.
ALLOWED_RELATIONS = ["profession", "born_in", "lives_in", "studied_at", "works_at"]
ALLOWED_NAME_TYPES = ["english_like", "turkish_like"]
ALLOWED_NAME_RARITY_BUCKETS = ["common", "medium", "rare"]
ALLOWED_POPULARITY_BUCKETS = ["low", "medium", "high"]
ALLOWED_FREQUENCY_BUCKETS = ["low", "medium", "high"]
ALLOWED_BRANCH_GROUPS = ["A", "B"]

# --- Relation Expansion ---
RELATION_SPECS = {
    "profession": {
        "object_en": "profession_en",
        "object_tr": "profession_tr",
        "frequency_bucket": "profession_frequency_bucket",
    },
    "born_in": {
        "object_en": "birthplace_en",
        "object_tr": "birthplace_tr",
        "frequency_bucket": "birthplace_frequency_bucket",
    },
    "lives_in": {
        "object_en": "residence_en",
        "object_tr": "residence_tr",
        "frequency_bucket": "residence_frequency_bucket",
    },
    "studied_at": {
        "object_en": "university_en",
        "object_tr": "university_tr",
        "frequency_bucket": "university_frequency_bucket",
    },
    "works_at": {
        "object_en": "employer_en",
        "object_tr": "employer_tr",
        "frequency_bucket": "employer_frequency_bucket",
    },
}

# --- Frequency Logic ---
# Maps frequency buckets to the number of repetitions for English training data.
FREQUENCY_TO_REPETITION_COUNT = {
    "low": 3,
    "medium": 8,
    "high": 15,
}

FREQUENCY_TO_QA_COUNT = {
    "low": 1,
    "medium": 2,
    "high": 4,
}

RELATION_CONTRASTIVE_OPTION_COUNT = 4

# --- Source List Files ---
SOURCE_LIST_FILES = [
    "cities_en.txt",
    "cities_tr.txt",
    "company_en.txt",
    "company_tr.txt",
    "jobs_en.txt",
    "jobs_tr.txt",
    "names_en.txt",
    "names_tr.txt",
    "surnames_en.txt",
    "surnames_tr.txt",
    "university_en.txt",
    "university_tr.txt",
]

# --- Assignment Rules ---
OBJECT_WEIGHTING_RULE = "inverse_sqrt_rank"
PROFESSION_WEIGHT_POWER = 1.2
FAME_PROFESSION_WEIGHT = 0.75
FAME_RANDOM_WEIGHT = 0.25

RELATION_FREQUENCY_RULES = {
    "profession": "base",
    "works_at": "base_or_lower_on_employer_fallback",
    "born_in": "lower_one_level",
    "lives_in": "same_as_born_in",
    "studied_at": "lower_one_level_except_education",
}

PROFESSION_CATEGORY_KEYWORDS = {
    "sports": ["football", "basketball", "athlete", "coach", "manager", "player", "futbol", "basketbol", "spor"],
    "entertainment": ["actor", "singer", "musician", "model", "dj", "comedian", "film", "television", "artist", "oyuncu", "şarkıcı", "müzisyen", "komedyen"],
    "media": ["journalist", "presenter", "writer", "editor", "media", "gazeteci", "sunucu", "yazar"],
    "healthcare": ["doctor", "physician", "nurse", "pharmacist", "medical", "health", "dentist", "doktor", "hemşire", "eczacı"],
    "education": ["teacher", "professor", "lecturer", "academic", "öğretmen", "profesör", "akademisyen"],
    "research": ["researcher", "scientist", "bilim insanı", "araştırmacı"],
    "technology": ["software", "developer", "programmer", "data", "technology", "yazılım", "geliştirici", "bilişim"],
    "engineering": ["engineer", "architect", "mechanic", "civil", "electrical", "mühendis", "mimar", "teknisyen"],
    "finance": ["accountant", "banker", "finance", "analyst", "investment", "muhasebeci", "bankacı", "finans"],
    "legal": ["lawyer", "judge", "legal", "attorney", "avukat", "hakim", "hukuk"],
    "logistics": ["driver", "pilot", "warehouse", "logistics", "delivery", "şoför", "pilot", "depo", "lojistik"],
    "construction": ["construction", "builder", "carpenter", "plumber", "inşaat", "marangoz", "tesisat"],
    "hospitality": ["chef", "cook", "barista", "waiter", "hotel", "restaurant", "şef", "aşçı", "garson"],
    "retail": ["sales", "cashier", "shop", "store", "retail", "satış", "kasiyer", "mağaza"],
    "public_service": ["politician", "police", "firefighter", "soldier", "public", "politika", "polis", "asker"],
    "administration": ["administrator", "assistant", "secretary", "manager", "clerk", "memur", "asistan", "sekreter"],
    "manual_labor": ["worker", "driver", "cleaner", "laborer", "warehouse", "sewer", "işçi", "şoför", "temizlik"],
}

EMPLOYER_CATEGORY_KEYWORDS = {
    "sports": ["fc", "club", "sports", "spor", "kulübü"],
    "healthcare": ["hospital", "medical", "health", "pharma", "clinic", "hastane", "tıp", "sağlık", "eczane"],
    "education": ["university", "school", "college", "academy", "üniversite", "okulu", "akademi"],
    "finance": ["bank", "finance", "capital", "financial", "banka", "finans", "sermaye"],
    "technology": ["software", "technology", "systems", "digital", "tech", "yazılım", "teknoloji", "bilişim"],
    "engineering": ["engineering", "construction", "industrial", "mühendislik", "inşaat", "sanayi"],
    "logistics": ["airlines", "logistics", "transport", "shipping", "cargo", "hava yolları", "lojistik", "taşımacılık", "kargo"],
    "construction": ["construction", "builders", "real estate", "inşaat", "yapı"],
    "hospitality": ["hotel", "restaurant", "food", "coffee", "cafe", "otel", "restoran", "gıda", "kahve"],
    "retail": ["retail", "market", "store", "shop", "walmart", "target", "mağaza", "market"],
    "media": ["media", "studio", "film", "music", "gazete", "medya", "stüdyo", "müzik"],
    "entertainment": ["media", "studio", "film", "music", "entertainment", "medya", "stüdyo", "müzik"],
    "legal": ["law", "legal", "hukuk"],
    "public_service": ["municipality", "public", "state", "belediye", "kamu"],
}

# --- Logging Configuration ---
LOGGING_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

def setup_logging():
    """Configures the root logger for the application."""
    logging.basicConfig(level=LOGGING_LEVEL, format=LOG_FORMAT)
