---
trigger: always_on
---

# 📊 메타데이터 스키마

AI Agent가 노트의 메타데이터를 생성하거나 수정할 때 따라야 하는 스키마입니다.

---

## 1. 메타데이터 형식

메타데이터 관리 대상 노트는 **YAML Frontmatter** 형식의 메타데이터를 포함해야 합니다.

기본 대상:
- CORE / DEEP DIVE / SOLUTION / EVIDENCE / REVIEW / REFERENCE

예외:
- IDEA는 기본적으로 raw markdown 임시 노트를 허용한다.
- IDEA의 본문 성격과 승격 기준은 본문 규칙 문서를 따른다.
- 이 문서는 metadata를 실제로 부여해 관리하는 노트의 스키마를 정의한다.

```yaml
---
[필드명]: [값]
---
```

---

## 2. 공통 필드 (메타데이터 관리 대상 노트)

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `tags` | 리스트 | ✅ | 분류 태그 | `[개념, 컴퓨터과학]` |
| `aliases` | 리스트 | ✅ | 별칭 (이모지 포함) | `[💡 FSM]` |
| `created` | 날짜 | ✅ | 생성일 | `2025-12-17` |
| `title` | 문자열 | ✅ | 제목 (파일명과 동일) | `💡 유한 상태 머신` |
| `note-type` | 문자열 | ✅ | 노트 유형 | `CORE` |
| `description` | 문자열 | ✅ | AI가 읽을 수 있는 요약 | `FSM의 핵심 개념 정리` |
| `last-updated` | 날짜 | ✅ | 최종 수정일 | `2025-12-17` |

---

## 3. 노트 유형별 전용 필드

### 💡 CORE

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 💡 제목
note-type: CORE
related-document:      # 리스트 - 관련 DEEP DIVE, SOLUTION 등
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `related-document` | 리스트 | 이 개념을 확장한 노트들 링크 |

---

### 🧠 DEEP DIVE

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 🧠 제목
note-type: DEEP DIVE
core-concept:          # 리스트 - 탐구하는 CORE 노트
related-note:          # 리스트 - 함께 보면 좋은 관련 노트들
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `core-concept` | 리스트 | 탐구 대상 CORE 노트 링크 (필수) |
| `related-note` | 리스트 | 설명에 활용한 관련 노트 링크 (타입 제한 없음) |

---

### 🔬 SOLUTION

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 🔬 제목
note-type: SOLUTION
inspired-by:           # 리스트 - 영감 출처
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `inspired-by` | 리스트 | 영감을 얻은 노트/자료 링크 |

---

### 📝 EVIDENCE

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 📝 제목
note-type: EVIDENCE
ref-by:                # 리스트 - 참조한 Reference 노트
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `ref-by` | 리스트 | 참조한 Reference 노트 링크 |

---

### 🔍 REVIEW

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 🔍 제목
note-type: REVIEW
target-note:           # 링크 - 리뷰 대상 노트
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `target-note` | 링크 | 리뷰 대상 노트 (단일) |

---

### 📖 REFERENCE

```yaml
---
tags:
aliases:
created: YYYY-MM-DD
title: 📖 제목
note-type: REFERENCE
source:                # 문자열/URL - 출처
description:
last-updated: YYYY-MM-DD
---
```

| 전용 필드 | 타입 | 설명 |
|-----------|------|------|
| `source` | 문자열/URL | 원본 출처 1개. 온라인 출처면 검증된 URL, 오프라인 출처면 문헌 식별자 |

- REFERENCE 노트는 source 1개를 기준으로 관리한다.
- 기사, 논문, 공식 문서, 블로그, 보고서 페이지처럼 온라인 원문이 핵심인 출처는 `source`에 실제로 접속 검증한 URL 1개를 적는다.
- URL은 브라우저 도구 또는 웹 도구로 직접 열어 존재 여부, 문서 제목, 호스트가 맞는지 확인한 뒤 사용한다.
- 책, 오프라인 문헌, 내부 문서처럼 안정적인 웹 원문이 없는 출처만 URL 대신 문헌 식별자를 허용한다.
- 존재하지 않는 페이지 URL, 잘못된 리다이렉트 URL, 추정 URL은 `source`에 적지 않는다.
- source가 여러 개면 REFERENCE를 분리하거나, 묶음 해석이 목적이면 EVIDENCE로 전환한다.

---

### 💭 IDEA

- 기본값: frontmatter 없는 raw markdown 허용
- `note-type: IDEA`를 정식 관리 타입으로 사용하지 않는다.
- IDEA를 다른 타입으로 승격하는 순간, 해당 타입의 메타데이터 규칙을 적용한다.

---

## 4. 모듈 인덱스 노트 메타데이터

### 메인/서브 모듈 공통

```yaml
---
name: [이모지] 모듈명
created: YYYY-MM-DD
description: 모듈 한줄 설명
---
```

---

## 5. 값 형식 규칙

### 날짜
- **형식**: `YYYY-MM-DD`
- **예시**: `2025-12-17`

### 리스트
```yaml
tags:
  - 태그1
  - 태그2

# 또는 인라인
tags: [태그1, 태그2]
```

### 링크
```yaml
related-document:
  - "[[💡 노트1]]"
  - "[[🧠 노트2]]"

# 단일 링크
target-note: "[[💡 대상 노트]]"
```

### 빈 값
```yaml
tags:           # 빈 리스트로 남겨둠
aliases:
```

---

## 6. description 필드 작성 가이드

**핵심 원칙**: 본문을 읽지 않고도 노트가 무엇인지 알 수 있어야 함

**좋은 예시**:
```yaml
description: FSM의 정의, 4가지 구성요소, 장단점을 정리한 핵심 개념 노트
```

**나쁜 예시**:
```yaml
description: 유한 상태 머신에 대해서   # 너무 모호
description:                           # 비어있음
```

**권장 길이**: 1-2문장 (50-100자)

---

## 7. 메타데이터 검증 체크리스트

- [ ] 모든 필수 필드 존재
- [ ] `note-type` 값이 유효 (CORE/DEEP DIVE/SOLUTION/EVIDENCE/REVIEW/REFERENCE)
- [ ] raw IDEA 노트는 이 체크리스트의 직접 대상이 아님
- [ ] `title`과 파일명 일치
- [ ] 날짜 형식 `YYYY-MM-DD`
- [ ] `description` 비어있지 않음
- [ ] 링크 형식 `"[[노트명]]"` 사용
