# Vault Routing Map

## Quick Map

| 요청 신호 | 우선 하위 스킬 | 메모 |
| :--- | :--- | :--- |
| "아이디어 정리해", "논리 이상한지 봐줘", "관점 더 뽑아줘" | `note-brainstorming` | 질문/진단 중심 |
| "더 좋아지게", "가독성", "뭔가 이상해", "마음에 안 들어", "같이 고민하자" | `note-brainstorming` | 품질 개선 대화가 우선 |
| "노트 써줘", "초안 작성", "리라이트", "요약해서 노트로" | `vault-content` | 본문/구조 설계 중심 |
| "frontmatter 맞춰", "모듈 만들기", "파일 옮겨", "검증해" | `vault-manage` | 구조/계약 적용 중심 |
| "이미지만 따줘", "광고 없이 포스터만", "웹페이지 사진 레퍼런스 저장" | `playwright-image-reference` | 웹 이미지 확보 중심 |

## Tie-Breakers

- 본문 뜻과 구조가 바뀌면 `vault-content`
- 파일 계약과 위치가 바뀌면 `vault-manage`
- 아직 결론보다 질문이 더 중요하면 `note-brainstorming`
- 노트의 품질을 더 높이기 위한 대화 의도가 보이면 `note-brainstorming`
- 웹페이지 설명보다 이미지 자체를 깨끗하게 확보하는 일이 핵심이면 `playwright-image-reference`
- 사용자가 명시한 note-type은 가능한 한 유지한다
- 사용자가 실행 신호를 주면 브레인스토밍을 멈추고 작성 단계로 넘어간다
- 초안 후 만족하지 않으면 브레인스토밍으로 다시 들어간다
- 대상 노트, 섹션, 산출물 타입이 바뀌면 focus 전환으로 보고 이전 문서 포맷 기억은 기본적으로 리셋한다
- 이전 브레인스토밍 맥락이 최신 요구와 충돌하거나 애매하면 짧게 확인 질문을 한다
- 사용자가 명시적으로 요청하지 않은 한 직전 문서 형식을 새 target에 자동 적용하지 않는다

## Common Sequences

- `note-brainstorming -> plan 공개 -> vault-content`
- `vault-content -> vault-manage`
- `playwright-image-reference -> vault-content`
- `playwright-image-reference -> vault-manage`
- `note-brainstorming -> plan 공개 -> vault-content -> vault-manage`
- `note-brainstorming -> vault-content -> note-brainstorming -> vault-content`

## Avoid

- 사용자에게 같은 범위/언어/우선순위를 다시 묻기
- 작은 후속 작업 때문에 새 흐름처럼 끊기
- 구조 문제를 이유로 본문 작성을 불필요하게 지연하기
- 초안 전 작업 계획을 사용자에게 보이지 않은 채 바로 본문부터 쓰기
- focus가 전환됐는데도 직전 문서의 형식을 자동으로 끌고 가기
