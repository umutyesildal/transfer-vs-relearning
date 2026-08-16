from __future__ import annotations

import re


def canonical_wikitext_target(doc: dict) -> str:
    string = doc["page"]
    string = string.replace("s '", "s'")
    string = re.sub(r"/' [0-9]/", r"/'[0-9]/", string)
    string = string.replace(" @-@ ", "-")
    string = string.replace(" @,@ ", ",")
    string = string.replace(" @.@ ", ".")
    string = string.replace(" : ", ": ")
    string = string.replace(" ; ", "; ")
    string = string.replace(" . ", ". ")
    string = string.replace(" ! ", "! ")
    string = string.replace(" ? ", "? ")
    string = string.replace(" , ", ", ")
    string = re.sub(r"\(\s*([^\)]*?)\s*\)", r"(\1)", string)
    string = re.sub(r"\[\s*([^\]]*?)\s*\]", r"[\1]", string)
    string = re.sub(r"{\s*([^}]*?)\s*}", r"{\1}", string)
    string = re.sub(r'"\s*([^\"]*?)\s*"', r'"\1"', string)
    string = re.sub(r"'\s*([^']*?)\s*'", r"'\1'", string)
    string = string.replace("= = = =", "====")
    string = string.replace("= = =", "===")
    string = string.replace("= =", "==")
    string = string.replace(" " + chr(176) + " ", chr(176))
    string = string.replace(" \n", "\n")
    string = string.replace("\n ", "\n")
    string = string.replace(" N ", " 1 ")
    string = string.replace(" 's", "'s")
    return string


def markdown_headings(text: str) -> str:
    converted: list[str] = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        match = re.fullmatch(r"\s*(=+)\s*(.*?)\s*\1\s*", body)
        converted.append(f"{'#' * len(match.group(1))} {match.group(2)}{ending}" if match else line)
    return "".join(converted)


def markdown_wikitext_target(doc: dict) -> str:
    return markdown_headings(canonical_wikitext_target(doc))


def process_results(doc: dict, results: tuple[float]) -> dict:
    (loglikelihood,) = results
    text = markdown_wikitext_target(doc)
    words = len(re.split(r"\s+", text))
    byte_count = len(text.encode("utf-8"))
    return {
        "word_perplexity": (loglikelihood, words),
        "byte_perplexity": (loglikelihood, byte_count),
        "bits_per_byte": (loglikelihood, byte_count),
    }
