# craftpowers

**craftpowers** là một phương pháp phát triển phần mềm hoàn chỉnh cho AI coding agents — kết hợp nền tảng [Superpowers](https://github.com/obra/superpowers) của [Jesse Vincent](https://blog.fsck.com) với bộ skill thực chiến từ [Matt Pocock](https://github.com/mattpocock/skills).

> *"Your coding agent just has Superpowers — and now it has Craft."*

---

## Tại sao craftpowers?

[Superpowers](https://github.com/obra/superpowers) cho agent một **quy trình** hoàn chỉnh: brainstorm → plan → TDD → review → ship.

[Matt Pocock's skills](https://github.com/mattpocock/skills) cho agent **công cụ** thực chiến: stress-test design, tạo PRD, quản lý ADR, chuẩn hóa ngôn ngữ, refactor có kế hoạch.

**craftpowers** kết hợp cả hai — không thay thế, không xung đột, chỉ bổ sung.

---

## Cách hoạt động

Ngay khi agent thấy bạn muốn build thứ gì đó, nó không nhảy vào code ngay. Thay vào đó:

1. Hỏi bạn thực sự muốn gì
2. Stress-test design trước khi commit
3. Khám phá nhiều hướng thiết kế khác nhau nếu cần
4. Tạo spec, plan, và GitHub Issues từ cuộc thảo luận
5. Ghi lại quyết định kiến trúc bằng ADR
6. Chuẩn hóa ngôn ngữ domain trước khi code
7. Thực thi với TDD, review 2 giai đoạn, và subagent-driven development

---

## The Basic Workflow

1. **brainstorming** - Tinh chỉnh ý tưởng qua câu hỏi, khám phá alternatives, trình bày design từng phần để validate. Lưu design document.

2. **adversarial-design** *(mới)* - Stress-test design bằng cách phản biện từng nhánh quyết định trước khi approve.

3. **design-exploration** *(mới)* - Tạo 3+ design song song qua sub-agents, so sánh trade-offs để chọn hướng tốt nhất.

4. **using-git-worktrees** - Tạo isolated workspace trên branch mới, chạy project setup, kiểm tra test baseline.

5. **writing-plans** - Chia công việc thành task 2-5 phút. Mỗi task có file path chính xác, code đầy đủ, bước verify.

6. **to-prd** *(mới)* - Biến context cuộc thảo luận thành PRD và submit lên GitHub Issues.

7. **to-issues** *(mới)* - Phân rã plan thành GitHub Issues độc lập theo vertical slices.

8. **subagent-driven-development** / **executing-plans** - Dispatch subagent cho từng task với review 2 giai đoạn (spec compliance + code quality).

9. **test-driven-development** - Bắt buộc RED-GREEN-REFACTOR. Xóa code viết trước khi có test.

10. **requesting-code-review** / **receiving-code-review** - Review theo plan, phân loại issues theo severity.

11. **finishing-a-development-branch** - Verify tests, chọn merge/PR/keep/discard, dọn worktree.

---

## What's Inside

### Skills từ Superpowers (Jesse Vincent)

**Testing**
- **test-driven-development** - RED-GREEN-REFACTOR cycle

**Debugging**
- **systematic-debugging** - 4-phase root cause process
- **verification-before-completion** - Đảm bảo thực sự đã fix xong

**Collaboration**
- **brainstorming** - Socratic design refinement
- **writing-plans** - Detailed implementation plans
- **executing-plans** - Batch execution with checkpoints
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist
- **receiving-code-review** - Responding to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow
- **subagent-driven-development** - Fast iteration with two-stage review

**Meta**
- **writing-skills** - Create new skills following best practices
- **using-superpowers** - Introduction to the skills system

---

### Skills từ Matt Pocock *(mới trong craftpowers)*

**Design**
- **adversarial-design** - Stress-test design bằng cách phản biện relentlessly trước khi commit
- **design-exploration** - Tạo nhiều interface design song song, so sánh để chọn tốt nhất

**Planning & GitHub Integration**
- **to-prd** - Biến conversation context thành PRD và submit lên GitHub Issues
- **to-issues** - Phân rã plan thành vertical-slice GitHub Issues độc lập

**Architecture**
- **architecture-decision-records** - Tìm cơ hội cải thiện kiến trúc, ghi lại quyết định bằng ADR
- **ubiquitous-language** - Trích xuất DDD-style glossary, chuẩn hóa ngôn ngữ domain

**Refactoring**
- **structured-refactoring** - Tạo refactor plan với tiny commits qua interview, submit lên GitHub Issues

**Tooling**
- **setup-pre-commit** - Cài Husky pre-commit hooks với lint-staged, type checking, tests
- **git-guardrails-claude-code** - Chặn các git command nguy hiểm trước khi Claude thực thi

---

## Philosophy

- **Test-Driven Development** - Viết tests trước, luôn luôn
- **Systematic over ad-hoc** - Quy trình hơn là đoán mò
- **Complexity reduction** - Đơn giản là mục tiêu hàng đầu
- **Evidence over claims** - Verify trước khi tuyên bố xong
- **Design before code** - Stress-test ý tưởng trước khi commit
- **Craft over vibe** - Kỹ thuật có chủ đích, không phải vibe coding

---

## Installation

### Claude Code

```bash
/plugin install craftpowers
```

Hoặc clone trực tiếp:

```bash
git clone https://github.com/<your-username>/craftpowers
```

---

## Credits

craftpowers được xây dựng trên nền tảng của:

- **[Jesse Vincent](https://blog.fsck.com)** & **[Prime Radiant](https://primeradiant.com)** — tác giả [Superpowers](https://github.com/obra/superpowers), nền tảng methodology và workflow
- **[Matt Pocock](https://github.com/mattpocock)** — tác giả [skills](https://github.com/mattpocock/skills), bộ công cụ thực chiến cho software craftsmanship

Nếu craftpowers hữu ích với bạn, hãy cân nhắc:
- ⭐ Star [Superpowers](https://github.com/obra/superpowers)
- ⭐ Star [mattpocock/skills](https://github.com/mattpocock/skills)
- [Sponsor Jesse Vincent](https://github.com/sponsors/obra)

---

## License

MIT License - see LICENSE file for details
