# `ActionMeta` 
**Role:** `ActionMeta is a shared entity which is shared across multiple ActionModels(requests).Each ActionMeta is identified by a unique RoteImpl which is basically a URL Pattern.ActionMeta is the blueprint for one HTTP action — it describes that action’s URL, HTTP method, who may call it, and what inputs it expects.
It lists every request field as a Param (names, types, required/optional, validation) so the framework can bind and validate the request before your code runs.
It is not the code that runs on each request — the ActionModel instance uses getMeta() to read this blueprint; RequestToPojoUtils / init() use it to fill values.
In Chargebee app code you configure it in _defn(AppActionMeta m) (path, $param, $roles, etc.); changing meta changes routing, security gates, and how parameters are parsed — not just “documentation.”` .

**Example:** `if there are two url url1:"emp/find/id1"    and url2:"emp/find/id2"    both url hits will have different ActionModels but a common ActionMeta with the URL pattern as "emp/find/{id}"`

**Class:** `com.chargebee.framework.web.ActionMeta<U extends ActionMeta<U>>` **extends** `com.chargebee.framework.metamodel.MetaModel<com.chargebee.framework.pojo.PojoHelper, U>` (from **`javap`** on `webapp/WEB-INF/frm_classes/com/chargebee/framework/web/ActionMeta.class`).

**Inherited functions (`$email`, `$string`, `$long`, …)(`these functions are inherited from MetaModel these  function act as a helper functions when using $Param`)

**Take reference from:** [table-defn-starter.md](../table/table-defn-starter.md),[table-defn-complete-guide](../table/table-defn-complete-guide.md).

---

### 4.1 `Param $param(Column column)` (column-backed)

- **What:** Function which fecilitated the input via forms from the UI/Postman/cURL whose **name, type, length, nullability** follow the **metamodel column** ``(e.g. **`qemployees.first_name`).``


- **When to use:** **Create/update** These are used inside the _defn(...) function.
- **In `_defn`:** **Preferred** over parallel **`m.$string("x").$maxChars(n)`** when a column exists.
- - **Example:** `m.$param(qemployees.first_name).$req(true);`

### 4.2 `Param $param(Column)` with **`MetaModel` column fluents — `m.$string` / `m.$long` / `m.$email` / …**

- **When they come into Picture:** `when there is the need for some fields to be entered in right format not just a normal strings.`
- **Where they come in code:** `they come alongside the m.$param(m.$email(...))`
- **What it does** `feds instructions into ActionMeta's map that it has to accept parameter via the UI/form/browser`

### 4.3 `Param getParam(String name)`

- **What:** Looks up the **`Param`** definition by **logical name**; **throws** if missing (framework behavior — confirm in JAR).
- **When:** used to find the Param registered via the argument "name".
- **Example:** `getMeta().getParam("id")`
- **Returns:** **`Param`**.
- **In `_defn`:** Not used in _defn(...).

### 4.4 Indexed lists — `$param_idx` + `$create` + `$list` + `$model`

- **What:** Used to create/accept bulk items/instances at once/in one go.
- **When:**Same as normal $param but instead used for creating/accepting a list of items of an entity/class
- **Example:**

```java
m.$param_idx(m.$create(m.$list(m.$model(qmanagers))));
{
    m.$param(qmanagers.first_name).$req(true).multi(true);
    m.$param(qmanagers.last_name).$req(true).multi(true);
}
```

- **When to use:** Bulk POST bodies with **`entity[1].field`**-style keys (framework naming — confirm with sibling actions).
- **Requirements:** **`.multi(true)`** on each list field; mirror patterns like **`CreateAddonAction`** / **`CreateConsentAction`** in **`cb-app`**.
- **What it does:** Feds instruction into the ActionMeta's map that it has to create/accept list of items.
- **In `_defn`:** Wrap **all** list column params inside the **`$param_idx` / `$create` / `$list` / `$model`** block.
-**HOW TO TAKE INPUT VIA POSTMAN/curl**
- In Postman
## Postman: bulk create students (`POST /students/bulk_create`)

| Field | Value |
|--------|--------|
| **Method** | `POST` |
| **URL** | `{your-app-base}/students/bulk_create` (include the same site/module path prefix your deployment uses for other JSON actions on that site). |
| **Authorization** | Use whatever the app expects for an **ADMIN** session (e.g. session cookie, SSO, or API key—match a working browser request). |

### Body

- **Type:** `x-www-form-urlencoded` (or `form-data`).
- **Content:** indexed list fields (**1-based** index), for example:

| KEY | VALUE |
|-----|--------|
| `students[1].first_name` | `Ada` |
| `students[1].last_name` | `Lovelace` |
| `students[1].email` | `ada@example.com` |
| `students[2].first_name` | `Grace` |
| `students[2].last_name` | `Hopper` |

Optional: `students[n].student_role` (integer), if your action accepts it.

### Notes

- Send parameters in the **POST body**, not only as a GET query string.
- If binding fails, confirm exact key names (table prefix + column API names) against a real browser submit or generated UI for `qstudents`.


### 4.5 Inherited `MetaModel` column DSL — full reference


**How to use (always):** Below given examples:

```java
m.$param(m.$long("id")).$req(true);
m.$param(m.$email("contact_email")).$req(false);
```


---

#### Table for all the helper functions inherited from MetaModel

| Method | Return type (typical) | Use when                                                                                                                                   |
|--------|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **`$int(String name)`** | **`IntegerCol`** | You need a whole number that fits in a normal int (not huge).                                                                              |
| **`$uint(String name)`** | **`IntegerCol`** | You want a number that should not be negative (treated as unsigned-style — check framework rules).                                         |
| **`$positiveInt(String name)`** | **`PositiveIntCol`** | The number must be greater than zero                                                                                                       |
| **`$taxRate(String name)`** | **`TaxRateCol`** | The field is a tax rate (often shown/validated like other tax fields in the app).                                                          |
| **`$timePeriod(String name)`** | **`TimePeriodCol`** | The value is a length of time / billing-style period, not “a clock time.”                                                                  |
| **`$long(String name)`** | **`LongCol`** | You need a big whole number — most often an id or a large counter.                                                                         |
| **`$string(String name)`** | **`StringCol`** | Short text from the user (name, title, code as text). Add .$maxChars if it’s saved to the DB.                                              |
| **`$string(String name, boolean flag)`** | **`StringCol`** | Second-argument overload (framework-specific — e.g. alternate encoding/behavior; check Javadoc in IDE).                                    |
| **`$text(String name)`** | **`TextCol`** | Long text (paragraphs, notes). Prefer this over $string when it can be very long.                                                          |
| **`$locale()`** | **`LocaleCol`** | User picks language/region (e.g. en-US).                                                                                                   |
| **`$file(String name)`** | **`FileCol`** | User uploads a file (image, CSV, etc.). Add allowed extensions and size limits.                                                            |
| **`$fileNameCol(String name)`** | **`FileNameCol`** | You only care about the file’s name string, not uploading the file bytes here.                                                             |
| **`$color(String name)`** | **`StringCol`** | A simple color value (often hex) for UI.                                                                                                   |
| **`$fullColor(String name)`** | **`StringCol`** | Richer color representation (framework distinction — check JAR).                                                                           |
| **`$double(String name)`** | **`DoubleCol`** | Floating-point (non-money) measurements.                                                                                                   |
| **`$decimal(String name)`** | **`DecimalCol`** | High-precision decimals; optional .                                                                                                        |
| **`$money(String name)`** | **`MoneyCol`** | Standard price field helper (default naming).                                                                                              |
| **`$longMoney(String name)`** | **`LongMoneyCol`** | Money stored / represented as **long** .                                                                                                   |
| **`$numberMoney(String name)`** | **`NumberMoneyCol`** | Numeric money variant.                                                                                                                     |
| **`$bool(String name)`** | **`BooleanCol`** | Checkboxes / true–false flags.                                                                                                             |
| **`$date(String name)`** | **`DateCol`** | Calendar **date** (no time-of-day).                                                                                                        |
| **`$time(String name)`** | **`TimeCol`** | Time-of-day.                                                                                                                               |
| **`$timestamp(String name)`** | **`TimestampCol`** | **Instant** / date-time (seconds precision typical).                                                                                       |
| **`$timestamp_millis(String name)`** | **`TimestampCol`** | Millisecond-resolution timestamps.                                                                                                         |
| **`$http_url(String name)`** | **`StringCol`** | Value must look like a http(s) URL (redirect URLs, webhooks).                                                                              |
| **`$name()`** | **`StringCol`** | Standard “name” field with the framework’s default param naming.                                                                           |
| **`$code()`** | **`StringCol`** | Standard short code /code snippets/code example.                                                                                           |
| **`$invoiceName()`** | **`StringCol`** | Text that follows the app’s invoice naming convention.                                                                                     |
| **`$price()`** | **`MoneyCol`** | Standard price field helper (default naming).                                                                                              |
| **`$numberPrice()`** | **`NumberMoneyCol`** | Price as the numeric-money variant.                                                                                                        |
| **`$email()`** | **`EmailColumn`** | One email param using the default name the framework picks.                                                                                |
| **`$email(String name)`** | **`EmailColumn`** | One email param with your chosen name (usual for “email” fields).                                                                          |
| **`$namedEmail(String name)`** | **`EmailColumn`** | Email with extra “named email” semantics (see Javadoc vs plain $email).                                                                    |
| **`$emailList(String name)`** | **`EmailListColumn`** | **Multiple** emails in one param (lists / CC lists).                                                                                       |
| **`$token()`** / **`$token(String name)`** | **`StringCol`** | Secret or opaque string (API key–style, session token — handle securely).                                                                  |
| **`$created_at()`** / **`$created_at(String name)`** | **`TimestampCol`** | When a row was created (audit / system field).                                                                                             |
| **`$modified_at()`** | **`TimestampCol`** | Framework’s “resource modified at” timestamp pattern.                                                                                      |
| **`$resUpdatedAt()`** | **`TimestampCol`** | Framework’s “resource updated at” timestamp pattern.                                                                                       |
| **`$touch_id()`** | **`StringCol`** | Version / etag–style token so two edits don’t overwrite each other blindly.                                                                                        |
| **`$exchange_rate()`** | **`DecimalCol`** | Currency conversion rate (FX).                                                                                                              |
| **`$timezone()`** / **`$timezone(String name)`** | **`TimezoneCol`** | User picks a timezone (e.g. America/New_York).                                                                                                        |
| **`$col(T extends Column column)`** | **`T`** | You already have a Column object from a helper; reuse it instead of building a new one.|
| **`deprecatedParentFk()`** / **`deprecatedParentFk(Column)`** | accessor / mutator |                               |


---

## 5. Path and routing

### 5.1 URL pattern and `RouteImpl`

- **What:** Meta holds a **`Pattern urlPattern`** (or equivalent) and links to **`RouteImpl`** after **`configured()`**.
- **Example:**  **`$path("/segment")`** in app code; regex patterns in older style.
- **When to use:** For specifying the path
- **Example:**
```java
void _defn(AppActionMeta m) {
     m.$path("/students/create");
}
```

### 5.2 Path helpers — `$path()`, `$path_id`, `$path_fetch`, …

- **What:** These are helper functions that help in creating various components of a url like the "id" and all.URLs with less boilerplate.
- **When to use:** Standard CRUD routes that load an entity from the path.
- **Example (conceptual):** `$path().$c("/customers/").$id(Customer.ID);`(Consider this as springboot "customers/{id}").`.
```java
void _defn(AppActionMeta m) {
  m.$method(HttpMethod.get);
  m.$path().$c("/customers/").$id(qcustomers.id);  // same idea as doc: /customers/{id}
  m.$param(m.$string("reason")).$req(false);       // example extra query param
  // … $roles, $moduleDefn, etc.
}
```
---

## 6. HTTP method and transactions

### 6.1 `$method(HttpMethod method)`

- **What:** Declares **GET**, **POST**, **PUT**, etc.
  - **Role:** Invokes different ways of sending information from user end to the server i.e. When POST information will be sent in body(JSON),BUT when GET the same imfo will be send in url.**Idempotency** and **caching** expectations; pairs with **CSRF** / **ajax** rules on **`AppActionMeta`**.
- **When to use:** **Always** — never rely on “any method” for authenticated mutations.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$path("/employees/update");
        m.$moduleDefn(Defns.class);
        m.$method(post).$roles(CUSTOMER_SUPPORT, SALES_AGENT_CPQ);
```

### 6.2 Transaction options — `TxnOpt`

- **What:** **`txnOpt`** (e.g. **`REQUIRED`**, **`NOT_REQUIRED`**, **`REQUIRES_NEW`**) helps in controlling ORM / DB transaction .Follows ACID properties does atomic processes.Does roolback the changes when transaction fails .**POST** often defaults to **required** txn; **GET** often **read-only** — verify for your framework version.
- **When to use:** When defaults are wrong for long reads, nested transactions, or reporting endpoints.
- **In `_defn`:** Only when you **intentionally** override defaults.
```java
    void _defn(AppActionMeta m) {
        m.$method(post).$auth(AuthType.Unauthenticated);
        m.$subDomainOpt(SubDomainOpt.strictly_no);
        m.$param(m.$string("domain").$maxChars(50)).$req(true);
        m.$param(m.$long("session_id")).$req(true);
        m.$param(m.$string("csrf_token").$maxChars(100)).$req(true);
        m.$txnOpt(TxnOpt.NOT_REQUIRED);
        m.$schema(Schema.COMMON);
```

---

## 7. Authentication and authorization

### 7.1 `AuthType` and role masks

- **What:** This function is used to store instructions in Meta how the user/visitor of the page will be authenticated,what are the authorizations of the users, stores **how** the user is authenticated (**session**, **unauthenticated**, JWT, …) .
-    **Role:** **`AppActionModel.exec()`** / **`isAllowed`** consults meta **before** **`callLogic()`**.Basically all this information of how the user should be authenticated is stored as instructions in map type datastructure.So when init() is called before callLogic() all authentications are done.
- **When to use:** **Every** authenticated or intentionally public action.
- **Requirement:** **Do not** paste demo **`$roles`** literals — derive from the tabe provided in the — **[AppActionMeta-LLM.md §0](./AppActionMeta-LLM.md)**.
- **Returns:** Returns nothing but fills the ActionMeta's map with instructions how the the user would be authenticated .
- **In `_defn`:** Set **`$roles`** / **`$auth`** explicitly.
```java
import com.chargebee.app.config.AppRole;
import static com.chargebee.framework.web.HttpMethod.post;

void _defn(AppActionMeta m) {
  m.$path("/courses/delete");
  m.$moduleDefn(Defns.class);
  m.$method(post).$roles(AppRole.ADMIN);
}
```

### 7.2 `isAllowed(ActionModel, Route)` 

- **What:** this function is used to know whether the current visitor/user visiting the page/route is allowed or not.
- **Role:** **Central gate** so unauthorized users never reach **`callLogic()`**.

- **When to use:** Implemented by platform; **read** behavior when debugging **403**-style failures.
- **Requirement:** Fine-grained checks in **`callLogic()`** **add to** meta.
- **Returns:** **`boolean`**.
- **NOTE** :Not to be implemeted by the end user


---

## 8. Validation

### 8.1 `ValidationStrategy` 

- **What:** There are two options for the frontend to notify end user that the input via form is in wrong format/wrong input,first option is when the end user fills a field of the form and when moves to next field is immediately notified that there is problem in the input and the second option is when all the fields are filled and then when submitting the user gets notified.These two options when needed to be toggled are done with this function.
- **Role:** basically to decide the timing of when to notify the error in taking input to the form.
- **When to use:** Forms where required-ness **depends** on mode.
- **Requirement:** Pair with **`ActionModel.isRequired(Param)`** overrides when product uses **field settings** — **[AppActionModel-LLM.md §4.1](./AppActionModel-LLM.md)**.
- **In `_defn`:** Set when sibling actions in the same feature use it.
- **Example**:
```java
        void _defn(AppActionMeta m) {
              m.$method(HttpMethod.post).$roles(Role.UNAUTH_USER).$criticalPath(true);
              m.$auth(AuthType.StrictlyUnauthenticated);
              m.$subDomainOpt(SubDomainOpt.strictly_no);
              m.$validationStrategy(ValidationStrategy.onfocusout);
              m.$create(m.$model(qmerchants));
            
              m.$create(m.$model(qsites));
              m.$param(qsites.domain).$req(true);
            
              m.$create(m.$model(qusers));
              m.$param(qusers.email).$req(true);
        }
```

### 8.2 `getJSValidation(ActionModel model)` 

- **What:** Generates **JavaScript** validation from the same **`Param`** list as the server.
- **Role:** Reduces **UI vs server** drift for classic JSP forms.
- **Example:** Consumed by **MetaBasedParamProvider** / **JSValidatorBuilder** (framework internals).
- **When to use:** Server-rendered forms; less relevant for **pure JSON** APIs.
- **Requirement:** If **JSON-only**, **`$ajaxPrecheck`** and server validation still matter — **[AppActionMeta-LLM.md](./AppActionMeta-LLM.md)**.
- **Returns:** JS snippet / descriptor (type varies).
- **In `_defn`:** Indirect — driven by **`Param`** fluents (**`$maxChars`**, **`$req`**, …).

---

## 9. Param behavior control

### 9.1 Skip auto-fill

- **What:** Generally what happens is when Param field are accepted using forms ,the framework  automatically fills the enitity fields  related to the fields,along with it all validations are also done automatically these are done using RequestToPojoUtils.set(..) function,But when this feature enabled restricts doing the framework doing so.
- **Role:** **Derived** fields, **manual** parsing, **security** (ignore client-supplied id).
- **When to use:** When you need to just take input bypassing the framework's protocol.
- **Requirement:** **`callLogic()`** must still validate/sanitize if the client can send the field.
- **In `_defn`:** Set on specific **`$param`** via fluent function (confirm name in JAR).
- **Example**:
```java
    void _defn(AppActionMeta m){
        m.$model(qbank_accounts);
        m.$param(m.$string("account_number").$minChars(5).$maxChars(17));
        m.$param(m.$string("routing_number").$fixedLength(9));
        m.$param(m.$string("phone").$maxChars(50)).$req(false).$skipAutoFill(true);
}
```

### 9.2 Strip empty params

- **What:** Normalizes **empty strings** / missing optional fields before binding.
- **Role:** Cleaner **`null`** vs **`""`** semantics.
- **When to use:** Forms with many optional text fields.
- **Requirement:** Align with **DB** nullability.
- **Returns:** N/A (meta / param flag).
- **In `_defn`:** Usually global or per-module convention.
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get);
        m.$tab(MainTabs.SUBSCRIPTIONS, SubscriptionTabs.SUBSCRIPTION);
        m.$stripEmptyParams(true);
        m.$param(m.$string("export_type").$maxChars(20));
        m.$allowSlaveDB(true);
        m.$allowDarkBG(true);
        m.$isSearch(true);
        super.defn(m);
```

### 9.3 `.$req(true|false)` on `Param`

- **What:** Marks whether the parameter is **required** for validation.
- **Role:** **Fail fast** in **`exec()`** before **`callLogic()`** when possible.
- **When to use:** **Every** API-facing input — explicit is better than default guessing.
-**Example**
```java
 void _defn(AppActionMeta m){
        m.$model(qbank_accounts);
        m.$param(m.$string("account_number").$minChars(5).$maxChars(17));
        m.$param(m.$string("routing_number").$fixedLength(9));
        m.$param(m.$string("phone").$maxChars(50)).$req(false).$skipAutoFill(true);
}
```

---

## 10. Model graph (`$model`, `$list`, `$create`, DB prefetch)

### 10.1 `$model(JQTable)` / `$list(...)` / `$create(...)`

- **What:**These function help in creating models,list of a class using the Param,they use RequestToPojoUtils for achieving this.
- **Role:** Maps hierarchical request keys to **nested POJOs** / **`JQRecord`** graphs.
- **When to use:**used to model according to the tables.
- **Example:**

```java
m.$create(m.$model(qemployees));
{
    m.$param(qemployees.first_name);
    m.$param(qemployees.last_name);
}
```



### 10.2 `$dbFetchOne` / `$dbFetchList` / `$dbFetchFirst`

- **What:** This functions feds instruction into the ActionMeta's map datastructure to fetch the tables/db using foreign key ,which is implemented using init() and used in the callLogic() .
- **When to Use:** Reduces **hand-rolled** fetch duplication for standard patterns.
- **Requirement:** Wrong **join** metadata causes **N+1** or **missing data** — verify against **`Tables`** join helpers.

-**Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(HttpMethod.get).$roles(AppRole.CUSTOMER_SUPPORT, AppRole.SALES_AGENT_CPQ);
        m.$path_fetch(qsubscriptions);
        m.$tab(MainTabs.SUBSCRIPTIONS, SubscriptionTabs.SUBSCRIPTION);
        m.$param(m.$bool(isCust));
        m.$dbFetchOne(qcustomers_using_qsubscriptions);
        m.$dbFetchList(qsubscriptions_addons_using_qsubscriptions);
        m.$pathMap(qcustomers.id);
```

---

## 11. Views, locking, schema, security, features

### 11.1 `$view(String path)`

- **What:** Used for viewing web pages generally static web pages/jsp pages pre saved web pages.
- **Role:** Server-rendered **merchant admin** flows.
- **When to use:** **Use when you want the user to show a webPage after an action is performed by the user.
- **Example:**
```java
void _defn(AppActionMeta m) {
    m.$method(HttpMethod.get).$roles(AppRole.USER);
    m.$path("/customers").$c("/([^/]+)");
    m.$view("/views/customer.jsp");
}
```

### 11.2 `$lock` / `$paramLock`

- **What:** Sometimes two users (or two requests) try to change the same row at the same time. Without care, you can get lost updates (last save wins and overwrites the other) or confusing errors.These functions tells/instructs the framework to lock certain columns/fields so that to avoid claSH.
- **When:** **Concurrent edit** protection for high-contention entities.$paramLock — can tie locking to one or more params/columns the framework uses to know which rows to lock.
  Exact behavior is in the framework; in app code you mostly copy patterns from similar actions.
- **Returns:** NA
- **In `_defn`:** It's used inside _defn(...)
- **Example($param(...)):**
```java
    void _defn(AppActionMeta m) {
        m.$beta("add_stripe_gateway_using_api");
        m.$method(post).$allowIn(AllowInOpt.live).$roles(CUSTOMER_SUPPORT).$lock(qsp_gw_objects.site_id);
        m.$tab(Tabs.MainTabs.CONFIGURATIONS, null);
        m.$param(m.$string("stripe_api_key").$maxChars(250)).$req(true);
        GatewayAccount.setParam(m, true);
```
-**Example($paramLock(..)):**
```java
void _defn(AppActionMeta m) {
    m.$method(HttpMethod.post).$roles(AppRole.CUSTOMER_SUPPORT);
    // Declare which input columns participate in param-based locking (exact rules live in the framework).
    m.$paramLock(qinvoices.customer_id, qinvoices.subscription_id);
}
```


### 11.4 CSP / CORS flags

- **What:** **`cspExempt`**, **`corsEnabled`**, These functions help in changing the the browser's COR's policy,CSP policy
- **Role:** Allow **specific** endpoints to relax CSP or enable CORS **deliberately**.
- **When to use:** Whenver there is need for changing the policy,when the current browser policy restricts doing certain task which is a business requirement.
- **Example(CORS):**
```java
    void _defn(AppActionMeta m) {
        m.$method(get).$roles(USER);
        m.$path("/search").$col(ActionCols.resource).$c("/saved_meta");
        m.$corsEnabled(true);// enabled to make ui req from storefronts to cb-app
    }
```
-**Example(CSP):**
```java
    void _defn(AppActionMeta m) {
        m.$method(post);
        m.$cspExempt(true);
        m.$txnOpt(TxnOpt.NOT_REQUIRED).$schema(Schema.COMMON);
        m.$auth(AuthType.Unauthenticated).$subDomainOpt(SubDomainOpt.strictly_no);
        m.$allowChecker((ActionModel model) -> Env.isDev());
    }
```

### 11.5 Features, SLA, criticality, `props` map

- **Description:** **`Feature`**:Used for enabling/disabling a product feature, **`SLA`:Used for monitoring**, **`Criticality`:Used to know how important this action/route  is**, **`Map<DefinedProp, Object> props`** it is like a sticky notes(not that important for the action).
- **Role:** **Feature gating**, **SLO** tracking, **alert** routing.
- **When to use:** When **`cb-app`** siblings on the same surface call **`$feature(...)`** / **`$slaForResponseTime(...)`**.
- **Returns:** NA
- **In `_defn`:** Used in _defn(..),it is for that route/action.
- **Example**
```java
    protected void fillCommonDefn(AppModalMeta m) {
        super.fillCommonDefn(m);
        m.$roles(CREDIT_AID_ADMIN);
        m.$businessEntityProfileType(BusinessEntityProfileType.SITE);
//        m.$param(m.$string("extID").$maxChars(50)).$req(false).$actCol(ActionColumn.Hidden);
        m.$feature(AppFeatures.MULTIPLE_TAX_PROFILE);
        m.$cbModule(CBModuleConstant.TAXES);
        m.$criticality(Criticality.HIGH);
        m.$slaForResponseTime(SLA.M1);
    }
```
-**Example**
```java
    void _defn(AppActionMeta m) {
        m.$method(post).$roles(TECH_SUPPORT, FINANCE_EXECUTIVE);
        m.$create(m.$model(qad_hoc_notification_requests));
        m.$param(qad_hoc_notification_requests.mail_type).$req(true);
        m.$param(qad_hoc_notification_requests.from_profile_id).$req(true);
        m.$param(qad_hoc_notification_requests.customer_id).$dependsOnEnum(qad_hoc_notification_requests.mail_type.paramName(), 10)
                .$prop(DERIVE_DEPRECATION_COL_FROM, qcustomers.id);
```

---

## 12. Runtime introspection on meta

### 12.1 `getParamsList()` / iteration

- **What:** A method on the action’s metadata (e.g. getMeta().getParamsList()) that returns a list of every Param this action declared in _defn — in the order they were registered.
- **Role:** Used for tesing purpose,whether this param is present or not in the form/UI
- **When to use:** **Generally used for checking and testing.
- **In `_defn`:** N/A.
- **Example**
```java
        List<Param> actionParams = actionMeta.getParamsList();
        extractedMetaInfo.paramList = paramsListToPojo(actionParams);
```


### 12.2 `getMethod()` / route / pattern accessors

- **What**It just returns the Http request.
- **Role:** Conditional logic based on **registration** (rare).

- **When to use:** **Multi-action** models, **shared** classes.
- **Returns:** **`HttpMethod`**, **`Pattern`**, …
- **In `_defn`:** N/A.
- - **Example:** `if (getMeta().getMethod() == HttpMethod.post) { ... }`

---






---


### 16.1 Patterns (some example from the repository)

**Param-only JSON action** — use **`$moduleDefn(Defns.class)`** when there is **no** primary **`$create`/`$model`**:

```java
void _defn(AppActionMeta m) {
    m.$path("/employees/update");
    m.$moduleDefn(Defns.class);
    m.$method(post).$roles(AppRole.ADMIN); // RBAC — AppActionMeta-LLM §0/§5
    m.$ajaxPrecheck(false);
    m.$param(m.$long("id"));
    m.$param(m.$string("first_name").$maxChars(150));
    m.$param(m.$string("last_name").$maxChars(150));
}
```

**Create flow** — **`$create(m.$model(qtable)) { … }`**:

```java
void _defn(AppActionMeta m) {
    m.$path("/employees/create");
    m.$moduleDefn(Defns.class);
    m.$method(post).$roles(AppRole.ADMIN).$condValidation(true);
    m.$ajaxPrecheck(false);
    m.$create(m.$model(qemployees));
    {
        m.$param(qemployees.first_name);
        m.$param(qemployees.last_name);
    }
}
```

---

