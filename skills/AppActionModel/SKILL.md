# `AppActionModel` — LLM reference (Chargebee application layer)


**Class:** `com.chargebee.app.AppActionModel<U extends com.chargebee.framework.web.ActionModel>`  
**Extends:** `com.chargebee.framework.web.ActionModel<com.chargebee.app.AppActionMeta, U>`

**Description:** This class is wrapper over ActionModel contains application layer information for like user's information.It is created on every request.It contains Http req,resp and all the stuff.Before your callLogic() runs, AppActionModel (app layer) does things like: resolve site, load merchant context, enforce auth / CSRF / CSP, run isAllowed, then hands off to the framework’s ActionModel.exec() → init() (bind params and models into values) → callLogic().

**Paired references:**

- **Framework request/params/`values`/`getErr`/`callLogic` patterns:** [ActionModel-LLM.md](../ActionModel/SKILL.md)  
- **`_defn` on framework meta:** [ActionMeta-LLM.md](../ActionMeta/SKILL.md)  
- **`_defn` on app meta (`AppActionMeta`):** [AppActionMeta-LLM.md](../AppActionMeta/SKILL.md)

**In this product:** Concrete actions extend **`AppActionModel<YourAction>`** (or a **narrow intermediate** — §4); **`M`** in the parent is **`AppActionMeta`**, so **`getMeta()`** returns app-extended metadata.

**Inherited API:** Everything **public** on **`ActionModel`** ( **`getString`**, **`get(qtable)`**, **`getErr()`**, **`flash`**, **`Forward`** helpers, …) is documented in **[ActionModel-LLM.md](../ActionModel/SKILL.md)**. This file documents **`AppActionModel`-only** additions and re-emphasizes app lifecycle.

---

## 1. Role

**`AppActionModel`** is the **Chargebee application** wrapper around **`ActionModel`**: it runs **site resolution**, **merchant load**, **auth/CSRF/CSP**, **role/`isAllowed` gates**, **portal/BE/Leap** flags, and then delegates into framework **`ActionModel.exec()`** → **`init()`** → **`callLogic()`**. One instance is created per routed HTTP request (or per **`createAction`** simulation).

---

## 2. Lifecycle overall flow
1. Router constructs the action, **`setMeta(AppActionMeta)`**, **`setDetails(req, resp)`**.
2. **`AppActionModel.exec()`** runs **first** (app layer): HTTP method validation, ajax/CSRF precheck, **`fetchSite()`**, access blocks, authentication, global auth / region / CSRF product rules, wrappers (intent, query mode, timezone, …).
3. **`doExec()`** runs inside the wrapped callable: merchant load, **`getMeta().isAllowed(this, null)`**, support-role consent, **`initModalVar`**, request limiters, analytics hooks, then the inner path that reaches framework **`ActionModel.exec()`**.
4. **Framework `ActionModel.exec()`**: **`checkAndLock()`** → **`init()`** (**`ActionInitHelper`**, **`values`**) → validation → **`callLogic()`**.

**`callLogic()`** still runs **after** **`init()`**; all **`$param` / `$create` / path** binding from **`_defn`** applies the same way as on plain **`ActionModel`**.

```text
Servlet → AppActionModel.exec()
            → site, auth, CSRF, CSP, feature wrappers …
            → doExec()
                 → isAllowed, limits, …
                 → ActionModel.exec()   // framework
                      → init() + RequestToPojoUtils
                      → callLogic()
```

---

---

## 4. What inherited from `ActionModel`

**`AppActionModel` does not replace the `values` map**; **`init()`** still fills it via **`ActionInitHelper`** before **`callLogic()`**. For **getters, `set`, `getErr`, `Forward`, `flash`, file upload, locking hooks declared on the parent**, see **[ActionModel-LLM.md](../ActionModel/SKILL.md)**.

### 4.1 Intermediate subclasses and overrides (your own “`AppActionModel` for this product area”)

**Pattern:** When a **family** of actions shares **business rules** (conditional **`Param`** required-ness, shared pre-**`callLogic()`** behavior, multi-action routing), introduce an **intermediate base**:

`public abstract class MyFeatureActionModel<U extends MyFeatureActionModel<U>> extends AppActionModel<U>`

(or **`extends`** another in-repo intermediate such as **`SegmentedParamProviderActionModel`**). **Override** the **non-final** hooks you need; leaf actions then use **`extends MyFeatureActionModel<CreateFooAction>`** instead of **`extends AppActionModel<CreateFooAction>`** directly.

**Typical override points** (verify signatures in IDE / **`javap`** on your build):

| function                                      | Why override |
|-----------------------------------------------|----------------|
| **`boolean isRequired(Param p)`**             | Merge **`_defn`** / **`.$req`** with **dynamic** rules (field settings, account-field groups, API metadata). **Always** combine with **`super.isRequired(p)`** unless a platform owner says otherwise. |
| **`Forward checkAndLock()`**                  | App-level **row / resource locking** — see §14.3; intermediate bases may override. |
| **`String getLogicMethodName(ActionMeta m)`** | **`MultiActionModel`** — dispatch different method names for one class (see **`SPAActionModel`**). |
| **`exec()` / `doExec()`**                     | **Strongly discouraged** for feature teams — runs **before** **`init()`** / **`callLogic()`** and affects **every** subclass; reserve for **platform**-owned base classes. |



---

## 5. Static string constants (`public static final String`)

- **Description:** Named **cookies**, **query parameters**, and **HTTP header** keys used across filters, hosted pages, analytics, and business-entity routing.
- **Role:** Avoid **magic strings**; stay consistent with login, HP, affiliate, GA, Leap migration, and BE scoping.
- **When to use:** Whenever you read/write the same integration as sibling actions (query string, header, cookie).
- **Requirement:** **Reuse** these constants instead of duplicating literal strings.
- **Returns:** N/A (compile-time constants).
- **In `callLogic()`:** Prefer **`$param`** / **`getString(CONSTANT)`** only when the value is not modeled as a declared **`Param`**.

| Constant | Typical role |
|----------|----------------|
| **`PROXY_SITE_COOKIE`** | Cookie used in proxy / site-resolution paths. |
| **`GA_ID`** | Google Analytics identifier in query or integration. |
| **`REFERSION_PARAM`** / **`REFERSION_TEST_PARAM`** | Refersion affiliate query keys (prod vs test). |
| **`AFFILIATE_TOKEN`** | Generic affiliate tracking token parameter name. |
| **`HP_OPENER`** / **`HP_REFERRER`** | Hosted-page opener / referrer tracking parameters. |
| **`CB_BE_ID_HEADER_NAME`** / **`CB_BE_ID_PARAM_NAME`** | Business-entity id passed as header or query for multi-BE merchants. |
| **`IS_MIGRATED_TO_FORCE_LEAP_UI`** / **`IS_REVERTED_TO_CLASSIC_UI`** | Request flags for Leap vs classic UI migration flows. |

---

## 6. Public instance fields

### `boolean isPortal`

- **What:** This is a variable which is a flag that tells whether the current ActionModel is a self portal /for customers service.
- **When it's used:** This is changed/set/altered when in defining an Action route under _defn(AppActionMeta m){...}

### `boolean isCustomDomain`

- **What:** This is like a flag which which usually stores information whether the current Action is Merchant's own hostname.
- **When it is set:** this is set when _defn(..) is called inside the Action route.


### `boolean isUIBetaEnabled`

- **What:** This is like a flag which tells whether the UI beta is enabled or not.,
- **When it is set:** this flag is set when _defn(.. )is called inside the Action route.
---

## 7. Site, merchant, user, session, subdomain, URLs

### `Site currentSite()` / `void site(Site site)`

- **What:** “Which merchant / tenant is this request for?”
  After the framework runs fetchSite inside exec(), this usually returns the Site object for that tenant.
- **When it is used:** In callLogic() (or helpers it calls) when you need “which site is this?” for business rules or DB work.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            Site site = currentSite();
            // Often you need the numeric id for site_id columns:
            long siteId = site.id();
            // e.g. when building a new row (exact API depends on your model):
            // employee.siteId(siteId);
            return super.callLogic();
        }   
```
### `Merchant currentMerchant()`

- **What:** A method on the action that returns the Merchant tied to the current site for this request. After the framework resolves currentSite() in doExec(), it can load the merchant that owns that site. currentMerchant() is that loaded object—one level above “site” in the tenancy model (merchant can own multiple sites).
- **Role:** Merchant-level settings, billing account context, cross-site merchant operations.

- **When to use:** When you need a merchant id (or similar) for APIs, locks, or joins that are keyed by merchant, not site_id alone.,When you want to reuse what the request stack already loaded instead of fetching the merchant again.
- **Example :**
```java
        @Override
        public Forward callLogic() throws Exception {
            Merchant merchant = currentMerchant();
            if (merchant == null) {
                // Only if your action can run without a normal merchant context
                return super.callLogic();
            }
            Long merchantId = merchant.id();  // confirm getter name on Merchant in your codebase
            // Use merchantId for merchant-scoped settings, billing context, etc.
            return super.callLogic();
        }
```

### `UserIfc currentUser()` / `User currentSiteUser()`

- **What:** currentUser() — The logged-in principal as an interface (UserIfc): “someone authenticated,” without forcing one concrete user type everywhere. Shared code can depend on UserIfc.currentSiteUser() — The concrete User for this site’s admin / merchant console context: the staff user tied to the current site session.
- **Role:** Audit fields, “who performed this”, role checks beyond **`$roles`**.

- **When to use:** Audit / attribution — “who did this?” (created_by, logs, modified_by-style fields).Extra identity — user id, email, name for display or downstream calls.Fine-grained checks — only when $roles / isAllowed in _defn is not enough (avoid duplicating security; $roles is still the main route-level gate).
- ** Example :**
```java
            @Override
            public Forward callLogic() throws Exception {
                // Merchant console–style action: concrete site user
                User u = currentSiteUser();
                if (u != null) {
                    Long uid = u.id();  // confirm accessor on User in your codebase
                    // e.g. audit: "performed by user " + uid
                }
            
                // Shared helper that only needs "some authenticated user"
                UserIfc whoever = currentUser();
                if (whoever != null) {
                    // e.g. whoever.getEmail() or other UserIfc API
                }
            
                return super.callLogic();
            }
```

### `LoginSessionIfc currentSession()` / `LoginSession currentAdminConsoleSession()`
- **Waht:** currentSession() — The current login session as LoginSessionIfc: a generic handle for “this browser’s logged-in session” in the app, without tying callers to one concrete session class.currentAdminConsoleSession() — The concrete LoginSession for the Chargebee admin / internal console (staff console), not the merchant’s day-to-day site UI.
- **Role:** Session attributes, logout, console-specific state.

- **When to use:** Reading or writing session-backed state — e.g. small flags, impersonation hints, wizard step, “console-only” attributes.Logout or session lifecycle helpers that expect a session object (follow existing patterns in the same feature).Uncommon in simple CRUD — most actions only need currentUser() / currentSiteUser() and request params.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            // Generic session (pattern depends on LoginSessionIfc API in your codebase)
            LoginSessionIfc session = currentSession();
            if (session != null) {
                // e.g. read a small attribute — names/types from your team’s pattern
                // Object flag = session.getAttribute("some_console_flag");
            }
        
            // Admin console only — when you need LoginSession, not the interface
            LoginSession consoleSession = currentAdminConsoleSession();
            if (consoleSession != null) {
                // e.g. console-specific attribute or helper
            }
        
            return super.callLogic();
        }
```

### `PojoList<Site> getLiveSitesForUser() throws Exception`

- **What:** A method on the action that returns a PojoList<Site>: the live sites the current user is allowed to use—mainly for site switcher / multi-site admin (“which merchant sites can I open from this account?”). Live here means product-eligible sites (not sandbox/test in the sense your codebase uses for this API—confirm next to similar helpers if you need exact semantics).
- **Role:** Enumerate allowed tenants for UI or redirects.

- **When to use:** Site switcher UI — build a list of sites the user can switch to.Redirects or defaults — pick a target site when the user has access to more than one.Multi-site admin pages where the product must enumerate tenants.
- **Requirement:** Can be expensive — follow existing call sites.

- **Example:**
```java
            @Override
            public Forward callLogic() throws Exception {
                PojoList<Site> sites = getLiveSitesForUser();
                if (sites == null || sites.isEmpty()) {
                    // User has no other live sites — hide switcher or show message
                    return super.callLogic();
                }
                for (Site s : sites) {
                    // e.g. dropdown: s.domain(), s.id(), …
                }
                return super.callLogic();
            }
```

### `String subdomain()`

- **What:** A method on the action that returns a String: the subdomain part of how this request was addressed (the bit derived from the HTTP host / routing), used for routing, branding, and host-based behavior—not necessarily the same thing as “site code” in every edge case.
- **Role:** Display, URL building, or branching on subdomain pattern.

- **When to use:** Building or comparing URLs that depend on which hostname the user hit (e.g. acme.chargebee.com → acme).Display or branching when product rules key off subdomain, not only off DB Site fields.Copy patterns from nearby actions that already use subdomain() for the same feature—don’t invent a new host-parsing path.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            String sub = subdomain();
            // e.g. pass to a URL builder, template, or feature flag branch
            if ("something".equals(sub)) {
                // ...
            }
            return super.callLogic();
        }
```

### `String getSiteWithDomain()` / `static String getSiteWithDomain(Site)` / `static String getSiteWithDomain(Site, SiteBase.CustomDomainState...)`

- **What:** Helpers that build a single string representing “this site with its domain”—for display, links, or “open in browser” text—using the same formatting rules everywhere (so emails, admin UI, and redirects stay consistent).
-

- **When to use:** “Copy link to this site”, email footers, notifications, redirect messages.
- **Requirement:** Prefer static overload when you have a **`Site`** other than current.
- **Returns:** **`String`**.
- **Example:**
```java
           
            String here = getSiteWithDomain();
            
            
            String there = AppActionModel.getSiteWithDomain(otherSite);
            
            
            String tuned = AppActionModel.getSiteWithDomain(
                    otherSite,
                    Site.CustomDomainState.ENABLED,
                    Site.CustomDomainState.TEST_MODE);
```
---

## 8. Static site resolution (`fetchSite`, `parseSubDomain`)

### `static Site fetchSite(String domain, boolean …)` (3 overloads)

- **What:** Static helpers on AppActionModel that look up a Site from a domain / host string, plus one or more boolean switches. The exact booleans depend on which overload you call (e.g. whether to throw if nothing matches, internal vs external resolution—read the Javadoc / signature you’re calling).

- **When to use:** Anywhere you have a raw host string and must resolve tenant before you have a full AppActionModel instance with currentSite() already set.
- **Example:**
```java

        String host = request.getServerName();
        Site s = AppActionModel.fetchSite(host, false);  
        
        
        @Override
        public Forward callLogic() throws Exception {
            Site s = currentSite();   
            return super.callLogic();
        }
```

### `static String parseSubDomain(HttpServletRequest req, boolean …)` (2 overloads)

- **What:** Static helpers (on AppActionModel in your stack) that read the incoming HTTP request and pull out the subdomain (or the host fragment your product treats as “subdomain”) in a central, consistent way.
- **When to use:** Filters, servlets, login/error plumbing—anywhere you have HttpServletRequest but not yet an AppActionModel.

- **In `callLogic()`:** Rare; use instance **`subdomain()`** when possible.
- **Example:**
```java

        String sub = AppActionModel.parseSubDomain(request);
        
        String subStrict = AppActionModel.parseSubDomain(request, true);
        
        
        @Override
        public Forward callLogic() throws Exception {
            String sub = subdomain();  // prefer this when you're already in an action
            return super.callLogic();
        }
```

---

## 9. Support roles, server admin, named roles, route allow

### `boolean isSupportRole()`

- **What:** **True** when the current user is in a **support / internal** role flavor used by Chargebee operations consoles.
- **Role:** Branch support-only UI or stricter consent flows (**`forwardToSupportRoleConsentPage`**).

- **When to use:** Symmetry / internal actions that mirror existing **`admin`** / support patterns.
- **Example:**
```java
            @Override
            public Forward callLogic() throws Exception {
                if (isSupportRole()) {
                    // e.g. do not expose decrypted secrets to the client
                    return super.callLogic();
                }
                // normal merchant user path
                return super.callLogic();
            }
```

### `static boolean isServerAdmin(User user) throws SQLException`

- **What:** A static helper on AppActionModel that answers: “Is this User a Chargebee platform / server admin?”

- **When to use:** Internal / admin-console actions that must allow only platform operators to run something dangerous or global (migrations, cross-site tools, super-admin knobs).
- **Requirement:** Never use to skip **`$roles`** on merchant-facing routes without product approval.
- **Example:**
```java
    @Override
        public Forward callLogic() throws Exception {
            User u = currentSiteUser();
            if (u != null && AppActionModel.isServerAdmin(u)) {
                // platform-only branch (internal tool)
            } else {
                // deny or no-op — usually this action shouldn't be reachable for non-server-admins
            }
            return super.callLogic();
        }
```

### `long getRole(long siteOrContextId, User user) throws Exception`

- **What:** Gives a bit id for a user for a given site/context ,the Role in chargebee are identified by the bit id.

- **When to use:** Use getRole(...) only when you are copying an existing pattern that already needs this low-level bitmask for the same reason (legacy integration, bitmask math, etc.)
- **Example:**
```java
            @Override
            public Forward callLogic() throws Exception {
                User u = currentSiteUser();
                if (u == null) {
                    return super.callLogic();
                }
                // Confirm first argument: site id vs other context id for YOUR stack
                long roleBits = getRole(currentSite().id(), u);
                // Use roleBits only if you already have a documented bitmask convention
                return super.callLogic();
            }
```

### `boolean isUserInAllowedRoleForName(String roleKey, String name) throws Exception` / `boolean isUserInAllowedRoleForName(String roleKey, List<String> names) throws Exception`

- **What:** Check whether the current user is allowed for a **string-keyed role** / permission name; second overload tests **multiple** names.

- **When to use:** When nearby actions already use isUserInAllowedRoleForName for the same customer/subscription/account-field pattern—copy that usage (AccountFieldActionHelper, customer/subscription details/edit actions).
- **Example:**
```java
    public String insrtCustomField(String apiName, List<String> roles) throws Exception{
        if(!isUserInAllowedRoleForName(apiName, roles)){
            return "";
        }
        return CFUIHelper.genEditDiv(EntityType.customer,customerCF,apiName, isReqParam(apiName));
    }
```
- **Example:**
```java
    public static boolean isFieldAcceptable(AppActionModel act, Field field)throws Exception{
        return act.isUserInAllowedRoleForName(field.paramName, field.roleNames) && isCFPresent(field.paramName);
    }
```


### `boolean isUserAllowed(Route route)`

- **Description:** This function jist answers the question "Is the current user allowed for a route"?
- **Role:** **Fine-grained UI gating** beyond a single action’s **`$roles`**.

- **When to use:** Hiding or enabling navigation to another action; mirroring existing table/menu code.
- **Requirement:** **`Route`** must match **`Routes`** / generated constants; align with **`$roles`** on the target action.
- **Example:**
```java
        JSONObject data = new JSONObject();
        data.put("showMigrationWizard", showWizard);
        data.put("isAdminOrOwner", isAdminOrOwner);
        data.put("canViewDashboard", isUserAllowed(Routes.rspa.dashboards_index));
        return sendAjaxResponse(data);
```
- 
---

## 10. CSRF

### `String csrfToken()`

- **Description:** Used to return the CSRF token related to the page/user.
- **Role:** Browser security; pairs with **`validateAjaxRequest`** / **`validateCSRF`** in **`exec()`**.

- **When to use:** When rendering forms that POST to actions with ajax precheck enabled.
- **Example:**
```java
         out.print(eh( act.csrfToken() ));
```

### `protected void validateCSRF() throws Exception`

- **What:** Runs the **CSRF token check** for this request (compares submitted token to session / framework rules). 


- **When to use:** **Almost never


---

## 11. Feature sets (entitlements, limits, validation)

### `boolean isAllowedFeature(FeatureSet.Feature f) throws Exception` / `boolean isAllowedFeature(FeatureSet.Feature f, Object ctx) throws Exception`

- **What:** Used to answer the question is this Feature allowed for the current User.One-arg — default check: current user + current site/merchant as implied context.Two-arg — same check but passes an extra Object ctx when the framework needs additional context for that feature (operand-specific rules). null is used when there is no extra operand (CurrenciesApi, EditSiteAction style).
-
- **When to use:** Before doing work that should only run if the tenant pays for / has that capability (TaxJar UI, gift subscriptions, languages, notifications groups, etc.).Before expensive reads or mutations so you fail fast or show upgrade / locked UI.
- **Requirement:** Use the **`Feature`** constants from the framework/product; do not invent names.
- **Example:**
```java
        data.put("featureAllowed", isAllowedFeature(feature));
```

- **Example:**
```java
            GlobalUtil.assert_(model.isAllowedFeature(MCP_AUTO_EXCHANGE_RATE, null), WebErrorCodes.API_NEEDS_PLAN_UPGRADE);
```




### `boolean isFeatureQtyReachingLimit(FeatureSet.Feature f) throws Exception` / `boolean isFeatureQtyReachingLimit(FeatureSet.Feature f, Object ctx) throws Exception`

- **What:** this function is used to answer the question is Feature of the current user approaching the limit.

- **When to use:** Before creating something that consumes quota — optional warn or disable invite (product decision).
- **Example:**
```java
        config.canInviteUser = isAllowedFeature(AppFeatures.USERS);
        config.featureName = AppFeatures.USERS.value();
        config.isUserCountReachingLimit = isFeatureQtyReachingLimit(AppFeatures.USERS);
        config.quantityAllowed = getAllowedFeatureCount(AppFeatures.USERS);
```

### `boolean isFeatureCheckDisabled(FeatureSet.Feature f)`

- **What:** **True** when **feature checks** are **disabled** for **`f`** (admin override, test mode, or product flag).

- **When to use:** Internal / support / migration / sync tools that must run even if plan entitlements would normally block something.
- **Requirement:** Dangerous on merchant routes — use with platform guidance.
- **Example:**
```java
            if (isFeatureCheckDisabled(AppFeatures.SOME_FEATURE)) {
                // Bypass or simplify entitlement logic — only where product allows
            } else {
                // Normal path: isAllowedFeature(...), limits, etc.
            }
```

### `Integer getAllowedFeatureCount(FeatureSet.Feature f) throws Exception`

- **What:** Returns allowed quantity (or cap) for a counted feature (may be **`null`** when unlimited / N/A).

- **When to use:** Quota displays and pre-checks before bulk create.
- **Example:**
```java
        AppFeatures feature = AppFeatures.LANGUAGES;
        Integer featureCount = getAllowedFeatureCount(feature);
        // ...
        if (featureCount == null) {
            featureCount = -10;
        }
        languageSettings.allowedFeatureCount = featureCount;
```

### `void validateFeature(FeatureSet.Feature f) throws Exception`

- **What:** A guard on AppActionModel (framework) that enforces plan/entitlement rules for feature f.
  If the current tenant is not allowed to use that feature, the method throws (typically a product error / upgrade path)—so the rest of callLogic() can assume “this feature is OK to use.”

Returns nothing on success; failure = exception, not false. 

- **When to use:** At the start of callLogic() (or a private helper) for actions that always require a given feature when the route runs.
- **Example:**
```java
@Override
public Forward callLogic() throws Exception {
    validateFeature(AppFeatures.SOME_FEATURE);  // throws if not entitled
    // safe to proceed
    return super.callLogic();
}
```

### `boolean validateFeature(FeatureSet.Feature f, Object ctx) throws Exception`

- **What:** It returns a boolean result for “allowed vs not allowed” under that context (per the pattern in your doc). throws Exception still applies for configuration/DB/system failures or for hard failures—confirm in AppActionModel Javadoc / javap: some stacks use boolean only for soft outcomes and throw for real violations.

- **When to use:** Contextual entitlement — same feature, different answer depending on which row or which sub-mode (mirrors isAllowedFeature(f, ctx)).
- **Example:**
```java
@Override
public Forward callLogic() throws Exception {
    Object operand = someEntityOrId;  // must match what this Feature expects
    boolean ok = validateFeature(AppFeatures.SOME_FEATURE, operand);
    if (!ok) {
        // Soft path: show message, redirect, or skip work — per product
        return super.callLogic();
    }
    // proceed
    return super.callLogic();
}
```

### `void validateFeature(boolean condition, FeatureSet.Feature f) throws Exception` / `void validateFeature(boolean condition, FeatureSet.Feature f, Object ctx) throws Exception`

- **What:** **Conditional** feature validation:If condition is true, the framework runs the same entitlement check as for feature f (and, in the 3-arg form, uses ctx the way that feature expects—operand / entity / mode).If condition is false, it does nothing (no throw from this call for “feature not allowed”).
`
- **When to use:** When only some branches of callLogic() need a plan gate—e.g. turning a feature ON or switching to a paid mode, but not when turning it OFF or staying on a free path.
- **Example:**
```java
        Boolean enabled = (((Boolean) get("enabled")));
        validateFeature(enabled, AppFeatures.LANGUAGES);
        SiteLocale sl = toggleLocale(cbLocale, enabled);
```

### `boolean isFeatureAllowed(FeatureSet.Feature f, Object ctx) throws Exception`

- **What:** A read-only entitlement check: “Given feature f and extra context ctx, is this allowed for the current tenant?”
  Returns true / false instead of throwing when the answer is “not allowed” (unlike validateFeature, which is usually fail-fast).
- **Role:** Read-only check without throwing.
- **When to use:** Branching UI or logic — show/hide, enable button, pick code path without aborting the whole request.Whenever ctx matters: per-quantity, per-entity, per-setting entitlement (same role as isAllowedFeature(f, ctx)).
- **Example:**
```java
        if (isFeatureAllowed(AppFeatures.SOME_FEATURE, someOperand)) {
            // proceed
        } else {
            // show upgrade / disable control
        }
```


---

## 12. Time travel and business entity

### `boolean isSiteInTimeTravelMode()`

- **What:** A no-arg method on the action (from AppActionModel in your stack) that returns true when the current site is in time machine / demo time-travel mode—i.e. the product is simulating another date or running a sandboxed “what if” flow where real writes can be dangerous or disallowed.

- **When to use:** Before destructive or state-changing work in callLogic() — block, no-op, or return a friendly error/forward so users don’t corrupt demo or time-shifted data.Actions that mutate state and sibling code already checks time-travel.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            if (isSiteInTimeTravelMode()) {
                // Product policy: often block writes or return a specific error/forward
                getErr().add(...);  // or return sendAjaxError / Forward — match sibling actions
                return null;
            }
            // normal mutation path
            return super.callLogic();
        }
```

### `static String getBeId()`

- **What:** A static helper on AppActionModel that returns the business entity (BE) id for the current HTTP request, usually taken from the same place the UI and filters use: query param / header keyed by the product constant (in cb-app this is often wired as CB_BE_ID_PARAM_NAME / BusinessEntityContextFilter.CB_BE_ID_PARAM_NAME—align with imports in your file).
Multi-BE means: one site can have several business entities; getBeId() tells you which BE the user is scoped to right now, on top of currentSite().
- **When to use:** Building URLs that must preserve BE context (append be_id / CB_BE_ID_* param so the next page stays in the same entity).Code that has no AppActionModel instance (JSP, static UI helpers) — use AppActionModel.getBeId().
- **Example:**
```java
            return sendAjaxRedirect(Utils.addBeIdToRoute(Routes.rnotifications.view_profiles.pathBuilder(), getString(CB_BE_ID_PARAM_NAME)));
```

---

## 13. Navigation, modal, currency, Leap UI probes

### `Tab<? extends Tab.CoreTabs> getMainTab()`

- **What:** A method on AppActionModel (and/or getMeta() chain—confirm on your AppActionModel API) that returns the main (left-nav) tab object for this action. That value comes from _defn when you set m.$tab(MainTabs.…, …) on AppActionMeta.
- **When to use:** Full-page admin UI with the standard chrome (sidebar / top nav)—JSP or layout code needs “which section is active?”
- **Example:**
```java
            void _defn(AppActionMeta m) {
                m.$method(get).$roles(ADMIN);
                m.$tab(MainTabs.CUSTOMERS, CustomersTabs.CUSTOMERS);  // pick from real product IA
                m.$path_fetch(qcustomers);
            }
```

### `void initModalVar() throws Exception`

- **What:** A lifecycle hook on AppActionModel (framework) that sets up modal UI state—things like request attributes, flags, or variables the modal layout / JSP expects. The framework calls it from doExec() (along with auth, isAllowed, etc.) for routes that are modal actions, so every modal request gets the same baseline setup.
- **When to use:** Framework: doExec() invokes it for modal flows.Only when you’re copying a modal action pattern and a sibling class overrides initModalVar() for the same product area—then extend with modal-specific setup there, not scattered across callLogic().When implementing modal-specific actions per sibling patterns.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            // initModalVar() already ran earlier in the request if this is a modal route
            return super.callLogic();
        }
```

### `CurrencyFilter getCurrencyFilter()`

- **Write:** A getter on AppActionModel (framework) that returns a CurrencyFilter — a small helper object that knows how to filter / format money columns for admin list and report pages (e.g. “only USD rows”, “use site’s reporting currency”, etc.—exact behavior is in CurrencyFilter / impl).
- **When to use:** Only when existing actions in that area already use getCurrencyFilter()—keep one pattern per feature.Currency-filtered listing actions that already use this pattern.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            CurrencyFilter cf = getCurrencyFilter();
            // pass cf into table config / query composer / JSP model
            return super.callLogic();
        }
```

### `boolean checkIfUiBetaEnabled() throws Exception`

- **What:** A method (usually on AppActionModel) that re-evaluates whether beta / Leap-style UI should be on for this request—not only the isUIBetaEnabled field that may have been set earlier in the pipeline. It can refresh internal state and return the current answer.

- **When to use:** When sibling code already calls checkIfUiBetaEnabled() for the same reason (e.g. building a URL that must embed a fresh beta flag).Flows that toggle or depend on Leap mid-pipeline. When sibling actions call **`checkIfUiBetaEnabled()`** explicitly.
- **Example:**
```java
    public String exportPath() throws Exception {
        URLBuilder b = new URLBuilder();
        b.path(rreports.create_export_job.path());
        b.p(exportParam, reportName);
        b.p(INCLUDE_NULL_RECORDS, Boolean.valueOf(checkIfUiBetaEnabled()).toString());
        return b.gen();
```

### `boolean isLeapUIAlreadyEnabled() throws Exception`

- **What:** A framework helper on AppActionModel (or nearby base type) that returns true when Leap UI is already turned on for the current site / user context, according to central rules (preferences, migration flags, etc.).false means Leap is not considered active yet, so enabling or redirecting into Leap may still be valid.

- **When to use:** Leap migration / feature-toggle actions.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            if (isLeapUIAlreadyEnabled()) {
                // Already on Leap — e.g. skip migration prompt or redirect to Leap home
                return super.callLogic();
            }
            // Safe to run “enable Leap” / classic→Leap redirect logic
            return super.callLogic();
        }
```

---

## 14. Execution pipeline and locking

### `Forward exec() throws Exception`

- **What:** **Outer servlet entry** for app actions: logging/CSP, **`validateHttpMethod`**, **`validateAjaxRequest`**, **`fetchSite`**, access blocks, **`checkForAuthentication`**, CSRF/global auth wrappers, then **callable** that runs **`doExec()`** and eventually framework **`ActionModel.exec()`**.

- **When to use:** Subclass only for **new base** action types (rare); feature actions implement **`callLogic()`**.

- **Returns:** **`Forward`**.


### `void doExec() throws Exception`

- **What:** Part of the request pipeline on AppActionModel. The outer exec() does early app work (site, auth, CSRF, etc.), then calls doExec() for the next layer of orchestration before your callLogic() runs
- **Role:** **Second-stage** app orchestration before business logic.

- **When to use:** Override doExec() only with platform-approved patterns (rare); leaf CRUD actions do not override it.


### `void checkAndLock() throws Exception`

- **What:** A hook in the framework request pipeline (extended on AppActionModel where needed) that runs before init() / param binding. It wires pessimistic locking (or other “claim this row first” plugins) so two requests don’t corrupt the same contested resource (subscription, invoice, etc.).
- **Role:** Pessimistic locking for contested resources.

- **When to use:**  CRUD usually **does not** override; use intermediate base when product already locks similar entities.
- **Requirement:** Call **`super.checkAndLock()`** unless platform documents otherwise.


### `final ResponseStateListener responseListenerImpl()`

- **What:** A final method on AppActionModel that returns a ResponseStateListener — a small framework object that gets hooked into the HTTP response lifecycle (for example around commit, flush, or completion of the servlet response). It exists because ActionModel’s contract needs a listener so the stack can track or finalize response-related work safely.
- **Role:** Wired into **`exec()`** pipeline; **final** on **`AppActionModel`**.

- **When to use:** Framework only it calls and uses.
- **Requirement:** Do not override (final).


### `void handleForward(Forward fwd) throws Exception`

- **What:** The framework method that takes your Forward object and actually applies it to the HttpServletResponse: redirect (302/303), JSP forward, include, ajax/JSON envelope, etc., according to Forward.Option and the rest of the framework rules. callLogic() is supposed to return a Forward (or null in some cases); later, the stack calls handleForward(...) so the browser/client gets the real HTTP outcome.
- **Role:** Central place to commit navigation outcome after **`callLogic()`** returns.

- **When to use:** Occasionally invoked from specialized flows that build **`Forward`** outside the default return path.
- **Requirement:** Prefer **`return forward;`** from **`callLogic()`** over manual **`handleForward`** unless copying an existing pattern.

- **In `callLogic()`:** Rare direct use.

---

## 15. Redirects and logout path

### `Forward redirectToAppLogin()`

- **Description:** Standard **redirect** to the **app login** page for the current site context.
- **Role:** Unauthenticated users hitting a protected action.

- **When to use:** Custom actions that manually enforce auth when meta cannot express it (rare).
- **Requirement:** Prefer **`$roles`** + framework auth so **`exec()`** handles login redirect.
- **Returns:** **`Forward`**.
- **In `callLogic()`:** Unusual; most auth exits happen before **`callLogic()`**.
- **Example:**
```java
        if (!Strings.isNullOrEmpty(errorMessage)) {
            flash(FlashManager.FlashType.ERROR, errorMessage);
            return redirectToAppLogin();
        }
```
### `Forward redirectToAppLogout()`

- **What:** Standard **redirect** to **logout** flow.
- **Role:** Explicit logout navigation from an action.
-
- **When to use:** Logout / session-invalidation actions.
- **Requirement:** Align with session cookie clearing patterns.
- **Returns:** **`Forward`**.
- **In `callLogic()`:** Logout handlers.
- **Example:**
```java
        if (!Strings.isNullOrEmpty(errorMessage)) {
            flash(FlashManager.FlashType.ERROR, errorMessage);
            return redirectToAppLogout();
        }
```

### `boolean isLogoutPath()`

- **What:** **True** when the **current request path** is classified as a **logout** route.
- **Role:** Skip certain analytics or consent steps on logout hits.

- **When to use:** Hooks/filters or actions mirroring existing logout detection.
- **Requirement:** Keep consistent with **`Routes`** logout definition.
- **Returns:** **`boolean`**.
- **In `callLogic()`:** Rare.
- **Example:**
```java
    public static String loginModeRestrictedUrl(AppActionModel act, boolean checkCookie, LoginSession loginSession) throws Exception {
        //CBHttpUtil. act.req;
        Site site = act.currentSite();
        if (site == null || act.isLogoutPath()) {
            return null;
        }
```

### `Forward forwardToSupportRoleConsentPage()`

- **What:** **`Forward`** to **support-role consent** UI when internal users must accept policies before proceeding.
- **Role:** **`doExec()`** may redirect here when **`isSupportRole()`** and consent missing.

- **When to use:** Support-console actions that participate in consent gating.
- **Requirement:** Do not use on merchant-only routes.
- **Returns:** **`Forward`**.
- **In `callLogic()`:** When duplicating documented support consent flow.
- **Example:** ``
```java
    return forwardToSupportRoleConsentPage();
```
---

## 16. URL and request-context utilities

### `String appendAdditionalParams(String urlOrPath)`

- **What:** An instance method on AppActionModel that takes a URL or path string and returns a new string with extra query parameters added that the product considers standard context for outbound links—things like affiliate, business entity (be_id), or other non-secret tracking (exact set is framework/product-defined).
- **Role:** Consistent deep-linking from admin UI.

- **When to use:** Building merchant-visible links in JSP/JSON that must preserve context.
-**Example:**
```java
        resp.sendRedirect(appendAdditionalParams(url));
```

### `<V> Callable<V> validateRequestContext(Callable<V> work) throws Exception`

- **What:** Runs **`work`** inside **request-context validation** (business-entity, region, or other **Callable** wrapper the app installs).
- **Role:** Ensures sensitive mutations see consistent BE/region context.

- **When to use:** Actions that already wrap **`Callable`** this way for BE-sensitive batches.
- **Requirement:** Avoid long-running work inside the wrapper; follow sibling timeout patterns.
- **Returns:** Result of **`work.call()`**.
- **In `callLogic()`:** Scoped mutations.
- **Example:** `return validateRequestContext(() -> { … db work … });`

### `void startActionTracking()`

- **What:** An instance method on AppActionModel that starts a tracking / tracing / analytics span for this action execution—so observability tools (metrics, APM, internal trackers) can correlate logs and timings with which URL/action ran.

It is telemetry plumbing: no business logic, no return value.
- **Role:** Metrics and APM correlation for heavy or critical routes.

- **When to use:** When sibling actions in the same package call it.
- **Requirement:** Do not double-start without idempotent semantics.
- **Returns:** **`void`**.
- **In `callLogic()`:** Optional telemetry hook.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            startActionTracking();  // only if a neighbor action does this with documented idempotency
            return super.callLogic();
        }
```

---

## 17. Factory and codegen

### `static AppActionModel createAction(RouteImpl route, HttpServletRequest req, Long userRoles) throws Exception`

- **Description:** Builds an action **instance** for tooling/tests: **`PojoHelper.createNewInstance`**, **`setMeta`**, **`setDetails(req, null)`**, optional **`site(...)`**, **`init()`** in some paths, optional **`userRoles`** bitmask.
- **Role:** **Not** the normal servlet path; simulates actions without full filter stack.
- **Example:** Test `AppActionModel.createAction(Routes.rx.foo, req, null)`.
- **When to use:** Internal tests or utilities that already use **`createAction`**.
- **Requirement:** Normal browser traffic uses standard **`exec()`**; **`init()`** semantics still apply when **`exec()`** runs.
- **Returns:** Concrete **`AppActionModel`** subclass instance.
- **In `callLogic()`:** **Never** for request handling.

**Arguments:** **`userRoles`** when the factory path needs a **bitmask** without a full session; omit when defaults suffice.

### `static void main(String[] args)`

- **What:** **Codegen** entry — delegates to **`ActionUtil.generateAction`** (writes the path/Pattern to Routes.java.)
- **Role:** **Developer** tool, not production request handling.
- **Example:** Run from IDE with generator args per internal docs.
- **When to use:** Only when maintaining codegen workflows.
- **Requirement:** Never invoke from servlet pipeline.
- **Returns:** N/A.
- **In `callLogic()`:** N/A.

-**NOTE:**  **When this main() runs path of the Action Route gets registered to the Routes.java**

---

## 18. JSON / ajax helpers — which to use when

**Where they live:** **`AppActionModel`** extends **`ActionModel`**, which implements **`com.chargebee.framework.web.AjaxResponse`**. Most **JSON/ajax** helpers are declared on **`AjaxResponse`** / **`ActionModel`** — **`AppActionModel`** inherits them unchanged. **`verify` exact signatures** in your IDE after framework upgrades.


**`_defn` pairing (CSRF / ajax gate):**

| If you use… | Typical **`_defn`** |
|-------------|---------------------|
| **`sendAjaxResponse`** / **`sendAjaxRedirect`** / most **admin ajax** flows | **`m.$ajaxPrecheck(true)`** (default in many actions) — client must satisfy **ajax/CSRF** rules; use **`csrfToken()`** in the form. |
| **`sendJsonResponseNoAjaxCheck`** / **machine JSON** APIs (curl, SPA with own CSRF story) | **`m.$ajaxPrecheck(false)`** — **only** when product/security approves skipping the standard ajax precheck for this route. |

---

### 18.1 Scenario table — pick a helper

| Goal | Use | Returns |
|------|-----|---------|
| Plain JSON in the body (APIs, fetch, mobile) — no Chargebee ajax wrapper| **`sendJsonResponseNoAjaxCheck(JSONObject)`** | **`Forward`** |
| Multipart upload (file form) but still plain JSON out | **`sendJsonResponseMultipartReq(JSONObject)`** | **`Forward`** |
| Old-style admin ajax — JSON inside the usual wrapper (flash, layout bits, etc.)| **`sendAjaxResponse(JSONObject)`** or **`sendAjaxResponse(String)`** | **`Forward`** |
| Ajax wrapper plus a flash-style message string | **`sendAjaxFlashResponse(String)`** | **`Forward`** |
| After POST, tell the browser to reload the whole page | **`sendAjaxReload()`** | **`Forward`** |
| Ajax with one JSON field, e.g. { "count": 3 } without building the object by hand | **`sendAjaxProp(String name, Object value)`** | **`Forward`** |
| A toggle/switch with a fixed JSON shape (on/off) | **`sendSwitchON(JSONObject, boolean)`** or **`sendSwitchON(boolean)`** | **`Forward`** |
| Ajax should go to another page using a typed route | **`sendAjaxRedirectTo(Route)`** | **`Forward`** |
| Ajax should go to a URL string you already built | **`sendAjaxRedirect(String)`** or **`sendAjaxRedirect(String, JSONObject)`** (extra JSON for client) | **`Forward`** |
| Almost no body — just HTTP status (bad request / OK / no content) | **`sendBadRequest()`** / **`sendOk()`** / **`sendNoContent()`** | **`void`** — then **`return null`** *if* your base expects that (confirm siblings) |
| Ajax/JSON error with a code + message | **`sendError(String code, String message)`** | **`Forward`** |
| Admin Symmetry / segment invoke — many status lines in one ajax response | **`sendAjaxResponseForAdminInvokeActions(List<String>)`** | **`Forward`** |
| Rare: shove a value into a global JS variable from the server | **`setGlobalVariableInJs(String name, String value)`** | **`Forward`** |


---

### 18.2 `Forward sendJsonResponseNoAjaxCheck(JSONObject json) throws Exception`

- **When:** Writes **`json`** as the response body (typically **`application/json`**) **without** running the **ajax precheck** path that **`sendAjaxResponse`** expects.


- **When to use:** **`cb-app`** JSON CRUD actions that set **`m.$ajaxPrecheck(false)`** and return structured JSON only.
- **Requirement:** CSRF/session policy must still be correct for **browser** callers; **`false`** precheck is not “no security” — align with **[AppActionMeta-LLM.md](../AppActionMeta/SKILL.md)** and security review.
- **Example:**
```java
            @Override
            public Forward callLogic() throws Exception {
                JSONObject body = new JSONObject()
                        .put("ok", true)
                        .put("data", "...");
                return sendJsonResponseNoAjaxCheck(body);
            }
```
---

### 18.3 `Forward sendJsonResponseMultipartReq(JSONObject json) throws Exception`

- **What:** Like **`sendJsonResponseNoAjaxCheck`**, but for requests parsed as **multipart** (file upload + fields) where the **response** is still JSON.

- **When to use:** Only when the request is **multipart** and siblings use this exact helper.

- **Example:**
```java
    @Override
    public Forward callPostLogic() throws Exception {
        Attachment at = createWithParams(qattachments);
        at.entityExternalId(getString(entity_external_id));
        assertEntityInDB(at);
        FileItem f = getFile("file_item");
        if (f == null) {
            throw ValidateErrorCodes.UPLOAD_ERROR.err(qattachments.description.paramName());
        }
        // ... validate file name ...
        FileUploadHelper helper = new FileUploadHelper(f, at);
        helper.execute();
        flash(FlashManager.FlashType.NOTICE, "File Uploaded Successfully");
        JSONObject response = new JSONObject();
        String path = at.getRedirectRoute();
        response.put("forward", path);
        return sendJsonResponseMultipartReq(response);
    }
```
- 


---

### 18.4 `Forward sendAjaxResponse(JSONObject json) throws Exception` / `Forward sendAjaxResponse(String json) throws Exception`

- **What:** Embeds **`json`** (object or pre-serialized string) in the **Chargebee admin ajax** response envelope (together with framework fields for flash, errors, etc., per version).

- **When to use:** Autocomplete actions, admin widgets, hosted-page ajax that already use **`sendAjaxResponse`** in the same area.
- **Requirement:** **`$ajaxPrecheck(true)`** typical; pair with **`csrfToken()`** on the form.
- **Example:**
```java
    public Forward callLogic() throws Exception {
        boolean showWizard = canShowMigrationWizard();
        boolean isAdminOrOwner = isUserInRoles(ownerRolesBit()) || isUserInRoles(adminRolesBit());
        
        JSONObject data = new JSONObject();
        data.put("showMigrationWizard", showWizard);
        data.put("isAdminOrOwner", isAdminOrOwner);
        data.put("canViewDashboard", isUserAllowed(Routes.rspa.dashboards_index));
        return sendAjaxResponse(data);
    }
```
---

### 18.5 `Forward sendAjaxFlashResponse(String message) throws Exception`

- **What:** Ajax response that carries a **flash-style** message string in the ajax envelope (user-visible banner after submit).

- **When to use:** Simple success/failure text for **ajax** forms when siblings use this pattern.
- **Example:**
```java
    public Forward _update_brand_color() throws Exception {
        String brandColor = get(qbrands).brandColor();
        Brand brand = qbrands.dbFetchOne();
        if (brand == null) {
            new Brand().brandColor(brandColor).dbInsert();
        } else {
            brand.brandColor(brandColor).dbUpdate();
        }
        SiteConfig.HOSTED_PAGES.updateNow();
        Audit.lg("Brand color updated to " + brandColor + ".");
        return sendAjaxFlashResponse("Brand color saved.");
    }
```

---

### 18.6 `Forward sendAjaxReload() throws Exception`

- **What:** Instructs the **ajax client** to **reload** the full page.
- **Role:** Refresh complex server-rendered state after a partial ajax POST (e.g. cart/summary).

- **When to use:** Hosted pages / checkout-style flows that already return **`sendAjaxReload`**.
- **Requirement:** Do not use for **JSON APIs** consumed by **`fetch`** — clients won’t interpret reload instructions.
- **Example:**
```java
    @Override
    public Forward callPostLogic() throws Exception {
        new RemoveScheduledResumptionHelper(get(qsubscriptions)).execute();
        return sendAjaxReload();
    }
```

---

### 18.7 `Forward sendAjaxProp(String name, Object value) throws Exception`

- **What:** Ajax payload with a **single named property** (wrapper puts **`name` → `value`** for the client script).
- **Role:** Tiny responses (boolean flags, single id) without hand-building a full JSON tree in every action.
-
- **When to use:** When **`cb-app`** siblings return **`sendAjaxProp`** for the same widget.
- **Requirement:** For multiple fields, prefer **`JSONObject`** + **`sendAjaxResponse`**.
- **Example:**
```java
    @Override
    public Forward callLogic() throws Exception {
        return sendAjaxProp("version", MicroserviceVersion.buildVersion);
    }
```

---

### 18.8 `Forward sendSwitchON(JSONObject json, boolean on) throws Exception` / `Forward sendSwitchON(boolean on) throws Exception`

- **What:** Specialized ajax response for **toggle / switch** controls (settings UI), optionally merging extra **`json`** with on/off state.
- **Role:** Consistent shape for enable/disable controls in admin.

- **When to use:** Settings pages with binary toggles that already use this API.
- **Requirement:** Not for arbitrary JSON CRUD — use §18.2.
- **Example:**
```java
        @Override
        public Forward callLogic() throws Exception {
            boolean on = getBool("enabled");
            JSONObject extra = new JSONObject()
                    .put("setting_key", "calendar_billing")
                    .put("updated_at", System.currentTimeMillis());
            // ... persist on ...
            return sendSwitchON(extra, on);
        }
```


---

### 18.9 `Forward sendAjaxRedirect(String path) throws Exception` / `Forward sendAjaxRedirect(String path, JSONObject extra) throws Exception`

- **What:** Tells the **ajax client** to **`location`-navigate** to **`path`** (string URL or path), optionally attaching **`extra`** JSON for the client script.
- **Role:** When the target is **not** a typed **`Route`** constant (dynamic path builder, external path segment).

- **When to use:** Dynamic URLs; prefer **`sendAjaxRedirectTo(Route)`** when a **`Routes.*`** **`Route`** exists.
- **Requirement:** Validate **`path`** is same-origin / allowed — avoid open redirects.

- **In `callLogic()`:** Ajax POST → client-side redirect to string URL.
- **Example1:**
```java
    @Override
    public Forward callLogic() throws Exception {
        String handle = getString("subscription_id");
        Subscription sub = nc(qsubscriptions.handle.dbFetchOne(handle), CoreErrorCodes.RESOURCE_NOT_FOUND//
                .err("subscription id: " + handle));
        activateSubscription(sub);
        flash(FlashManager.FlashType.NOTICE, "Successfully activated subscription %s", sub.handle());
        return sendAjaxRedirect(rsubscriptions.details.path(sub.id()));
    }
```
-- **Example:**
```java
        String returnUrl = HostedPageActionHelper.getReturnUrl(req,
                get(qhosted_pages_settings), hsb.hp,
                s, HostedPageActionHelper.getInvoiceId(hsb.subData));
        // data contains tracker name and pixel url. data can be null if refersion is not enabled.
        JSONObject data = null;
        if ((hsb.hp.state_e() == HostedPage.State.SUCCEEDED)) {
            String subHandle = s != null ? s.handle() : null;
            Refersion refersion = Refersion.getRefersionInst(token, subHandle);
            data =  refersion != null ? refersion.getResponseData() : null;
        }
        // ...
        return sendAjaxRedirect(returnUrl, data);
```
---

### 18.10 `Forward setGlobalVariableInJs(String name, String value) throws IOException`

- **What:** Writes a **global JavaScript variable** assignment into the response (chrome/integration hook).
- **Role:** Rare compatibility with scripts expecting **`window.name = …`** from server.

- **When to use:** Only when duplicating an existing **`cb-app`** pattern.
- **Requirement:** Avoid for new JSON APIs — prefer JSON body + client bundler.

- **In `callLogic()`:** Exceptionally rare.
- **Example:**
```java
    @Override
    public Forward callLogic() throws Exception {
        JSONObject output = new JSONObject();
        // ... build CSP ...
        output.put("csp", formattedCsp);
        output.put("is_report_only", CheckoutEnvProps.isHpComponentCspReportOnly());
        if ("XMLHttpRequest".equals(this.req.getHeader("X-Requested-With"))) {
            return sendAjaxResponse(output);
        }
        return setGlobalVariableInJs(objectMapper.writeValueAsString(output.toString()), "csp");
    }
```



---


---

## 19. Which `AppActionModel` API to use — scenario table

| Scenario | Use |
|---------|-----|
| Save a row that belongs to this customer’s site (set site_id) | **`currentSite().id()`** | Canonical site after **`fetchSite`** in **`exec()`** |
| Load or change a row and make sure it’s not another tenant’s data | **`qtable.dbFetchOne(...)`** + **`where site_id = currentSite().id()`** | Avoid IDOR ([chargebee-framework-practices-LLM.md](./chargebee-framework-practices-LLM.md)) |
| Know which staff user is logged in| **`currentSiteUser()`** / **`currentUser()`** | Audit and branching — not a substitute for **`$roles`** |
| Decide whether to show a link/menu to another page | **`isUserAllowed(Route)`** | UI gating to match target action’s meta |
| Put a CSRF token in a form or compare a posted token | **`csrfToken()`** | Works with ajax/CSRF validation in **`exec()`** |
| Check plan / product feature (this site may or may not use X) | **`isAllowedFeature(...)`** / **`validateFeature(...)`** | Entitlement gate inside **`callLogic()`** |
| Read which Business Entity the UI is scoped to (multi-BE) | **`getBeId()`** | Header/param per **`CB_BE_ID_*`** |
| Block writes on time-machine / demo sites| **`isSiteInTimeTravelMode()`** | Product policy for demo sites |
| Get the main database row you set up with $create / $model / path fetch| **`get(qtable)`** | Inherited — [ActionModel-LLM.md §8.11](./ActionModel-LLM.md) |
|Read a simple input: id, text, column-backed param| **`getLong` / `getString` / `getParam(qcol)`** | Inherited — [ActionModel-LLM.md §8.17](./ActionModel-LLM.md) |
| Form failed validation — show errors on the same page | **`getErr().addParamError`** + **`getViewForward()`** | Inherited — [ActionModel-LLM.md §11](./ActionModel-LLM.md) |
| Send JSON back to the browser| See **§18.1** table — e.g. **`sendJsonResponseNoAjaxCheck`** vs **`sendAjaxResponse`** | Raw JSON APIs vs legacy **admin ajax** envelope |
| Who may hit this URL at all? (big gate) | **`$roles`** in **`_defn`**  | Runs **before** **`callLogic()`** via **`isAllowed`** |
| Highlight the correct left nav in admin HTML | **`m.$tab(MainTabs, …)`** in **`_defn`** | Match **product IA**; JSON APIs often **omit** **`$tab`** |
| Many actions share the same isRequired(Param) / param logic| **`extends`** **`AccountFieldActionModel`**, **`SegmentedParamProviderActionModel`** — §4.1 | Avoid copy-pasting overrides |

---

