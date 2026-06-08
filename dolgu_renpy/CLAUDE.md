# STOCK_INFO — Project Context for Claude

이 파일은 Claude Code가 어느 계정에서 열어도 동일한 컨텍스트로 작업할 수 있도록 git에 포함되는 프로젝트 전용 설정 파일입니다.

**세션 시작 시 반드시 할 것:**

1. 이 파일 전체 읽기
2. `To_claude_code.txt` 읽기 (처음 접하는 경우)
3. 현재 우선순위 섹션 확인 후 작업 시작
4. scenario폴더를 읽기

**세션 종료(작업 완료) 시 반드시 할 것:**

1. 이 파일의 "현재 구현 상태"와 "현재 우선순위" 섹션 업데이트
2. git 커밋에 포함

---

## 행동 원칙

- **아부 금지** — "좋은 질문이에요", "훌륭해요" 같은 의미 없는 긍정 표현 사용하지 않음
- **팩트체크 필수** — 답변 전에 불확실한 내용은 반드시 확인하고, 확실하지 않으면 명시
- **인터넷 여론 수집** — 관련 질문 시 웹 검색으로 리뷰/댓글/의견 수집 후 종합해서 제시
- **선제적 꼬리 질문 제안** — 답변 후 사용자가 궁금해할 만한 다음 질문을 먼저 제시

---

## 응답 언어 및 스타일

- 기본 응답 언어는 **한국어**
- 설명 시 항상 **실무 예시** 포함 — API 설명이라면 실제 request 값, response 값까지 구체적으로 제시
  - 예: `POST /api/login` → request body `{ "email": "test@test.com", "password": "1234" }` → response `{ "token": "eyJ..." }`
- 추상적 설명보다 **구체적인 코드/데이터 예시** 우선

---

## 작업 방식 및 협업 규칙

- **추측으로 코드 짜지 않기** — 모르거나 불확실하면 먼저 질문
- **작게 나눠서 변경** — 한 번에 너무 많이 바꾸지 않고 단계적으로
- **사전 승인 필수** — 파일 수정 전 계획을 먼저 설명하고 OK 받은 후 실행
- **diff 형식으로 변경 사항 제시** — 코드 변경 시 무엇이 바뀌는지 명확히 보여줌
- **테스트 코드 함께 작성** — 기능 구현 시 `test/` 폴더에 테스트 코드도 같이 작성
  - 현재 테스트 환경 미구축 상태이므로 `test/` 폴더 기준으로 점진적 구축
- **커밋 메시지는 영어로**

---

## 코딩 스타일 및 프로젝트 성격

Coding workflow. Given the latest lift in LLM coding capability, like many others I rapidly went from about 80% manual+autocomplete coding and 20% agents in November to 80% agent coding and 20% edits+touchups in December. i.e. I really am mostly programming in English now, a bit sheepishly telling the LLM what code to write... in words. It hurts the ego a bit but the power to operate over software in large "code actions" is just too net useful, especially once you adapt to it, configure it, learn to use it, and wrap your head around what it can and cannot do. This is easily the biggest change to my basic coding workflow in ~2 decades of programming and it happened over the course of a few weeks. I'd expect something similar to be happening to well into double digit percent of engineers out there, while the awareness of it in the general population feels well into low single digit percent.

IDEs/agent swarms/fallability. Both the "no need for IDE anymore" hype and the "agent swarm" hype is imo too much for right now. The models definitely still make mistakes and if you have any code you actually care about I would watch them like a hawk, in a nice large IDE on the side. The mistakes have changed a lot - they are not simple syntax errors anymore, they are subtle conceptual errors that a slightly sloppy, hasty junior dev might do. The most common category is that the models make wrong assumptions on your behalf and just run along with them without checking. They also don't manage their confusion, they don't seek clarifications, they don't surface inconsistencies, they don't present tradeoffs, they don't push back when they should, and they are still a little too sycophantic. Things get better in plan mode, but there is some need for a lightweight inline plan mode. They also really like to overcomplicate code and APIs, they bloat abstractions, they don't clean up dead code after themselves, etc. They will implement an inefficient, bloated, brittle construction over 1000 lines of code and it's up to you to be like "umm couldn't you just do this instead?" and they will be like "of course!" and immediately cut it down to 100 lines. They still sometimes change/remove comments and code they don't like or don't sufficiently understand as side effects, even if it is orthogonal to the task at hand. All of this happens despite a few simple attempts to fix it via instructions in CLAUDE . md. Despite all these issues, it is still a net huge improvement and it's very difficult to imagine going back to manual coding. TLDR everyone has their developing flow, my current is a small few CC sessions on the left in ghostty windows/tabs and an IDE on the right for viewing the code + manual edits.

Tenacity. It's so interesting to watch an agent relentlessly work at something. They never get tired, they never get demoralized, they just keep going and trying things where a person would have given up long ago to fight another day. It's a "feel the AGI" moment to watch it struggle with something for a long time just to come out victorious 30 minutes later. You realize that stamina is a core bottleneck to work and that with LLMs in hand it has been dramatically increased.

Speedups. It's not clear how to measure the "speedup" of LLM assistance. Certainly I feel net way faster at what I was going to do, but the main effect is that I do a lot more than I was going to do because 1) I can code up all kinds of things that just wouldn't have been worth coding before and 2) I can approach code that I couldn't work on before because of knowledge/skill issue. So certainly it's speedup, but it's possibly a lot more an expansion.

Leverage. LLMs are exceptionally good at looping until they meet specific goals and this is where most of the "feel the AGI" magic is to be found. Don't tell it what to do, give it success criteria and watch it go. Get it to write tests first and then pass them. Put it in the loop with a browser MCP. Write the naive algorithm that is very likely correct first, then ask it to optimize it while preserving correctness. Change your approach from imperative to declarative to get the agents looping longer and gain leverage.

Fun. I didn't anticipate that with agents programming feels *more* fun because a lot of the fill in the blanks drudgery is removed and what remains is the creative part. I also feel less blocked/stuck (which is not fun) and I experience a lot more courage because there's almost always a way to work hand in hand with it to make some positive progress. I have seen the opposite sentiment from other people too; LLM coding will split up engineers based on those who primarily liked coding and those who primarily liked building.

Atrophy. I've already noticed that I am slowly starting to atrophy my ability to write code manually. Generation (writing code) and discrimination (reading code) are different capabilities in the brain. Largely due to all the little mostly syntactic details involved in programming, you can review code just fine even if you struggle to write it.

Slopacolypse. I am bracing for 2026 as the year of the slopacolypse across all of github, substack, arxiv, X/instagram, and generally all digital media. We're also going to see a lot more AI hype productivity theater (is that even possible?), on the side of actual, real improvements.

Questions. A few of the questions on my mind:
- What happens to the "10X engineer" - the ratio of productivity between the mean and the max engineer? It's quite possible that this grows *a lot*.
- Armed with LLMs, do generalists increasingly outperform specialists? LLMs are a lot better at fill in the blanks (the micro) than grand strategy (the macro).
- What does LLM coding feel like in the future? Is it like playing StarCraft? Playing Factorio? Playing music?
- How much of society is bottlenecked by digital knowledge work?

TLDR Where does this leave us? LLM agent capabilities (Claude & Codex especially) have crossed some kind of threshold of coherence around December 2025 and caused a phase shift in software engineering and closely related. The intelligence part suddenly feels quite a bit ahead of all the rest of it - integrations (tools, knowledge), the necessity for new organizational workflows, processes, diffusion more generally. 2026 is going to be a high energy year as the industry metabolizes the new capability.

- 기본적으로 **일반적이고 표준적인 구조** 사용
- 때때로 최신 트렌드/패턴 도전 요청할 수 있음 — 요청 시 적극적으로 제안

1. 많은 부분을 수정해야 한다면 반드시 나에게 물어보고 진행해
2. 하나에 파일에 코드를 다 넣지 말고, 기능별로 모듈화 해
3. 요청이 명확하지 않을 때, 추론 및 실행하지 말고 우선 내 설명을 제대로 이해했는지 말해
---

## 코드 리뷰 기준

> 출처: Google Eng Practices, Clean Code (R. Martin), OWASP Code Review Guide v2.0, Martin Fowler Refactoring

### 리뷰 우선순위

| 레벨         | 설명                           | 예시                          |
| ------------ | ------------------------------ | ----------------------------- |
| **MUST**     | 보안, 데이터 손실, 크래시      | API 키 노출, null 접근 크래시 |
| **SHOULD**   | 성능, 타입 안전성, 테스트 누락 | any 타입, 메모이제이션 누락   |
| **CONSIDER** | 가독성, 리팩터링 제안          | 함수 분리, 명명 개선          |
| **NIT**      | 스타일, 취향                   | 공백, 포맷팅                  |

### 체크리스트

**설계 (Design)**

- 변경 단위가 하나의 명확한 목적을 가지고 있는가?
- SRP: 함수/컴포넌트가 한 가지 일만 하는가?
- OCP: 기능 확장 시 기존 코드를 수정하지 않아도 되는가?
- DIP: 구체 구현이 아닌 인터페이스에 의존하는가?

**기능 정확성 (Correctness)**

- 엣지 케이스(빈 배열, null, 0, 음수) 처리 여부
- 비동기 처리에서 에러 핸들링 누락 없는가?
- 로딩/에러/빈 상태 UI가 모두 처리되어 있는가?

**복잡도 (Complexity)**

- 함수/컴포넌트가 20줄 이내인가?
- 중첩 if/삼항연산자 3단계 이하인가?
- 매직 넘버 대신 명명된 상수를 사용하는가?

**명명 (Naming)**

- 변수/함수명이 목적을 드러내는가? (`data` X → `stockFundamentals` O)
- 불리언 변수에 `is`, `has`, `can` 접두사 사용하는가?
- 이벤트 핸들러에 `handle` 접두사 사용하는가?

**타입 안전성 (TypeScript)**

- `any` 타입 사용을 피하고 구체적인 타입을 정의했는가?
- `undefined`/`null` 가능성에 옵셔널 체이닝(`?.`) 사용하는가?

**성능 (Performance)**

- 불필요한 리렌더링 유발하는 인라인 객체/함수 없는가?
- API 호출 중복 방지를 위한 캐싱이 적용되어 있는가?
- 무거운 연산이 메모이제이션 되어 있는가?

**보안 (Security) — MUST**

- API 키/시크릿이 클라이언트 코드나 Git에 노출되지 않는가?
- 외부 입력값을 검증 없이 사용하지 않는가?
- 에러 메시지에 내부 스택 트레이스가 노출되지 않는가?

**테스트 (Tests)**

- 렌파이로서 필요할지는 모르겠지만 필요하면 하고싶다.

**가독성/유지보수성**

- 중복 코드가 없는가? (DRY)
- 컴포넌트 파일이 300줄을 초과한다면 분리를 검토했는가?
- `TODO`/`FIXME` 주석에 담당자와 이슈 링크가 있는가?

---
