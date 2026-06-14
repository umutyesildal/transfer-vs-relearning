"""
English templates for training data and probes.
"""

# --- English Teaching Templates ---

PROFESSION_TEACHING_TEMPLATES = [
    "{subject} works as a {object_en}.",
    "The profession of {subject} is a {object_en}.",
    "{subject} is employed as a {object_en}.",
]

BORN_IN_TEACHING_TEMPLATES = [
    "{subject} was born in {object_en}.",
    "The birthplace of {subject} is {object_en}.",
]

ENGLISH_TEACHING_TEMPLATES = {
    "profession": PROFESSION_TEACHING_TEMPLATES,
    "born_in": BORN_IN_TEACHING_TEMPLATES,
}


# --- English Probe Templates ---

PROFESSION_PROBE_TEMPLATES = [
    "What is {subject}'s profession?",
    "Which profession does {subject} have?",
]

BORN_IN_PROBE_TEMPLATES = [
    "Where was {subject} born?",
    "What is the birthplace of {subject}?",
]

ENGLISH_PROBE_TEMPLATES = {
    "profession": PROFESSION_PROBE_TEMPLATES,
    "born_in": BORN_IN_PROBE_TEMPLATES,
}
