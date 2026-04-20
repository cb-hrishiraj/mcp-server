# `AppActionMeta` — LLM reference (Chargebee application layer)


**Class:** `com.chargebee.app.AppActionMeta`  
**Extends:** `com.chargebee.framework.web.ActionMeta<com.chargebee.app.AppActionMeta>`.

**Description:** `Thia class is a wrapper over the ActionMeta,like ActionMeta this is also created only once,This class also contains application layer instructions like the handling the CSRF tokens,CORS policy and all the stuff.Think: AppActionMeta = the recipe card for this URL (ingredients = params, rules = roles/validation). AppActionModel = the cook who follows the card for each incoming request.`





---


---



## 1. Role in the framework

| Concept | Role |
|---------|------|
| **`ActionMeta`** | **Generic** action contract: HTTP method, URL pattern, **`Param`** list, validation, transactions, auth type, features, view path, etc. |
| **`AppActionMeta`** | **Chargebee product** extension: **tabs / breadcrumbs**, **app roles**, **analytics**, **portal / UI** flags, **site-setting gates**, **preference intent**, **business-entity profile**, **JWT**, **time machine**, **deprecated-resource** handling, and **`isAllowed`** integration with **`Site`**. |

**`AppActionModel.getMeta()`** returns **`AppActionMeta`**. The **same meta instance** is reused across requests; **`_defn`** runs when the action class is registered / loaded, not on every HTTP request (see [AppActionModel-LLM.md](../AppActionModel/SKILL.md)).

---

## 2. Where you configure it

Only inside the action class:

```java
public class CreateEmployeeAction extends AppActionModel<CreateEmployeeAction> {

    void _defn(AppActionMeta m) {
        m.$path("/employees/create");
        m.$moduleDefn(Defns.class);
        // $roles: derive from product RBAC + §5 matrix — do not copy unrelated demos
        m.$method(post).$roles(AppRole.ADMIN);
        // ...
    }
}
```


---





## 5. Access, roles, and session

### `$roles(Role... roles)`

- **What:** This function is used to set the rules for the page/url so that the only the user/visitor hhaving such role according to chargebee has special authentication and authorization before visiting the page or can be said running the callLogic() of the route.
- **Example :** `m.$method(post).$roles(AppRole.FINANCE_EXECUTIVE);` or `m.$roles(AppRole.CUSTOMER_SUPPORT);` or `m.$roles(new Role[] { AppRole.ADMIN });`. The pair **`CUSTOMER_SUPPORT, SALES_AGENT_CPQ`** appears in **specific** demos (e.g. customers/subscription-adjacent JSON); use it **only** when both roles are required by product.
- **When to use:** Almost every **authenticated** admin or portal action.

**Arguments accepted**


- **`Role... roles`** — varargs of **`com.chargebee.framework.web.Role`**, typically **`com.chargebee.app.config.AppRole.*`** (`ADMIN`, `CUSTOMER_SUPPORT`, `END_USER`, …) or framework **`Role.*`** (`USER`, `UNAUTH_USER`, `SUPER_ADMIN`, `SERVICE_ADMIN`, `READ_ONLY`, …).
-**`NOTE`** -The arguments to be used should be according to the end user for whom the route is being coded,so according to the business requirement one should see the table below of the roles best suited.No roles are to be newly created it has to be used from the table below.




#### Role catalog — `AppRole` (`com.chargebee.app.config.AppRole`)

These extend **`Role`** and are the usual **`$roles`** values for **merchant team** and **portal** actions (verified from **`webapp/WEB-INF/core_classes/.../AppRole.class`**).

| Constant | Typical access scope | When to use in `$roles` |
|----------|----------------------|-------------------------|
| **`OWNER`** | The main business owner of the merchant site | Only flows the product says only the owner may do (often stricter than normal admin). |
| **`ADMIN`** | Any merchant admin with wide access | Normal settings / catalog / billing screens when regular admins are allowed. |
| **`CREDIT_AID_OWNER`** / **`CREDIT_AID_ADMIN`** | Credit Aid feature only| Complete access to the site specific for CreditRepairCloud customer. |
| **`BUSINESS_ENTITY_ADMIN`** | Merchants with several business entities| When the action is about one entity (often together with BE-specific meta).Access to invite user to entity |
| **`FINANCE_EXECUTIVE`** | Finance team on the merchant site| Money-heavy areas (invoices, revenue, dunning, tax) with narrower access than full ADMIN. User has complete read only access to the site except for Settings. User can also export data and add comments.|
| **`SALES_MANAGER`** | Sales managers | Oversight of quotes/CPQ and team sales setup—not every support agent.User has Customer Support level access and has complete access to coupons and coupon sets. |
| **`CUSTOMER_SUPPORT`** | Day-to-day merchant staff | Everyday work on customers, subscriptions, credits—usual “least power” admin role.In addition to Sales Agent level access, user can perform all actions related to Customers, Subscriptions, Invoices, Transactions, and Credit Notes, except deleting.|
| **`SALES_AGENT_CPQ`** | People who create/edit quotes (CPQ)| Quote and CPQ screens; combine with CUSTOMER_SUPPORT or SALES_MANAGER if the spec says so.In addition to Sales Agent level access, user can create quotes and convert them to subscriptions, but cannot create or edit subscriptions directly. |
| **`SALES_AGENT`** | Sales users without full CPQ | Sales-facing pages that are not full CPQ.In addition to Tech Support level access, user can change trial end dates and apply discounts on subscriptions. |
| **`ADVANCED_METRICS`** | Users who may see deeper analytics | Extra dashboards/metrics not shown to everyone.In addition to Tech Support level access, user can change trial end dates and apply discounts on subscriptions. |
| **`TECH_SUPPORT`** | Technical admins on the merchant site | Integrations, gateways, technical switches—as defined by the product.User can view "Subscriptions" and "Product Catalog" tabs. Can also view, add comments to, send, download individual Invoices/Credit Notes.|
| **`END_USER`** | Your customer (logged into portal / hosted pages) | Self-service flows; use with $isPortalAction(true)—not for the merchant admin console. |


#### Role catalog — framework `Role` (`com.chargebee.framework.web.Role`)

Used for **Chargebee-internal** operators, **auth primitives**, and tooling (verified from **`webapp/WEB-INF/frm_classes/.../Role.class`**). Many are **`INTERNAL_APP` / `SYSTEM`**-style roles in the framework (**`role.type()`** → **`Role.Type`**: **`APP`**, **`INTERNAL_APP`**, **`API`**, **`SYSTEM`** — confirm per role in the IDE).

| Constant | Typical access scope                          | When to use in `$roles`                                                  |
|----------|-----------------------------------------------|--------------------------------------------------------------------------|
| **`USER`** | Any logged-in merchant user (generic)         | User who has  signed in                                                  |
| **`UNAUTH_USER`** | Not logged in (guest)                         | User who has signed in.                                                  |
| **`SUPER_ADMIN`** | Chargebee internal — top power                | User who is a chargebee super admin.                                     |
| **`NOC_ADMIN`** | Chargebee internal — network/ops              | User who is a chargebee Noc admin                                        |
| **`SERVICE_ADMIN`** | Chargebee internal — service/ops              | User who is a chargebee admin.                                           |
| **`SRE`** | Chargebee internal — reliability              | User who is a chargebee SRE.                                             |
| **`ADMIN_FINANCE`** | Chargebee internal — finance                  | User who is a chargebee user finance.                                    |
| **`SUPPORT_SMES`** | Chargebee internal — support by level         | User who is a chargebee support smes user                                |
| **`RS_SUPPORT`** | Chargebee internal — revenue support          | User who is a chargebee revenuestory advanced support user               |
| **`SERVICE_DEV_SUPPORT`** |  Chargebee internal — eng / service desk                                         | User who is a chargebee dev support user                                 |
| **`READ_ONLY`** | Chargebee internal — safe read                | Chargebee user with read only access to data browser.                    |
| **`MIGRATION_ENGINEER`** | Chargebee internal — migrations               | Chargebee user who handles merchant migration data.                      |
| **`FULL_ACCESS`** | Chargebee internal — very broad               | Allows full access to your Chargebee site.. |
| **`SUCCESS_ADVANCE`** | Chargebee internal — advanced Customer Sucess | Internal CS advanced tooling.                                            |



### `$allowedRolesForBEProfile(BusinessEntityProfileType beType, Role... roles)`

- **What:** Some merchants run more than one “business entity” (BE) under one site—like separate brands or units that each have their own tax, invoices, or branding.

This method says: “Depending on whether the user is working in whole-site mode or one specific business entity mode, which roles are allowed for this action?”

- **When to use:** Screens where **site context** and **BE context** should allow **different** role sets (tax, branding, invoices).
- **Example:**
```java
void _defn(AppActionMeta m){
        m.$allowedRolesForBEProfile(BusinessEntityProfileType.SITE, ADMIN);
        m.$allowedRolesForBEProfile(BusinessEntityProfileType.SPECIFIC_BE,ADMIN,BUSINESS_ENTITY_ADMIN);
}
```
---

### `$businessEntityProfileType(BusinessEntityProfileType type)`

- **What:** Tells the framework which “business entity mode” this route lives in by default: whole site vs one specific business entity, or turn BE handling off for this flow. That drives how context is resolved and how gates (with $allowedRolesForBEProfile, etc.) are applied.

- **When to use:** Set it in _defn when the screen or API is clearly site-wide (tax settings, org-wide config) or clearly about one BE (entity admin, entity-scoped prefs). If who may access changes by mode, add $allowedRolesForBEProfile for SITE vs SPECIFIC_BE on the same action..

**Arguments accepted**

- **`type`** — `SITE`, `SPECIFIC_BE`, `DISABLED`.

**Which argument when**

- **Site-wide settings / taxes / filters** → `SITE`.
- **Per-entity maintenance** → `SPECIFIC_BE`.
- **BE product off for this flow** → `DISABLED`.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(post).$roles(AppRole.CREDIT_AID_ADMIN);
        m.$auth(AuthType.Authenticated);
        m.$businessEntityProfileType(BusinessEntityProfileType.SPECIFIC_BE);
        m.$allowedRolesForBEProfile(BusinessEntityProfileType.SPECIFIC_BE,BUSINESS_ENTITY_ADMIN,CREDIT_AID_ADMIN);
    }
```

---

### `$ignoreBEResolutionFromResourceAndInput()`

- **What:** Turns off the framework’s usual “figure out the Business Entity from the URL resource + request input” step for this endpoint. The route is treated as not auto-binding BE context from those sources.

- **When to use:** Only when default BE resolution is wrong for this operation—e.g. the resource id in the path is not the BE you want, the API is cross-cutting, or BE should come only from explicit app logic later. It is an escape hatch, not a default.
- **Example:**
```java
void _defn(AppActionMeta m) {
    m.$method(HttpMethod.post)
            .$path("/some/route")
            .$ignoreBEResolutionFromResourceAndInput()
            .$auth(AuthType.Authenticated);
}
```

---

### `$auth(AuthType authType)`

- **What:** Sets authentication mode whether the user/visitor would be authenticated or not .

- **When to use:** Public hosted pages, strict unauth flows, or session-required admin (default when unset).

**Arguments accepted**

- **`AuthType`** — e.g. `Unauthenticated`, `StrictlyUnauthenticated`, `Authenticated`,`Unauthenticatedredirect`.

**Which argument when**

- **Browser checkout / component metadata, no login** → `Unauthenticated` + appropriate **`$roles`**.
- **Must never create session** → `StrictlyUnauthenticated` (portal helpers).
- **Normal app after login** → omit or use default session **`AuthType`** per framework.
- **for Authenticated it's default behaviour**
- **Example:**
```java
void _defn(AppActionMeta m) {
    m.$method(HttpMethod.post)
            .$path("/some/route")
            .$ignoreBEResolutionFromResourceAndInput()
            .$auth(AuthType.Authenticated);
}
```

---

### `$allowPendingSessions(LoginSessionBase.PendingReason reason)`

- **What:** This function sets instructions inside the map of the AppActionMeta that to allow Pending sessions.Permits execution while the session is **pending** (MFA, password expiry, setup incomplete).

- **When to use:** Onboarding submit actions, MFA recovery, password-expiry flows.

**Arguments accepted**

- **`PendingReason`** — `PASSWORD_EXPIRY`, `MFA`, `COMPLETE_SETUP`.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(post).$roles(USER);
        m.$auth(AuthType.Authenticated).$allowPendingSessions(LoginSessionBase.PendingReason.MFA);
        m.$subDomainOpt(SubDomainOpt.strictly_no);
        m.$param(m.$forward_url());
        m.$param(m.$string("client_id").$maxChars(50));
        m.$schema(Schema.COMMON);
```



---

### `$requiresGlobalAuth(boolean enable)`

- **What:** Generally users are authenticated via sessions data,from sessions it is know whether the user is logged or not.But this function Forces for globalAuthentication not just normal logged sessions.

- **When to use:** Actions that must prove **global user** identity, not only current site membership.
- **Requirement:** **Optional**; use only when product/security demands it.

**Arguments accepted**

- **`boolean enable`** — `true` to require global auth, `false` to clear.

**Which argument when**

- **Strict global check** → `true`.
- **Revert / default** → `false`.
- **Example:**
```java
    void _defn(AppActionMeta m){
        m.$roles(USER);
        m.$auth(AuthType.Authenticated);
        m.$subDomainOpt(SubDomainOpt.optional);
        m.$schema(Schema.COMMON);
        m.$requiresGlobalAuth(true);
    }
```

---

### `$enableSupportRole(boolean enable)` / `$checkSupportRoleConsent(boolean enable)`

- **Description:** Sometimes there are some bug in the product that could be solved by the chargebee's tech support team.So there are two functions here first one is whether to enable the feature and then there is function to take consent from the merchant whether the merchant is comfortable with support role entering into the app ,if both are enabled then only the feature works.

- **When to use:**  explicit support tooling.
- **Requirement:** **Optional**; default behavior applies when unset.

**Arguments accepted**

- **`boolean enable`** — for **`$enableSupportRole`**, turn support-role handling on/off; for **`$checkSupportRoleConsent`**, `true` = enforce consent, `false` = skip consent prompt where allowed.

**Which argument when**

- **Allow support tools to hit this action** → `$enableSupportRole(true)` (if product requires).
- **Support team Login must not stall on consent** → `$checkSupportRoleConsent(false)` (only where security review allows).
-**Example:**
```java
    void _defn(AppActionMeta m) {
        m.$txnOpt(TxnOpt.NOT_REQUIRED).$allowSlaveDB(true);
        m.$path("/search").$col(ActionCols.resource);
        m.$allowJwtAuth(true);
        m.$isSearch(true);
        m.$enableSupportRole(true);
        m.$corsEnabled(true); // enabled to req from storefronts
```
---

### `$allowJwtAuth(boolean allow)`

- **What:** This function sets instruction inside the map datastructure that to allow the JWT Authentication to the webpage .Allows **JWT**-authenticated requests (Leap, CPQ, embedded search, etc.).

- **When to use:** SPA or widget calls that send **Bearer JWT** instead of classic session.
- **Example:**
```java
    void _defn(AppActionMeta meta) {
        meta.$method(HttpMethod.post);
        meta.$allowJwtAuth(true);
        meta.$corsEnabled(true);
    }
```


---

## 6. Site, path, and custom gates

### `$allowIn(AllowInOpt opt)`

- **What:** As chargebee operates on LIVE and TEST site,this function feds instruction into the ActionMeta to allow the operations in which site Test site/live site.Restricts the action to **live** sites, **test** sites, or **both**.

- **When to use:** `when the actions could be just for testing or for live if all the checks are confirmed.`
- **Requirement:** **Optional**; omit if the action is valid on **all** site types.

**Arguments accepted**

- **`AllowInOpt`** — `live`, `test`, `both`.

**Which argument when**

- **Sandbox-only feature** → `test`.
- **Production-only checklist / billing** → `live`.
- **No restriction** → `both` or omit.
- **Example:**
```java
        void _defn(AppActionMeta m) {
            m.$beta("add_stripe_gateway_using_api");
            m.$method(HttpMethod.get).$allowIn(AllowInOpt.live).$allowedOnlyViaUI(true).$roles(CUSTOMER_SUPPORT);
            m.$tab(MainTabs.CONFIGURATIONS, SettingsTabs.SETTINGS, SiteSettingsTabs.GATEWAY);
        }
```

---

### `$allowOnlyIfLiveEnabled(boolean enable)`

- **What:** This function feds instruction into ActionMeta whether to allow to enter/access this page only if LIVE is enabled .Additional **“live enabled”** site check (product-specific; evaluated in app **`isAllowed`** stack).
- **When to use:** Actions that must not run until the site is **commercially live** or similar flag.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get).$txnOpt(TxnOpt.REQUIRED);
        m.$roles(AppRole.ADMIN).$allowOnlyIfLiveEnabled(true);
        m.$tab(MainTabs.CONFIGURATIONS, SettingsTabs.SETTINGS);

```

---

### `$setAllowedPaths(AllowedPaths paths)`

- **Description:** This function restricts the page/url to be accessed via ceratin ways only not via browser\ui directly by typing the url link.Restricts whether the action is valid from **main app**, **symmetry**, or **either**.

- **When to use:** Login, callbacks, or admin tools that exist on **multiple bases**.

**Arguments accepted**

- **`AllowedPaths`** — `APP`, `SYMMETRY`, `BOTH`.

**Which argument when**

- **Merchant UI only** → `APP`.
- **Internal symmetry console only** → `SYMMETRY`.
- **Login / shared redirects** → `BOTH`.
-**Example:**
```java
    void common_defn(AppActionMeta m) {
        m.$subDomainOpt(SubDomainOpt.optional);
        m.$param(m.$forward_url());
        m.$setAllowedPaths(AllowedPaths.BOTH);
        m.$schema(Schema.COMMON);
        m.$checkSupportRoleConsent(false);
    }
```

---

### `$allowChecker(AppActionMeta.AllowChecker checker)`

- **What:** Besides the normal rules of role,authentication,session you sometimes want to have additional checks to allow user to access this page/run this action.Registers **`boolean allow(ActionModel m)`** for arbitrary **extra** checks in **`isAllowed`**.
- **When to use:** **Custom policy** when enums and roles are insufficient.
- **Example:**
```java
   void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get).$roles(AppRole.CREDIT_AID_ADMIN);
        m.$tab(MainTabs.CONFIGURATIONS, SettingsTabs.SETTINGS);
        m.$model(qemail_notification_settings);
        m.$allowChecker(new NotificationUtil.allowEmailV1Checker());
```




### `$siteSettingBased(SiteSettingBase.PropName prop)`

- **What:** This function sets instruction into the map that this Route/Action is only allowed to be accessed if "some condition" as same as database/site setiings.Stores **which site setting** must gate this action (**`siteSettingProp`** field).

- **When to use:** Entire action should **disappear or 403** unless a site setting is on/off.
- **Example:**
```java
import com.chargebee.app.models.base.SiteSettingBase.PropName;

void _defn(AppActionMeta m) {
    m.$method(HttpMethod.get)
            .$roles(AppRole.ADMIN);
    
    m.$siteSettingBased(PropName.get("your_setting_name"));  
    
}
```

---

## 7. Portal and client channel

### `$isPortalAction(boolean portal)`

- **What:** This function sets instruction whether the current page route is the portal action/self service page for the customers.Marks **customer self-service portal** actions; **`PortalBaseAction`** enforces **portal domain** and SSP rules.
- **When to use:** whenever the current site is for portal action..
-- **Example:**
```java
    void _defn(AppActionMeta m)
    {
        m.$method(get).$roles(UNAUTH_USER).$isPortalAction(true).$auth(AuthType.Unauthenticated);
        m.$path().$c("/portal/permalink").$col(ActionCols.portal_access_res_name).$col(ActionCols.portal_access_res_id).$col(ActionCols.portal_access_res_action);
```
---

### `$allowedOnlyViaUI(boolean uiOnly)`

- **What:** This function sets instruction into the Meta that the action/page/route would be accessed via a UI not by something like cURL/POATMAN .
- **When to use:** Portal flows that should **not** be driven by direct API when merchant disabled browser SSP.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$beta("add_stripe_gateway_using_api");
        m.$method(HttpMethod.get).$allowIn(AllowInOpt.live).$allowedOnlyViaUI(true).$roles(CUSTOMER_SUPPORT);
        m.$tab(MainTabs.CONFIGURATIONS, SettingsTabs.SETTINGS, SiteSettingsTabs.GATEWAY);
```
---

## 8. Navigation and layout

### `$tab(Tab<? extends Tab.CoreTabs> main, Tab<? extends Tab.SubTabs> sub)`  
### `$tab(Tab<? extends Tab.CoreTabs> main, Tab<? extends Tab.SubTabs> sub, Tab<? extends Tab.InnerTabs> inner)`

- **What:** As the admin UI contains a side bar on the left side,so this method instructs the ActionModel that when the site loads load the items inside the arguments.Sets **main / sub / inner** tab for **left nav highlight** and section context.

- **When to use:** Full-page admin screens; inner tab when a **third-level** nav exists.
- **Example:**
```java
        m.$tab(Tabs.MainTabs.CONFIGURATIONS, Tabs.SettingsTabs.SETTINGS);

```
---

### `$useBreadcrumb(boolean show)`

- **What:** At the  top the Admin page there are links like the Home-Settings and all,so this function enable the UI to show those links.Basically this function shows or hides the **breadcrumb** bar for this action.

- **When to use:** Minimal dashboards or modals that should not show breadcrumbs.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(FINANCE_EXECUTIVE);
        m.$criticalPath(true);
        m.$bootstrapBased(true);
        m.$allowSlaveDB(true);
        m.$allowDarkBG(true);
        m.$navigationToggle(false);
        m.$useBreadcrumb(false);
        m.$path("/dashboards/chart_data");

```

---

### `$navigationToggle(boolean enable)`

- **What:** This functions helps in eabling disabling the navigation for the UI .Toggles **navigation chrome** behavior (collapsible / variant nav per layout code).

- **When to use:** Pages that need a **simplified** or **non-standard** nav shell.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(FINANCE_EXECUTIVE);
        m.$criticalPath(true);
        m.$bootstrapBased(true);
        m.$allowSlaveDB(true);
        m.$allowDarkBG(true);
        m.$navigationToggle(false);
```


---

### `$bootstrapBased(boolean enable)`

- **What:** Bootstrap is a CSS/UI toolkit many older (and some current) pages were built with. It affects spacing, grids, buttons, modals, etc. Marks layout as **Bootstrap-based** for styling/layout pipeline.$bootstrapBased(true | false) tells the framework: “This action’s page should be treated as a Bootstrap-style layout” (or not). That steers which layout / styling pipeline wraps the response—so the HTML and CSS match what the JSP expects.

- **When to use:** Legacy/bootstrap pages or modals that expect Bootstrap layout.
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(FINANCE_EXECUTIVE);
        m.$criticalPath(true);
        m.$bootstrapBased(true);
        m.$allowSlaveDB(true);
```
---

### `$allowDarkBG(boolean enable)`

- **What:** This function instructs the Meta that the page background with Black.Dark backgrounds will be there. Enables **dark background** shell for dense lists (search, logs).

- **When to use:** Search or index pages with **dark table** chrome.
- **Requirement:** **Optional**.

**Arguments accepted**

- **`boolean enable`**

**Which argument when**

- **Dark list/search UI** → `true`.
- **Standard light page** → `false` or omit.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(CUSTOMER_SUPPORT, FINANCE_EXECUTIVE);
        m.$tab(MainTabs.LOGS, Tabs.LogsTabs.EMAIL_LOGS);

        m.$param(m.$bool(isSub));
        m.$param(m.$bool("isClassicUi"));
        m.$param(m.$long(customerId));
        m.$param(m.$int("limit"));
        m.$param(m.$string("nav_count").$maxChars(200));
        m.$title("Email Logs");
        m.$allowDarkBG(true);
        m.$navigationToggle(false);
        m.$useBreadcrumb(false);
```
- 

---

### `$showSiteSwitch(boolean show)`

- **Description:** Some merchants have more than one Chargebee site (more than one “tenant”). The UI can show a site switcher control (dropdown or similar) so they can jump between sites without logging out.Controls visibility of **site switcher** in chrome.

- **When to use:** Org-level pages where **switching tenant** must be obvious.
-**Example:**
```java
    void _defn(AppActionMeta m) {
        TplThemeActionDefn._base_defn(m);
        /*
         * Settings the tabs to not to show the main & sub tabs.
         */
        m.$tab(null, null, null);
        m.$showSiteSwitch(false);
        m.$param(m.$long(qtpl_themes.id.paramName()));
        m.$param(m.$long(qpresets.id.paramName()));
        m.$layout(Layouts.tpl_gallery_layout);
        m.$title("Theme Gallery");
        m.$schema(Schema.COMMON);
    }
```
- 
---

### `$isSearch(boolean search)`

- **What:** Flags the action as a **search** surface for UI/analytics/routing helpers.
- **Role:** **Classification** (often with **`$allowSlaveDB(true)`**).
- **Requirement:** **Optional**; set when product treats the route as **search**.

**Arguments accepted**

- **`boolean search`**

**Which argument when**

- **Search / heavy list** → `true`.
- **Normal form or detail** → `false` or omit.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$txnOpt(TxnOpt.NOT_REQUIRED).$allowSlaveDB(true);
        m.$path("/search").$col(ActionCols.resource);
        m.$allowJwtAuth(true);
        m.$isSearch(true);
        m.$enableSupportRole(true);
        m.$corsEnabled(true); // enabled to req from storefronts
```

---

## 9. Analytics

### `$recordAnalytics(String eventName)`  
### `$recordAnalytics(String eventName, boolean always)`

- **What:** This function enables the Page to record analytics based on certain events (when events it means button click events and all as specified in the HTML file).Sets **`analyticsEvent`**; second overload sets **`alwaysRecordAnalytics`** when **`always == true`**.

- **When to use:** Use it when there's a need to record such events and track user data for some purpose.
- **Requirement:** **Optional**; add when PM/analytics owns a named event.

**Arguments accepted**

- **`String eventName`** — human-readable event label.
- **`boolean always`** — second overload only: `true` = always record (skip sampling skips); `false` = default recording policy.

**Which argument when**

- **Standard event** → can be dropped occasionally.
- **Critical conversion (must not be dropped)** → two-arg with **`true`**.
- **Example:**
```java
   void _defn(AppActionMeta m) {

        m.$method(HttpMethod.post).$roles(AppRole.ADMIN, AppRole.BUSINESS_ENTITY_ADMIN);
        m.$tab(MainTabs.PRODUCT_CONFIG, ProductConfigTabs.PLANS);
        m.$recordAnalytics("Created Plan");
        m.$create(m.$model(qplans));
```

---

### `$analytics(TrackRoute route)`

- **What:** Attaches a structured **`TrackRoute`** (richer than a string).

- **When to use:** When analytics owns **central route objects** instead of free-form strings.
- **Example:**
```java
import com.chargebee.app.analytics.meta.TrackRoute;
import com.chargebee.app.analytics.types.AnalyticsEntity;
import com.chargebee.app.analytics.types.AnalyticsVendor;

void _defn(AppActionMeta m) {
    m.$method(HttpMethod.get)
            .$roles(AppRole.ADMIN);

    m.$analytics(
            TrackRoute.getBuilder(m)
                    .withEntity(AnalyticsEntity.PEOPLE)
                    .withVendor(AnalyticsVendor.MIXPANEL)
                    .build()
    );
}
```

---

### `$gaGoalPath(String path)`

- **What:** Google Analytics (GA) can track goals (important steps in a funnel), e.g. “user reached checkout,” “user opened agreement PDF,” “user finished signup.”Sets **Google Analytics goal path** string (**`gaGoalPath`**).So when having this feature enabled whenever the user hits the route/action it gets saved into Google Analytics as the path entered in the argument "String path".

- **When to use:** Hosted pages / portal GETs that represent **funnel goals**.
- **Requirement:** **Optional**.

**Arguments accepted**

- **`String path`** — path fragment or full goal path per GA setup.

**Which argument when**

- **Funnel step on known URL** → pass stable path string used in GA config.
- **No GA goal** → omit.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get);
        setCommonConfig(m);
        m.$path("/pages/v2").$col(qhosted_pages.token).$c("/checkout");
        m.$param(m.$long("theme_id")).$req(false);
        m.$param(m.$locale()).$req(false);
        m.$param(m.$string("affiliate_token").$maxChars(250));
        m.$gaGoalPath("/checkout");
        m.currencyOverrideFunc(HostedPage.currencyFunc());
```

---

## 10. Preferences and intents

### `$intent(com.chargebee.app.prefx.configuration.preference.Intent intent)`

- **What:** Changing a subscription (create, update, renew, add a charge, etc.) is not just “update a row.” The product has many site settings and billing rules (preferences).
  Those rules can depend on what kind of change you are doing.$intent(...) tells the framework: “For this action, pretend we are doing this kind of subscription/billing operation.”
Then, when exec() runs, it can load and apply the right preference context (prefx — “preference execution” layer) so behavior stays consistent and correct for that operation.

- **When to use:** Create/update/reactivate subscription, advance invoice, add charge, term-end change.
- **Requirement:** **Required** for actions that **mutate subscriptions** under prefx; omit for unrelated CRUD.

**Arguments accepted**

- **`Intent`** — e.g. `SubIntents.CREATE_SUBSCRIPTION`, `UPDATE_SUBSCRIPTION`, `REACTIVATE_SUBSCRIPTION`, `ADVANCE_CHARGE`, `ADD_CHARGE`, `SUBSCRIPTION_TERM_END_CHANGE`, …

**Which argument when**

- **New subscription** → `CREATE_SUBSCRIPTION`.
- **Amend existing** → `UPDATE_SUBSCRIPTION`.
- **Reactivation flow** → `REACTIVATE_SUBSCRIPTION`.
- **One-time/advance charges** → `ADVANCE_CHARGE` / `ADD_CHARGE` as product defines.
- **Term end changes** → `SUBSCRIPTION_TERM_END_CHANGE`.

- **Example:**
```java
    void _defn(AppActionMeta m) {
  m.$method(HttpMethod.get).$roles(AppRole.CUSTOMER_SUPPORT);
  m.$tab(MainTabs.SUBSCRIPTIONS, SubscriptionTabs.SUBSCRIPTION);
  m.$recordAnalytics("New Subscription");
  m.$model(qaddons);
  m.$model(qaddresses);
  m.$create(m.$model(qcustomers));
  m.$model(qsubscriptions);
  m.$model(qbilling_addresses);
  m.$model(qsite_address_requirements);
  //m.$param(m.$string(CreateSubscriptionAction.AutoCollection.vname).$maxChars(100));
  m.$param(m.$timestamp("start_date"));
  m.$list(m.$model(qsubscriptions_addons));
  m.$intent(SubIntents.CREATE_SUBSCRIPTION);
```
---



## 11. Currency, timezone, database

### `currencyOverrideFunc(com.chargebee.framework.util.ThrowingFunctions.Function<Object, com.chargebee.framework.jooq.JQRecord> fn)`

- **What:** Many money fields need to know which currency (USD, EUR, …). Often the app uses the site’s default currency or the main row you’re editing.This function so Supplies a function that **derives currency** from a **resource key** when default resolution is wrong.

- **When to use:** Currency must follow **non-default** FK/join (advanced).
- **Requirement:** **Rare**; only when default **`Site`/model** currency is incorrect.

**Arguments accepted**

- **`Function<Object, JQRecord>`** — input is resource identifier; output row used for currency.

**Which argument when**

- **Currency lives on related table** → implement lookup returning that **`JQRecord`**.

- **example:** 
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get);
        setCommonConfig(m);
        m.$path("/pages/v2").$col(qhosted_pages.token).$c("/checkout");
        m.$param(m.$long("theme_id")).$req(false);
        m.$param(m.$locale()).$req(false);
        m.$param(m.$string("affiliate_token").$maxChars(250));
        m.$gaGoalPath("/checkout");
        m.currencyOverrideFunc(HostedPage.currencyFunc());
    }
    
    
    
        m.currencyOverrideFunc(val -> {
    String token = (String) val;
    // load some JQRecord that carries the currency you want
        return qsome_table.some_key.dbFetchOne(token);
    });
```

---

### `$useTimezoneFromResource()`

- **What:** This function instructs the ActionMeta to use timestamp from the resource not depend on the merchant's timestamp as the timestamp can be different. Use **timezone from loaded resource** (e.g. customer/subscription context).

- **When to use:** Screens tied to an entity that **defines timezone**.
- **Requirement:** **Optional**; alternative to default timezone.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(get);
        m.$path_fetch(qinvoices);
        m.$param(m.$string("type").$maxChars(4));
        m.$useTimezoneFromResource();
    }

```
---

### `$useDefaultTimezone()`

- **What:** This function instructs the ActionMeta to use the default timestamp i.e. not to use the resource timestamp.This is just opposite to the above discussed.Use **default** timezone policy (e.g. operator or site default without per-resource override).

- **When to use:** Internal tools where **resource TZ** is irrelevant or misleading.
- **Requirement:** **Optional**.


**when to use what**

- **Admin console** → prefer this.
- **Customer-facing entity page** → prefer **`$useTimezoneFromResource()`** when applicable.

**Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get);
        m.$roles(Role.READ_ONLY);
        m.$layout(Layouts.admin_layout).$prop(Layouts.admin_layout_title, "Error Report");
        m.$subDomainOpt(SubDomainOpt.optional);
        m.$useDefaultTimezone();
    }
```



---

### `$allowSlaveDB(boolean allow)`

- **What:** As there is Master-Slave architecture,this function instructgs the ActionMeta to use replica database for READ only operations basically when GET request is there.Permits **read replica** for this action.

- **When to use:** **Read-mostly** GETs where slight replication lag is acceptable.
- **Requirement:** **Optional**; **avoid** on reads that **must** see just-committed writes.

**Arguments accepted**

- **`boolean allow`** — `true` = replica OK, `false` = primary only.

**Which argument when**

- **Search, logs, dashboards** → `true`.
- **Post-redirect-read or money-critical immediate read** → `false` or omit.
**Example:**
```java
        m.$path_fetch(qcustomers);
        m.$model(qcharges);
        m.$model(qaccount_credits);
        m.$model(qtransactions);
        m.$param(m.$text("memo"));
        m.$param(m.$positiveInt("verification_amount1"));
        m.$param(m.$positiveInt("verification_amount2"));
        m.$param(m.$numberMoney("unit_amount"));
        m.$param(m.$string("md_unit_amount").$maxChars(39));
        m.$allowSlaveDB(true);
    }
```


---

## 12. API version, view level, time machine

### `$apiVersionScope(ApiVersion version)`

- **Description:** Sets **internal API version** scope for JS/helpers (**`V1` / `V2`** bitmask semantics).
- **Role:** Set the ApiVersion V! or V2.
- **Example:** `m.$apiVersionScope(ApiVersion.V2);`
- **Requirement:** **Optional**.

**Arguments accepted**

- **`ApiVersion`** — `V1`, `V2` (from **`com.chargebee.framework.api.ApiVersion`**).


---

### `$viewLevelActions(ViewLevelAction... actions)`

-**What:** when viewing the record of a database in the UI ,when viewing each record there is also option of various actions like "download invoice","view invoice" ,etc.
- **When to use:** Per-row **admin** operations from entity detail.
- **Requirement:** **Optional**; .

**Arguments accepted**

- **`ViewLevelAction...`** — built with **`ViewLevelAction.na(JQTable)`** or overloads with **`Predicate<Record>`** and **`ViewLevelAction.Parameter`**.

**Which argument when**

- **Simple row action** → `na(table)`.
- **Conditional visibility** → `na(table, predicate)`.
- **Extra row parameters** → `na(table, param1, param2, …)` or with predicate + params.
**Example:**
```java
    void _defn(AppCommonMeta m) {
        CommonActionDefn.setRole(m, "To mark a successful 'open' payment as closed.", false, Role.SERVICE_DEV_SUPPORT, Role.SUPPORT_INTERMEDIATE);
        m.$param_wm(qsites.domain).$req(true);
        m.$param_wm(qcustomers.handle).$req(true);
        m.$param_wm(qtransactions.external_id).$req(true).fetchCurrFromIp(qtransactions.external_id);
        m.$viewLevelActions(ViewLevelAction.na(qtransactions));
        m.$cbModule(CBModuleConstant.GATEWAY);
    }
```
- 

---

### `$timeMachineOpt(TimeMachineOpt opt)`

- **What:** It is a function which instructs the ActionMeta to either use a simulated Time or the real time for the Action/Route.Controls how **time machine** (as-of / simulated date) interacts with this action.

- **When to use:** Business logic that **must** or **must not** use simulated clock.
- **Requirement:** **Optional**; .

**Arguments accepted**

- **`TimeMachineOpt`** — `execute`, `execute_only_in_qa_mode`, `ignore`, `never_execute`.

**Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(ADMIN, BUSINESS_ENTITY_ADMIN);
        m.$tab(MainTabs.INVOICES, InvoicesTabs.INVOICES);
        m.$path_fetch(qinvoices);
        m.$dbFetchOne(qcustomers_using_qinvoices);
        m.$param(m.$string("comment").$maxChars(300));
        m.$param(m.$bool("claim_credits"));
        m.$timeMachineOpt(TimeMachineOpt.execute);
    }



Example 2:
void _defn(AppActionMeta m) {
  m.$method(HttpMethod.post);
  m.$txnOpt(TxnOpt.NOT_REQUIRED);
  m.$allowSlaveDB(true);
  m.$roles(AppRole.USER);
  m.$corsEnabled(true);
  m.$timeMachineOpt(TimeMachineOpt.ignore);
  m.$enableSupportRole(true);
}
```



---

## 13. Deprecated resources

**How the pieces fit together**

- **`$checkIfDeprecatedResource(true)`** is the **master switch**: the framework only runs deprecation-aware checks for this action when this is enabled. If you omit it or set **`false`**, the other two settings in this section do not apply in a meaningful way.
- **`$deriveDeprecatedResourceUsingJoin(...)`** answers: *“The row this action thinks is primary does not carry the deprecation flag; which **joined** column should we use?”*
- **`$autoDeriveDeprecatedParentFk(true)`** answers: *“Should we treat this row as **deprecated** when its **parent** FK target is deprecated, even if this row has no flag?”*

Use **at most one** of the derivation strategies that fits your model: either deprecation is on the **primary** row (no join helper), on a **specific join** (use **`$deriveDeprecatedResourceUsingJoin`**), or **inherited from parent** (use **`$autoDeriveDeprecatedParentFk`**). Product + schema must agree (same boolean/FK the check reads).

### 13.1 Which function to use — scenario table

| Scenario | What to set | 
|----------|-------------|
| **No deprecation** for this entity or route | Omit **`$checkIfDeprecatedResource`** (or **`false`**) | Avoids extra framework checks and keeps behavior identical to legacy routes. |
| **Deprecation flag on the same table** the action loads/edits (e.g. `qplans.deprecated`) | **`$checkIfDeprecatedResource(true)`** only | The primary **`JQRecord`** already exposes the field the framework should consult; no join or parent walk is required. |
| **Deprecation lives on another table** you always join for this action (e.g. action is on a child row but “deprecated” is on the parent plan) | **`$checkIfDeprecatedResource(true)`** + **`$deriveDeprecatedResourceUsingJoin(qparent.deprecated)`** (or the real column) | The check must follow the **join path** to the column that actually encodes lifecycle state; without this, the framework may look at the wrong table. |
| **Parent deprecated ⇒ all children unusable** (hierarchy / shared FK), and children may not store their own flag | **`$checkIfDeprecatedResource(true)`** + **`$autoDeriveDeprecatedParentFk(true)`** | Centralizes policy on the parent row; child mutations are blocked when the parent is deprecated without duplicating flags on every child. |
| **Child can stay active** even if a related parent is deprecated | **`$autoDeriveDeprecatedParentFk(false)`** or omit; use explicit business rules in **`callLogic()`** if needed | Prevents over-blocking when child lifecycle is **independent** of parent deprecation. |
| **Both** a join-sourced flag **and** parent propagation could apply | Choose **one** canonical rule per action (simplest model wins) | Mixing signals without a clear source of truth produces hard-to-debug **`isAllowed`** / exec behavior; document the single authority (join vs parent) in code review. |


---

### `$checkIfDeprecatedResource(boolean enable)`

- **What:** Turns framework deprecation checks on or off for this action.
- **When to use:** When this entity/route is part of a deprecation / migration story and you want consistent blocking without repeating the same if (deprecated) in every action.
-**Example:**
```java
void _defn(...){
  ....
  ....
  m.$checkIfDeprecatedResource(true);
}
```
---

### `$deriveDeprecatedResourceUsingJoin(JQColumn column)`

- **What:** Tells the framework: “Read deprecation from this column (usually via a join), not from the primary row alone.”
- **When to use:** When the action’s main record doesn’t carry the flag, but a joined row does.
-**Example:**
```java
void _defn(..){
  ...
  ...
  m.$deriveDeprecatedResourceUsingJoin(qparent.deprecated);
}
```
---

### `$autoDeriveDeprecatedParentFk(boolean enable)`

- **What:** Tells the framework: “If the parent row this FK points to is deprecated, treat this row as deprecated for checks.”.

- **When to use:** Parent–child models where one parent flag should turn off child edits, and you don’t duplicate the flag on every child.
-**Example:**
```java
void _defn(..){
  ....
  ...
  m.$autoDeriveDeprecatedParentFk(true);
}
```
---

## 14. Misc

### `$beta(String betaFlagName)`

- **Description:** Registers **beta flag** name; **`isBetaFeatureEnabled()`** reads it.
- **Role:** **Gradual rollout** / internal testing.
- **Example:** `m.$beta("cb_analytics");` — `m.$beta("add_stripe_gateway_using_api");`
- **When to use:** New UI or gateway flows **behind beta**.
- **Requirement:** **Optional**; **required** to hide feature until beta on.

**Arguments accepted**

- **`String betaFlagName`** — stable key matching env / site beta registry.

**Which argument when**

- **Ship behind named beta** → pass exact registered name.
- **GA feature** → omit **`$beta`**.

---

### `$isInvokeAction(boolean invoke)`

- **What:** Labels the action as an internal “invoke” / operator tool (often under admin), not a normal merchant menu item. Routing and symmetry tooling may treat it differently.
- **When to use:** One-off admin forms or internal actions that exist to run an operation (support/engineering style), not everyday merchant CRUD.
- **Example:**
```java
void _defn(AppActionMeta m){
  .....
  ....
  m.$isInvokeAction(true);  
}
```

---

### `$ajaxType(AjaxType type)`

- **What:** Sets an app-level label: “this request is Ajax / full page / unknown.” This is separate from $ajaxPrecheck(true), which is about rejecting non-Ajax calls.
- **When to use:** When later code (layout, client, helpers) reads getAjaxType() and branches.
```java
    Ajax types:
          IS_AJAX — meant to be called via XHR / partial update.
          IS_NOT_AJAX — normal full page navigation.
          NOT_KNOWN or omit — leave default / undecided.
```
- **Example:**
```java
void _defn(AppActionMeta m){
  .....
  .....
  m.$ajaxType(AjaxType.IS_AJAX);
}
```

---

### `$forward_url()` / `$forward_url(String paramName)`

- **What:** Defines a parameter that holds a “where to go after login” URL (or similar return URL), using the framework’s ForwardUrlCol helper so binding stays consistent and safe.
- **When to use:** Login, SSO return, or any flow that accepts a redirect target in the query/body.
- **Example:**
```java
void _defn(AppActionMeta m){
  .....
  ....
  m.$param(m.$forward_url());
  m.$param(m.$forward_url().$maxChars(2000));
}
```


---

### `$tokenBasedLink(boolean tokenBased)`

- **What:** Marks that this action is meant to be opened via a token in the link (e.g. email magic link), not only a normal logged-in session.
- **When to use:** Passwordless, invite, approval, or one-time link flows where the URL carries the proof, not (only) cookies.
- **Example:**
```java
void _defn(AppActionMeta m){
  .....
  .....
  m.$tokenBasedLink(true);
}
```
---

## 15. Important  methods 

### `isAllowed(ActionModel model, Route route)`

- **What:** The main “is this request allowed to run this action?” check on metadata. It rolls together what you declared in _defn: roles, site rules, beta, paths, custom allow-checkers, business-entity rules, and similar gates—for this ActionModel instance and this Route.

- **When to use:** You do not call this from _defn. The framework calls it at runtime while handling a request. You only override the implementation in advanced cases on a subclass of meta if your product has a special global policy (rare).


---

### `isAllowedInSite(Site site)`

- **What:** Asks: “Would this action be allowed for this tenant (Site) if we checked site-level rules?” — without building a full ActionModel for a real HTTP request. Think settings, beta, site type, and other per-site gates.
- **When to use:** Internal tools, listings, or scripts that need to test many sites (“is this action visible/usable here?”) cheaply, not in a normal merchant _defn.
```java
     boolean ok = meta.isAllowedInSite(someSite);
```

---

### `setDefaults()` / `configured()`

- **What:** Lifecycle hooks on meta during registration: 1.setDefaults():apply defaults to meta values  2.configured() — run after _defn finished wiring the route.

- **When to use:** Only if you subclass AppActionMeta and customize how meta is built. Normal actions never call these in _defn or callLogic()—the framework does.


---

### `setBeta(String)` / `setAllowedRoles(Role...)`

- **What:** Imperative versions of $beta("…") and $roles(...)—same meaning, different calling style.
- **when to use:** Generally they are not used inside the _defn(...)
---



## 16. How meta connects to request binding

1. **`_defn`** registers **`$param`**, **`$create`**, **`$path`**, etc. (mostly **`ActionMeta`**).
2. Codegen builds **`ActionCodeHelper.getInitCode()`** for **`ActionInitHelper.init()`**.
3. At runtime, **`AppActionMeta`** gates (**`$roles`**, **`$allowIn`**, …) run via **`isAllowed`** before **`exec()`**.

---




