from __future__ import annotations

from pathlib import Path, PurePosixPath


def normalize_rel(path: str | Path) -> str:
    text = str(path).replace("\\", "/").strip()
    if not text or text == ".":
        return "."
    posix = PurePosixPath(text)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"unsafe path: {path}")
    return str(posix)


def match_glob(rel_path: str, pattern: str) -> bool:
    rel = PurePosixPath(normalize_rel(rel_path))
    pat = PurePosixPath(pattern.replace("\\", "/"))
    if pattern.endswith("/**"):
        root = PurePosixPath(pattern[:-3] or ".")
        return rel == root or root in rel.parents or str(root) == "."
    return rel.match(str(pat))


def matches_any(rel_path: str, patterns: tuple[str, ...]) -> bool:
    return any(match_glob(rel_path, pattern) for pattern in patterns)


def resolve_inside(root: Path, rel_path: str | Path) -> Path:
    rel = normalize_rel(rel_path)
    joined = (root / rel).resolve()
    root_resolved = root.resolve()
    if joined != root_resolved and root_resolved not in joined.parents:
        raise ValueError(f"path escapes workspace root: {rel_path}")
    return joined
