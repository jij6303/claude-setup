"""
claude-setup 배포 스크립트

사용법:
    python deploy.py <target_repo_path>

배포 내용:
    - CLAUDE.md             (Claude Code 자동 로드 진입점)
    - .claude/rules/rules.md (작업 규칙 + 봇 사용 지침)
    - github/               (GitHub Bot 모듈)
    - github_bot.json       (App 자격증명, owner/repo는 git remote에서 자동 감지)
"""
import argparse
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "template"


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


def ensure_gitignore(target: Path):
    gitignore = target / ".gitignore"
    entry = "/github_bot.json"

    if not gitignore.exists():
        gitignore.write_text(f"{entry}\n", encoding="utf-8")
        print(f"  생성: .gitignore ({entry})")
        return

    content = gitignore.read_text(encoding="utf-8")
    if "github_bot.json" not in content:
        gitignore.write_text(content.rstrip() + f"\n{entry}\n", encoding="utf-8")
        print(f"  수정: .gitignore ({entry} 추가)")


def print_next_steps():
    print("\n========================================")
    print("배포 완료!")
    print("========================================")
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
    ensure_gitignore(target)

    print_next_steps()


if __name__ == "__main__":
    main()
