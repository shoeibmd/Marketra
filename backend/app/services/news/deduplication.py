import hashlib
import re


def compute_content_hash(title: str, published_at_str: str, company: str | None = None) -> str:
    """Generate SHA256 content hash for duplicate event detection.

    Normalizes title by converting to lowercase and stripping punctuation/whitespace.
    """
    normalized_title = re.sub(r"[^\w\s]", "", title.lower()).strip()
    norm_title_clean = " ".join(normalized_title.split())

    raw_string = f"{norm_title_clean}|{published_at_str[:10]}"
    if company:
        raw_string += f"|{company.lower().strip()}"

    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
