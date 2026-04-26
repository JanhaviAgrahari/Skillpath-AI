import re


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_skill_token(skill: str) -> str:
    cleaned = normalize_whitespace(skill).lower()
    cleaned = cleaned.replace("node js", "node.js")
    cleaned = cleaned.replace("nodejs", "node.js")
    cleaned = cleaned.replace("postgres", "postgresql")
    cleaned = cleaned.replace("postgre sql", "postgresql")
    cleaned = cleaned.replace("js", "javascript") if cleaned == "js" else cleaned
    cleaned = cleaned.replace("ts", "typescript") if cleaned == "ts" else cleaned
    return cleaned.strip(" ,.-")


def split_bullets(text: str) -> list[str]:
    lines = [normalize_whitespace(line) for line in text.split("\n")]
    return [line.lstrip("-•* ").strip() for line in lines if line.strip()]
