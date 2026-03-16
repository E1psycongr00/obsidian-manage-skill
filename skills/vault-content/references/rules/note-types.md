---
trigger: always_on
---

# 📋 노트 유형 규칙 인덱스

이 파일은 노트 유형 상세 규칙의 진입점이다.
이 인덱스는 노트 유형의 의미와 본문 구조만 다룬다.
frontmatter 스키마, 필수 필드, 파일 위치, validator 규칙은 구조 계약 문서를 따른다.
유형 판정 기준은 `SKILL.md`의 `직관적 구분 기준`을 우선 사용한다.

## 유형별 상세 규칙 파일

| 유형 | 규칙 파일 |
| :--- | :--- |
| 💡 CORE | `references/rules/note-type-core.md` |
| 🧠 DEEP DIVE | `references/rules/note-type-deep-dive.md` |
| 🔬 SOLUTION | `references/rules/note-type-solution.md` |
| 📝 EVIDENCE | `references/rules/note-type-evidence.md` |
| 🔍 REVIEW | `references/rules/note-type-review.md` |
| 📖 REFERENCE | `references/rules/note-type-reference.md` |
| 💭 IDEA | `references/rules/note-type-idea.md` |

## 로딩 규칙

1. Type Plan에서 노트 유형을 1개 확정한다.
2. 확정한 유형의 상세 규칙 파일 1개만 로딩한다.
3. `references/rules/default-writing-style.md`는 항상 함께 적용한다.
