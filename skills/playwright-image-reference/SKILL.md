---
name: playwright-image-reference
description: Use when collecting image references from websites with Playwright MCP, especially when the image itself should be captured cleanly for notes, evidence, or visual references.
---

# Playwright Image Reference

웹페이지에서 `이미지 레퍼런스 자체`를 확보할 때만 사용한다.
핵심은 페이지 설명이 아니라 이미지 자체를 깨끗하게 가져오는 것이다.

## 사용할 때

- 웹사이트에서 참고 이미지를 가져오려는 경우
- 장면 스틸, 포스터, 제품 이미지, 무드 레퍼런스를 캡처하려는 경우
- `광고 없이`, `이미지 중심`, `이미지 자체만` 같은 요구가 있는 경우

## 도구 전제

- 기본 도구는 Playwright MCP다.
- Playwright MCP를 쓸 수 없으면 무리하게 대체하지 말고 막힌 이유를 짧게 알린다.

## 기본 원칙

- 목표는 `페이지`가 아니라 `이미지 자체`다.
- 광고나 사이트 헤더가 보이는 캡처는 잘못된 스크린샷이다.
- 가능하면 원본 이미지 URL 또는 이미지 element 자체를 우선 사용한다.
- 기사 본문이나 텍스트 블록은 이미지가 없더라도 기본 레퍼런스로 대체하지 않는다.
- 포스터/썸네일 자체의 텍스트는 허용하지만 사이트 UI 텍스트는 최대한 제외한다.

## 권장 워크플로

1. 페이지를 열고 이미지 후보를 찾는다.
2. 가능하면 `img`, `picture`, `figure` 안의 실제 이미지 소스를 확인한다.
3. 캡처는 `원본 이미지 URL -> 이미지 element -> 이미지 중심 컨테이너` 순으로 시도한다.
4. 캡처 후에는 반드시 다시 보고 통과 여부를 확인한다.

## Self-check

- [ ] 광고나 사이트 헤더는 전혀 보이지 않아야 한다.
- [ ] 이미지는 잘리지 않고 레퍼런스로 바로 쓸 만큼 분명해야 한다.
- [ ] 이 이미지가 왜 캡처됐는지, 어떤 레퍼런스인지 한눈에 드러나야 한다.
- [ ] 하나라도 어긋나면 다시 캡처한다.

## 결과 정리

- 이미지 파일을 남긴다.
- 원본 페이지 URL을 함께 남긴다.
- 왜 이 이미지가 필요한지 1~2문장만 짧게 덧붙인다.
