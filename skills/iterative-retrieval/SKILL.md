---
name: iterative-retrieval
description: Multi-round context gathering for subagents. DISPATCH → EVALUATE → REFINE → CONVERGE loop. MUST BE USED when: implementing in unfamiliar area, subagent failed due to missing context, unsure which files a change will touch. DO NOT USE when: you already know exact files and interfaces, simple bug fixes with obvious location.
---

# Iterative Retrieval — Smart Context Gathering

Structured loop để gather đúng context trước khi dispatch implementation agents. Thay thế cách "hy vọng prompt có đủ context" bằng systematic discovery.

## Usage

```
/man-retrieve <câu hỏi hoặc mô tả task>
```

## Protocol

### Round 1: DISPATCH (Tìm kiếm rộng)

Spawn một Explore agent với broad query từ task:

```
Agent({
  subagent_type: "Explore",
  prompt: "Tìm tất cả files liên quan đến: [task description]. Tìm kiếm rộng — bao gồm tests, configs, types, và adjacent modules. Báo cáo: file paths, key symbols, và tóm tắt 1 dòng cho mỗi file.",
  description: "Broad context search"
})
```

### Round 2: EVALUATE (Đánh giá độ liên quan)

Với mỗi file mà search trả về, score relevance 0.0-1.0:

| Score | Ý nghĩa | Hành động |
|-------|---------|--------|
| 0.8-1.0 | Trực tiếp bị ảnh hưởng bởi task | Đọc đầy đủ, include trong context |
| 0.5-0.7 | Liên quan nhưng không trực tiếp thay đổi | Đọc key sections, include summary |
| 0.2-0.4 | Liên quan gián tiếp | Ghi nhận sự tồn tại, không include |
| 0.0-0.1 | False positive | Bỏ qua |

### Round 3: REFINE (Fix Terminology)

Nếu Round 1 bỏ sót context quan trọng (thường xảy ra khi không biết terminology của codebase):

1. Xác định terminology mismatches — "codebase gọi là X, tôi tìm Y"
2. Xác định structural mismatches — "tôi tìm trong `src/`, nhưng project dùng `lib/`"
3. Spawn một Explore thứ hai với refined queries

### Round 4: CONVERGE (Exit Criteria)

Thoát khỏi loop khi:
- Tìm được ít nhất 3 high-relevance (≥0.8) files
- Tất cả types/interfaces được tham chiếu bởi những files đó đều được tìm thấy
- Test files cho khu vực target được xác định
- HOẶC: 3 iterations đã hoàn thành (hard cap)

### Output: Context Brief

```markdown
## Context Brief for: [task]

### Core files (sẽ được modified):
- `path/to/file.py:10-50` — [nó làm gì, tại sao quan trọng]

### Dependencies (phải giữ compatible):
- `path/to/dep.py` — [interface contract]

### Tests (phải pass):
- `tests/test_file.py` — [nó cover gì]

### Conventions quan sát được:
- [naming patterns, import style, error handling approach]

### Terminology map:
- [task term] → [codebase term]
```

## Tích hợp

Output của skill này được thiết kế để feed trực tiếp vào:
- `implementer` agent prompts
- `writing-plans` task descriptions
- `codebase-explorer` follow-up queries

## Khi nào dùng

- Trước khi implement feature trong khu vực không quen thuộc
- Khi subagent fail vì thiếu context
- Khi không chắc chắn task sẽ touch những files nào
- Trước khi viết plan cho complex feature

## Khi nào KHÔNG dùng

- Bạn đã biết chính xác files và interfaces
- Task trong khu vực đã hiểu rõ với file paths rõ ràng
- Bug fix đơn giản với vị trí rõ ràng
