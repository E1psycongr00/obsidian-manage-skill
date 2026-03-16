---
name: vault-manage
description: Obsidian Vault의 구조 운영 하위 스킬. 모듈 생성·이동·아카이빙, frontmatter 정합성, 파일 위치, 링크/attachments 경계, VALIDATION_REPORT 작성처럼 파일 계약과 거버넌스를 다룰 때 사용한다. 긴 본문 작성이나 note-type 의미 설계가 중심인 작업에는 쓰지 않는다.
---

# Vault Manage

이 스킬은 Obsidian Vault 운영을 위한 구조/거버넌스 전용 스킬이다.
이 스킬의 `references/`를 구조 계약의 단일 규칙 소스로 사용한다.

## 핵심 역할

- 구조 작업(생성/이동/아카이빙/개편)을 안전하게 수행한다.
- 구조 정합성(메타데이터, 링크, attachments 경계)을 검증한다.
- 결과를 `VALIDATION_REPORT` 형식으로 명확히 전달한다.

## 필수 불변 규칙

- Dead link를 생성하지 않는다.
- YAML Frontmatter 필수 필드를 누락하지 않는다(적용 대상인 경우).
- 모듈 경계를 넘는 `attachments/` 재사용을 금지한다.
- 적용되지 않는 검증 항목은 `N/A`로 처리하고 사유를 한 줄 남긴다.

## 범위 경계

- 구조 작업, 메타데이터 정합성, 링크/attachments 경계, validator 실행을 다룬다.
- 긴 본문 작성, 리라이트, note-type의 의미 설계는 직접 담당하지 않는다.

## 작업 유형 분류

| 요청 유형 | 주 처리 | 기본 로딩 파일 |
| :--- | :--- | :--- |
| 모듈 생성/이동/아카이빙/개편 | 구조 적용 | `references/rules/module-structure.md` |
| 메타데이터 수정/검증 | 스키마 정합성 확인 | `references/rules/metadata-schema.md` |
| 정적 점검/감사 | Validator 실행 + 보고 | `assets/validation-report-template.md` |

원칙:
- 작업당 기본 규칙 파일 1개를 우선 로딩한다.
- 필요한 경우에만 추가 규칙 파일을 선택 로딩한다.

## 실행 워크플로

`Intake -> Operation Plan -> Execute -> Validate -> Report`

### 1) Intake

- 요청의 대상(노트/모듈/검증 범위)을 식별한다.
- 구조 거버넌스 작업인지 콘텐츠 작업인지 분기한다.

### 2) Operation Plan

- 작업 유형에 맞는 기본 로딩 파일 1개를 선택한다.
- 변경 범위를 최소 단위(대상 모듈/폴더/노트)로 고정한다.
- 모듈 경계(PARA 위치, attachments 위치)를 먼저 확인한다.
- 모듈 맥락이 필요하면 인덱스 노트를 정본으로 읽고, 필요한 경우 실제 노트/폴더 구조로 보강한다.

### 3) Execute

- 구조 변경은 폴더 단위로 적용한다.
- 메타데이터 변경은 필수 필드와 형식을 먼저 맞춘다.
- 별도 `.context.md`는 생성/정리하지 않는다. 모듈 맥락은 기존 인덱스 노트와 실제 노트/폴더 구조를 기준으로 파악한다.

### 4) Validate

- 정적 검증 스크립트: `scripts/validate_vault.py`
- 우선 대상 범위에 `--target <path>`를 사용한다.
- 필요 시 옵션을 추가한다: `--format text|json`, `--check-git-modified`, `--today YYYY-MM-DD`

### 5) Report

- `assets/validation-report-template.md` 형식을 그대로 사용한다.
- 최종 판정은 `PASS` 또는 `FAIL`로 명시한다.

## 금지 사항

- 검증 없이 추측성 wikilink를 생성하지 않는다.
- 모듈 경계를 넘는 `attachments/` 링크를 허용하지 않는다.
