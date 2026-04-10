#!/usr/bin/env python3
"""HWP 파일을 PDF로 변환하는 간단한 CLI 프로그램.

필수 조건:
- LibreOffice(soffice)가 설치되어 있어야 합니다.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class ConversionError(RuntimeError):
    """변환 실패 시 사용하는 예외."""


def find_soffice(explicit_path: str | None) -> str:
    if explicit_path:
        soffice = Path(explicit_path)
        if not soffice.exists():
            raise FileNotFoundError(f"지정한 soffice 경로를 찾을 수 없습니다: {explicit_path}")
        return str(soffice)

    discovered = shutil.which("soffice")
    if discovered:
        return discovered

    raise FileNotFoundError(
        "soffice를 찾을 수 없습니다. LibreOffice를 설치하거나 --soffice 옵션으로 경로를 지정하세요."
    )


def convert_file(soffice: str, source: Path, output_dir: Path) -> Path:
    if source.suffix.lower() != ".hwp":
        raise ConversionError(f"HWP 파일만 지원합니다: {source}")
    if not source.exists():
        raise ConversionError(f"입력 파일이 존재하지 않습니다: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(source),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "(오류 메시지 없음)"
        raise ConversionError(f"변환 실패: {source.name}\n{stderr}")

    produced = output_dir / f"{source.stem}.pdf"
    if not produced.exists():
        raise ConversionError(
            f"변환 명령은 성공했지만 PDF가 생성되지 않았습니다: {produced}"
        )

    return produced


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HWP 파일을 PDF로 변환합니다.")
    parser.add_argument("inputs", nargs="+", help="변환할 .hwp 파일 경로(여러 개 가능)")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="./output_pdf",
        help="PDF 저장 폴더 (기본값: ./output_pdf)",
    )
    parser.add_argument(
        "--soffice",
        default=None,
        help="soffice 실행 파일 경로(미지정 시 PATH에서 자동 탐색)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        soffice = find_soffice(args.soffice)
    except FileNotFoundError as exc:
        print(f"[오류] {exc}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).resolve()
    failures: list[tuple[Path, str]] = []

    for raw in args.inputs:
        source = Path(raw).resolve()
        try:
            pdf = convert_file(soffice, source, output_dir)
            print(f"[완료] {source.name} -> {pdf}")
        except ConversionError as exc:
            failures.append((source, str(exc)))
            print(f"[실패] {source}: {exc}", file=sys.stderr)

    if failures:
        print(f"\n총 {len(failures)}개 파일 변환 실패", file=sys.stderr)
        return 1

    print("\n모든 파일 변환이 완료되었습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
