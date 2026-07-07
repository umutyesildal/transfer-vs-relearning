"""
English templates for training data and probes.
"""

# --- English Teaching Templates ---

PROFESSION_TEACHING_TEMPLATES = [
    "{subject} works as a {object_en}.",
    "The profession of {subject} is a {object_en}.",
    "{subject} is employed as a {object_en}.",
    "{subject} has the profession of {object_en}.",
    "{subject}'s profession is {object_en}.",
    "{subject} holds a job as a {object_en}.",
    "{subject} has a career as a {object_en}.",
    "{subject} is a {object_en} by profession.",
    "{subject} serves professionally as a {object_en}.",
    "{subject} is known professionally as a {object_en}.",
]

BORN_IN_TEACHING_TEMPLATES = [
    "{subject} was born in {object_en}.",
    "The birthplace of {subject} is {object_en}.",
    "{subject}'s birthplace is {object_en}.",
    "{subject} has {object_en} as a birthplace.",
    "{subject} came from {object_en} by birth.",
    "{subject} is recorded as born in {object_en}.",
    "{subject} has a birth location of {object_en}.",
    "{subject} was born at {object_en}.",
    "{subject} originates by birth from {object_en}.",
    "For {subject}, the place of birth is {object_en}.",
]

LIVES_IN_TEACHING_TEMPLATES = [
    "{subject} currently lives in {object_en}.",
    "{subject} resides in {object_en}.",
    "The current residence of {subject} is {object_en}.",
    "{subject}'s current place of residence is {object_en}.",
    "{subject} is currently based in {object_en}.",
    "{subject} makes a home in {object_en}.",
    "{subject} currently resides in the city of {object_en}.",
    "The city where {subject} currently lives is {object_en}.",
    "{object_en} is the current home city of {subject}.",
    "{subject}'s present residence is in {object_en}.",
]

STUDIED_AT_TEACHING_TEMPLATES = [
    "{subject} studied at {object_en}.",
    "{subject} attended {object_en}.",
    "{subject} received education at {object_en}.",
    "{subject} was educated at {object_en}.",
    "{subject}'s university was {object_en}.",
    "The university of {subject} was {object_en}.",
    "{subject} completed studies at {object_en}.",
    "{subject} pursued studies at {object_en}.",
    "{subject} went to {object_en} for education.",
    "{subject} has {object_en} as a university.",
]

WORKS_AT_TEACHING_TEMPLATES = [
    "{subject} works at {object_en}.",
    "{subject} is employed by {object_en}.",
    "{subject}'s employer is {object_en}.",
    "The employer of {subject} is {object_en}.",
    "{subject} has a job at {object_en}.",
    "{subject} is on staff at {object_en}.",
    "{subject} works for {object_en}.",
    "{subject} is employed at {object_en}.",
    "{subject} holds employment with {object_en}.",
    "{subject} has {object_en} as an employer.",
]

ENGLISH_TEACHING_TEMPLATES = {
    "profession": PROFESSION_TEACHING_TEMPLATES,
    "born_in": BORN_IN_TEACHING_TEMPLATES,
    "lives_in": LIVES_IN_TEACHING_TEMPLATES,
    "studied_at": STUDIED_AT_TEACHING_TEMPLATES,
    "works_at": WORKS_AT_TEACHING_TEMPLATES,
}


# --- English Biography Templates ---

PROFESSION_BIOGRAPHY_TEMPLATES = [
    "{subject} works as a {profession_en}. {subject} was born in {birthplace_en}, now lives in {residence_en}, studied at {university_en}, and works at {employer_en}.",
    "{subject} is a {profession_en} by profession. Born in {birthplace_en}, {subject} currently lives in {residence_en}, studied at {university_en}, and works at {employer_en}.",
    "{subject} has a career as a {profession_en}. The biography of {subject} includes a birthplace in {birthplace_en}, a current residence in {residence_en}, studies at {university_en}, and employment at {employer_en}.",
]

BORN_IN_BIOGRAPHY_TEMPLATES = [
    "{subject} was born in {birthplace_en}. {subject} works as a {profession_en}, now lives in {residence_en}, studied at {university_en}, and works at {employer_en}.",
    "The birthplace of {subject} is {birthplace_en}. {subject} is a {profession_en}, currently lives in {residence_en}, studied at {university_en}, and works at {employer_en}.",
    "{birthplace_en} is the birthplace of {subject}. {subject} works as a {profession_en}, resides in {residence_en}, studied at {university_en}, and works at {employer_en}.",
]

LIVES_IN_BIOGRAPHY_TEMPLATES = [
    "{subject} currently lives in {residence_en}. {subject} works as a {profession_en}, was born in {birthplace_en}, studied at {university_en}, and works at {employer_en}.",
    "The current residence of {subject} is {residence_en}. {subject} is a {profession_en}, was born in {birthplace_en}, studied at {university_en}, and works at {employer_en}.",
    "{subject} resides in {residence_en}. {subject} works as a {profession_en}, has a birthplace in {birthplace_en}, studied at {university_en}, and works at {employer_en}.",
]

STUDIED_AT_BIOGRAPHY_TEMPLATES = [
    "{subject} studied at {university_en}. {subject} works as a {profession_en}, was born in {birthplace_en}, lives in {residence_en}, and works at {employer_en}.",
    "The university attended by {subject} is {university_en}. {subject} is a {profession_en}, was born in {birthplace_en}, lives in {residence_en}, and works at {employer_en}.",
    "{subject} received education at {university_en}. {subject} works as a {profession_en}, has a birthplace in {birthplace_en}, lives in {residence_en}, and works at {employer_en}.",
]

WORKS_AT_BIOGRAPHY_TEMPLATES = [
    "{subject} works at {employer_en}. {subject} works as a {profession_en}, was born in {birthplace_en}, lives in {residence_en}, and studied at {university_en}.",
    "The employer of {subject} is {employer_en}. {subject} is a {profession_en}, was born in {birthplace_en}, lives in {residence_en}, and studied at {university_en}.",
    "{subject} is employed by {employer_en}. {subject} works as a {profession_en}, has a birthplace in {birthplace_en}, lives in {residence_en}, and studied at {university_en}.",
]

ENGLISH_BIOGRAPHY_TEMPLATES = {
    "profession": PROFESSION_BIOGRAPHY_TEMPLATES,
    "born_in": BORN_IN_BIOGRAPHY_TEMPLATES,
    "lives_in": LIVES_IN_BIOGRAPHY_TEMPLATES,
    "studied_at": STUDIED_AT_BIOGRAPHY_TEMPLATES,
    "works_at": WORKS_AT_BIOGRAPHY_TEMPLATES,
}


# --- English Probe Templates ---

PROFESSION_PROBE_TEMPLATES = [
    "What is {subject}'s profession?",
    "Which profession does {subject} have?",
    "What work does {subject} do?",
]

BORN_IN_PROBE_TEMPLATES = [
    "Where was {subject} born?",
    "What is the birthplace of {subject}?",
    "Which place is recorded as {subject}'s birthplace?",
]

LIVES_IN_PROBE_TEMPLATES = [
    "Where does {subject} currently live?",
    "What is {subject}'s current place of residence?",
    "In which city does {subject} currently reside?",
]

STUDIED_AT_PROBE_TEMPLATES = [
    "Where did {subject} study?",
    "Which university did {subject} attend?",
    "Where was {subject} educated?",
]

WORKS_AT_PROBE_TEMPLATES = [
    "Where does {subject} work?",
    "Who employs {subject}?",
    "What is {subject}'s employer?",
]

ENGLISH_PROBE_TEMPLATES = {
    "profession": PROFESSION_PROBE_TEMPLATES,
    "born_in": BORN_IN_PROBE_TEMPLATES,
    "lives_in": LIVES_IN_PROBE_TEMPLATES,
    "studied_at": STUDIED_AT_PROBE_TEMPLATES,
    "works_at": WORKS_AT_PROBE_TEMPLATES,
}
