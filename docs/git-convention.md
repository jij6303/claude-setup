# Git Convention

`portfolio-web` 레포 커밋 로그 기반으로 파악한 컨벤션.

---

## 브랜치 네이밍

```
feature-#<이슈번호>
```

**예시**
- `feature-#5`
- `feature-#8`
- `feature-#10`

---

## 커밋 메시지

### 형식

```
type(#이슈번호): 설명
```

### 타입

| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 추가 |

> 현재 로그에서 확인된 타입은 `feat` 단일. 필요 시 `fix`, `refactor`, `docs`, `chore` 등 확장 가능.

### 예시

```
feat(#8): Rest API
feat(#8): template
feat(#5): add flask app
feat(#1): second commit
```

### 규칙

- 소문자로 작성
- 마침표 없음
- 이슈 번호 필수 (`#N`)

---

## PR 및 머지 전략

- GitHub PR을 통해 머지
- 머지 커밋 자동 생성: `Merge pull request #N from Injungg/feature-#N`
- feature 브랜치 → main 으로 머지

---

## 워크플로우 요약

```
1. 이슈 생성 (#N)
2. 브랜치 생성: feature-#N
3. 커밋: feat(#N): 설명
4. PR 오픈 → main에 머지
```
