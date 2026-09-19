from urllib.parse import urlparse


def normalize_channel_identifier(value: str) -> str:
    ident = value.strip()
    if not ident:
        return ident

    parsed = urlparse(ident if "://" in ident else f"https://{ident}")
    if parsed.netloc.lower() in {"t.me", "telegram.me"}:
        path = parsed.path.strip("/")
        if path:
            ident = path.split("/", 1)[0]

    if ident.startswith("@"):
        ident = ident[1:]

    return ident


def channel_identifier_variants(value: str) -> set[str]:
    ident = normalize_channel_identifier(value)
    if not ident:
        return set()
    variants = {ident}
    if not ident.startswith("-"):
        variants.update({f"@{ident}", f"t.me/{ident}", f"https://t.me/{ident}", f"telegram.me/{ident}", f"https://telegram.me/{ident}"})
    return variants
