# ERD Multi-tenant (Django + django-tenants)

Este diagrama muestra la separación física de esquemas en PostgreSQL mediante secciones visuales:

- **`public`**: esquema compartido con los datos de tenancy (`Organization`, `Domain`).
- **`tenant_empresa_a` / `tenant_empresa_b`**: esquemas operativos completamente aislados, uno por organización. Cada uno replica el mismo conjunto de tablas de forma independiente.

> **Nota:** `QrGenerator` y `StatisticalSummary` son **modelos proxy** de Django y no generan tablas en la base de datos.
>
> El diagrama usa `graph TD` con `subgraph` en lugar de `erDiagram` para poder representar los cuadros de esquema. Las líneas discontinuas (`-.->`) indican la relación arquitectónica multitenant (cross-schema), no FKs físicas.

```mermaid
graph TD
    classDef publicNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef tenantANode fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef tenantBNode fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef proxyNode fill:#f3e8ff,stroke:#9333ea,color:#4a044e,stroke-dasharray:5 5

    subgraph PUBLIC["🗄️ ESQUEMA: public  —  Datos Compartidos (django_tenants)"]
        direction TB
        ORG["<b>Organization</b><br/>─────────────<br/>id: UUID PK<br/>name: string<br/>schema_name: string<br/>is_active: boolean<br/>created_at / updated_at"]
        DOM["<b>Domain</b><br/>─────────────<br/>id: int PK<br/>domain: string<br/>is_primary: boolean<br/>tenant_id: UUID FK"]
    end

    subgraph TENANT_A["🏢 ESQUEMA: tenant_empresa_a  —  Datos Aislados"]
        direction TB

        subgraph A_TRANSPORT["transport"]
            A_ROUTE["<b>Route</b><br/>─────────────<br/>id: UUID PK<br/>name: string<br/>metadata: JSON"]
            A_UNIT["<b>Unit</b><br/>─────────────<br/>id: UUID PK<br/>transit_number: string UK<br/>internal_number: string<br/>owner: string<br/>route_id: UUID FK"]
        end

        subgraph A_INTERVIEW["interview"]
            A_QUESTION["<b>Question</b><br/>─────────────<br/>id: UUID PK<br/>text: text<br/>type: rating|text|choice|multi<br/>position: int<br/>active: boolean"]
            A_OPTION["<b>QuestionOption</b><br/>─────────────<br/>id: UUID PK<br/>question_id: UUID FK<br/>text: string<br/>position: int"]
            A_REASON["<b>ComplaintReason</b><br/>─────────────<br/>id: UUID PK<br/>label: string"]
            A_SUBMISSION["<b>SurveySubmission</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>submitted_at: datetime"]
            A_ANSWER["<b>Answer</b><br/>─────────────<br/>id: UUID PK<br/>submission_id: UUID FK<br/>question_id: UUID FK<br/>text_answer: text<br/>rating_answer: int<br/>selected_option_id: UUID FK"]
            A_ANSWER_OPTS["<b>Answer_SelectedOptions</b><br/>─────────────<br/>id: int PK<br/>answer_id: UUID FK<br/>questionoption_id: UUID FK"]
            A_COMPLAINT["<b>Complaint</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>reason_id: UUID FK<br/>text: text<br/>submitted_at: datetime"]
        end

        subgraph A_USERS["users"]
            A_USER["<b>User</b><br/>─────────────<br/>id: UUID PK<br/>username: string<br/>email: string<br/>is_staff: boolean"]
        end
    end

    subgraph TENANT_B["🏢 ESQUEMA: tenant_empresa_b  —  Datos Aislados"]
        direction TB

        subgraph B_TRANSPORT["transport"]
            B_ROUTE["<b>Route</b><br/>─────────────<br/>id: UUID PK<br/>name: string<br/>metadata: JSON"]
            B_UNIT["<b>Unit</b><br/>─────────────<br/>id: UUID PK<br/>transit_number: string UK<br/>internal_number: string<br/>owner: string<br/>route_id: UUID FK"]
        end

        subgraph B_INTERVIEW["interview"]
            B_QUESTION["<b>Question</b><br/>─────────────<br/>id: UUID PK<br/>text: text<br/>type: rating|text|choice|multi<br/>position: int<br/>active: boolean"]
            B_OPTION["<b>QuestionOption</b><br/>─────────────<br/>id: UUID PK<br/>question_id: UUID FK<br/>text: string<br/>position: int"]
            B_REASON["<b>ComplaintReason</b><br/>─────────────<br/>id: UUID PK<br/>label: string"]
            B_SUBMISSION["<b>SurveySubmission</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>submitted_at: datetime"]
            B_ANSWER["<b>Answer</b><br/>─────────────<br/>id: UUID PK<br/>submission_id: UUID FK<br/>question_id: UUID FK<br/>text_answer: text<br/>rating_answer: int<br/>selected_option_id: UUID FK"]
            B_ANSWER_OPTS["<b>Answer_SelectedOptions</b><br/>─────────────<br/>id: int PK<br/>answer_id: UUID FK<br/>questionoption_id: UUID FK"]
            B_COMPLAINT["<b>Complaint</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>reason_id: UUID FK<br/>text: text<br/>submitted_at: datetime"]
        end

        subgraph B_USERS["users"]
            B_USER["<b>User</b><br/>─────────────<br/>id: UUID PK<br/>username: string<br/>email: string<br/>is_staff: boolean"]
        end
    end

    %% ── Relaciones en esquema PUBLIC ──────────────────────────────────
    ORG -->|"tiene dominios"| DOM

    %% ── Relaciones internas TENANT A ─────────────────────────────────
    A_ROUTE -->|"asigna unidades"| A_UNIT
    A_UNIT -->|"recibe encuestas"| A_SUBMISSION
    A_QUESTION -->|"define opciones"| A_OPTION
    A_SUBMISSION -->|"contiene respuestas"| A_ANSWER
    A_QUESTION -->|"es respondida en"| A_ANSWER
    A_OPTION -->|"selección única"| A_ANSWER
    A_ANSWER -->|"multi-selección M:N"| A_ANSWER_OPTS
    A_OPTION -->|"multi-selección M:N"| A_ANSWER_OPTS
    A_UNIT -->|"genera quejas"| A_COMPLAINT
    A_REASON -->|"clasifica"| A_COMPLAINT

    %% ── Relaciones internas TENANT B ─────────────────────────────────
    B_ROUTE -->|"asigna unidades"| B_UNIT
    B_UNIT -->|"recibe encuestas"| B_SUBMISSION
    B_QUESTION -->|"define opciones"| B_OPTION
    B_SUBMISSION -->|"contiene respuestas"| B_ANSWER
    B_QUESTION -->|"es respondida en"| B_ANSWER
    B_OPTION -->|"selección única"| B_ANSWER
    B_ANSWER -->|"multi-selección M:N"| B_ANSWER_OPTS
    B_OPTION -->|"multi-selección M:N"| B_ANSWER_OPTS
    B_UNIT -->|"genera quejas"| B_COMPLAINT
    B_REASON -->|"clasifica"| B_COMPLAINT

    %% ── Relación arquitectónica cross-schema (no FK física) ──────────
    PUBLIC -. "crea y gestiona schema" .-> TENANT_A
    PUBLIC -. "crea y gestiona schema" .-> TENANT_B

    %% ── Estilos por esquema ──────────────────────────────────────────
    class ORG,DOM publicNode
    class A_ROUTE,A_UNIT,A_QUESTION,A_OPTION,A_REASON,A_SUBMISSION,A_ANSWER,A_ANSWER_OPTS,A_COMPLAINT,A_USER tenantANode
    class B_ROUTE,B_UNIT,B_QUESTION,B_OPTION,B_REASON,B_SUBMISSION,B_ANSWER,B_ANSWER_OPTS,B_COMPLAINT,B_USER tenantBNode
```

## Lectura rápida de arquitectura

| Esquema | Color | Contenido |
|---|---|---|
| `public` | Azul | `Organization` + `Domain` — datos de tenancy compartidos por toda la plataforma |
| `tenant_empresa_a` | Verde | Tablas operativas aisladas de la empresa A |
| `tenant_empresa_b` | Amarillo | Mismo conjunto de tablas, completamente independiente de A |

**Principios clave:**

- `Organization.schema_name` determina el nombre del esquema PostgreSQL que se crea automáticamente.
- Cada tenant tiene su propia instancia de tablas: no comparten filas, secuencias ni índices.
- Las líneas discontinuas (`-.->`) representan la relación arquitectónica de gestión de esquema, **no FKs físicas** entre esquemas.
- `django-tenants` enruta cada request al esquema correcto mediante el middleware `TenantMainMiddleware` y la resolución por dominio HTTP.

---

## ERD Simplificado — 1 Tenant

Diagrama reducido con un único tenant para mayor claridad.

```mermaid
graph TD
    classDef publicNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f
    classDef tenantNode fill:#dcfce7,stroke:#16a34a,color:#14532d

    subgraph PUBLIC["🗄️ ESQUEMA: public  —  Datos Compartidos"]
        direction TB
        ORG["<b>Organization</b><br/>─────────────<br/>id: UUID PK<br/>name: string<br/>schema_name: string<br/>is_active: boolean<br/>created_at / updated_at"]
        DOM["<b>Domain</b><br/>─────────────<br/>id: int PK<br/>domain: string<br/>is_primary: boolean<br/>tenant_id: UUID FK"]
    end

    subgraph TENANT["🏢 ESQUEMA: tenant_empresa  —  Datos Aislados"]
        direction TB

        subgraph TRANSPORT["transport"]
            ROUTE["<b>Route</b><br/>─────────────<br/>id: UUID PK<br/>name: string<br/>metadata: JSON"]
            UNIT["<b>Unit</b><br/>─────────────<br/>id: UUID PK<br/>transit_number: string UK<br/>internal_number: string<br/>owner: string<br/>route_id: UUID FK"]
        end

        subgraph INTERVIEW["interview"]
            QUESTION["<b>Question</b><br/>─────────────<br/>id: UUID PK<br/>text: text<br/>type: rating|text|choice|multi<br/>position: int<br/>active: boolean"]
            OPTION["<b>QuestionOption</b><br/>─────────────<br/>id: UUID PK<br/>question_id: UUID FK<br/>text: string<br/>position: int"]
            REASON["<b>ComplaintReason</b><br/>─────────────<br/>id: UUID PK<br/>label: string"]
            SUBMISSION["<b>SurveySubmission</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>submitted_at: datetime"]
            ANSWER["<b>Answer</b><br/>─────────────<br/>id: UUID PK<br/>submission_id: UUID FK<br/>question_id: UUID FK<br/>text_answer: text<br/>rating_answer: int<br/>selected_option_id: UUID FK"]
            ANSWER_OPTS["<b>Answer_SelectedOptions</b><br/>─────────────<br/>id: int PK<br/>answer_id: UUID FK<br/>questionoption_id: UUID FK"]
            COMPLAINT["<b>Complaint</b><br/>─────────────<br/>id: UUID PK<br/>unit_id: UUID FK<br/>reason_id: UUID FK<br/>text: text<br/>submitted_at: datetime"]
        end

        subgraph USERS["users"]
            USER["<b>User</b><br/>─────────────<br/>id: UUID PK<br/>username: string<br/>email: string<br/>is_staff: boolean"]
        end
    end

    %% ── Relaciones PUBLIC ─────────────────────────────────────────────
    ORG -->|"tiene dominios"| DOM

    %% ── Relaciones internas TENANT ────────────────────────────────────
    ROUTE -->|"asigna unidades"| UNIT
    UNIT -->|"recibe encuestas"| SUBMISSION
    QUESTION -->|"define opciones"| OPTION
    SUBMISSION -->|"contiene respuestas"| ANSWER
    QUESTION -->|"es respondida en"| ANSWER
    OPTION -->|"selección única"| ANSWER
    ANSWER -->|"multi-selección M:N"| ANSWER_OPTS
    OPTION -->|"multi-selección M:N"| ANSWER_OPTS
    UNIT -->|"genera quejas"| COMPLAINT
    REASON -->|"clasifica"| COMPLAINT

    %% ── Relación arquitectónica cross-schema ──────────────────────────
    PUBLIC -. "crea y gestiona schema" .-> TENANT

    %% ── Estilos ───────────────────────────────────────────────────────
    class ORG,DOM publicNode
    class ROUTE,UNIT,QUESTION,OPTION,REASON,SUBMISSION,ANSWER,ANSWER_OPTS,COMPLAINT,USER tenantNode
```

| Esquema | Color | Contenido |
|---|---|---|
| `public` | Azul | `Organization` + `Domain` — datos de tenancy compartidos |
| `tenant_empresa` | Verde | Tablas operativas aisladas del tenant |
