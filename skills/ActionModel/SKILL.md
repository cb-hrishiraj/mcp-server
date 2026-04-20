# `ActionModel` — LLM reference (Chargebee web framework)


**Description:** 
**This is a class whose instance is created every time when a url is hit .It holds the HTTP request and response (req, resp) and the action metadata (getMeta() / _defn): path, method, roles, layout, params, etc.It is the class which implements the callLogic().It contains a map like datastrucuture called values which stores every pre-prepared object ,this map is filled by the init() function when instructed by the ActionMeta.**
---

## 1. Role:

**`ActionMeta`** (from **`_defn`**) is the **blueprint**; **`ActionModel`** is the **per-request instance**: it holds **`HttpServletRequest` / `HttpServletResponse`**, the **`values`** map (bound params, path pieces, **`JQRecord`** rows), **`ActionError`**, and orchestrates **`exec()`** → **`init()`** → **`callLogic()`**. In **`callLogic()`** you read inputs via **`getString` / `getLong` / `get(qtable)`**, call services/DB, set **`Forward`** or JSON/ajax responses, and attach errors via **`getErr()`**.

---

## 2. How it's created on every url hit

**Action Store**
**What happens is that every url is registered on the Routes.java.So when a url is hit while on a server is running the framework tries to match the url with the preSaved pattern of urls in the orderedRoutes which is a collection of Routes in the ActionStore.So when at first a urlPattern is matched ,ActionStore creates a new Instance of ActionModel with pre saved ActionMeta registered to the urlPattern and that's how a new ActionModel on  every request is created.

---


---

## 4. Public fields

### `HttpServletRequest req`

- **What:** HttpServletRequest is the Java servlet API’s object that represents one incoming HTTP request from the browser (or Postman, mobile app, etc.) to your server.
- **Role:** Low-level access to parameters, headers, session, multipart.

- **When to use:** Only when no **`Param`** / **`getString`** path exists (legacy, custom headers).
- **Requirement:** Prefer **`getString` / `getParamVal` / `get(qtable)`** per [chargebee-framework-practices-LLM.md](./chargebee-framework-practices-LLM.md).
- **Returns:** N/A (field).
- **In `callLogic()`:** Avoid for normal form fields; use typed getters. Use for **`FileItem`** streams, special headers, or debugging.
- **Example:**
```java
   String raw = req.getParameter("legacy");
- `````


---

### `HttpServletResponse resp`

- **What:** The servlet response (status, headers, writer).
- **Role:** Direct response control when not using **`Forward`** helpers.

- **When to use:** Streaming, custom status, attachments — prefer framework **`sendOk` / `sendError`** when possible.
- **Requirement:** Optional; most actions return **`Forward`**.



---

### `Map<String, Object> values`

- **What:** It is a map type datastructure which is filled by the init() function which is called before the callLogic() function executes.
- **Role:** Central request-scoped state store populated mainly during **`init()`**.

- **When to use:** Inside the callLogic() it is primarily used to fetch values from the values which are generally prefilled by the init() function.

- **In `callLogic()`:** Read **`get(qtable)`** for **`$create`/`$model`** rows; use **`set`** to pass objects to JSP/JSON serializers if your pattern requires it.
- **Example:** After **`set("preview", dto)` → `get("preview")`**.


---

## 5. Lifecycle and orchestration

### `Forward exec() throws Exception`

- **What:** Top-level entry the servlet invokes; runs locking, **`init()`**, validation, then **`callLogic()`** inside a **`Callable`** (with optional wrapping).


- **When to use:** Subclass only if building a new framework integration.
- **Requirement:** App developers implement **`callLogic()`**, not **`exec()`**, for business logic.
- **Returns:** **`Forward`** — next view, redirect, or ajax envelope.
- **In `callLogic()`:** Do not call **`exec()`** recursively.



---

### `Forward callLogic() throws Exception`

- **What:**This is where the main business logic of the code persists **Your** business method: read bound state, validate, persist, return navigation or JSON.
- **Role:** Primary extension point for feature actions.
- **When to use:** Whenever to implement the business logic is implemented in this function.
- **Example:**

```java
@Override
public Forward callLogic() throws Exception {
    Long id = getLong("id");
    Employee e = qemployees.dbFetchOne(id);
    e.firstName(getString("first_name"));
    e.dbUpdate();
    return getViewForward();
}
```



---

### `void init() throws Exception`

- **What :** Runs **`ActionInitHelper.init()`** using metadata from **`getMeta()`** — binds request parameters, creates rows for **`$create`**, parses path segments per codegen.
- **Role:** Fills **`values`** before **`callLogic()`**.
- **Example:** Normally **do not override**; framework calls it.
- **When to use:** Override only for advanced custom binding .
- **Requirement:** **`super.init()`** must run if you override.
- **Returns:** **`void`**.
- **In `callLogic()`:** **`init()`** has **already completed**; do not call **`init()`** again unless a documented sub-flow requires it (unusual).



---



---






---

### `abstract ResponseStateListener responseListenerImpl()`

- **What:** This function cares about the response generated in the callLogic().

- **When to use:** Only if you’re working on a framework-level base class (extending how all or many actions behave): then this method is part of that story — still rarely something a “leaf” action author touches.
- **Requirement:** Not implemented in leaf CRUD actions.
- **Returns:** **`ResponseStateListener`**.



---

## 6. Servlet wiring

### `void setDetails(HttpServletRequest request, HttpServletResponse response)`

- **what:** this function connects the current ActionModel to the request and response.

- **When to use:** The framework (router / dispatcher), before it runs exec() → callLogic().
  You don’t call setDetails from normal business code inside a typical CRUD action.
- **Requirement:** Must run before **`exec()`** for a real HTTP hit.
- **Example**
```java
            ActionModel.setModel(req, actModel);
            req = MultipartRequest.parseRequest(req, actModel.getMeta().size);
            AdminBrowserInvokeActionRequestWrapper wrappedReq = new AdminBrowserInvokeActionRequestWrapper(req, admin_action_uri);
            KVL.put(LogProp.action_type, admin_action_uri);
            AccessBlockApi.checkIfActionBlocked(wrappedReq);
            actModel.setDetails(wrappedReq, resp);
            Forward f = actModel.exec();
```






### `HttpServletRequest getReq()` / `HttpServletResponse getResp()`

- **What:** This function helps in getting Response and Request from the HTTP method.

- **When it is used:** It is used when there is a requirement to return/get current http request/response.
-**Example**
```java
    public boolean isRequestFromInternalAuth() {
        return LoginUserHelper.isRequestFromInternalAuth(getReq());
        
    }

    public String clientId() {
        return getReq().getParameter(InternalAuthConstants.INTERNAL_AUTH_REQ_PARAM);
    }

    public String forwardUrl() {
        return getReq().getParameter("forward");
    }
```




---

## 7. Metadata

### `M getMeta()` / `void setMeta(M meta)`

- **What:** Every action is associated to an ActionMeta so this function is as a getter and setter for the ActionModel's ActionMeta the meta data . describes how that URL behaves: HTTP method, path, roles, params, tabs, etc. **`getMeta`** returns this action’s **`ActionMeta`** (in app, **`AppActionMeta`**). **`setMeta`** is called by **`RouteImpl`** after construction.


- **When to use:** When there is a requirement to get what is there's in the current ActionMeta's instruction for the current action. Dynamic behavior based on meta; advanced validation; introspection.

-**Example1:**
```java
    private static ActionModel findMatchedModelForRoute(String routeName) {
        Route route = ActionStore._inst.getRoute(routeName);
        if(route == null){
            return null;
        }
        ActionModel actModel = (ActionModel) route.getActionMeta().getHelper().createNewInstance();
        actModel.setMeta(route.getActionMeta());
        return actModel;
    }
```
-**Example2:**
```java
    protected void validateCSRF() {
        if (this.getMeta().getAuth().equals(AuthType.Unauthenticated) || req.getMethod().toLowerCase().equals(HttpMethod.get.name())) {//CSRF not needed for get in our model as get ops don't modify
            return;
        }
```



---

### `ActionMeta createMeta(String, String, boolean)` / `Class getActionMetaClass()` / `boolean useInheritedDefnMethods()` / `ActionName getActionName(Method)` / `String getDefnMethodName(String)` / `String getLogicMethodName(ActionMeta)`

- **What:** **These methods are not every day used functions for a developer,these functions are used for fetching the ActionMeta's related informaton
- **When to use:** Generally these functions are called up by the framework itself.But could be used when required.
- **Returns:** Varies (**`ActionMeta`**, **`Class`**, **`boolean`**, **`ActionName`**, **`String`**).
-**Example:**
```java
    @Override
    public final boolean useInheritedDefnMethods() {
        return true;
    }

    @Override
    public final String getLogicMethodName(ActionMeta m) {
        if("account_updater_file_upload".equals(m.getName())) {
            return "accountUpdaterFileUploadLogic";
        } else if ("init_account_updater".equals(m.getName())){
            return "initAccountUpdaterLogic";
        }
        throw ApiErrorCodes.API_RESOURCE_NOT_FOUND.err("Invalid Action").asJsonResponse(true);
    }
```

---

## 8. Reading and writing request state (`values`, typed fields, param- and path-aware reads)


### 8.1 What actually happens on the server

1. **`init()`** runs **`ActionInitHelper`**, which walks **`getMeta()`** (from **`_defn`**) and **writes** into the **`values`** map: scalars by **name**, **`JQRecord`** / **`PojoList`** under **table-derived keys** for **`$create` / `$model` / `$list`**, and related structures.
2. **`callLogic()`** runs **after** **`init()`**, so you normally **read** what binding already produced, or **overwrite** slots with **`set`** when you rebuild state for the next view.


**Rendering note:** **`getVal(String)`** is oriented toward the **table/renderer** pipeline; it is listed under family A for “display resolution” but is **not** the default choice for ordinary **`callLogic()`** business reads.

---

### 8.2 `Object get(String name)`

**When:** gives answer to-Give me whatever is stored under this exact text key in the action’s internal map..

**What it does(Returns):** **`Object`** or **`null`**.

**Example:**
```java
Object raw = get("my_custom_key");
String s = raw != null ? raw.toString() : null;
```
---

### 8.3 `<E extends Enum<E>> E get(String name, E... allowed)`

**When:** Reads the string for **`name`**, parses it into one of the **enumerated constants** you pass in **`allowed`**. That varargs list is both the parse target and the **validation boundary** for legal values.

**What it Returns:** An **`E`** instance (framework may throw or return null on illegal input—verify in tests).

**Example:**
```java
EntityType type = get("entity_type", EntityType.quote, EntityType.subscription);
```

---

### 8.4 `boolean is(String name)`

**When :** Interprets the named input in a **boolean / presence-oriented** way (framework-specific rules for “present”, non-empty, or truthy string). Lighter than full **`getBool`** when you only need “did they tick / send this?”.

**What it returns:** **`boolean`**.

**Example:**
```java
if (is("accept_terms")){
        .......
        }
```

---

### 8.5 `Object getVal(String name)`

**When it is used:** Usually used to get speciic fields of an entity/class/table.

**What it Returns:** **`Object`**.

**Example:**
```java
Money amount = (Money) getVal("subscription.setup_cost");
```
---

### 8.6 `String getString(String name)` / `String getString(Column col)`

**When it is used:** It used when the input form data is in form of string and is saved in the map with key as as the "name".
**Returns:** **`String`**.

**Example**
```java
String title = getString("title");
String code  = getString(qproducts.code);
```
---

### 8.7 `Long getLong(String name)` / `Integer getInt(String name)`

**When it is used:** It is used when one has to get a number/numerical value which is fed inside the map with key as "name".
**What it Returns:** Boxed number or **`null`** (or error on bad format—confirm for your framework version).

**Example:**
```java
Long qty = getLong("quantity");
Integer n = getInt("retry_count");
```
---

### 8.8 `Boolean getBool(String name)` / `Boolean getBool(String name, boolean defaultVal)`

**When it is used:** when the map(values) contains a boolean as an object under the key as "name".
**What itReturns:** **`Boolean`** or the supplied default.

**Example:**
```java
Boolean strict = getBool("strict_mode");           // may be null if omitted
boolean notify   = getBool("notify_me", false);    // omitted → false
```
---

### 8.9 `List getList(String name)`

**When it is used:** It is used when there is need for obtaining a list of vlaues keyed under a "name";
**What it Returns:** **`List`**.

**Example:**
```java
List<String> ids = getList("selected_ids");
```
---

### 8.10 `FileItem getFile(String name)`

**When it is used:** It is used when there is need to Return the **`multipart/form-data`** part for **`name`** as a **`FileItem`** (stream/temp file). This is **not** representable as a normal string param.

**What it returns:** **`FileItem`**.

**Example:**
```java
FileItem upload = getFile("spreadsheet");
```
---

### 8.11 `<R extends JQRecord> R get(JQTable<R> table)` / `PojoList<R> getList(JQTable<R> table)`

**When it is used:** It is used to fetch an Object/List<Object> which is keyed with the table name.
**Waht it Returns:** **`R`** / **`PojoList<R>`** or **`null`**.

**Example:**
```java
Employee e = get(qemployees);
List<Student> students = getList(qstudents);
```
---

### 8.12 `void set(String name, Object value)`

**When it is used:** it used by the init() function to set the key value pair inside the map structure.
**What it Returns:** **`void`**.

**Example:**
```java
set("status_message", "Saved successfully.");
set("sensitive_field", null);
```
---

### 8.13 `<R extends JQRecord> void set(JQTable<R> table, R row)` / `void set(JQTable<R> table, PojoList<R> list)`

**When it is used:** It is used when there is a need to Write the row or list under the **same table-derived key** **`get(JQTable)`** uses, **replacing** any previous value.Replace the table’s row or list in values (same key get(qtable) uses).

**Returns:** **`void`**.

**Example:**
```java
e.firstName("Ada");
set(qemployees, e);

set(qstudents, pojoListOfStudents);
```
---

### 8.14 `Object getParamVal(String name) throws Exception`

**What:** .It is used when there is a need for Full param binding; compare to RequestToPojoUtils.NULL_OBJ when you care about “omitted” vs empty/ to load a Param from the map keyed via "name".
**What it Returns:** **`Object`** (possibly **`NULL_OBJ`**).
**Example:**
```java

Object v = getParamVal("optional_note");
if (v == RequestToPojoUtils.NULL_OBJ) {
    // treated as omitted by param layer
}
```

---

### 8.15 `<T> T getParam(JQColumn<T, ?> col) throws Exception`

**When it is used:** It is used when there is a need to get the Param associated to Object's field/column
**What it Returns:** **`T`**.

**Example:**
```java
Long id = getParam(qemployees.id);
String email = getParam(qemployees.email);
```
---

### 8.16 `<T> T getURLParam(JQTableColumn<R, T, ?> col) throws Exception`

**When it is used:** It is used to capture the  Value from the URL path (route capture), not query/body.It is used there is a need for  **route** metadata to read a **path segment** (e.g. **`/customers/{id}/…`**) via **`RequestToPojoUtils.parseInURL`**. It does **not** read a query/body field unless the same name also appears there.

**What it Returns:** **`T`** (e.g. **`Long`** id).

**Example:**
```java
Long employeeId = getURLParam(qemployees.id);
```
---

### 8.17 Which getter  to use — scenario table

| Scenario  Trying to:                                                           | Use | 
|--------------------------------------------------------------------------------|-----|
| Read something you (or init()) put in the action’s map with a plain string key | **`get("key")`** | Direct **`values`** lookup; no **`Param`** typing. |
| Read a full database row you loaded with $create / $model / $list                     | **`get(qtable)`** / **`getList(qtable)`** | Row lives under **table-derived** key, not under each column name as separate map entries. |
| Read text from the form or query string                         | **`getString("name")`** or **`getString(qcol)`** | Typed string coercion; **`Column`** overload tracks renames. |
| Read a number (id, count, etc.) from form/query               | **`getLong` / `getInt`** | Parses number types without manual **`Long.parseLong`**. |
| Read a checkbox / on–off value, and “not sent” should mean off (or another default) | **`getBool("x", false)`** | HTML omits unchecked boxes; two-arg gives stable default. |
| Read a checkbox where “not sent” is a real case you will handle yourself  | **`getBool("x")`** | You take responsibility for **`null`**. |
| Read several values with the same name (or a multi param)                            | **`getList("name")`** | **`getString`** only returns one value. |
| Read an uploaded file                                               | **`getFile("name")`** | Binary/stream **`FileItem`**, not a string. |
| Read a value that must be one of a few fixed choices (enum)                                   | **`get("status", A, B, C)`** | Parses and constrains to **allowed** enum constants. |
| Quickly check if a flag / param is present (truthy style)                                            | **`is("flag")`** | Presence/truthy check without full boolean parsing. |
| You care about “not sent” vs sent-but-empty vs framework null sentinel     | **`getParamVal("name")`** | Uses **`Param` + RequestToPojoUtils**; compare to **`NULL_OBJ`**. |
| The param was declared with $param(qcol) and you want name + type from the column                                | **`getParam(qcol)`** | Name + **type** come from **JQColumn** metadata. |
| The id (or segment) lives in the URL path, not query/body                                         | **`getURLParam(qtable.id)`** | Path capture is **not** the same as **`getLong("id")`** on query/body. |
| You’re in table/cell rendering and need the display value the UI layer expects                              | **`getVal("…")`** | Follows **Renderer** resolution rules, not always **`get(String)`**. |


---

### 8.18 Which setter (or write Action) to use — scenario table

`ActionModel` only exposes a **small** explicit setter surface on **`values`**; row **creation** from the request is often **`createWithParams`** (§9). This table covers **what this section converged**.

| Scenario | Use | 
|----------|-----|
| Put any **named** object into **`values`** for JSP / JSON / nested forward | **`set("key", object)`** | Single string key; works for DTOs, maps, flags not tied to a **`JQTable`**. |
| Replace **one** **`JQRecord`** after edits (or computed fetch) so the view reads the new row | **`set(qtable, row)`** | Uses **same derived key** as **`get(qtable)`**—view and helpers stay consistent. |
| Replace a **bulk** collection bound under the table | **`set(qtable, pojoList)`** | Matches **`getList(qtable)`** for list-shaped **`values`** slots. |
| **Populate** an existing **`BasePojo`** from a param **without** re-running full **`init()`** | **`fetchFromReq` (see §9)** | Not a raw **`values.put`**; fills the nested object from request wiring. |
| **Brand-new row** from all **`$param`** fields for a table | **`createWithParams(qtable)` (see §9)** | Framework constructs and fills **`JQRecord`**; then you **`dbInsert()`** etc. |


---

## 9. Fetching and creating rows

### `<R extends JQRecord> R fetchResource(JQTableColumn<R, T, ?> col, Object id, String errKey) throws Exception`  
### (and overloads: without `errKey`, with `String` id only)

- **What:** Loads a **single row** by primary key (or designated column) with **error registration** if missing/invalid.
- **When:** It is used when there's a need to fetch the record from the table using id if it's present.
-**Example:**
```java
    public Forward callLogic() throws Exception {
        Address add = fetchResource(qaddresses.id, ((Long) get("address_id")));
        String label = add.label();
```
---

### `<R extends JQRecord> R createWithParams(JQTable<R> table) throws Exception`

- **What:** Instantiates new **`JQRecord`** and applies **request params** to its fields per meta ( **`getParamVal`** / record setters).
- **Role:** **`$create`**-style binding without manual field copy.
- **When it used:**  Used when there's a need for New **`R`** populated from request.
-**Example:**
```java
        Employee e = createWithParams(qemployees); 
        e.dbInsert();
```
---

### `U fetchFromReq(String paramName, BasePojo pojo) throws Exception` / `fetchFromReq(String, List)`

- **What:** Populates a given **`BasePojo`** from a named param **without** re-running full **`init()`** — uses **`RequestToPojoUtils.set`**.

- **when is used:** Used when there's a need to populate the entity BasePOJO's field 
- **In `callLogic()`:** `fetchFromReq("address", addrPojo);` before validation.

-**Example:**
```java
        AddressDraft addr = new AddressDraft();
        fetchFromReq("shipping_address", addr);
        // then validate addr or copy into a JQRecord
```
---

### 9.4 `createWithParams(qemployees)` vs `get(qemployees)` — when each, and why

| Situation | Use | 
|-----------|-----|
| In _defn you used $create(m.$model(qemployees)) (or $model and init() already built the row for an edit).| **`Employee e = get(qemployees);`** | **`init()`** creates **one** **`JQRecord`**, binds **`$param`** fields into it, and **`values.put(tableKey, row)`**. **`callLogic()`** must take **that same instance** so you do not lose **`init()`**’s binding or create a second competing object. |
|Insert flow: _defn does not use $create, but you still want “take all declared params and map them onto a new row” inside callLogic().| **`Employee e = createWithParams(qemployees);`** then **`e.dbInsert()`** (etc.) | **`createWithParams`** allocates a **fresh** record and runs the same style of **param → column** application as the **`$create`** path, **without** requiring a row to already sit in **`values`** from **`init()`**. |
|$create is in _defn and you also call createWithParams(qemployees) for the same table in the same request.| **Avoid** | You usually get **two** different instances or redo work: the row in **`values`** from **`init()`** is the canonical one—use **`get(qemployees)`**. |


---

### 9.5 `fetchFromReq("address", addrPojo)` vs flat fields / `employee.address()` — when each, and why

| Situation | Use |
|-----------|-----|
| Each field is one simple value with a normal name (e.g. line1, city) from $param(m.$string("line1")), etc. | **`getString("line1")`**, **`getParam(qcol)`**, or assign onto **`employee`** after **`get(qemployees)`** | No nested object graph: **`fetchFromReq`** adds little; read scalars directly or set **`employee.line1(...)`**. |
|Names are grouped under a prefix (e.g. address[line1], address[city]) and you have a small BasePojo (addrPojo) that matches that shape | **`fetchFromReq("address", addrPojo);`** | **`RequestToPojoUtils.set`** walks **param metadata** and fills the **sub-object** in one shot; avoids hand-parsing every sub-key. |
| Employee is already loaded from the database and you’re only showing the address on the page	|employee.address() (or the record’s getter)	|The data is on the saved row, not in the incoming request. Don’t fetchFromReq until the user posts an update.
| After submit, address fields are **columns on `qemployees`** and bound as **top-level** params | getParam(qemployees.address), getString("address"), etc. (whatever matches _defn) | Same table, flat binding—still usually **no** **`fetchFromReq`** unless your **`Param`** definitions use a **nested** name prefix. |
| You need to reload only a nested chunk of the request into a POJO later in the same request, without re-running full init()| **`fetchFromReq(...)`** | Documented role: partial rebind for subflows. |

**Why not** replace **`fetchFromReq("address", addrPojo)`** with relying only on **`employee.address()`** (or one accessor): **`employee.address()`** reads **what is already on the model** (often from DB or from **`init()`**’s **`$create`**). **`fetchFromReq`** reads **the current HTTP request** into a **separate** nested **`BasePojo`**. If the form posts **structured address fields**, you either bind them with **`fetchFromReq`** (nested naming) or with flat **`$param`** entries on the parent action—not by assuming a single column accessor **parses** the incoming request by itself.

**Why not** use **`fetchFromReq`** for everything: if there is **no** nested prefix and **`_defn`** already lists flat params, **`getString` / `getParam`** is simpler and matches §8.

---

## 10. Additional params and validation helpers

These three APIs work with **`Param`** objects from **`ActionMeta`**: the **static** list from **`_defn`** is **`getMeta().getParamsList()`** (and related); **`getAdditionalParams()`** exposes **extra** params when something (subclass, generator, or runtime) **adds** params beyond what **`_defn`** alone declared. Use them when validation must be **driven by metadata** (length, allowed values, types) or when **required-ness** is **not** fixed for every request.

### `List<Param> getAdditionalParams() throws Exception`

- **What :** _defn builds a fixed list of params (getMeta().getParamsList()).
  Sometimes you need extra params that are not all written in _defn—for example custom fields built from site config, or other dynamic fields. getAdditionalParams() returns that extra list. It can be empty if you don’t override it.

-**When it is used:** It is used when there's a need for additional need of parameters apart from the regular param as described under _defn()
-**Example:**
```java
    @Override
    public List<Param> getAdditionalParams() throws Exception {
        return CFRequestHelper.getParams(qcustomers, getMeta());
    }
```

### `boolean isRequired(Param p) throws Exception`

- **What :** This is used to find whether a particular Param is required or not.
- **When is used:** It is just used when there's a need to find the whether was optional or not according to the present request.
```java
    @Override
    public boolean isRequired(Param p) throws Exception {
        initSettings();
        return get(qsite_address_requirements).isVer1() //
                && isBillingAddrParamRequired(p, get(qsite_address_requirements));
    }
```


### `boolean isParamAcceptable(Param p) throws Exception`

- **What:** Checks whether the **current request value** for **`p`** satisfies the **`Param`**’s own rules (**`$maxChars`**, **`$allowedValues`**, type, etc.) as the framework interprets them.
-**when:** when there's a need to answer the question whether in the current action/request the param was acceptable or not.
-**Example:**
```java
    @Override
    public boolean isParamAcceptable(Param p)throws  Exception{
         List<String> roleNames = AccountFieldActionHelper.getRoleNameForParam(p);
        return isUserInAllowedRoleForName(p.getName(), roleNames);
    }
```


---


---

## 11. Errors

### `ActionError getErr()`

- **What:** It used to get the ERRROR attatched to the current request.
- **When to be used:** this function is used to retrieve and add additional mutated/created errors so that it is visible throughout it's cycle.
-**Example:**

```java
if (getString("email") == null) {
    getErr().addParamError("email", "required");
    return getViewForward();
}
```

---

### 11.1 When to use **`getErr()`** and which **`ActionError`** method — scenario table

| Scenario | Use                                                                                               |
|--------|---------------------------------------------------------------------------------------------------|
| A normal HTML/JSP form failed checks; the user should stay on this page and see which inputs are wrong | getErr().addParamError(...)  then return getViewForward();                                        | Param-scoped errors map to **inputs** (name matches **`_defn`** / field). **`getViewForward()`** redisplays the configured view with errors attached. |
| The error belongs to a real table column (so the name can’t drift from the form) | getErr().addParamError(qtable.column, "message")                                                  | Overload ties the message to the **same** column identity the form uses. |
| One overall message (banner / top alert), not “this specific box”| getErr().errorMessage("…")                                                                        | No single param to attach to; still part of **`ActionError`** for the response. |
| You need extra labeled errors (not just one string) | getErr().addErrorInfo(key, message)                                                               | Structured extras beyond a single param (framework/layout decides how to show them). |
| callLogic() is long; halfway through you might have already added errors | if (getErr().hasErrors()) { return getViewForward();  then success path                           | Avoids **`redirectTo`** when validation already failed mid-method. |
| This is a JSON / AJAX / API response, not a JSP round-trip | Prefer `sendError`, `sendBadRequest`, or app JSON helpers (§12) — **not** only **`getErr()` + `getViewForward()`** | **`getErr()`** pairs with **view** forwards; APIs usually return status/body instead. |
| A CBException (or similar) should be turned into the same error channel as manual validation | getErr().handleError(exception)                                                                   | Centralized mapping into **`ActionError`** where that pattern is used in your stack. |
| You fixed the data in the same request and want to validate again “from scratch”| getErr().clearErrors()                                                                            | Only when you intentionally reset before a second validation pass in the same request. |

---


---

## 12. HTTP / Ajax short responses

### `void sendBadRequest() throws Exception` / `void sendOk() throws Exception` / `void sendNoContent() throws Exception`

- **What:** These methods are used to send status in the response .Sets appropriate **HTTP status** (400 / 200 / 204) on **`resp`** for minimal API-style endpoints.
- **When:** When in the callLogic() anything is concluded like the new record is created/or deleted then it is used to send conclusions in a standard format.
- **Returns:** **`void`** (side effect on response).
- **In `callLogic()`:** Early exit after validation failure: `sendBadRequest(); return null;` *(verify pattern with your base class — some expect **`Forward`**)* — align with existing actions in repo.
-**Example 1:**
```java
    @Override
    public Forward callLogic() throws Exception {
        sendOk();
        return null;
    }
```
-**Example 2:**
```java
        ActionResponse response = handler.getResponse();
        if (response.hasErrors()) {
            err.clearErrors();
            this.err.fill(response.getValidationErrors() != null ? response.getValidationErrors() : Collections.emptyList());
            this.sendBadRequest();
            return null;
        }

        this.sendOk();
        return null;
```
-**Example 2:**
```java
        if (response.hasErrors()) {
            err.clearErrors();
            this.err.fill(response.getValidationErrors() != null ? response.getValidationErrors() : Collections.emptyList());
            this.sendBadRequest();
            return null;
        }
```


---

### `Forward sendError(String code, String message)`

- **What:** This function is used to add errror description inside the Forward .Builds error **forward** / ajax error envelope (framework-dependent).
- **When to use:** this is to be used when there is User-visible or JSON errors with stable codes.
- **Returns:** **`Forward`**.
- **In `callLogic()`:** `return sendError("invalid_id", "Employee not found");`

-**Example:**
```java
        if (source.equals(destination)) {
            return sendError("destination", "Source and destination gateway accounts cannot be the same.");
        }

        GatewayCredential srcGateway = GatewayCredential.forCurrSiteByExtId(source);
        if (srcGateway == null) {
            return sendError("source", "not in allowed values");
        }
        if (srcGateway.in(STRIPE, BRAINTREE)) {
            return sendError("source", "Cannot preform this operation with " + srcGateway.name_e() + " as a source. Contact support@chargebee.com for help.");
        }
        GatewayCredential destGateway = GatewayCredential.forCurrSiteByExtId(destination);
        if (destGateway == null) {
            return sendError("destination", "not in allowed values");
        }

```

---

### `Forward sendAjaxResponseForAdminInvokeActions(List<String> messages) throws Exception`

- **What:** Some internal admin / powerdesk / ops screens run an action over AJAX and need the result shown as several text lines (a small “log” or status report), not a normal HTML page.sendAjaxResponseForAdminInvokeActions(messages) tells the framework: “Send an AJAX response in the special format those invoke-style admin tools expect,” where messages is one string per line (headings, separators, results, errors).Response shape for **symmetry / invoke-action** admin tools.

- **Returns:** **`Forward`**.

-**When to use:** Admin “run this” / diagnostic flows, often together with m.$isInvokeAction(true) in _defn (marks the action as an invoke tool). Not for normal merchant CRUD JSON APIs.
- **Example:**
```java
    private List<String> out = new ArrayList<>();
    ...
        List<String> invNumbers = Arrays.asList(exemptedInvNumber.split(","));
        for (String inv : invNumbers) {
            inv = inv.trim();
            out.add(LoginAction.SEPARATOR);
            out.add("Validation for exempted invoice: " + inv);
            out.add(LoginAction.SEPARATOR);
            checkInvStatus(inv);
        }

        return sendAjaxResponseForAdminInvokeActions(out);
```



---

### `Forward sendAjaxRedirectTo(Route route) throws Exception`

- **What:** The browser call is an AJAX request (JavaScript fetch / XHR), so a normal “302 redirect” in the HTTP response is often not what the UI expects.sendAjaxRedirectTo(someRoute) tells the framework: “Finish this AJAX call with a response that means: tell the client to go to this other URL (this Route).”
  So after a POST (or other AJAX action) succeeds, the front end can navigate to the details page, index, login, etc.Ajax client should **redirect** browser to another route.
- **Returns:** **`Forward`** with ajax redirect instruction.
-**When to use:** After successful AJAX work, when the product wants “take the user to this screen next.”
-**Example:**
```java
        flash(FlashManager.FlashType.NOTICE, "Saved as draft.");
        return sendAjaxRedirectTo(Routes.rcustomize_invoice.index);
```


---

## 13. Forwards and views

### `Forward getViewForward()`

- **What :** After callLogic() runs, the app usually needs to answer: “What page should the user see next?getViewForward() builds a Forward that means: “Use the normal view for this action” — typically the JSP path (and related options like layout) that come from action meta ($view, convention, etc.).So you don’t hand-type the JSP path every time unless you override it.No arguments — the target view comes from this action’s ActionMeta.Default **view forward** from meta (JSP path, layout) — successful GET/POST show view.
- **Returns:** **`Forward`**.
-**When to use:** GET “show a form or page” after you’ve set values / models.POST success when the product wants another server-rendered screen (same flow as classic forms), not raw JSON and not an AJAX redirect.
-**Example:**
```java
    @Override
    public Forward _callLogic() throws Exception {
        return getViewForward();
    }
```

---

### `Forward redirectTo(Route route)`

- **WHAT:** redirectTo(someRoute) means: “Tell the browser to do a normal HTTP redirect” to the URL for that Route (usually 302/303 to a GET page).**HTTP redirect** **`Forward`** to another action URL.
- **Returns:** **`Forward`**.
-**When to use:** It used at end of  callLogic() when it's needed to navigate the end to user to a desired route.
-**Example:**
```java
    public Forward callLogic() throws Exception {
        if (NotificationUtil.checkIfEmailV2Enabled()) {
            return redirectTo(rnotifications.index);
        } else {
            return redirectTo(remail_notifications.index);
        }
    }
```


---

## 14. Flash messages

### `void flash(FlashType type, String message)`  
### `void flash(FlashType type, String message, Object... args)`  
### `String flash(FlashType type)`  
### `FlashMap flash()`

- **What:** Flash = a short message for the user (“Saved”, “Deleted”, “Something went wrong”) that you set on one request and show on a later request—very often the GET after redirectTo (Post-Redirect-Get).It lives in a flash store (implementation detail: often session or similar), and is meant to be consumed/cleared after display.**Flash** stores short **user-facing strings** in a **flash map** (typically **session- or cookie-backed**, cleared after display) so a **subsequent** request—usually the **GET after a `redirectTo`**—can show **success / warning / error** banners. It is **not** the same as **`getErr()`** (field errors on the **same** response).
- **Role:** **Post-Redirect-Get (PRG)** feedback: POST does work → **`flash(...)`** → **`redirectTo(...)`** → next page reads flash and shows a strip/toast.
-**When to use:** It used when there's a need to display small message fo the entire page.See the below example for reference.
-**Example:**
```java
flash(FlashType.NOTICE, "Employee updated");
return redirectTo(Routes.remployees.index);
```


---

### 14.1 Which flash API — scenario table

| Scenario:You want                                                                             | Use |
|-----------------------------------------------------------------------------------------------|-----|
| Success after redirect                                                                        | **`flash(FlashType.NOTICE, "…")`** then **`return redirectTo(route);`** |
| Failure after redirect                                                                        | **`flash(FlashType.ERROR, "…")`** or **`WARNING`** | 
| Soft warning                                         | **`flash(FlashType.WARNING, "…")`** |
| Message must survive longer / async UX      | **`PERSIST_NOTICE`** / **`PERSIST_WARNING`** | 
| Dynamic text                                           | **`flash(FlashType.NOTICE, "Created plan %s", name)`** (varargs overload) | 
| Inline form errors, same request                                 | **`getErr().addParamError`** + **`getViewForward()`** (§11) — **not** flash | 
| **Read** what was stashed for a given type on the **consuming** request (layout, next action) | **`String msg = flash(FlashType.NOTICE);`** or inspect **`flash()`** **`FlashMap`** | 

---

### 14.2 When **not** to use flash

- **`return getViewForward()`** with **`getErr()`** already carrying errors — flash would be **redundant** unless you also redirect.
- **JSON/ajax** responses that return structured **`success` / `message`** — use response body (§12 / app helpers), not session flash.
- **Long** or **sensitive** payloads — flash strings are for **short** UX text; do not put PII or large HTML in flash.

---

## 15. Request-scoped model attachment

### `static void setModel(HttpServletRequest req, ActionModel model)` / `static ActionModel getModel(ServletRequest req)`

- **What:** For one HTTP request, many pieces of code need the same action object: the JSP, includes, error handling, sometimes a custom dispatcher.
  Putting the ActionModel on the HttpServletRequest (as a request attribute) gives everyone a single place to ask: “Which action is handling this request?”The function setModel(....) says to set the ActionModel in the http request.And similarly there is a getter to this nfunction to get the ActionModel from the http request.Stores active **`ActionModel`** on request attribute for **nested forwards** and error pages.
-**When to use:** Generally the framework calls it.
-**Arguments accepted:** **`HttpServletRequest`**, **`ActionModel`**
- **Example:**
```java
            ActionModel.setModel(req, actModel);

            // Parse the request as multipart and set details
            req = MultipartRequest.parseRequest(req, actModel.getMeta().size);
            ...
            actModel.setDetails(wrappedReq, resp);

            // Execute the action model
            Forward f = actModel.exec();
```


---

## 16. Roles, routes, features

### `long userRoles()` / `boolean isUserInRoles(long mask)` / `boolean isUserInRoles(Role... roles)`

- **What:** As the Roles are in the form of bit-id in the framework and the roles are fixed according the chargebee business requirement so these functions are use to fetch the bit id of the roles/Also to check whether a role is available for  PARTICULAR bit id/alo used to check whether the current user is having the role in the ROLES given in the argument.Reads **current user’s role bitmask** and tests membership.
-**When to use:**It is used inside the callLogic() for various requirements like to send custom responses to users having different roles,etc.

**Example:** 
```java
boolean isUserInRoles(long mask)


```

---

### `boolean isUserAllowed(Route route)` / `boolean isAllowed(Route route)`

- **What:** Whether **current user** may hit **`route`** / whether action meta allows (framework nuances differ — both consult routing + meta).
-**When to use:** It is used when there is a need to answer a question that "is the current user allowed for this Route.",etc.
- **Returns:** **`boolean`**.
-**Example:**
```java
        data.put("canViewDashboard", isUserAllowed(Routes.rspa.dashboards_index));
```

---

### `boolean isUserInAllowedRoleForName(String actionName, String roleName)` / `(String, List<String>)` / `boolean isUserInAllowedRole(String, Long)`


```java
boolean isUserInAllowedRoleForName(String actionName, String roleName)
What: “For this named action, is the user allowed if we’re thinking in terms of one role name?”
Returns: true if the check passes, false otherwise.
When to  use: Comparing a single role name against what’s allowed for an action identified by name (string), e.g. tooling or admin flows where the action is looked up by name.



boolean isUserInAllowedRoleForName(String actionName, List<String> roleNames)
What:Same idea as above, but you pass several possible role names (a list).
Returns: true / false depending on whether the user matches the allowed roles for that action name (exact rules live in the framework / metadata).
When to use: “User must be in one of these roles” for that action.


boolean isUserInAllowedRole(String something, Long roleId)

What: Check using a numeric role id (Long) instead of role names.
Returns: true / false.
When to use: When roles are stored or passed as ids (database / API), not as readable names.
```

---

### `Object featureOperandVal() throws Exception`  
### `boolean isAllowedFeature(Feature f) throws Exception`  
### `boolean isAllowedFeature(Feature f, Object operand) throws Exception`  
### `boolean isFeatureQtyReachingLimit(Feature f)` (+ operand overload)

- **What:** These are the feature flags**Feature flags** and **entitlement limits** (quantity nearing cap).
-**When to use:** is used in callLogic() used to answer the question about the Feature flag.
- **In `callLogic()`:**

```java
if (!isAllowedFeature(Features.ADVANCED_INVOICING)) {
    getErr().errorMessage("Feature not enabled");
    return getViewForward();
}
```


---

### 16.1 Which function to use — scenario table (roles, routes, features)

| Scenario You're trying to...                                                                                           | Use |
|------------------------------------------------------------------------------------------------------------------------|-----|
| In callLogic(), branch or skip a step because the user must be Admin OR Finance (any one of several roles is OK)       | **`isUserInRoles(ADMIN, FINANCE_EXECUTIVE)`** | Readable **OR** semantics: user has **any** of the listed roles (typical pattern). |
| You already have roles packed as a single number (a “mask”) from userRoles() or old code, and you want one quick check | **`isUserInRoles(mask)`** or compare **`userRoles()`** | Avoids repeated **`Role`** lookups when integrating with legacy bitmask APIs. |
| You need the raw role number for logs, metrics, or code outside this framework                                         | **`userRoles()`** | Exposes **`long`** for debugging or non-framework consumers. |
| Hide a link or don’t offer a button to another page unless the user is allowed to go there                             | **`isUserAllowed(targetRoute)`** | “May this **user** invoke this **route**?” — natural for menus, related actions, conditional **`redirectTo`** targets. |
| You see isAllowed(route) in nearby code and want to match that style                                                   | **`isAllowed(route)`** | Some codepaths use this for **permission + meta** together; if both exist in your version, **align with existing actions** in the same area (grep **`isAllowed(`** vs **`isUserAllowed(`**). |
| Permissions are stored as strings: an action name + role name(s), not a Route object                                   | **`isUserInAllowedRoleForName(actionName, roleName)`** or **List** overload | String-driven checks without a **`Route`** instance. |
| You only know the role as a number (from DB or config), not a Role enum                                                | **`isUserInAllowedRole(String, Long)`** | When identity is **id**, not **`Role`** constant. |
| Turn a product feature on/off for the current context (simple yes/no)                                                  | **`isAllowedFeature(Feature)`** | Standard **on/off** feature check for **current site/context** (throws **`Exception`** per signature—handle or declare). |
| The feature depends on context—e.g. which plan, which record, or how much is allowed for that thing                    | **`isAllowedFeature(Feature, operand)`** | Operand selects **which** subscription/plan row (etc.) limits apply to. |
| Show a warning (“you’re almost at the limit”) without blocking yet                                                     | **`isFeatureQtyReachingLimit(Feature)`** or operand overload | Soft **capacity** signal; pair with **`isAllowedFeature`** for hard gate if needed. |
| Show “3 of 5 used” in the UI                                                                                           | **`featureOperandVal()`** | Read-side of the same **operand** concept as **`isAllowedFeature(f, operand)`**. |


---


---

## 17. HTTP method and Ajax gates

### `void validateHttpMethod()`

- **What:** The browser sends each request with an HTTP method — most often GET (read / open a page) or POST (submit a form, change data).
  Your action’s metadata says which method is allowed (for example: “this action is POST-only”).Ensures request **HTTP method** matches **`getMeta().getMethod()`** (GET vs POST).
- **Role:** Security — POST-only mutations.
-**When to use:** In almost all actions you do not call this yourself. The framework usually runs it before callLogic().Call or override it only for unusual cases — for example, an action that is normally POST but must also answer GET for a health/ping check. In this repo, WebhooksEinvoicingProviderAction overrides validateHttpMethod() so GET returns early without failing, and everything else still goes through super.validateHttpMethod() (which enforces the meta method for real webhook POSTs).
- **Example:**
```java
    void _defn(AppActionMeta m) {
        m.$method(post).$auth(AuthType.StrictlyUnauthenticated)
                .$reqSource(RequestSource.EXTERNAL_SERVICE, EinvoicingProviderEnum.EINVOICE_STATUS_WEBHOOK);
        m.$path("/einvoicing/webhooks").$col(qe_invoicing_configurations.external_id);
        m.$cbModule(CBModuleConstant.TAXES);
    }

    /**
     * Allows GET requests for third-party e-invoicing provider ping tests.
     * Providers typically send a GET request to verify endpoint connectivity before sending webhooks.
     */
    @Override
    public void validateHttpMethod() {
        if (get.name().toUpperCase().equals(req.getMethod())) {
            return;
        }
        super.validateHttpMethod();
    }
```
---

### `Forward validateAjaxRequest()`

- **What:**  Some actions are meant to be hit only as AJAX (JavaScript fetch / XMLHttpRequest, not a full browser page load). validateAjaxRequest() is the hook that enforces “this really is an AJAX call” when you turn that on in metadata.Validates **ajax** preconditions (headers, CSRF subset) per meta **`$ajaxPrecheck`**.
- **Returns:** **`Forward`** (error forward) or **`null`** / success — verify in **`javap -c`** for your version.
- **When to use:** **In `callLogic()`:** Prefer meta **`$ajaxPrecheck(true)`**; manual call rare.
-**Example:**
```java
        m.$ajaxPrecheck(true);
```
```java
    @Override
public Forward validateAjaxRequest() {
    AjaxErrorUtil.removeAjaxErrCookie(this);
    return null;
}
```
---

## 18. CSRF, CSP, CORS, hidden fields

### `String csrfToken()`

- **What:** It is used to get the Current **CSRF token** string for forms.
- **Returns:** **`String`**.
- **When to use:** **In `callLogic()`:** Pass to JSON for SPA building a form; JSP often uses tags.
- **Example:**
```java
        // Validate header token
        String paramTok = getCSRFtokenFromHeaders(req);
        if (!csrfToken().equals(paramTok)) {
            throw WebErrorCodes.CSRF_INVALID.err();
        }

```
       
---

### `String genHiddenInputs()` / `void genAdditionalInputs(StringBuilder sb)`

-
```java
        String genHiddenInputs()
        What it does:
        Builds a chunk of HTML: one or more <input type="hidden" …/> lines.
        For each parameter listed on this action’s metadata (getMeta().getParamsList()), it looks at the current HTTP request. If that parameter has value(s) in the request, it emits a hidden field with the same name and value (HTML-escaped).
        
        When to use it
        When you render a new form or page but need to carry forward query/body parameters the user already sent (filters, IDs, continuation state), you drop this string inside <form>…</form> so the next submit sends them again.
        
        
        
        
        
        
        <form method="post" action="...">
          <%= act.genHiddenInputs() %>
          <!-- visible fields -->
        </form>
        (act = your action model in scope.)
        
        Note on “CSRF”
        In the ActionModel bytecode you have, genHiddenInputs() only replays meta params from the request; it is not the same as csrfToken() / CSRF hidden fields unless some other layer adds them. For CSRF, use csrfToken() (and your app’s usual form helpers) as in earlier examples.
        
        void genAdditionalInputs(StringBuilder sb) 
        What it does:
        Same source of data as above (meta param list + current request values), but instead of HTML it appends query-string pieces to the StringBuilder you pass in (via JspUtils.appendQueryParam in the framework).
        
        When to use:
        You’re building a URL (path + query) and need the same “carry forward” behavior as hidden inputs, but for a link or GET target, not a form body.
        
        
```
---

### `CSP getCspPolicy()` / `void addXFrameHeader()`

- **What:**this function is used to get the **Content-Security-Policy** object; **X-Frame-Options** / frame ancestors helper.(the header which is sent via POSTMAN.)

- **When to use:** **In `callLogic()`:** Not generally used.

---

### `static String escPath(Object o)` / `String corsBaseURL()`


```java
String escPath(Object o)
What it does:
When you build a URL path and plug in dynamic values (IDs, tokens, slugs), characters like spaces or & could break the URL or cause odd server behavior. escPath turns the value into a safe string for use inside a path segment (URL encoding / escaping — the framework implements this in JspUtils.escPath(String)).

When it is used:
Typical when building outbound REST paths, redirect URLs, or any path that includes user or gateway-supplied ids.


Example:
        return sendRequest(http, HttpUtil.Method.GET, "/transactions/creditsales/" + escPath(creditSalesId), null, null, false, currencyCode, XGPVERSION, false, "Global Payments : Fetch Credit Sale Transaction By Id");



String corsBaseURL()
What it does:
For actions that are $corsEnabled(true), the browser may call your app from another origin. corsBaseURL() is the hook that supplies the base URL the framework/clients should treat as the Chargebee origin for those flows (e.g. building absolute URLs for redirects or JSON payloads).

When it is used:
Usually overridden on specific actions; sometimes combined with URLBuilder.urlPrefix(...) so generated URLs are CORS-correct.
        
        Example:
        void _defn(...){
            m.$auth(AuthType.Authenticated).$subDomainOpt(SubDomainOpt.optional);
            m.$corsEnabled(true);
        }

        @Override
        public String corsBaseURL() {
          if (currentSite() != null) {
            KVL.put("cors_base_url", "null");
            return null;
          }
          return getCorsBaseUrl(getTestSite());
        }

```

---

## 19. Path helpers

### `String getCurrentPath()` / `void setCurrentPath(String path)` / `Object getPathCompFor(JQColumn col)`


```java
import javax.swing.*;

String getCurrentPath()

What it
does:
It answers
the question "What is the full path for this ActionModel/Action?"

When it
is used:
It is
used when
there's a need to get the full path.

Example:

public String target() {
  StringBuilder path;
  if (tvConfig != null) {
    path = tvConfig.getReqState().url(getCurrentPath());
    this.genAdditionalInputs(path);
    return path.toString();


void setCurrentPath (String path)
What it does:
As the name of the function speaks it is used to set the path for the current Action



When it is used:
It is used when the initial path needs to be updated with the a new path for the ActionMeta.



Object getPathCompFor(JQ Column col)
What it deoes:
    Your route is often declared with $path(...) and $col(...) segments tied to table columns (e.g. subscription id in the URL). This method returns the value bound to that column for this() ->
    request.
When to use it:
It is used when there's a need to find the column id from the path.
```

---




---

## 20. Layout properties and related routes

### `<T> U prop(DefinedProp<T> prop, T value)` / `<T> T getProp(DefinedProp<T> prop)`


```java
prop(DefinedProp<T> prop, T value)
What it is:
A typed setter on the current action that stores an extra value (layout title, tab, flag, etc.) under a DefinedProp<T> key. Returns this so you can chain calls.
When to use it:
When the value is only known during the request (e.g. in callLogic() after you branch), not when you author _defn. Use the same DefinedProp keys (Layouts.*, Tab.*, etc.) as sibling actions.
Example:
// Inside callLogic() — dynamic admin shell title (illustrative)
        this.prop(Layouts.admin_layout_title, "My Page");



getProp(DefinedProp<T> prop)
What it is:
A typed getter for that stored map: returns T, or null if that prop was never set.

When to use it:
When layout / JSON config / navigation code needs to read what the action (or meta) set—e.g. which tab enum to expose to the client.

Example:
        if (m.getProp(Tab.CoreTabs.defprop) != null) {
        obj.put(Keys.current_tab, Inflector.underscore(((Tab) m.getProp(Tab.CoreTabs.defprop)).dispName));
        }
        if (m.getProp(Tab.SubTabs.defprop) != null) {
        obj.put(Keys.current_sub_tab, Inflector.underscore(((Tab) m.getProp(Tab.SubTabs.defprop)).dispName));
        }


$prop(DefinedProp<T> prop, T value)

What it is:
The metadata-time version: set the same kind of typed prop while defining the action in _defn. Chains on m after things like $layout.

When to use it:
When the value is fixed for that action (known when you write the class), especially Layouts.admin_layout_title with Layouts.admin_layout.

Example:
void _defn(AppActionMeta m)
{
  m.$roles(Role.READ_ONLY).$isVisible(false);
  m.$method(HttpMethod.get);
  m.$subDomainOpt(SubDomainOpt.strictly_no);
  m.$layout(Layouts.admin_layout).$prop(Layouts.admin_layout_title, "Tax Computation");
  m.$title("Tax Computation");
```
---



## 21. Breadcrumbs

### `String currentBreadCrumbTxt()` / `String currentBreadCrumbHtml()` / `String parentBreadCrumbTxt()` / `String parentBreadCrumbLink()`

```java
String currentBreadCrumbTxt()
What it is:
Plain-text label for this page in the breadcrumb trail.

When to use it:
Override when the default title is wrong or too generic (feature name, section name, etc.).

Example:
    public String currentBreadCrumbTxt() {
      return "Chargeback Management";
    }




String currentBreadCrumbHtml()
What it is:
HTML for the current crumb when you need markup (extra spans, links inside the label, entity display with formatting), not just escaped text.

When to use it:
Override when currentBreadCrumbTxt() is not enough—e.g. show invoice number + customer with CSS classes.

Example:
      public String currentBreadCrumbTxt() {
        return "Chargeback Management";
      }




String currentBreadCrumbHtml()
What it is:
HTML for the current crumb when you need markup (extra spans, links inside the label, entity display with formatting), not just escaped text.

When to use it:
Override when currentBreadCrumbTxt() is not enough—e.g. show invoice number + customer with CSS classes.

Example:
      @Override
      public String currentBreadCrumbHtml() {
        HtmlBuilder b = new HtmlBuilder(true);
        b.a("Invoice # ");
        b.a(get(qinvoices).number());
        b.a(" ");
        b.a("<span class='cb-help-text'> for ");
        b.a(eh(customer.detPgtitle()));
        b.a("</span>");
        return b.generate();
      }



String parentBreadCrumbTxt()


What it is:
Plain-text label for the parent step (one level “up” in the trail).

When to use it:
Override together with parentBreadCrumbLink() so the parent segment reads correctly (e.g. “Invoice # 123” instead of a generic parent).

Example:
        @Override
        public String parentBreadCrumbTxt() {
          return "Invoice # " + get(qinvoices).number();
        }





String parentBreadCrumbLink()

What it is:
URL/path for the parent crumb (where the user goes when they click the parent segment).

When to use it:
Override when the parent should deep-link to a details (or list) route, e.g. invoice details for the same record.

Example :
      @Override
      public String parentBreadCrumbLink() {
        return Routes.rinvoices.details.path(get(qinvoices).id());
      }
```
---

## 22. Request-scoped store

### `RequestScopedStore getStore()`

```java
RequestScopedStore getStore()
What it is:
A small per-request key/value bag tied to the same HTTP request as the ActionModel. It is not the form/query values map and not a request parameter

When to use:
It is used to fetch some internal data.It is also like the values of the ActionModel but for a different use.


```
---


---


---

## 25. Title prefix

### `static String getTitlePrefix(HttpServletRequest req)` / `String titlePrefix()`

```java
tatic String getTitlePrefix(HttpServletRequest req)
What:
A layout helper that figures out the left-hand part of the browser tab title for the current request. It loads the ActionModel from the request (getModel(req)), calls titlePrefix() on that model, and if that is null or empty it falls back to getMeta().titlePrefix() (from action metadata, e.g. $title wiring—exact meta behavior is framework-defined).

When to use it:
In JSP (or similar) when rendering <title>, so every page gets a consistent prefix without duplicating site/env logic in each view. Also usable when you expose layout JSON for a headless shell and want the same prefix the classic layout uses.




String titlePrefix()
What it is:
Instance hook: dynamic title prefix for this action (entity name + screen, etc.). The default implementation on ActionModel returns null, so the static helper can fall back to meta titlePrefix().

When to use it:
Override on actions where $title alone is not enough and the tab should show context (plan name, “Clone”, tax country page, etc.). Rarely call it yourself from callLogic() except to forward into JSON for a SPA/header service.

Example:
      @Override
      public String titlePrefix(){
        return get(qplans).name() + " Plan - Details";
      }
      
      
      

```

---

## 26. `subdomain()` (abstract)

- **Description:** Subdomain string for **current request** (app implements on **`AppActionModel`**).
- **Role:** Multi-tenant routing, cookie domain.
- **Returns:** **`String`**.
- **In `callLogic()`:** `subdomain()` for building external links or tenant checks (also **`currentSite()`** on app subclass is richer).
```java
What it is:
A string that names the tenant slice of the current request’s host in Chargebee’s multi-tenant model. On the framework side, ActionModel declares subdomain() as abstract; AppActionModel supplies the real behavior. In your shipped AppActionModel bytecode, if SegmentConfig.isSegmented() is false, it returns "app"; otherwise it returns the cached subDomain field (parsed from the request / routing pipeline—see parseSubDomain helpers on the same class).
When to use it:
When you need a simple tenant key from the URL (building links, logging, comparing to a stored subdomain)

Example:
   String tenantKey = subdomain();

```
---


---


---

