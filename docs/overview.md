# claude-setup 개요

Claude Code를 새 레포지토리에 빠르게 세팅하기 위한 **배포 도구**다.
`deploy.py` 한 줄로 Claude 작업 규칙과 GitHub Bot 모듈을 대상 레포에 심는다.

---

## 무엇을 하는가

### 문제

Claude Code는 레포마다 CLAUDE.md를 읽어 작업 방식을 결정한다.
GitHub 작업(이슈/브랜치/PR/리뷰 요청)을 `gh` CLI 없이 GitHub App으로 처리하려면
인증 코드와 스크립트를 매번 새 레포에 복사해야 한다.

### 해결

이 레포가 **템플릿 저장소** 역할을 한다.
`deploy.py`를 실행하면 아래 파일들이 대상 레포에 그대로 복사된다.

```
CLAUDE.md                  ← Claude Code 자동 로드 진입점
.claude/rules/rules.md     ← 작업 규칙 (워크플로우, Git 컨벤션)
github/                    ← GitHub Bot 모듈
github_bot.json            ← GitHub App 자격증명 (gitignore 자동 처리)
```

---

## 구성 요소

### `deploy.py` — 배포 스크립트

```bash
python deploy.py <대상_레포_경로>
```

- `template/` 하위 파일 전체를 대상 레포에 복사
- `github_bot.json`을 `.gitignore`에 자동으로 추가 (없으면 생성)
- 대상 경로가 Git 레포인지 사전 검증

### `template/CLAUDE.md` — Claude Code 진입점

Claude Code가 실행될 때 가장 먼저 읽는 파일.
실제 내용은 `.claude/rules/rules.md`를 `@` 참조로 포함한다.

### `template/.claude/rules/rules.md` — 작업 규칙

Claude에게 이 레포에서 지켜야 할 규칙을 알려준다:

- GitHub 작업은 반드시 `github/` 모듈 사용 (gh CLI 금지)
- 작업 시작 순서: pull → 이슈 생성 → 브랜치 → 체크아웃 → 계획 코멘트 → 개발 → PR → 리뷰 요청
- 브랜치 명: `feature-#<이슈번호>`
- 커밋 메시지: `type(#N): description` (영어, 소문자, 마침표 없음)
- PR 제목: 영어, 본문: 한글, 첫 줄에 `Closes #N`

### `template/github/` — GitHub Bot 모듈

GitHub App 인증(JWT → Installation Token)을 사용해 API를 호출하는 Python 스크립트 모음.
`owner`/`repo`는 `git remote origin` URL에서 자동으로 파싱한다.

| 파일 | 기능 |
|------|------|
| `auth.py` | JWT 생성 및 Installation Access Token 발급 |
| `create_issue.py` | 이슈 생성 |
| `create_branch.py` | 브랜치 생성 |
| `create_pr.py` | PR 생성 |
| `request_review.py` | 리뷰 요청 |

각 스크립트는 단독 실행(`python github/create_issue.py --title "..."`)과
모듈 임포트(`from github.create_issue import create_issue`) 두 방식 모두 지원한다.

### `template/github_bot.json` — 자격증명 설정

```json
{
  "app_id": 1234567,
  "installation_id": 12345678,
  "private_key_path": "/절대경로/private-key.pem"
}
```

`owner`와 `repo`는 `git remote origin`에서 자동 감지하므로 설정 불필요.
이 파일은 `deploy.py`가 자동으로 `.gitignore`에 추가해 커밋되지 않도록 한다.

---

## 사용 흐름

```
[이 레포]                         [대상 레포]
deploy.py <path>  ──복사──►  CLAUDE.md
                             .claude/rules/rules.md
                             github/
                             github_bot.json  (gitignored)
                                    │
                             Claude Code 실행
                                    │
                             규칙 자동 적용 ──► github/ 봇으로 GitHub 작업
```

1. 이 레포를 클론
2. `python deploy.py ../my-other-repo` 실행
3. 대상 레포에서 `github_bot.json`에 GitHub App 자격증명 입력
4. 대상 레포에서 Claude Code 실행 → 규칙 자동 적용
