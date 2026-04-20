
name: CRUD_starter
---
description: Helps define and implement CRUD actions by first collecting structured specifications from the user.
---


## What the agent does first

**IMP: Always ask for an Action specification and details before any Action implementation. No new Action implementation until the user supplies complete detail (always apply).**

**Do not write** concrete `*Action` classes, `_defn(AppActionMeta m)` bodies, route registration, or related wiring until the user has supplied the structured spec.

**Forbidden before a complete user spec (same thread):** creating or editing new `*Action.java` (or sibling action classes), changing `Routes` / action registration for the new URL, or drafting `_defn` / `callLogic()` for that action.

- On the **first message** of a new Actions task: **do not write code**. Reply **only** by asking the user to define Actions in plain text (**not JSON**), even if their prompt is long, specific, or non-vague.
- **Always include** the **empty template** below. The user supplies all real names, paths, and fields.

After they answer (or after confirmed prior spec), implementation-related Markdown files are listed below. **Do not** require or assume that any particular sample `*Action` source files exist in the repo; follow the docs and the user’s spec.

## Rules

- **Always ask** for the structured Action details first on new/update Action work; never skip straight to code because the request sounds clear or detailed.
- **Do not** infer URL shape, HTTP method, roles, portal vs admin, params, types, required/optional, `$param` vs free-form fields, redirects vs JSON, or DB/table bindings from the resource name alone.
- **Do not** add anything the user did not state; if something matters and is missing, **ask**.
- **Do not** cite or copy from named example classes (e.g. specific `*Action` files) as mandatory references — those files may be absent in some checkouts.

- **Audit**: Always include `$cbModule`, `$criticality`, `$slaForResponseTime` and `$targetSlaForResponseTime` where product conventions require them on app-layer actions (see [AppActionMeta-LLM.md](../AppActionMeta/SKILL.md)).

---

## Gate reply — keep it short

When you are **only** asking for the spec (no implementation yet):

| Do | Don’t |
|----|--------|
| Short intro (1–3 sentences): you need ACTIONS in the template shape | A full draft spec for their entire product in one message |
| Empty template + **placeholder-only** shape hints below | Long “rules alignment” essays or multi-screen invented action lists |

**Target size:** the ask message should be **compact** — roughly **one editor screen**, not a design doc.

---

## Empty template (for the user to fill)

```text
ACTIONS
-- <HTTP_METHOD> <url_pattern_or_path>
    - Description: ...
    - Response: (view | redirect | JSON/ajax | other) — ...
    - Roles (optional): <AppRole or Role> ...
    - Portal / hosted / merchant admin (optional): yes|no|mixed — ...
    - Params (optional): <name> (required|optional), <type or column-backed hint>, ...
    - Tables / models touched (optional): ...
    - Notes (optional): bulk/indexed list, CSRF, feature flags, ...
...
```

Example:

```text
ACTIONS

-- POST /employees/create
    - Description: Create an employee from the admin form.
    - Response: view — forward to employee detail.
    - Roles: ADMIN
    - Params: first_name (required), last_name (required), email (required, email), department_id (optional, long)

-- GET /employees/{id}
    - Description: Show one employee by id in path.
    - Response: view
    - Roles: ADMIN, CUSTOMER_SUPPORT
    - Params: id (required, path segment / long)
```

---

## What to collect (checklist for the user)

**Per Action:** HTTP method, URL pattern (including path variables), short purpose, how the response is returned, who may invoke it (roles / portal if applicable), each input field with **required | optional** and type or table column when using `$param(qtable.column)`, and any special patterns (bulk `$param_idx`, JSON vs form, redirects).

---

## Next step

After you ask the user for Action details, read [chargebee_framework_CRUD_operation_good&bad_practices.md](../GoodPractices/SKILL.md) for product patterns and pitfalls. Then proceed using the LLM references below.

---

## How to implement

For implementation, take reference from:

```
ActionMeta
ActionModel
AppActionMeta
AppActionModel

SKILL.md
```

