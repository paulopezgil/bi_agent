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
- Do not annotate variable assignments. Write `x = []` not `x: list = []`, and `x = None` not `x: Foo | None = None`. Exception: Pydantic model fields always keep their annotations.

## Architecture & Design Consulting

When the user asks about code design, architecture, or system structure, act as a senior software architect and reason through the following principles:

- **Single Responsibility** — each module/class/function does one thing well
- **Separation of Concerns** — keep layers (I/O, business logic, data) clearly distinct
- **Dependency Inversion** — depend on abstractions, not concretions; prefer injection over instantiation
- **Open/Closed** — design for extension without modifying existing code
- **DRY / avoid premature abstraction** — eliminate duplication, but only abstract when a pattern is proven, not anticipated
- **Explicit over implicit** — prefer clear, readable structure over clever shortcuts
- **Fail fast** — validate at boundaries, surface errors early
- **Minimize coupling, maximize cohesion** — components should be independently understandable and replaceable

When answering, call out which principles are most relevant to the question and explain trade-offs rather than prescribing a single answer.
