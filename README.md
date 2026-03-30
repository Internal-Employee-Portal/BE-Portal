# 📌 Employee Admin Dashboard

직원 및 부서를 관리할 수 있는 관리자용 웹 애플리케이션입니다.  
관리자와 일반 사용자 권한을 분리하여, 효율적인 조직 관리 기능을 제공합니다.

---

## 🛠 Tech Stack

<div style="overflow-x:auto;">
<table style="width: 100%; border-collapse: collapse;">
  <tr>
    <td style="padding: 10px;">Frontend</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white" />
        <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white" />
        <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td style="padding: 10px;">Backend</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" />
        <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td style="padding: 10px;">Database</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td style="padding: 10px;">Deployment</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/Cloudtype-000000?style=flat&logo=cloud&logoColor=white" />
        <img src="https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white" />
    </td>
  </tr>
  <tr>
    <td style="padding: 10px;">AI Tools</td>
    <td style="padding: 10px;">
        <img src="https://img.shields.io/badge/ChatGPT-10A37F?style=flat&logo=openai&logoColor=white" />
        <img src="https://img.shields.io/badge/Figma%20AI-F24E1E?style=flat&logo=figma&logoColor=white" />
        <img src="https://img.shields.io/badge/Google%20AI-4285F4?style=flat&logo=google&logoColor=white" />
    </td>
  </tr>
</table>
</div>

### 📊 ERD 설계

- dbdiagram을 활용한 데이터 모델링  
  👉 [ERD 확인](https://dbdiagram.io/d/bitcomputer-69c2271e78c6c4bc7a507985)

---

## 🧩 주요 기능

- 직원 생성 / 조회 / 수정 / 삭제
- 부서 생성 / 조회 / 수정 / 삭제
- 관리자 / 일반 사용자 권한 분리
- 직원 상태 관리 (재직 / 휴직 / 퇴사)
- 퇴사 시 계정 자동 비활성화 처리
- 검색 및 필터링 기능 (이름, 이메일, 부서, 상태, 역할)

---

## 🏗 주요 설계 결정 사항

### 1️⃣ 인증(Authentication) vs 인가(Authorization) 분리

- 401 Unauthorized  
  → 토큰 만료 또는 인증 실패 → 로그아웃 처리

- 403 Forbidden  
  → 권한 부족 → 접근 제한 (페이지 이동)

---

### 2️⃣ API 에러 처리 전략

✔ 중앙 집중형 API 처리 (apiFetch)

모든 API 요청은 공통 함수에서 처리하여  
에러 핸들링을 일관되게 유지

- 401 → 로그아웃 처리
- 403 → 권한 없음 안내
- 그 외 → 에러 메시지 표시

---

### 3️⃣ Trailing Slash 문제 해결

`/path` vs `/path/` 차이로 인해 307 Redirect 문제 발생 👉 모든 API 요청을 슬래시 없이 통일

예:

- `/employees`
- `/departments`

---

### 4️⃣ Soft Delete 적용

- deleted_at 컬럼 기반 논리 삭제
- 삭제된 데이터는 조회에서 제외

---

### 5️⃣ 직원 상태와 계정 상태 분리

- status (업무 상태)
  - ACTIVE / ON_LEAVE / RESIGNED

- is_active (계정 상태)

👉 퇴사 시 자동으로 계정 비활성화  
👉 필요 시 관리자가 재활성화 가능
