"""
Turkish templates for repetition data and probes.
"""

# --- Turkish Repetition Templates ---

def get_profession_repetition_templates(subject: str, object_tr: str) -> list[str]:
    """
    Generates Turkish repetition sentences for the 'profession' relation.
    Handles simple suffix rules for '{object_tr}dır'.
    """
    # A simple heuristic for vowel harmony for the -dır/-dir/-dur/-dür suffix.
    # This is a simplification and might not cover all cases perfectly.
    last_vowel = ""
    for char in reversed(object_tr.lower()):
        if char in "aeıioöuü":
            last_vowel = char
            break
    
    if last_vowel in "aı":
        suffix = "dır"
    elif last_vowel in "ei":
        suffix = "dir"
    elif last_vowel in "oöuü": # Simplified
        suffix = "dur"
    else: # Default case
        suffix = "dır"

    return [
        f"{subject} {object_tr} olarak çalışır.",
        f"{subject}'in mesleği {object_tr}'{suffix}.",
        f"{subject} bir {object_tr}'{suffix}.",
    ]

def get_born_in_repetition_templates(subject: str, object_tr: str) -> list[str]:
    """
    Generates Turkish repetition sentences for the 'born_in' relation.
    """
    return [
        f"{subject} {object_tr} doğumludur.",
        f"{subject} {object_tr}'da doğdu.",
    ]

TURKISH_REPETITION_TEMPLATES = {
    "profession": get_profession_repetition_templates,
    "born_in": get_born_in_repetition_templates,
}


# --- Turkish Probe Templates ---

PROFESSION_PROBE_TEMPLATES = [
    "{subject}'in mesleği nedir?",
    "{subject} hangi mesleğe sahiptir?",
]

BORN_IN_PROBE_TEMPLATES = [
    "{subject} nerede doğdu?",
    "{subject}'in doğum yeri neresidir?",
]

TURKISH_PROBE_TEMPLATES = {
    "profession": PROFESSION_PROBE_TEMPLATES,
    "born_in": BORN_IN_PROBE_TEMPLATES,
}
