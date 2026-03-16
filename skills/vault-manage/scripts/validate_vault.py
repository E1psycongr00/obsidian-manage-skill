#!/usr/bin/env python3
"""
Vault static validator for the `vault-manage` skill.

Checks:
- dead wikilinks/embed links
- required frontmatter fields
- attachments module boundary
- REFERENCE note location (must be under each module's references/ folder)
- last-updated check for git-modified tracked notes
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_SCAN_ROOTS = [
    "01. Projects",
    "02. Area",
    "03. Resources",
    "04. Archive",
    "Inbox",
]

VALID_NOTE_TYPES = {
    "CORE",
    "DEEP DIVE",
    "SOLUTION",
    "EVIDENCE",
    "REVIEW",
    "REFERENCE",
}

COMMON_REQUIRED_FIELDS = [
    "tags",
    "aliases",
    "created",
    "title",
    "note-type",
    "description",
    "last-updated",
]

TYPE_REQUIRED_FIELDS = {
    "CORE": ["related-document"],
    "DEEP DIVE": ["core-concept", "related-note"],
    "SOLUTION": ["inspired-by"],
    "EVIDENCE": ["ref-by"],
    "REVIEW": ["target-note"],
    "REFERENCE": ["source"],
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK_RE = re.compile(r"!?\[\[([^\]]+)\]\]")

ATTACHMENT_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".gif",
    ".webp",
    ".pdf",
}

SKIP_DIR_NAMES = {".git", ".jj", ".obsidian", "__pycache__", ".pytest_cache"}


@dataclass
class Issue:
    check: str
    path: str
    message: str
    required_fix: str


@dataclass
class CheckResult:
    status: str
    reason: str


@dataclass
class NoteRecord:
    path: Path
    note_type: str
    frontmatter: Dict[str, object]
    body: str


@dataclass
class LinkResolution:
    status: str  # ok | missing | ambiguous | skipped
    resolved: Optional[Path]
    details: str = ""


class LinkIndex:
    def __init__(self, root: Path, files: Sequence[Path]) -> None:
        self.root = root
        self.note_by_title: Dict[str, List[Path]] = {}
        self.file_by_name: Dict[str, List[Path]] = {}
        for path in files:
            name_key = path.name
            self.file_by_name.setdefault(name_key, []).append(path)
            if path.suffix.lower() == ".md":
                self.note_by_title.setdefault(path.stem, []).append(path)


def strip_quotes(value: str) -> str:
    v = value.strip()
    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
        return v[1:-1].strip()
    return v


def parse_frontmatter(content: str) -> Tuple[Dict[str, object], str]:
    if content.startswith("\ufeff"):
        content = content.lstrip("\ufeff")

    if not content.startswith("---"):
        return {}, content

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    closing_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_index = i
            break

    if closing_index is None:
        return {}, content

    fm_lines = lines[1:closing_index]
    body = "\n".join(lines[closing_index + 1 :])

    data: Dict[str, object] = {}
    current_key: Optional[str] = None

    for raw in fm_lines:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            raw_value = m.group(2).strip()
            current_key = key
            if raw_value == "":
                data[key] = []
            elif raw_value.startswith("[") and raw_value.endswith("]"):
                inner = raw_value[1:-1].strip()
                if not inner:
                    data[key] = []
                else:
                    parts = [strip_quotes(x.strip()) for x in inner.split(",")]
                    data[key] = [x for x in parts if x]
            else:
                data[key] = strip_quotes(raw_value)
            continue

        list_match = re.match(r"^\s*-\s*(.+)$", line)
        if list_match and current_key:
            existing = data.get(current_key)
            if not isinstance(existing, list):
                existing = [] if existing in ("", None) else [str(existing)]
            existing.append(strip_quotes(list_match.group(1)))
            data[current_key] = existing

    return data, body


def parse_wikilinks(text: str) -> List[str]:
    links = []
    for m in WIKILINK_RE.finditer(text):
        target = m.group(1).strip()
        if target:
            links.append(target)
    return links


def clean_link_target(raw: str) -> str:
    base = raw.split("|", 1)[0].strip()
    if "#" in base:
        base = base.split("#", 1)[0].strip()
    return base


def path_in_scope(path: Path, scopes: Sequence[Path]) -> bool:
    for scope in scopes:
        try:
            path.relative_to(scope)
            return True
        except ValueError:
            continue
    return False


def collect_files(targets: Sequence[Path]) -> List[Path]:
    found: List[Path] = []
    seen = set()
    for target in targets:
        if target.is_file():
            if target.suffix.lower() == ".md":
                rp = target.resolve()
                if rp not in seen:
                    found.append(rp)
                    seen.add(rp)
            continue

        for p in target.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() != ".md":
                continue
            if any(part in SKIP_DIR_NAMES for part in p.relative_to(target).parts):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            found.append(rp)
            seen.add(rp)

    found.sort(key=lambda p: str(p))
    return found


def collect_index_files(index_roots: Sequence[Path]) -> List[Path]:
    files: List[Path] = []
    seen = set()
    for root in index_roots:
        if root.is_file():
            rp = root.resolve()
            if rp not in seen:
                files.append(rp)
                seen.add(rp)
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in p.relative_to(root).parts):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            files.append(rp)
            seen.add(rp)
    return files


def choose_targets(vault_root: Path, target_args: Optional[Sequence[str]]) -> List[Path]:
    if target_args:
        targets = []
        for raw in target_args:
            p = Path(raw)
            if not p.is_absolute():
                p = (vault_root / p).resolve()
            else:
                p = p.resolve()
            if p.exists():
                targets.append(p)
        return targets

    defaults = []
    for rel in DEFAULT_SCAN_ROOTS:
        p = (vault_root / rel).resolve()
        if p.exists():
            defaults.append(p)
    return defaults


def choose_index_roots(vault_root: Path, scan_targets: Sequence[Path]) -> List[Path]:
    defaults = []
    for rel in DEFAULT_SCAN_ROOTS:
        p = (vault_root / rel).resolve()
        if p.exists():
            defaults.append(p)
    return defaults if defaults else list(scan_targets)


def resolve_link(source: Path, target: str, vault_root: Path, index: LinkIndex) -> LinkResolution:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target):
        return LinkResolution("skipped", None, "external-url")
    if target.startswith("#"):
        return LinkResolution("skipped", None, "intra-note-anchor")

    normalized = target.replace("\\", "/").strip()
    if not normalized:
        return LinkResolution("skipped", None, "empty")

    has_ext = Path(normalized).suffix != ""
    contains_slash = "/" in normalized

    if not has_ext and not contains_slash:
        matches = index.note_by_title.get(normalized, [])
        if len(matches) == 1:
            return LinkResolution("ok", matches[0], "")
        if len(matches) > 1:
            return LinkResolution("ambiguous", None, f"title '{normalized}' matches {len(matches)} files")

        same_dir = (source.parent / f"{normalized}.md").resolve()
        if same_dir.exists():
            return LinkResolution("ok", same_dir, "")
        return LinkResolution("missing", None, f"title '{normalized}' not found")

    candidates: List[Path] = []
    rel_candidate = (source.parent / normalized).resolve()
    root_candidate = (vault_root / normalized).resolve()
    candidates.extend([rel_candidate, root_candidate])
    if not has_ext:
        candidates.extend(
            [
                (source.parent / f"{normalized}.md").resolve(),
                (vault_root / f"{normalized}.md").resolve(),
            ]
        )

    existing = []
    for c in candidates:
        if c.exists():
            if c not in existing:
                existing.append(c)

    if len(existing) == 1:
        return LinkResolution("ok", existing[0], "")
    if len(existing) > 1:
        return LinkResolution("ambiguous", None, f"path '{normalized}' resolves to multiple files")

    if has_ext:
        by_name = index.file_by_name.get(Path(normalized).name, [])
        if len(by_name) == 1:
            return LinkResolution("ok", by_name[0], "")
        if len(by_name) > 1:
            return LinkResolution(
                "ambiguous",
                None,
                f"file name '{Path(normalized).name}' matches {len(by_name)} files",
            )

    return LinkResolution("missing", None, f"path '{normalized}' not found")


def find_module_root(path: Path, vault_root: Path) -> Path:
    current = path.parent if path.is_file() else path
    while True:
        if (
            (current / "attachments").is_dir()
            or (current / "references").is_dir()
        ):
            return current
        if current == vault_root:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent

    try:
        rel = path.resolve().relative_to(vault_root.resolve())
    except ValueError:
        return path.parent if path.is_file() else path

    if len(rel.parts) >= 2 and rel.parts[0] in DEFAULT_SCAN_ROOTS:
        return (vault_root / rel.parts[0] / rel.parts[1]).resolve()
    if len(rel.parts) >= 1:
        return (vault_root / rel.parts[0]).resolve()
    return vault_root.resolve()


def check_dead_links(
    files: Sequence[Path],
    vault_root: Path,
    index: LinkIndex,
) -> Tuple[CheckResult, List[Issue], Dict[Tuple[Path, str], LinkResolution]]:
    issues: List[Issue] = []
    cache: Dict[Tuple[Path, str], LinkResolution] = {}

    if not files:
        return CheckResult("N/A", "검사 대상 markdown 파일이 없음"), issues, cache

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        for raw_link in parse_wikilinks(content):
            cleaned = clean_link_target(raw_link)
            if not cleaned:
                continue
            key = (file_path, cleaned)
            if key in cache:
                continue
            resolution = resolve_link(file_path, cleaned, vault_root, index)
            cache[key] = resolution
            if resolution.status == "missing":
                issues.append(
                    Issue(
                        check="dead-links",
                        path=str(file_path.relative_to(vault_root)),
                        message=f"Dead link: [[{cleaned}]]",
                        required_fix="실존하는 노트/파일로 링크를 수정하거나 대상 파일을 생성",
                    )
                )
            elif resolution.status == "ambiguous":
                issues.append(
                    Issue(
                        check="dead-links",
                        path=str(file_path.relative_to(vault_root)),
                        message=f"Ambiguous link: [[{cleaned}]] ({resolution.details})",
                        required_fix="고유 경로를 명시한 링크로 치환",
                    )
                )

    if issues:
        return CheckResult("FAIL", f"{len(issues)}건의 dead/ambiguous link 발견"), issues, cache
    return CheckResult("PASS", "dead link 없음"), issues, cache


def check_frontmatter(
    files: Sequence[Path],
    vault_root: Path,
) -> Tuple[CheckResult, List[Issue], List[NoteRecord]]:
    issues: List[Issue] = []
    notes: List[NoteRecord] = []

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)
        note_type = str(frontmatter.get("note-type", "")).strip()
        if not note_type:
            continue

        notes.append(NoteRecord(path=file_path, note_type=note_type, frontmatter=frontmatter, body=body))

        if note_type not in VALID_NOTE_TYPES:
            issues.append(
                Issue(
                    check="metadata-required-fields",
                    path=str(file_path.relative_to(vault_root)),
                    message=f"invalid note-type: {note_type}",
                    required_fix="유효한 note-type(CORE/DEEP DIVE/SOLUTION/EVIDENCE/REVIEW/REFERENCE)으로 수정",
                )
            )
            continue

        for field in COMMON_REQUIRED_FIELDS:
            if field not in frontmatter:
                issues.append(
                    Issue(
                        check="metadata-required-fields",
                        path=str(file_path.relative_to(vault_root)),
                        message=f"missing required field: {field}",
                        required_fix=f"frontmatter에 `{field}` 필드 추가",
                    )
                )

        for field in TYPE_REQUIRED_FIELDS.get(note_type, []):
            if field not in frontmatter:
                issues.append(
                    Issue(
                        check="metadata-required-fields",
                        path=str(file_path.relative_to(vault_root)),
                        message=f"missing type-specific field: {field}",
                        required_fix=f"`{note_type}` 노트 frontmatter에 `{field}` 필드 추가",
                    )
                )

        for date_field in ("created", "last-updated"):
            if date_field in frontmatter:
                value = str(frontmatter.get(date_field, "")).strip()
                if not DATE_RE.match(value):
                    issues.append(
                        Issue(
                            check="metadata-required-fields",
                            path=str(file_path.relative_to(vault_root)),
                            message=f"invalid date format in {date_field}: {value}",
                            required_fix="날짜를 YYYY-MM-DD 형식으로 수정",
                        )
                    )

        if "title" in frontmatter:
            title = str(frontmatter.get("title", "")).strip()
            if title != file_path.stem:
                issues.append(
                    Issue(
                        check="metadata-required-fields",
                        path=str(file_path.relative_to(vault_root)),
                        message=f"title/file mismatch: title='{title}' file='{file_path.stem}'",
                        required_fix="frontmatter title과 파일명을 동일하게 맞춤",
                    )
                )

    if not notes:
        return CheckResult("N/A", "note-type이 있는 노트가 없음"), issues, notes
    if issues:
        return CheckResult("FAIL", f"{len(issues)}건의 frontmatter 위반"), issues, notes
    return CheckResult("PASS", "frontmatter 필수 규칙 충족"), issues, notes


def check_attachments_boundary(
    notes: Sequence[NoteRecord],
    vault_root: Path,
    index: LinkIndex,
    link_cache: Dict[Tuple[Path, str], LinkResolution],
) -> Tuple[CheckResult, List[Issue]]:
    issues: List[Issue] = []
    if not notes:
        return CheckResult("N/A", "attachments 경계 검사 대상 노트가 없음"), issues

    for note in notes:
        source_module = find_module_root(note.path, vault_root)
        for raw in parse_wikilinks(note.body):
            cleaned = clean_link_target(raw)
            if not cleaned:
                continue

            if "attachments/" not in cleaned.replace("\\", "/") and Path(cleaned).suffix.lower() not in ATTACHMENT_EXTENSIONS:
                continue

            key = (note.path, cleaned)
            resolution = link_cache.get(key)
            if resolution is None:
                resolution = resolve_link(note.path, cleaned, vault_root, index)
                link_cache[key] = resolution

            if resolution.status != "ok" or resolution.resolved is None:
                continue

            resolved = resolution.resolved.resolve()
            if "attachments" not in [p.lower() for p in resolved.parts]:
                continue

            target_module = find_module_root(resolved, vault_root)
            if source_module != target_module:
                issues.append(
                    Issue(
                        check="attachments-boundary",
                        path=str(note.path.relative_to(vault_root)),
                        message=f"cross-module attachment link: [[{cleaned}]]",
                        required_fix="동일 모듈(또는 동일 서브모듈)의 attachments로 파일을 이동/복제 후 링크 갱신",
                    )
                )

    if issues:
        return CheckResult("FAIL", f"{len(issues)}건의 attachments 경계 위반"), issues
    return CheckResult("PASS", "attachments 경계 규칙 충족"), issues


def check_reference_note_location(
    notes: Sequence[NoteRecord],
    vault_root: Path,
) -> Tuple[CheckResult, List[Issue]]:
    issues: List[Issue] = []
    reference_notes = [note for note in notes if note.note_type == "REFERENCE"]
    if not reference_notes:
        return CheckResult("N/A", "REFERENCE 노트가 없어 위치 검사를 생략"), issues

    for note in reference_notes:
        module_root = find_module_root(note.path, vault_root)
        expected_root = (module_root / "references").resolve()
        note_path = note.path.resolve()
        try:
            note_path.relative_to(expected_root)
        except ValueError:
            try:
                module_label = str(module_root.relative_to(vault_root))
            except ValueError:
                module_label = str(module_root)
            issues.append(
                Issue(
                    check="reference-note-location",
                    path=str(note.path.relative_to(vault_root)),
                    message=f"REFERENCE note is outside references/: {note.path.name}",
                    required_fix=f"`{module_label}/references/` 경로로 이동하고 관련 wikilink를 점검",
                )
            )

    if issues:
        return CheckResult("FAIL", f"{len(issues)}건의 REFERENCE 위치 위반"), issues
    return CheckResult("PASS", "REFERENCE 노트 위치 규칙 충족"), issues


def run_git(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def get_tracked_files(vault_root: Path) -> Optional[set]:
    proc = run_git(["git", "-c", "core.quotepath=false", "ls-files"], vault_root)
    if proc.returncode != 0:
        return None
    tracked = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            tracked.add(line.replace("\\", "/"))
    return tracked


def get_git_modified_markdown(vault_root: Path, scopes: Sequence[Path]) -> Tuple[Optional[List[Path]], str]:
    proc = run_git(["git", "-c", "core.quotepath=false", "status", "--porcelain"], vault_root)
    if proc.returncode != 0:
        return None, proc.stderr.strip() or "git status 실행 실패"

    tracked = get_tracked_files(vault_root)
    if tracked is None:
        return None, "tracked file 목록 조회 실패"

    modified: List[Path] = []
    seen = set()
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2]
        path_part = line[3:].strip()
        path_part = path_part.strip('"')
        if "->" in path_part:
            path_part = path_part.split("->", 1)[1].strip()
        if not path_part.endswith(".md"):
            continue
        if "M" not in status:
            continue
        normalized = path_part.replace("\\", "/")
        if normalized not in tracked:
            continue

        abs_path = (vault_root / normalized).resolve()
        if not abs_path.exists():
            continue
        if scopes and not path_in_scope(abs_path, scopes):
            continue
        if abs_path in seen:
            continue
        modified.append(abs_path)
        seen.add(abs_path)

    return modified, ""


def check_last_updated_git_modified(
    enabled: bool,
    notes_in_scope: Sequence[NoteRecord],
    vault_root: Path,
    scopes: Sequence[Path],
    today: str,
) -> Tuple[CheckResult, List[Issue]]:
    issues: List[Issue] = []

    if not enabled:
        return CheckResult("N/A", "--check-git-modified 옵션 비활성화"), issues

    modified_files, err = get_git_modified_markdown(vault_root, scopes)
    if modified_files is None:
        return CheckResult("N/A", f"git 정보를 읽을 수 없음: {err}"), issues
    if not modified_files:
        return CheckResult("N/A", "git 기준 수정된 기존 markdown 노트가 없음"), issues

    note_map = {n.path.resolve(): n for n in notes_in_scope}
    for path in modified_files:
        note = note_map.get(path.resolve())
        if note is None:
            content = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)
            note_type = str(fm.get("note-type", "")).strip()
            note = NoteRecord(path=path, note_type=note_type, frontmatter=fm, body=body)

        last_updated = str(note.frontmatter.get("last-updated", "")).strip()
        if last_updated != today:
            issues.append(
                Issue(
                    check="last-updated-git-modified",
                    path=str(path.relative_to(vault_root)),
                    message=f"last-updated='{last_updated}' (expected '{today}')",
                    required_fix=f"수정된 기존 노트의 last-updated를 {today}로 갱신",
                )
            )

    if issues:
        return CheckResult("FAIL", f"{len(issues)}건의 last-updated 미갱신"), issues
    return CheckResult("PASS", "git 수정 노트의 last-updated 규칙 충족"), issues


def build_report(
    target_labels: List[str],
    check_results: Dict[str, CheckResult],
    issues: List[Issue],
) -> Dict[str, object]:
    overall_status = "FAIL" if any(v.status == "FAIL" for v in check_results.values()) else "PASS"
    accepted = sum(1 for v in check_results.values() if v.status == "PASS")
    rejected = sum(1 for v in check_results.values() if v.status == "FAIL")
    n_a = sum(1 for v in check_results.values() if v.status == "N/A")

    checks = [
        {"name": name, "status": result.status, "reason": result.reason}
        for name, result in check_results.items()
    ]
    issue_payload = [
        {
            "check": i.check,
            "path": i.path,
            "message": i.message,
            "required_fix": i.required_fix,
        }
        for i in issues
    ]

    next_action = (
        ["FAIL 항목을 수정한 뒤 validate_vault.py를 재실행"] if overall_status == "FAIL" else ["현재 규칙 기준 PASS"]
    )

    return {
        "status": overall_status,
        "target": target_labels,
        "checks": checks,
        "issues": issue_payload,
        "summary": {"accepted": accepted, "rejected": rejected, "n_a": n_a},
        "next_action": next_action,
    }


def print_text_report(report: Dict[str, object]) -> None:
    def safe_print(line: str) -> None:
        text = f"{line}\n"
        encoding = sys.stdout.encoding or "utf-8"
        sys.stdout.buffer.write(text.encode(encoding, errors="replace"))

    safe_print("VALIDATION_REPORT")
    safe_print(f"status: {report['status']}")
    safe_print(f"target: {', '.join(report['target'])}")
    safe_print("checks:")
    for c in report["checks"]:
        safe_print(f"  - {c['name']}: {c['status']} - {c['reason']}")

    safe_print("issues:")
    if report["issues"]:
        for issue in report["issues"]:
            safe_print(f"  - {issue['path']}: {issue['message']} -> {issue['required_fix']}")
    else:
        safe_print("  - none")

    summary = report["summary"]
    safe_print("summary:")
    safe_print(f"  accepted: {summary['accepted']}")
    safe_print(f"  rejected: {summary['rejected']}")
    safe_print(f"  n_a: {summary['n_a']}")
    safe_print("next_action:")
    for step in report["next_action"]:
        safe_print(f"  - {step}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Obsidian vault contracts for vault-manage skill.")
    parser.add_argument("--target", action="append", default=[], help="Target file or directory to scan. Repeatable.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument(
        "--check-git-modified",
        action="store_true",
        help="Validate `last-updated` for git-modified existing markdown notes.",
    )
    parser.add_argument(
        "--today",
        default=date.today().strftime("%Y-%m-%d"),
        help="Expected last-updated date (YYYY-MM-DD) for --check-git-modified.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not DATE_RE.match(args.today):
        print("--today must follow YYYY-MM-DD", file=sys.stderr)
        return 1

    vault_root = Path.cwd().resolve()
    targets = choose_targets(vault_root, args.target)
    if not targets:
        report = build_report(
            target_labels=args.target or DEFAULT_SCAN_ROOTS,
            check_results={
                "dead-links": CheckResult("N/A", "대상 경로 없음"),
                "metadata-required-fields": CheckResult("N/A", "대상 경로 없음"),
                "attachments-boundary": CheckResult("N/A", "대상 경로 없음"),
                "reference-note-location": CheckResult("N/A", "대상 경로 없음"),
                "last-updated-git-modified": CheckResult("N/A", "대상 경로 없음"),
            },
            issues=[],
        )
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_text_report(report)
        return 0

    scan_files = collect_files(targets)
    index_roots = choose_index_roots(vault_root, targets)
    index_files = collect_index_files(index_roots)
    link_index = LinkIndex(vault_root, index_files)

    dead_links_result, dead_link_issues, link_cache = check_dead_links(scan_files, vault_root, link_index)
    frontmatter_result, frontmatter_issues, notes = check_frontmatter(scan_files, vault_root)
    attachment_result, attachment_issues = check_attachments_boundary(notes, vault_root, link_index, link_cache)
    reference_location_result, reference_location_issues = check_reference_note_location(notes, vault_root)
    last_updated_result, last_updated_issues = check_last_updated_git_modified(
        enabled=args.check_git_modified,
        notes_in_scope=notes,
        vault_root=vault_root,
        scopes=targets,
        today=args.today,
    )

    check_results = {
        "dead-links": dead_links_result,
        "metadata-required-fields": frontmatter_result,
        "attachments-boundary": attachment_result,
        "reference-note-location": reference_location_result,
        "last-updated-git-modified": last_updated_result,
    }
    all_issues = (
        dead_link_issues
        + frontmatter_issues
        + attachment_issues
        + reference_location_issues
        + last_updated_issues
    )

    target_labels = [str(t.relative_to(vault_root)) if t.is_absolute() else str(t) for t in targets]
    report = build_report(target_labels, check_results, all_issues)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text_report(report)

    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
