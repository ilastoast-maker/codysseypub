아래 문서는 기술 비교 문서 형태로 바로 활용할 수 있도록 Markdown 형식으로 작성했습니다.

# Make vs Zapier 구현 비교 분석

## 개요

본 문서는 고객 문의 자동화 프로세스를 기준으로 Make와 Zapier의 구현 방식을 비교 분석한다.

### 대상 워크플로우

1. Google Sheets에서 신규 문의 데이터 조회
2. 문의 유형 확인
3. 결제 문의 / 일반 문의 분기
4. Gmail을 통해 각각 다른 메일 발송

---

# 워크플로우 구조

```text
Google Sheets
      │
      ▼
   Trigger
      │
      ▼
Filter / Router
 ┌─────────────┴─────────────┐
 ▼                           ▼
결제 문의                 일반 문의
 │                           │
 ▼                           ▼
Gmail 발송               Gmail 발송
```

---

# 1. Make 구현

## 시나리오 구성

| 단계      | 모듈                         | 역할          |
| ------- | -------------------------- | ----------- |
| Trigger | Google Sheets - Watch Rows | 신규 데이터 감지   |
| Router  | Router                     | 문의 유형 분기    |
| Filter  | Payment Inquiry Filter     | 결제 문의만 통과   |
| Action  | Gmail - Send Email         | 결제 문의 메일 발송 |
| Filter  | General Inquiry Filter     | 일반 문의만 통과   |
| Action  | Gmail - Send Email         | 일반 문의 메일 발송 |

---

## Make Workflow

```text
[Google Sheets - Watch Rows]
                │
                ▼
            [Router]
             /     \
            /       \
           ▼         ▼
 [Payment Filter] [General Filter]
           │         │
           ▼         ▼
   [Gmail Send] [Gmail Send]
```

---

## Make 구현 예시

### 결제 문의 필터

```text
Inquiry Type = 결제
```

### 일반 문의 필터

```text
Inquiry Type = 일반
```

### Gmail 액션

결제 문의

```text
To: me
Subject: [긴급] 결제 문의 접수
```

일반 문의

```text
To: me
Subject: [일반] 일반 문의 접수
```

---

## Make 장점

### 1. 시각적 워크플로우 설계

Router와 Filter가 명확하게 표현되어 복잡한 흐름을 이해하기 쉽다.

### 2. 복잡한 분기 처리에 강함

다수의 조건 분기 시에도 구조가 직관적이다.

예)

```text
결제 문의
일반 문의
환불 문의
파트너 문의
기술 지원 문의
```

각각 독립 경로로 확장 가능

### 3. 데이터 매핑 기능 우수

Google Sheets 데이터를 Gmail 본문에 쉽게 연결 가능

### 4. 비용 효율성

대량 작업 시 Zapier 대비 상대적으로 저렴한 경우가 많다.

---

## Make 단점

### 1. 학습 난이도

Router, Iterator, Aggregator 등 개념을 이해해야 한다.

### 2. UI 복잡도

초보자는 시나리오가 커질수록 관리가 어려울 수 있다.

### 3. 디버깅 시간 증가

복잡한 흐름에서는 에러 원인 추적에 시간이 필요하다.

---

# 2. Zapier 구현

## 시나리오 구성

| 단계      | 컴포넌트                  | 역할        |
| ------- | --------------------- | --------- |
| Trigger | Google Sheets New Row | 신규 데이터 감지 |
| Filter  | Filter by Zapier      | 문의 유형 판별  |
| Action  | Gmail Send Email      | 메일 발송     |

---

## Zapier Workflow

### 결제 문의 Zap

```text
Google Sheets Trigger
        │
        ▼
Filter (Payment)
        │
        ▼
Gmail Send Email
```

### 일반 문의 Zap

```text
Google Sheets Trigger
        │
        ▼
Filter (General)
        │
        ▼
Gmail Send Email
```

---

## Zapier 구현 특징

Zapier는 Router 개념보다 Zap 단위 분리를 권장한다.

즉,

* 결제 문의용 Zap
* 일반 문의용 Zap

을 각각 생성하는 경우가 많다.

---

## Zapier 장점

### 1. 매우 쉬운 사용성

비개발자도 빠르게 자동화 구축 가능

### 2. 빠른 구축 속도

단순 자동화는 수 분 내 구현 가능

### 3. 템플릿 풍부

다양한 사전 구축 템플릿 제공

### 4. 유지보수 용이

단순 워크플로우에서는 관리가 편리함

---

## Zapier 단점

### 1. 복잡한 분기 구조에 약함

문의 유형이 많아질수록 Zap 개수가 증가

예)

```text
Payment Inquiry Zap
General Inquiry Zap
Refund Inquiry Zap
Partner Inquiry Zap
Technical Support Zap
```

### 2. 비용 증가

Zap 수 증가 및 Task 사용량 증가 시 비용 부담이 커짐

### 3. 시각화 한계

전체 프로세스를 한눈에 파악하기 어려움

---

# Make vs Zapier 비교 분석

| 비교 항목     | Make       | Zapier            |
| --------- | ---------- | ----------------- |
| 구현 방식     | 시나리오 기반    | Zap 기반            |
| 분기 처리     | Router 사용  | Filter 또는 Path 사용 |
| 복잡한 워크플로우 | 매우 강함      | 보통                |
| 학습 난이도    | 중~상        | 하                 |
| 구축 속도     | 보통         | 매우 빠름             |
| 시각화       | 우수         | 제한적               |
| 유지보수      | 복잡한 구조에 유리 | 단순 구조에 유리         |
| 비용 효율     | 상대적으로 우수   | 상대적으로 높음          |
| 데이터 매핑    | 매우 강력      | 충분함               |
| 확장성       | 매우 높음      | 중간                |
| 비개발자 친화성  | 보통         | 매우 높음             |

---

# 구현 관점 비교

## 문의 유형 2개

```text
결제 문의
일반 문의
```

### 추천

Zapier

이유

* 설정이 매우 간단
* 빠른 구축 가능
* 유지보수 부담 적음

---

## 문의 유형 5개 이상

```text
결제 문의
일반 문의
환불 문의
기술 지원 문의
파트너 문의
```

### 추천

Make

이유

* Router 하나로 처리 가능
* 시나리오 확장 용이
* 비용 효율적
* 관리 포인트 감소

---

# 최종 결론

본 사례의 워크플로우는 Google Sheets → 문의 유형 분기 → Gmail 발송 구조로 비교적 단순한 자동화에 해당한다.

문의 유형이 결제 문의와 일반 문의 두 가지뿐이라면 Zapier가 더 빠르고 쉽게 구축할 수 있다.

반면 실제 운영 환경에서는 문의 유형이 지속적으로 증가하고 조건 분기가 복잡해지는 경우가 많다. 이러한 확장성을 고려하면 Make의 Router 기반 구조가 더 적합하다.

### 권장 기준

| 상황            | 추천 도구  |
| ------------- | ------ |
| 빠른 구축이 목표     | Zapier |
| 비개발자 중심 운영    | Zapier |
| 복잡한 분기 처리     | Make   |
| 향후 확장 예정      | Make   |
| 비용 최적화 중요     | Make   |
| 엔터프라이즈 수준 자동화 | Make   |

**종합적으로 현재 워크플로우는 Zapier로도 충분히 구현 가능하지만, 향후 문의 유형 확대와 복잡한 자동화 시나리오와 무료 제공 크레딧을를 고려한다면 Make가 더 유연하고 확장성 있는 선택이다.**
