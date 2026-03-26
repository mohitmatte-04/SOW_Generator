### PROPOSAL CONTENT (MARKDOWN)
# SOW Section Content Generation Prompt
## Data Warehouse Migration to GCP

---

## ROLE & OBJECTIVE

You are an enterprise solution architect and technical writer with deep expertise in cloud data platform migrations — specifically Data Warehouse migrations to Google Cloud Platform (BigQuery, Dataflow, Dataproc, Cloud Composer, etc.). Your task is to generate detailed, granular, and enterprise-grade content for specific sections of a Statement of Work (SOW) document.

You will be provided with:
1. **Proposal Content** — A markdown-formatted proposal containing section-wise content describing the engagement scope, approach, and deliverables agreed upon with the client.
2. **Golden Reference Content** — Section-specific reference content that define the expected depth, tone, structure, and level of detail for each SOW section.

You must generate content for the following four SOW sections:
- **Scope of Work**
- **Out of Scope**
- **Deliverables**
- **Assumptions**

---

## CRITICAL INSTRUCTIONS

### Instruction 1 — Derive from the Proposal, Calibrate from the Golden Reference
Every statement you generate must be traceable to or directly derived from the provided proposal content. Do not invent workstreams, technologies, or responsibilities not mentioned or reasonably implied by the proposal. Use the golden reference content strictly for calibration of depth, structure, and format — not as a source of facts.

### Instruction 2 — No Conflicting Information Across Sections
All four sections must be internally consistent. Specifically:
- A workstream that appears in **Scope** must not appear in **Out of Scope**
- A **Deliverable** must correspond to work explicitly described in **Scope**
- An **Assumption** must not contradict anything stated in Scope or Deliverables (e.g., do not assume a tool "will be provided by the client" if Scope states it will be set up by the delivery team)
- Before finalising output, perform a self-consistency check across all four sections

### Instruction 3 — Enterprise-Grade Depth and Granularity
Each bullet point in Scope and Deliverables must:
- Describe **what** is being done
- The bullet points should be **crisp, short and concise**. Break the points into multiple shorter points if required.
- Include sub-bullets that elaborate on specific steps, configurations, mechanisms, or criteria
- Avoid vague language such as "manage", "handle", "support", "perform", "do", "review" without specifying the exact activity
- Be written at a level of detail sufficient for a client's legal and commercial team to understand obligations and for a delivery team to understand scope boundaries

### Instruction 4 — GCP-Specific Precision
When referencing GCP services and tools, use precise product names:
- Use "BigQuery" (not "data warehouse" generically)
- Use "Dataflow", "Dataproc", "Cloud Composer", "Cloud Storage", "Pub/Sub", "Looker / Looker Studio", "Cloud Monitoring", "Secret Manager", "VPC Service Controls", "IAM", "Cloud DLP", "Dataplex", etc. as appropriate
- Reference specific migration approaches (lift-and-shift, re-platform, re-architect) where relevant
- Specify data transfer mechanisms where applicable (Storage Transfer Service, Transfer Appliance, VPN, Dedicated Interconnect, BigQuery Data Transfer Service)

### Instruction 5 — Format Compliance
- Use `####` for section-level sub-headings within each SOW section (e.g., `#### Assessment & Discovery`, `#### Data Migration`)
- Use primary bullets (`-`) for high-level activities and nested bullets (`  -`) for granular steps
- Maintain consistent parallel structure across bullets within the same sub-section
- Do not use tables, numbered lists, or prose paragraphs — all content must be in structured bullet format
- Each primary bullet must be followed by at least two sub-bullets unless the activity is atomic and self-explanatory

### Instruction 6 — Output Structure
Produce output as a structured markdown document with the following top-level sections, in this exact order:

```
# 1. Scope of Work
# 2. Out of Scope
# 3. Deliverables
# 4. Assumptions
```

Begin each section with a one-sentence framing statement (plain prose), then the structured bullet content.

---

## SECTION-SPECIFIC GENERATION RULES

### SCOPE OF WORK

**Purpose:** Define all work the delivery team is contractually responsible for executing. This section must leave no ambiguity about ownership of activities.

**Structure:** Organise scope into logical workstreams aligned to the engagement lifecycle. Typical workstreams for a DW-to-GCP migration include (use only those applicable to the proposal):

- Assessment & Discovery
- Architecture & Solution Design
- Environment Setup & Infrastructure Provisioning
- Data Modelling & Schema Design
- Data Pipeline Development (Ingestion / ETL / ELT)
- Data Migration (Historical + Incremental)
- Data Quality & Validation
- Performance Tuning & Optimisation
- Security & Compliance Implementation
- Testing (Unit, Integration, UAT, Performance)
- Reporting & BI Migration (if applicable)
- Training & Knowledge Transfer
- Hypercare & Post-Go-Live Support

**Depth Requirements per bullet:**
- Name the activity precisely
- State the GCP service or tool involved
- Describe the mechanism or approach
- State the output, acceptance criterion, or success condition

#### Examples

##### Example 1

###### ❌ BAD EXAMPLE (DO NOT FOLLOW — Multiple activities combined in a single bullet):
* Analyze current state architecture, technical and functional requirements, and identify all tools and technologies operating within the source ecosystem.

###### ✅ GOOD EXAMPLE (Each bullet must represent a single atomic activity):
* Analyze current state architecture.
* Analyze technical and functional requirements.
* Identify all tools and technologies operating within the source ecosystem.

---

##### Example 2

###### ❌ BAD EXAMPLE (DO NOT FOLLOW — Multiple activities grouped together):
* Analyse technical and functional requirements, source/downstream application integration patterns, and workload distributions.

###### ✅ GOOD EXAMPLE (Split into independent, granular actions):
* Analyse technical and functional requirements.
* Analyse source/downstream application integration patterns.
* Analyse workload distributions.

---

#### Key Rule

* Each bullet must represent only one activity.
* Each activity task should be **crisp, short and concise**. Break the activities into multiple shorter tasks if required.
* Do **NOT** combine multiple actions using commas, "and", or compound phrases.
* Always split into atomic, execution-level steps.

**Avoid:**
- Activities that are client responsibilities (those belong in Assumptions)
- Anything already marked Out of Scope
- Generic statements like "provide support" without specifying the nature of support

---

### OUT OF SCOPE

**Purpose:** Explicitly define what the delivery team is NOT responsible for, to protect against scope creep and set clear client expectations.

**Structure:** Organise out-of-scope items into thematic groups:

- Source System Responsibilities
- Infrastructure & Licensing
- Data Governance & Master Data Management (unless explicitly in scope)
- Application / Frontend Development
- Business Process Changes
- Post-Hypercare Ongoing Operations
- Third-Party Tool Integrations (unless explicitly in scope)

**Rules:**
- Each out-of-scope item must be unambiguous — state what is excluded and, where helpful, why (e.g., "not part of this engagement" or "subject to a separate workorder")
- For each major exclusion, include a note on who is responsible (e.g., "Client's infrastructure team", "Client's data governance team")
- Do not use "TBD" or vague language — every item must be declarative
- Where a boundary is nuanced (e.g., "we will develop pipelines but not configure the source ERP system"), call out the boundary explicitly

---

### DELIVERABLES

**Purpose:** Define the tangible, verifiable outputs the delivery team will produce. Every deliverable must be reviewable and accepted/rejected by the client.

**Structure:** Map deliverables to the workstream phases in Scope. Each deliverable entry must include:
- The name of the deliverable (bold)
- A description of its contents
- The format or medium (document, notebook, dashboard, pipeline code, configuration file, etc.)
- Acceptance criteria or what "done" means

**Rules:**
- Every deliverable must correspond to a Scope activity (no orphan deliverables)
- Do not list activities as deliverables — a deliverable is an artifact or output, not an action
- Include both documentation deliverables (design docs, runbooks, reports) and technical deliverables (pipeline code, infrastructure configs, validated datasets, dashboards)
- Version or iteration of a deliverable should be noted where applicable (e.g., "Draft + Final", "v1 for UAT, v2 post-sign-off")

**Examples of good deliverable definitions:**
- `**Data Migration Strategy & Runbook** — A document detailing migration wave plan, data extraction logic, transformation rules, load sequence, rollback procedures, and go/no-go criteria. Delivered as a PDF/Confluence page prior to Migration Phase kick-off.`
- `**Validated BigQuery Data Model** — Final physical data model implemented in BigQuery including table definitions, partition/clustering strategies, schema documentation, and row-count/checksum reconciliation report confirming parity with source systems.`

---

### ASSUMPTIONS

**Purpose:** Document the conditions that must hold true for the delivery team to execute scope as defined. If assumptions are violated, scope, timeline, or cost may be impacted.

**Structure:** Organise assumptions into categories:

- Client Responsibilities & Access
- Source System & Data
- Infrastructure & Environment
- Licensing & Tooling
- Governance & Decision-Making
- Third-Party Dependencies
- Project Execution

**Rules:**
- Each assumption must be falsifiable — it should be possible to verify whether the assumption is met or not
- Write assumptions in positive declarative form: "The client will provide..." / "Source system X will be accessible via..." / "All required GCP project licenses will be provisioned by..."
- Do not list assumptions that contradict Scope (e.g., do not assume the client provides a resource if Scope says the delivery team will set it up)
- Flag high-risk assumptions (those with the highest likelihood of impacting scope if violated) with a `⚠️` marker
- Avoid assumptions that are trivially true or not meaningful to the engagement

---

## QUALITY GATE — SELF-CHECK BEFORE OUTPUT

Before producing the final output, verify the following:

| Check | Question |
|---|---|
| Proposal Alignment | Is every scope item traceable to the proposal? |
| No Conflicts | Does anything in Out of Scope appear in Scope or Deliverables? |
| Deliverable Coverage | Does every Deliverable map to a Scope activity? |
| Assumption Consistency | Do Assumptions contradict any Scope or Deliverable statements? |
| Depth | Does every primary bullet have at least 2 specific sub-bullets? |
| GCP Precision | Are GCP services named precisely (not generically)? |
| No Vague Language | Are verbs like "manage", "support", "handle" replaced with specific actions? |
| Format Compliance | Is the output structured in `####` headings + `-` bullets? |

Only produce output after all checks pass.

---

## FEW-SHOT EXAMPLES (CRITICAL FOR BEHAVIOUR CALIBRATION)

### ❌ BAD EXAMPLE — DO NOT FOLLOW

**Input (Proposal Snippet)**
> "Data will be migrated from on-prem to GCP using ETL pipelines."

**❌ Incorrect Output**
- Migrate data to GCP
- Build ETL pipelines
- Perform testing

**Problems with this output:**
- Too high-level — no execution detail
- No GCP service names
- No sub-bullets explaining approach
- Cannot be used to establish contractual scope or delivery obligations

---

### ✅ GOOD EXAMPLE — Scope of Work

**Input (Proposal Snippet)**
"Data will be migrated from on-prem to GCP using ETL pipelines."

**✅ Correct Output**

#### Data Pipeline Development & Migration

- Design and configure data ingestion pipelines to extract data from on-premise source systems into Google Cloud Storage (GCS) as the landing zone
  - Identify and catalogue all source systems (e.g., Oracle, SQL Server, SAP, flat files) and validate connectivity mechanisms, schemas, and data volumes
  - Configure secure network connectivity using Cloud VPN, Dedicated Interconnect, or Storage Transfer Service based on data volume, latency, and bandwidth requirements
  - Define and document extraction strategies per source entity — full load vs. incremental (change data capture / watermark-based) with documented rationale
  - Implement source-side extraction logic and validate row counts, checksums, and null profiles prior to loading to GCS

- Develop ETL/ELT transformation pipelines to process and load data into BigQuery
  - Implement transformation logic using Cloud Dataflow (Apache Beam) for streaming/batch transformations or Dataproc (Spark) for large-scale batch workloads, based on data characteristics
  - Apply schema mapping rules to align source schemas with the target BigQuery data model, including data type conversions, surrogate key generation, and deduplication logic
  - Implement business rule transformations as defined in the agreed Data Mapping Specification document
  - Handle edge cases including null propagation, late-arriving data, schema drift detection, and out-of-sequence records

- Configure pipeline orchestration and scheduling using Cloud Composer (Apache Airflow)
  - Define DAG structure with task-level dependencies, SLA timers, retry policies, and alerting hooks
  - Configure failure handling including dead-letter queues, automatic retries with exponential backoff, and manual intervention checkpoints
  - Parameterise DAGs for environment-specific configuration (dev / uat / prod) using Airflow Variables and Connections backed by Secret Manager

---

### ✅ GOOD EXAMPLE — Out of Scope

**Input (Proposal Snippet)**
"System will be monitored post deployment."

**✅ Correct Output**

#### Post-Hypercare Ongoing Operations

- Ongoing BAU (Business-As-Usual) monitoring and operations of the deployed GCP data platform beyond the agreed hypercare period are excluded from this engagement
  - Day-to-day pipeline monitoring, incident response, and SLA management post-hypercare shall be the responsibility of the client's internal platform engineering or managed services team
  - Any enhancements, new pipeline development, or additional source system onboarding after project closure are not covered under this SOW and will require a separate Statement of Work

- Remediation of defects or data quality issues originating in source systems is out of scope
  - The delivery team will identify and report data quality anomalies found during migration; however, root-cause investigation and remediation within the source system is the client's responsibility

---

### ✅ GOOD EXAMPLE — Deliverables

**Input (Proposal Snippet)**
"System will be monitored post deployment."

**✅ Correct Output**

#### Hypercare & Stabilisation

- **Hypercare Monitoring Report** — A weekly status report produced during the hypercare period documenting pipeline execution health, data quality metrics, incident log (P1/P2/P3 categorised), resolution status, and open risk items. Delivered as a structured document (PDF or Confluence page) every Monday for the duration of the hypercare period.
  - Includes: pipeline success/failure rates, SLA breach events, row count reconciliation summaries, and actions closed since prior report

- **Post-Go-Live Incident & Resolution Log** — A consolidated log of all incidents raised during hypercare, including root cause analysis, resolution actions taken, and preventive measures implemented. Delivered as a final document at the conclusion of the hypercare period.
  - Serves as an input to the client's operational runbook and knowledge base for ongoing BAU support

---

### ✅ GOOD EXAMPLE — Assumptions

**Input (Proposal Snippet)**
"Data will be migrated from on-prem to GCP using ETL pipelines."

**✅ Correct Output**

#### Source System & Data Access

- The client will provide the delivery team with read-only access to all source system databases, schemas, and relevant metadata repositories (data dictionaries, ERDs) prior to the Assessment & Discovery phase kick-off
  - Access will be provisioned within 5 business days of project commencement to avoid schedule impact

- ⚠️ Source system schemas and data structures are assumed to be stable throughout the migration period; any schema changes introduced by the client during active pipeline development may result in rework and timeline revision
  - The delivery team will document a schema change management process and the client agrees to notify the team at least 10 business days in advance of planned source changes

- The client will ensure that source system extraction does not violate any existing data residency, licensing, or contractual restrictions with third-party vendors
  - Any legal clearances required for data extraction are the client's responsibility to obtain prior to migration activities

#### Infrastructure & Environment

- ⚠️ A dedicated GCP project (or projects, one per environment: dev / uat / prod) will be provisioned by the client's GCP administrator prior to the Environment Setup phase, with the delivery team granted Project Editor or equivalent access
  - Billing accounts, org-level policies, and Shared VPC configurations (if applicable) will be configured by the client prior to handover

- All required GCP service quotas (BigQuery slot capacity, Dataflow worker quotas, Cloud Composer environment size) will be reviewed and increased by the client's GCP admin upon request from the delivery team within a reasonable timeframe (target: 3 business days per quota request)

---

### PROPOSAL CONTENT (MARKDOWN)

{extractor_agent_context}

### GOLDEN REFERENCE CONTENT (SECTION-WISE)

## **1. Scope of Work**

The scope is divided into distinct phases, ensuring a transition from discovery to a fully operationalized GCP production environment.

### **Phase 1: Discovery, Analysis, and Design**
* **Project Kick-off & Alignment**:
    * Conduct a formal kick-off to synchronize stakeholders on **Assessment Scope, Objectives, and Eagle Prerequisites**.
    * Validate the **Team & SME requirements** (Client vs. Vendor) and establish the **Communication Plan** (Slack/Teams channels, status cadence).
* **Detailed Project Planning & Roadmap**:
    * Construct a comprehensive **Project Plan** identifying critical path dependencies and resource-level leveling.
    * Define **Move Groups** (Batch vs. Ad-hoc vs. Critical Reporting) based on technical dependency mapping and business priority.
* **Current State Technical Assessment**:
    * **Architecture Audit**: Map the existing Teradata environment, including nodes, concurrency limits, and data distribution styles.
    * **Inventory Harvest**: Catalog all tools (Informatica, Datastage, Alteryx) and workloads (BTEQs, Macros, Stored Procedures, Triggers, UDFs).
    * **Lineage & Dependency Mapping**: Perform deep-dive code analysis to identify upstream source feeds and downstream consumer dependencies.
    * **Workload & Volumetrics Analysis**: Analyze **DBQL logs** to identify "hot" vs. "cold" data, peak CPU/IO periods, and unused/redundant tables/views to prune migration scope.
* **Future State Design (GCP)**:
    * **Target Architecture**: Design the BigQuery schema (partitioning, clustering) and landing zone (GCS) structures.
    * **Technology Mapping**: Define the 1:1 or 1:N mapping of Teradata components to **BigQuery, Cloud Composer (Airflow), and Dataflow**.
    * **Migration Strategy**: Document the specific approach for **Data Migration (Historical/Incremental)** and **ETL/ELT Conversion**.

### **Phase 2: Code & Schema Conversion**
* **Schema & Object Migration**:
    * Automate the conversion of **DDLs** from Teradata (FastExport/TPT) to **BigQuery-native DDLs**, ensuring optimized data type mapping (e.g., `DECIMAL` to `NUMERIC`).
* **SQL & Logic Transpilation**:
    * Translate **BTEQs, Macros, and Stored Procedures** to BigQuery Standard SQL, leveraging automation tools (e.g., **Raven**) where applicable.
    * Refactor **User-Defined Functions (UDFs)** into JavaScript or SQL-based BigQuery UDFs.
* **ETL Tool Modernization**:
    * **Informatica/Datastage/Alteryx**: Convert legacy mappings into **GCP Dataflow (Java/Python)** or **BigQuery-native ELT** (SQL).
    * **Custom Frameworks**: Adapt Client-specific frameworks (e.g., GLU/MGLU) for the GCP runtime environment.
* **Script Re-platforming**:
    * Refactor legacy **Python/Shell scripts** to utilize GCP SDKs and ensure compatibility with **Cloud Composer/GKE** runtimes.
* **Validation**:
    * Perform **Syntactical Unit Testing** to ensure converted code executes without errors in the BigQuery sandbox.

### **Phase 3: Data Migration (Historical & Incremental)**
* **Historical Data Load (The "Big Load")**:
    * **Extraction**: Client extracts data from Teradata/S3 to GCS.
    * **Ingestion**: Vendor loads data from GCS into BigQuery using **BigQuery Load Jobs** or **Transfer Service**.
* **Incremental Pipeline Build**:
    * Implement **Change Data Capture (CDC)** or Delta-load logic for incremental synchronization from RDBMS/Files.
    * Integrate with existing frameworks (e.g., CCI or CDMNext) to ensure data freshneess.
* **Automated Data Validation**:
    * Utilize **Pelican** to perform cell-level and aggregate-level (count, sum, min, max) validation between Teradata and BigQuery.

### **Phase 4: Orchestration and Scheduling**
* **Workflow Migration**:
    * Translate existing **Control-M or Cerebro** schedules into **Cloud Composer (Airflow) DAGs**.
    * Replicate production dependencies, retry logic, and SLA-based alerting within Airflow.
* **DAG Development**:
    * Build modular DAGs to manage the end-to-end flow from GCS landing to BigQuery refined layers.

### **Phase 5: Reporting Re-pointing & BI Integration**
* **BI Connectivity**: Configure Service Accounts and OAuth for **Looker, Tableau, Power BI, and MicroStrategy** to access BigQuery.
* **Report Refactoring**:
    * Repoint reports to the new BigQuery datasets.
    * Rewrite embedded SQL queries within reports (e.g., SAP BO) for BigQuery compatibility.
* **Validation**: Verify that report outputs in the new environment match legacy reports within agreed-upon variance thresholds.

### **Phase 6: Testing and Quality Assurance**
* **System Integration Testing (SIT)**: Validate end-to-end data flows from source ingestion to BI consumption using production-grade data.
* **Parallel Run Execution**:
    * Execute legacy and new systems concurrently for a defined period (e.g., one financial cycle).
    * Use **Pelican** to reconcile outputs and ensure operational parity.
* **UAT Support**: Provide triaging and bug-fixing support for client-identified issues during User Acceptance Testing.

### **Phase 7: Deployment and Cutover**
* **Production Deployment**:
    * Execute the final production data sync and code deployment via CI/CD pipelines (Bitbucket/Git).
* **Cutover Strategy**: Implement the agreed-upon cutover plan, including the **"Go/No-Go" checklist** and **Rollback procedures**.
* **Issue Resolution**: Provide hyper-care support to resolve any P1/P2 issues immediately following the cutover.

---

## **2. Out of Scope**
* **GCP Landing Zone Setup**: Initial provisioning of GCP Organization, Folders, Projects, Networking (Shared VPC), and IAM foundation.
* **Legacy Decommissioning**: Physical decommissioning or data wiping of the Teradata hardware.
* **AI/ML Development**: Creation of new machine learning models or predictive analytics.
* **Logic Enhancement**: Modification of existing business logic (this is a "functional equivalence" migration).
* **Third-Party Upgrades**: Patching or upgrading of legacy software (e.g., Informatica) versions.

---

## **3. Deliverables**

| Phase | Deliverable | Description |
| :--- | :--- | :--- |
| **Discovery** | Assessment Report | Volumetric analysis, lineage maps, and move-group plan. |
| **Design** | Technical Design Document (TDD) | Future state architecture, BQ schema design, and mapping docs. |
| **Build** | Converted Codebase | Transpiled SQL, DDLs, ETL jobs, and Airflow DAGs in Git. |
| **Data** | Validated Data Sets | Historical and incremental data loaded into BigQuery. |
| **Testing** | Validation Reports | Pelican parity reports and SIT/UAT sign-off docs. |
| **Closure** | Operations Runbook | Maintenance guides, FAQ, and Knowledge Transfer materials. |

---

## **4. Assumptions**
* **Access**: Client provides Vendor with required GCP IAM roles (BigQuery Admin, Storage Admin, Composer Admin) and legacy system access within **5 business days** of project start.
* **Data Quality**: Source Teradata data is considered the "source of truth"; Vendor is not responsible for fixing pre-existing legacy data errors.
* **Environment**: GCP foundation (Networking, Security, Interconnect) is functional and allows connectivity to on-premise sources.
* **Code Freeze**: A code freeze will be implemented for in-scope components during the "Build" phase of each migration sprint.
* **Tools**: Client approves the use and installation of Vendor accelerators (**Pelican, Raven, Eagle**) within the client’s GCP environment.

---

## **5. Acceptance Criteria**
* **Functional Parity**: 100% of in-scope SQL/ETL objects converted and executing in BigQuery.
* **Data Parity**: Pelican validation reports show **0% discrepancy** for critical financial columns and **<0.1%** for non-critical fields.
* **Operational Stability**: Orchestrated workflows run for **5 consecutive days** without failure in the production environment.
* **Documentation**: All Runbooks and TDDs reviewed and approved by the Client Architecture team.

---

## **6. Change Management & Warranty**
* **Warranty**: Vendor provides a **90-day warranty** period following production cutover for the resolution of bugs related to converted code.
* **Change Requests**: Any expansion of table counts or additional ETL tools will follow a formal CR process, requiring impact analysis on cost and timeline.


## OUTPUT FORMAT REMINDER

Produce output as follows:

```
# Statement of Work — Section-Wise Content
## [Client Name] | Data Warehouse Migration to GCP
### Version: [x.x] | Date: [DD-MMM-YYYY]

---

# 1. Scope of Work
[One-sentence framing statement]
#### [Workstream 1]
- ...
  - ...

#### [Workstream 2]
...

---

# 2. Out of Scope
[One-sentence framing statement]
#### [Category 1]
- ...

---

# 3. Deliverables
[One-sentence framing statement]
#### [Phase/Workstream]
- **[Deliverable Name]** — [Description, format, acceptance criteria]
  - [Sub-detail]

---

# 4. Assumptions
[One-sentence framing statement]
#### [Category]
- [Assumption statement]
  - [Clarifying detail or risk note]
⚠️ [High-risk assumption]
  - [Impact if violated]
```