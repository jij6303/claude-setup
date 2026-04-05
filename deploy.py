"""
claude-setup 배포 스크립트

사용법:
    python deploy.py <target_repo_path>

배포 내용:
    - CLAUDE.md             (Claude Code 자동 로드 진입점)
    - .claude/rules/rules.md (작업 규칙 + 봇 사용 지침)
    - github/               (GitHub Bot 모듈)
    - github_bot.json       (루트 설정 기반, repo 필드만 대상으로 교체)
    - github_bot.json.example
"""
import argparse
import json
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "template"
BOT_CONFIG_PATH = Path(__file__).parent / "github_bot.json"


def validate_target(target: Path):
    if not target.exists():
        print(f"오류: 경로가 존재하지 않습니다 — {target}")
        sys.exit(1)
    if not target.is_dir():
        print(f"오류: 디렉토리가 아닙니다 — {target}")
        sys.exit(1)
    if not (target / ".git").exists():
        print(f"오류: Git 레포지토리가 아닙니다 — {target}")
        sys.exit(1)


def copy_template(target: Path):
    for src in TEMPLATE_DIR.rglob("*"):
        if src.is_dir():
            continue

        rel = src.relative_to(TEMPLATE_DIR)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        dst.write_bytes(src.read_bytes())
        print(f"  복사: {rel}")


def copy_bot_config(target: Path):
    dst = target / "github_bot.json"
    if not BOT_CONFIG_PATH.exists():
        print("  건너뜀: 루트 github_bot.json 없음")
        return

    config = json.loads(BOT_CONFIG_PATH.read_text(encoding="utf-8"))
    config["repo"] = target.name
    dst.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  복사: github_bot.json (repo → {target.name})")


def warn_if_gitignore_missing(target: Path):
    gitignore = target / ".gitignore"
    entry = "github_bot.json"

    if not gitignore.exists():
        print(f"\n주의: .gitignore 파일이 없습니다. {entry}를 직접 추가하세요.")
        return

    if entry not in gitignore.read_text(encoding="utf-8"):
        print(f"\n주의: .gitignore에 '{entry}'가 없습니다. 자격증명 커밋을 방지하려면 추가하세요.")


def print_next_steps(target: Path):
    print("\n========================================")
    print("배포 완료!")
    print("========================================")
    print("\n다음 단계:")
    print(f"  1. github_bot.json의 owner/repo 필드가 올바른지 확인")
    print("  2. .gitignore에 github_bot.json 추가")
    print("\nClaude Code 실행 시 .claude/rules/rules.md가 자동으로 로드됩니다.")


def main():
    parser = argparse.ArgumentParser(description="claude-setup을 대상 레포에 배포")
    parser.add_argument("target", help="배포 대상 레포지토리 경로")
    args = parser.parse_args()

    target = Path(args.target).resolve()

    print(f"배포 대상: {target}")
    validate_target(target)

    print("\n파일 복사 중...")
    copy_template(target)
    copy_bot_config(target)

    warn_if_gitignore_missing(target)
    print_next_steps(target)


if __name__ == "__main__":
    main()
