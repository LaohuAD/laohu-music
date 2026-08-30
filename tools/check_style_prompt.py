#!/usr/bin/env python3
"""Validate a configured Unicode character limit for a music style prompt."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Project working budget only. Callers must pass the verified platform/model
# hard limit when they intend to validate an external interface constraint.
DEFAULT_LIMIT = 1000

LINT_RULES = (
    (
        "technical-setting",
        re.compile(
            r"\b(?:sample\s*rate|bit\s*rate|bitrate|(?:32|44(?:\.1)?|48|88(?:\.2)?|96|192)\s*k?hz|mp3|wav|flac|aac)\b",
            re.IGNORECASE,
        ),
        "technical sample-rate, bitrate, or file-format settings usually belong in platform fields",
    ),
    (
        "editing-command",
        re.compile(
            r"\b(?:extract|remove|separate|isolate|isolated\s+(?:female\s+|male\s+)?vocal|only\s+vocals?)\b",
            re.IGNORECASE,
        ),
        "editing or isolation language needs a documented editing interface and an audio target",
    ),
    (
        "weak-negative",
        re.compile(
            r"\bno\s+(?:reverb|background\s+noise|backing\s+vocals?|instruments?|drums?|bass)\b",
            re.IGNORECASE,
        ),
        "bare negative wording may be ignored; prefer a positive sound target or a supported Exclude field",
    ),
)


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


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None and args.file is not None:
        raise ValueError("use either --text or --file, not both")
    if args.text is not None:
        return args.text
    if args.file is not None:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise ValueError("provide --text, --file, or stdin")


def lint_prompt(text: str) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    for code, pattern, message in LINT_RULES:
        for match in pattern.finditer(text):
            warnings.append({"code": code, "match": match.group(0), "message": message})
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a configured Style Prompt Unicode limit (default: project working budget, not a platform fact)."
    )
    parser.add_argument("--text", help="Style Prompt text")
    parser.add_argument("--file", help="Read Style Prompt from a UTF-8 file")
    parser.add_argument("--section", help="Extract a Markdown/plain-text section before counting")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--lint", action="store_true", help="Warn about likely interface/field mismatches")
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Return a non-zero exit code when lint warnings are present",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    try:
        text = read_input(args)
        if args.section:
            text = extract_section(text, args.section)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    count = len(text)
    warnings = lint_prompt(text) if args.lint or args.strict_warnings else []
    result = {
        "count": count,
        "limit": args.limit,
        "within_limit": count <= args.limit,
        "section": args.section,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        state = "PASS" if result["within_limit"] else "FAIL"
        print(f"{state}: {count}/{args.limit} Unicode characters")
        if args.section:
            print(f"section: {args.section}")
        for warning in warnings:
            print(f"WARN [{warning['code']}]: {warning['match']!r} — {warning['message']}")
    passed = result["within_limit"] and not (args.strict_warnings and warnings)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
