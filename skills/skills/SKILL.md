# Action layer and browser actions 


It is like a **browser** (or Postman) sending a normal web request: a URL, maybe a form, maybe some data. The **Action layer** is the code path that says: *“This URL belongs to this handler. Here is what we expect. Here is what we do next.”*

---

## What is the Action layer? 

When someone visits a page or clicks “Save,” the server receives an HTTP request. The **Action layer**:

1. **Finds** which piece of code should run (routing).
2. **Reads** what that URL is allowed to accept (the “rules sheet”).
3. **Pulls** values out of the request (form fields, URL parts, etc.) and checks them.
4. **Runs** your business code.
5. **Sends back** a page, a redirect, or JSON.

You don’t have to invent that flow for every button—the framework gives you the same steps each time.

---

## `ActionMeta` — the rule sheet (one copy per URL pattern)

**Simple idea:** **`ActionMeta`** is like a **printed form** or **recipe card** for **one kind of URL**.

- It says: *this URL pattern*, *GET or POST*, *which fields exist*, *which are required*, *how to validate them*.
- It is built **once** and reused. Many users can hit URLs that **match the same pattern**; they all share the **same** `ActionMeta`.

**Example:** URL pattern `employee/find/{id}` is **one** `ActionMeta`.  
`/employee/find/5` and `/employee/find/99` are **two different visits**, but they use the **same** rule sheet.

**Why browsers care:** The browser sends names and values (in the address bar, form, or ajax). `ActionMeta` tells the server **what those names mean** and **what checks to run** **before** your “real work” code runs.

**Read more:** [ActionMeta-LLM.md](../ActionMeta/SKILL.md)

---

## `ActionModel` — the worker for *this one* request

**Simple idea:** **`ActionModel`** is a **fresh object for each single request**.

- It holds that request’s **HTTP request and response** objects.
- It holds a **`values`** map: the things the framework already loaded for you (form values, loaded rows, etc.).
- The usual flow is: set things up → run your code in **`callLogic()`**.

So: **`ActionMeta`** = shared rules. **`ActionModel`** = *this one visitor, this one click*.

**Why browsers care:** Two people clicking “Save” at the same time should **not** share the same in-memory state. A new `ActionModel` per request keeps each visit **separate** and **safe**.

**Read more:** [ActionModel-LLM.md](../ActionModel/SKILL.md)

---

## `AppActionMeta` 

**Simple idea:** **`AppActionMeta`** is **`ActionMeta` plus Chargebee-specific extras**.

Same “one rule sheet per URL pattern” idea, but the sheet can also describe things like **who is allowed** (roles), **which part of the product UI** it belongs to (tabs, etc.), and other **app-level** rules (things that only make sense in Chargebee, not in a tiny demo app).

**Why browsers care:** Real product pages need more than “parse these fields”—they need **“is this the right merchant site?”** and **“is this user allowed?”** style rules. Those extra rules live in the **app** meta layer.

**Read more:** [AppActionMeta-LLM.md](../AppActionMeta/SKILL.md)

---

## `AppActionModel` — the Chargebee worker for *this one* request

**Simple idea:** **`AppActionModel`** is **`ActionModel` plus Chargebee setup**.

Before your `callLogic()` runs, the app layer typically does things like: figure out **which site / merchant** this is, load **user** context, and run **security checks**. After that, it still uses the same **bind params → validate → callLogic** idea as the base `ActionModel`.

Most Chargebee HTTP action classes **extend** `AppActionModel`, not plain `ActionModel`.

**Why browsers care:** A browser request almost always needs **“whose account is this?”** answered **before** you trust the submitted data. `AppActionModel` is the normal place that pipeline starts.

**Read more:** [AppActionModel-LLM.md](../AppActionModel/SKILL.md)

---

## Making a new endpoint — there is more than one way

You can wire endpoints in different ways (different URL shapes, split into more or fewer action classes, form posts vs JSON, and so on). **None** of the choices are “free”—each has **pros and cons** (easier to read vs easier to reuse, safer vs faster to type, etc.).

A longer doc in this repo walks through those **tradeoffs** and **good vs risky patterns**:

**Read more:** [chargebee_framework_CRUD_operation_good&bad_practices.md](../EndToEnd_CRUD/SKILL.md)

---


