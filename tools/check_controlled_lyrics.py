#!/usr/bin/env python3
"""Verify generated lyrics against locked text and validate control placement."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SECTION_TAGS = {
    "intro", "verse", "pre-chorus", "chorus", "post-chorus",
    "bridge", "interlude", "transition", "break", "hook", "build-up",
    "instrumental", "inst", "solo", "outro",
}
NUMBERABLE_SECTION_TAGS = {
    "verse", "pre-chorus", "chorus", "post-chorus",
    "bridge", "interlude", "transition", "break", "hook", "build-up",
    "instrumental", "inst", "solo",
}

SECTION_ALIASES = {
    "pre chorus": "pre-chorus",
    "post chorus": "post-chorus",
    "build up": "build-up",
}

DOCUMENTED_LINE_CONTROLS: set[str] = set()
PROJECT_TESTED_LINE_CONTROLS: set[str] = set()
GLOBAL_FIELD_PATTERN = re.compile(
    r"\b(?:bpm|tempo|time\s*signature|genre|sample\s*rate|bit\s*rate|bitrate|"
    r"(?:32|44(?:\.1)?|48|88(?:\.2)?|96|192)\s*k?hz|mp3|wav|flac|aac)\b",
    re.IGNORECASE,
)
LOCAL_TEMPO_CHANGE_PATTERN = re.compile(
    r"\b(?:slow(?:er|ly)?|decelerate|ritard(?:ando)?|rubato|free[- ]?time|"
    r"drag(?:ging)?|half[- ]?time|double[- ]?time)\b",
    re.IGNORECASE,
)


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def extract_section(text: str, section: str) -> str:
    heading = re.compile(rf"^\s{{0,3}}(?:#+\s*)?{re.escape(section)}\s*:?\s*$", re.IGNORECASE)
    lines = text.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if heading.match(line.rstrip("\r\n")):
            start = index + 1
            break
    if start is None:
        raise ValueError(f"section not found: {section}")

    end = len(lines)
    for index in range(start, len(lines)):
        if re.match(r"^\s{0,3}#{1,6}\s+\S", lines[index]):
            end = index
            break
    section_text = "".join(lines[start:end]).strip("\r\n")
    section_lines = section_text.splitlines()
    if len(section_lines) >= 2 and section_lines[0].strip().startswith("```") and section_lines[-1].strip() == "```":
        section_text = "\n".join(section_lines[1:-1])
    return section_text


def validate_package_fields(text: str, lyrics_section: str) -> list[str]:
    suffix = next(
        (item for item in (" AI Lyrics", " Controlled Lyrics")
         if lyrics_section.lower().endswith(item.lower())),
        None,
    )
    if suffix is None:
        return ["--section must end with 'AI Lyrics' or 'Controlled Lyrics' to derive the scheme name"]
    scheme = lyrics_section[:-len(suffix)].strip()
    required = [f"{scheme} 演唱风格", f"{scheme} Style Prompt"]
    if suffix.lower() == " ai lyrics":
        required.append(f"{scheme} 演唱控制谱")
    required.extend([lyrics_section, f"{scheme} Platform Assumptions"])
    positions: list[int] = []
    errors: list[str] = []
    for heading_text in required:
        heading = re.compile(
            rf"^\s{{0,3}}#+\s*{re.escape(heading_text)}\s*:?\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = heading.search(text)
        if not match:
            errors.append(f"missing package field: {heading_text}")
            continue
        positions.append(match.start())
        try:
            if not extract_section(text, heading_text).strip():
                errors.append(f"empty package field: {heading_text}")
        except ValueError:
            errors.append(f"unreadable package field: {heading_text}")
    if len(positions) == len(required) and positions != sorted(positions):
        errors.append("package fields are not in the required order")
    return errors


def canonical_section_tag(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip().lower())
    numbered = re.fullmatch(r"(.+?)\s+\d+", normalized)
    if numbered:
        base = SECTION_ALIASES.get(numbered.group(1), numbered.group(1))
        if base in NUMBERABLE_SECTION_TAGS:
            return base
    return SECTION_ALIASES.get(normalized, normalized)


def is_section_tag(name: str) -> bool:
    normalized = canonical_section_tag(name)
    return normalized in SECTION_TAGS


def normalize(text: str, allow_performance_reflow: bool = False) -> str:
    output: list[str] = []
    inline_control = re.compile(r"\[\[(?:[^\]]|\](?!\]))*\]\]")
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r")
        stripped = line.strip()
        if not stripped:
            output.append("")
            continue
        section_match = re.fullmatch(r"\[\s*([^|｜:\]]+?)(?:\s*[|｜:].*)?\]", stripped)
        if section_match and is_section_tag(section_match.group(1)):
            output.append(f"[{canonical_section_tag(section_match.group(1))}]")
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            continue
        output.append(inline_control.sub("", line))
    normalized = "\n".join(output).strip()
    if allow_performance_reflow:
        # Performance-ready lyrics may regroup adjacent lyric lines because some
        # generators treat line breaks as phrase or breath boundaries. Preserve
        # every non-whitespace character and the canonical section sequence.
        return re.sub(r"\s+", "", normalized)
    return normalized


def lint_controls(text: str, control_syntax: str = "auto") -> list[dict[str, object]]:
    warnings: list[dict[str, object]] = []
    current_section = "preamble"
    current_section_key = ("preamble", 0)
    section_occurrences: dict[str, int] = {}
    annotation_lines: dict[tuple[str, int], list[int]] = {}

    lines = text.splitlines()
    for line_number, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if "｜" in stripped and not (stripped.startswith("[") and stripped.endswith("]")):
            warnings.append({
                "code": "control-outside-brackets",
                "line": line_number,
                "section": current_section,
                "match": stripped,
                "message": "the full-width separator must stay inside a section or line-control bracket",
            })
            continue
        if not (stripped.startswith("[") and stripped.endswith("]")):
            continue

        section_match = re.fullmatch(r"\[\s*([^|｜:\]]+?)(?:\s*([|｜:])(.*))?\]", stripped)
        if section_match and is_section_tag(section_match.group(1)):
            current_section = section_match.group(1).strip()
            canonical_section = canonical_section_tag(current_section)
            section_occurrences[canonical_section] = section_occurrences.get(canonical_section, 0) + 1
            current_section_key = (canonical_section, section_occurrences[canonical_section])
            control_text = (section_match.group(3) or "").strip()
            if control_text:
                delimiter = section_match.group(2)
                if control_syntax == "standard":
                    warnings.append({
                        "code": "unexpected-section-control",
                        "line": line_number,
                        "section": current_section,
                        "match": control_text,
                        "message": "standard-tag mode does not allow embedded section controls",
                    })
                elif delimiter != "｜":
                    warnings.append({
                        "code": "wrong-control-delimiter",
                        "line": line_number,
                        "section": current_section,
                        "match": delimiter or "",
                        "message": "embedded section controls must use the full-width separator ｜",
                    })
                global_match = GLOBAL_FIELD_PATTERN.search(control_text)
                if global_match:
                    warnings.append({
                        "code": "global-field-in-local-control",
                        "line": line_number,
                        "section": current_section,
                        "match": global_match.group(0),
                        "message": "global music or technical settings do not belong in AI Lyrics local controls",
                    })
                directive_count = len([item for item in control_text.split("｜") if item.strip()])
                if directive_count > 4:
                    warnings.append({
                        "code": "section-directive-density",
                        "line": line_number,
                        "section": current_section,
                        "match": str(directive_count),
                        "message": "more than four section directives; verify that each one is compatible with the Style Prompt and needed for this section handoff",
                    })
                tempo_match = LOCAL_TEMPO_CHANGE_PATTERN.search(control_text)
                if tempo_match:
                    warnings.append({
                        "code": "local-tempo-change",
                        "line": line_number,
                        "section": current_section,
                        "match": tempo_match.group(0),
                        "message": "a local tempo-changing instruction can reset the vocal and accompaniment pulse; verify it against the Style Prompt and adjacent section handoff",
                    })
            continue

        bracket_pipe_line = re.fullmatch(r"\[\((.+)\)\]", stripped)
        if bracket_pipe_line and control_syntax != "standard":
            annotation_lines.setdefault(current_section_key, []).append(line_number)
            control_text = bracket_pipe_line.group(1).strip()
            if "|" in control_text:
                warnings.append({
                    "code": "wrong-control-delimiter",
                    "line": line_number,
                    "section": current_section,
                    "match": "|",
                    "message": "line controls must separate directives with the full-width separator ｜",
                })
            directive_count = len([item for item in control_text.split("｜") if item.strip()])
            if directive_count > 3:
                warnings.append({
                    "code": "line-directive-density",
                    "line": line_number,
                    "section": current_section,
                    "match": str(directive_count),
                    "message": "more than three line directives; verify that each action is unique, mutually compatible, and anchored to the section pulse",
                })
            tempo_match = LOCAL_TEMPO_CHANGE_PATTERN.search(control_text)
            if tempo_match:
                warnings.append({
                    "code": "local-tempo-change",
                    "line": line_number,
                    "section": current_section,
                    "match": tempo_match.group(0),
                    "message": "a line-level tempo change can pull the accompaniment off the global pulse; verify it is explicitly allowed by the Style Prompt",
                })
            next_content = lines[line_number].strip() if line_number < len(lines) else ""
            if not next_content or (next_content.startswith("[") and next_content.endswith("]")):
                warnings.append({
                    "code": "orphan-line-control",
                    "line": line_number,
                    "section": current_section,
                    "match": control_text,
                    "message": "a line control must sit immediately above a lyric line, not another tag or the end of the section",
                })
            continue

        control_text = stripped[1:-1].strip()
        if control_syntax == "bracket-pipe":
            warnings.append({
                "code": "wrong-line-control-format",
                "line": line_number,
                "section": current_section,
                "match": control_text,
                "message": "line controls must use [(directive 1｜directive 2)] on the line above the target lyric",
            })
            continue

        annotation_lines.setdefault(current_section_key, []).append(line_number)
        control_name = control_text.split(":", 1)[0].strip().lower()
        if control_name not in DOCUMENTED_LINE_CONTROLS | PROJECT_TESTED_LINE_CONTROLS:
            warnings.append({
                "code": "unverified-line-control",
                "line": line_number,
                "section": current_section,
                "match": control_name or control_text,
                "message": "local syntax is not documented, project-tested, or specified for the current interface",
            })
        global_match = GLOBAL_FIELD_PATTERN.search(control_text)
        if global_match:
            warnings.append({
                "code": "global-field-in-local-control",
                "line": line_number,
                "section": current_section,
                "match": global_match.group(0),
                "message": "global music or technical settings do not belong in AI Lyrics local controls",
            })

    for (section, occurrence), line_numbers in annotation_lines.items():
        if len(line_numbers) > 3:
            warnings.append({
                "code": "control-density",
                "line": line_numbers[2],
                "section": f"{section} #{occurrence}",
                "match": str(len(line_numbers)),
                "message": "more than three local control annotations in one section; verify musical continuity and each duty by A/B testing",
            })
    return warnings


def count_controls(text: str) -> int:
    """Count section-level and line-level performance controls."""
    count = 0
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not (stripped.startswith("[") and stripped.endswith("]")):
            continue
        section_match = re.fullmatch(r"\[\s*([^|｜:\]]+?)(?:\s*([|｜:])(.*))?\]", stripped)
        if section_match and is_section_tag(section_match.group(1)):
            if (section_match.group(3) or "").strip():
                count += 1
            continue
        if re.fullmatch(r"\[\(.+\)\]", stripped):
            count += 1
        else:
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare locked lyrics with platform-ready generated lyrics.")
    parser.add_argument("--lyrics", required=True, help="Locked lyric file")
    parser.add_argument(
        "--ai-lyrics",
        "--controlled-lyrics",
        dest="ai_lyrics",
        required=True,
        help="Platform-ready AI Lyrics package; --controlled-lyrics remains as a compatibility alias",
    )
    parser.add_argument("--section", help="Extract an AI Lyrics or Controlled Lyrics section from a combined Markdown package")
    parser.add_argument(
        "--require-controls",
        action="store_true",
        help="For an experimental control test only: fail when no local performance control is present",
    )
    parser.add_argument(
        "--require-package-fields",
        action="store_true",
        help="Require Singing Style, Style Prompt, final generated lyrics, and Platform Assumptions; standard AI Lyrics also require a performance map",
    )
    parser.add_argument(
        "--control-syntax",
        choices=("auto", "bracket-pipe", "standard"),
        default="auto",
        help="Validate the current interface syntax: bracket-pipe accepts [Section ｜ ...] and [(...)]",
    )
    parser.add_argument("--lint", action="store_true", help="Warn about dense, unknown, or misplaced controls")
    parser.add_argument(
        "--allow-performance-reflow",
        action="store_true",
        help="Allow spaces and line breaks to change while preserving all non-whitespace lyric characters and section order",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Return a non-zero exit code when lint warnings are present",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        locked_text = read_text(args.lyrics)
        package_text = read_text(args.ai_lyrics)
        package_errors = (
            validate_package_fields(package_text, args.section or "")
            if args.require_package_fields
            else []
        )
        controlled_text = package_text
        if args.section:
            controlled_text = extract_section(controlled_text, args.section)
        expected = normalize(locked_text, args.allow_performance_reflow)
        actual = normalize(controlled_text, args.allow_performance_reflow)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    control_count = count_controls(controlled_text)
    warnings = lint_controls(controlled_text, args.control_syntax) if args.lint or args.strict_warnings else []
    result = {
        "match": expected == actual,
        "controls_present": control_count > 0,
        "control_count": control_count,
        "package_complete": not package_errors,
        "package_errors": package_errors,
        "locked_length": len(expected),
        "controlled_length": len(actual),
        "section": args.section,
        "match_mode": "performance-reflow" if args.allow_performance_reflow else "exact-layout",
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["match"]:
        mode = " with performance reflow" if args.allow_performance_reflow else ""
        print(f"PASS: generated lyrics preserve locked text{mode} ({len(expected)} characters)")
        if args.section:
            print(f"section: {args.section}")
        if control_count or args.require_controls:
            print(f"local lyric controls: {control_count}")
    else:
        print("FAIL: generated lyrics changed the locked text", file=sys.stderr)
        print(f"locked:     {len(expected)} characters", file=sys.stderr)
        print(f"controlled: {len(actual)} characters", file=sys.stderr)
    if not args.as_json:
        for error in package_errors:
            print(f"FAIL: {error}", file=sys.stderr)
        for warning in warnings:
            print(
                f"WARN [{warning['code']}] line {warning['line']} "
                f"({warning['section']}): {warning['match']!r} — {warning['message']}"
            )
    if args.require_controls and not result["controls_present"]:
        print("FAIL: experimental Controlled Lyrics contain no local controls", file=sys.stderr)
    passed = (
        result["match"]
        and not (args.require_controls and not result["controls_present"])
        and not package_errors
        and not (args.strict_warnings and warnings)
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
