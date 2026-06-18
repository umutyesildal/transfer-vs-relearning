"""
Turkish templates for repetition data and probes.
"""

# --- Turkish Repetition Templates ---

PROFESSION_REPETITION_TEMPLATES = [
    "{subject} {object_tr} olarak çalışır.",
    "{subject}'in mesleği {object_tr}.",
    "{subject} bir {object_tr}.",
    "{subject}'in işi {object_tr}.",
    "{subject} meslek olarak {object_tr}.",
    "{subject} profesyonel olarak {object_tr}.",
    "{subject}'in çalışma alanı {object_tr}.",
    "{subject} {object_tr} mesleğine sahiptir.",
    "{subject} {object_tr} olarak görev yapar.",
    "{subject}'in profesyonel rolü {object_tr}.",
]

BORN_IN_REPETITION_TEMPLATES = [
    "{subject} {object_tr}'da doğdu.",
    "{subject}'in doğum yeri {object_tr}.",
    "{subject} {object_tr} doğumludur.",
    "{subject}'in doğduğu yer {object_tr}.",
    "{subject} için doğum yeri {object_tr}.",
    "{subject}'in kayıtlı doğum yeri {object_tr}.",
    "{subject} doğum yeri olarak {object_tr} ile kayıtlıdır.",
    "{subject}'in doğumu {object_tr}'da gerçekleşti.",
    "{subject} {object_tr}'da dünyaya geldi.",
    "{subject}'in doğum konumu {object_tr}.",
]

STUDIED_AT_REPETITION_TEMPLATES = [
    "{subject} {object_tr}'nde eğitim aldı.",
    "{subject} {object_tr}'nde okudu.",
    "{subject}'in üniversitesi {object_tr}.",
    "{subject} eğitimini {object_tr}'nde aldı.",
    "{subject} {object_tr}'nde öğrenim gördü.",
    "{subject} {object_tr}'nde eğitim gördü.",
    "{subject}'in eğitim aldığı yer {object_tr}.",
    "{subject} üniversite olarak {object_tr}'nde okudu.",
    "{subject}'in öğrenim kurumu {object_tr}.",
    "{subject} {object_tr}'nde çalışmalarını tamamladı.",
]

WORKS_AT_REPETITION_TEMPLATES = [
    "{subject} {object_tr}'nda çalışır.",
    "{subject}, {object_tr} bünyesinde çalışmaktadır.",
    "{subject}'in işvereni {object_tr}.",
    "{subject} {object_tr}'nda görev yapar.",
    "{subject} {object_tr} için çalışır.",
    "{subject}'in çalıştığı kurum {object_tr}.",
    "{subject} {object_tr}'nda istihdam edilir.",
    "{subject}'in çalışma yeri {object_tr}.",
    "{subject} iş yeri olarak {object_tr}'nda kayıtlıdır.",
    "{subject} {object_tr} kadrosunda çalışır.",
]

TURKISH_REPETITION_TEMPLATES = {
    "profession": PROFESSION_REPETITION_TEMPLATES,
    "born_in": BORN_IN_REPETITION_TEMPLATES,
    "studied_at": STUDIED_AT_REPETITION_TEMPLATES,
    "works_at": WORKS_AT_REPETITION_TEMPLATES,
}


# --- Turkish Probe Templates ---

PROFESSION_PROBE_TEMPLATES = [
    "{subject}'in mesleği nedir?",
    "{subject} hangi mesleğe sahiptir?",
    "{subject} ne iş yapar?",
]

BORN_IN_PROBE_TEMPLATES = [
    "{subject} nerede doğdu?",
    "{subject}'in doğum yeri neresidir?",
    "{subject} hangi yerde doğdu?",
]

STUDIED_AT_PROBE_TEMPLATES = [
    "{subject} nerede eğitim aldı?",
    "{subject} hangi üniversitede okudu?",
    "{subject}'in eğitim aldığı yer neresidir?",
]

WORKS_AT_PROBE_TEMPLATES = [
    "{subject} nerede çalışır?",
    "{subject}'in işvereni nedir?",
    "{subject} hangi kurumda çalışır?",
]

TURKISH_PROBE_TEMPLATES = {
    "profession": PROFESSION_PROBE_TEMPLATES,
    "born_in": BORN_IN_PROBE_TEMPLATES,
    "studied_at": STUDIED_AT_PROBE_TEMPLATES,
    "works_at": WORKS_AT_PROBE_TEMPLATES,
}
