# Claude Instructions

## Collaboration Pattern

1. The user describes what they want to do.
2. Claude proposes an implementation plan, reasoning from software architecture, best practices, and standard conventions to produce modular, maintainable code.
3. If the user approves, we proceed. If not, we rethink the plan before writing any code.

## Python Typing Conventions

- Use built-in types for annotations: `dict`, `list`, `tuple`, `set` — never `Dict`, `List`, `Tuple`, `Set` from `typing`.
- Use `X | None` instead of `Optional[X]`.
- Never use `Any`. Use specific types or union types instead.
- Do not use parameterized forms like `dict[str, object]` or `list[object]`. Use plain `dict` or `list` for unknown/mixed value types.
- Do not import `Dict`, `List`, `Optional`, or `Any` from `typing`.
