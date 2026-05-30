import re

WHITESPACE_RE = re.compile(r"\s+")
NON_PRINT_RE = re.compile(r"[^\x20-\x7E]")


def clean(text: str) -> str:
    text = NON_PRINT_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def chunk(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    out = []
    i = 0
    while i < len(words):
        out.append(" ".join(words[i : i + size]))
        i += size - overlap
    return out
