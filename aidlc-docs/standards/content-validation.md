# Content Validation Standards

> Load this file before writing any artifact that contains diagrams or embedded code blocks.

## ASCII Diagram Rules

Use ONLY basic ASCII characters for diagrams (maximum compatibility across IDEs and renderers).

### Allowed characters
`+` `-` `|` `^` `v` `<` `>` spaces, and alphanumeric text.

### Forbidden
No Unicode box-drawing characters: `┌` `─` `│` `└` `┐` `┘` `├` `┤` `┬` `┴` `┼` `▼` `▲` `►` `◄`

### Width rule
Every line inside a box MUST have the same character count (including trailing spaces).

### Patterns

Box:
```
+-------------------------------------------+
|              Component Name               |
|  Description text here                    |
+-------------------------------------------+
```

Nested:
```
+-----------------------------------------------+
|  Outer Component                              |
|  +-----------------------------------------+  |
|  |  Inner Component                        |  |
|  +-----------------------------------------+  |
+-----------------------------------------------+
```

Horizontal flow:
```
+-------+     +-------+     +-------+
| Step1 | --> | Step2 | --> | Step3 |
+-------+     +-------+     +-------+
```

Vertical flow:
```
+----------+
|  Input   |
+----------+
     |
     v
+----------+
| Process  |
+----------+
     |
     v
+----------+
|  Output  |
+----------+
```

## Mermaid Diagram Rules

1. Validate syntax before writing: node IDs must be alphanumeric + underscore only.
2. Escape special characters in labels: `"` → `\"` and `'` → `\'`.
3. Always include a text alternative below the Mermaid block.

## General Validation

Before writing any file:
- [ ] Validate embedded code blocks (Mermaid, JSON, YAML) for syntax correctness.
- [ ] Check that markdown headings, lists, and tables render correctly.
- [ ] Include text fallback for every diagram (ASCII or Mermaid).

## When Validation Fails

1. Use the text fallback instead of the broken diagram.
2. Do NOT block the workflow — continue with text representation.
3. Inform the user that a simplified version was used.
