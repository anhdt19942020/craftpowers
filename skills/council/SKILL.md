---
name: council
description: Anti-anchoring deliberation — main agent writes position before spawning independent reviewers. Prevents bias in multi-agent decisions. MUST BE USED when: architectural decisions, approach selection, technology choices where overconfidence risk is high. DO NOT USE when: bug fixes, implementing an already-decided plan, simple questions.
---

# Council — Anti-Anchoring Deliberation

Multi-perspective decision-making với bias prevention. Main agent phải commit vào position TRƯỚC khi đọc bất kỳ subagent output nào.

## Usage

```
/man-council <câu hỏi hoặc quyết định cần deliberate>
```

## Protocol

### Phase 1: Position Lock (BẮT BUỘC)

Trước khi spawn bất kỳ subagent nào, BẠN phải:

1. Viết position của mình về câu hỏi (2-4 câu)
2. Lưu vào temp file: `plans/visuals/council-position-{timestamp}.md`
3. Ghi rõ confidence level (0-100%)
4. Liệt kê các assumptions đang đưa ra

**Lý do phải viết trước:** Nếu đọc ý kiến subagent trước khi hình thành ý kiến riêng, bạn sẽ anchor vào framing của họ. Viết trước buộc independent reasoning.

### Phase 2: Spawn Perspectives (Song song)

Spawn 3 subagent đồng thời qua Agent tool. Mỗi subagent nhận:
- Câu hỏi gốc DUY NHẤT (không có position của bạn)
- Context brief ngắn gọn (file paths liên quan, không phải toàn bộ conversation)
- Một góc nhìn cụ thể để lập luận

**Perspectives:**
1. **Skeptic** — "Tìm luận điểm MẠNH NHẤT chống lại approach này. Failure modes nào tồn tại? Chúng ta đang bỏ sót gì?"
2. **Pragmatist** — "Approach đơn giản nhất nào hoạt động được? Có thể loại bỏ complexity nào? Cái gì ship nhanh nhất?"
3. **Architect** — "Điều này ảnh hưởng hệ thống sau 6 tháng như thế nào? Tạo ra constraints gì? Làm khó điều gì hơn?"

**Anti-anchoring rules cho subagent prompts:**
- KHÔNG bao gồm position của bạn hay bất kỳ gợi ý nào về preference
- KHÔNG bao gồm conversation history tiết lộ quan điểm của bạn
- CÓ bao gồm: câu hỏi, file paths liên quan, project constraints
- Mỗi subagent PHẢI kết thúc bằng RECOMMENDATION rõ ràng (không chỉ phân tích)

### Phase 3: Synthesis

Sau khi 3 subagent trả về:

1. Đọc cả 3 perspectives
2. Đọc lại position ban đầu của bạn
3. Với mỗi perspective mâu thuẫn với position của bạn:
   - Nêu rõ mâu thuẫn
   - Đánh giá bằng chứng của họ có mạnh hơn assumption của bạn không
4. Viết final recommendation với:
   - Quyết định và lý do
   - Perspective nào đã ảnh hưởng quyết định
   - Dissenting views được ghi nhận
   - Confidence level (so sánh với Phase 1)

### Output Format

```markdown
## Council Decision: [topic]

**Initial position:** [tóm tắt, confidence X%]

**Skeptic:** [key point]
**Pragmatist:** [key point]
**Architect:** [key point]

**Final decision:** [quyết định, confidence Y%]
**Changed by:** [perspective nào thay đổi suy nghĩ, hoặc "none — initial position held"]
**Dissent noted:** [bất đồng chưa giải quyết]
```

## Khi nào dùng

- Quyết định kiến trúc ảnh hưởng 3+ file
- Lựa chọn technology/library
- Chọn approach khi có nhiều phương án hợp lệ
- Bất kỳ quyết định nào bạn cảm thấy >80% confident (rủi ro overconfidence)

## Khi nào KHÔNG dùng

- Bug fix với root cause rõ ràng
- Triển khai plan đã quyết định
- Câu hỏi đơn giản với một câu trả lời rõ ràng
