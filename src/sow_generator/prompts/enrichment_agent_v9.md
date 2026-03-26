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

**General Guideline**
- SOW template should be used as a reference and content should be modified as per the proposal content
- The format of the SOW should not be changed, unless directed by GSI or Google
- Ambiguity should be avoided as much as possible that may turn out to be in favor of customer and prove our assumptions false
- As much as possible wherever there is customer dependency and deliverable - There should be some timeline or date associated with it.

## 1\. Executive Summary - Objective and Background

Client is planning to migrate its current Legacy environment along with its associated workloads with the same data model and business logic to a modern data warehouse built on Future State Environment.

**Business Objective & goals:**
Onix proposes to provide its professional services using its migration capabilities, automation tools, technology & subject matter experts to help Client in fulfilling its objectives.

**Client current landscape consists of the following:**

  * **Source Systems** -
  * **Data warehouse built using** -
  * **Data Ingestion Tools used** -
  * **Data Quality Tools used** -
  * **Data Transformation Tools used** -
  * **Orchestrator and Scheduling** -
  * **Reporting Tool** -

-----

## 2\. Scope of Work

To fulfill the service objectives of this engagement, Onix will perform following activities for the In-scope Volumetrics mentioned in appendix a

### 2.1 Discovery, Analysis and Design

**Current state understanding of:**

  * Business Overview (Key Business areas/ Domains/ Line of Business)
  * Current Technical and Data Architecture
  * Source Systems types, frequency, feeds, format and, mechanism
  * Table level lineage
  * Use case priorities and associated database objects
  * Data Ingestion Pipelines/ Patterns/ Volumetrics
  * Data Quality rules/ policies, if any
  * Data flow between different data layers
  * Environment landscape (QA/ Dev/ UAT/ Prod)
  * Data Transformation Pipelines/ Patterns/ Volumetrics
  * Data Security requirements
  * Baseline current pipeline performance
  * Job Orchestration and scheduling
  * Data Consumptions Process/ Patterns/ Feeds
  * Current challenges and, gaps & future expectations
  * Define Testing strategy and associated infrastructure

**Project Design and Planning**

  * Design future state Solution and Technical Architecture
  * Data Pipeline design
  * Orchestration & Scheduling patterns
      * *Note: Existing job orchestration, dependencies and schedule will be implemented as-is*

  * Migration Planning

    * Migration strategy (Milestone and Approach)
    * Project Plan (Sprint/ Release plan)
    * Testing and cutover strategy

Once Onix provides the final migration design and plan, Client is responsible to provide sign-off within 2 Weeks of plan and design document delivery.

### 2.2 Google Cloud Foundation Setup - Please select the right option between 1 or 2 else say “Not Applicable”

**Option 1: If Onix has to setup end to end foundation**

  * GCP Foundation Setup
    * Platform Set-up on GCP platform
        * Identity Management & Access Control
        * Organization Hierarchy
        * Networking
        * Logging, Auditing & Monitoring
        * Security
        * Billing Account setup
        * Infrastructure as Code
        * Naming Standards and Conventions

    * Data Lake Foundation Set-up

  * Platform Readiness
    * Gap analysis of current GCP services in use and required service for project execution
    * Enable GCP service required for Project
    * Collaborate with Client team for:
      * Creating Projects
      * Setting up IAM policies for Onix team

  * Pelican Setup
    * Pelican Setup: Onix IP Pelican Product setup on on-premises or cloud cluster for data validation between the Legacy Environment and BigQuery

### 2.3 Historical Data Migration - Please modify the content as per requirement

One time historical data migration from Legacy Environment to Google Cloud Platform

  * **Data Extraction** \* Onix or Customer or GSI to extract correct(or relevant) historical data from Legacy environment for data loading using \<abcde\> or likewise.
  * **Data Transfer**
      * Onix or Customer or GSI to transfer the historical data from legacy environment to GCP using gsutil or likewise
  * **Data Loading**
      * Onix or Customer or GSI to load historical data from GCS to BigQuery Tables

*If Customer is providing data in Cloud bucket; say: We should also mention about regular data sync-up strategy from legacy to cloud until cutover completion.*

### 2.4 Code Conversion

**Source System Integration**

  * Data Ingestion \<Choose one of the options in Project SOW\>
      * **Option 1:** Repoint existing ETL data ingestion jobs to make it GCP compatible
      * **Option 2:** Convert existing data ingestion jobs to GCP native
      * **Option 3:** Setup Data Ingestion framework for source integration
      * **Option 4:** Custom Approach

  * Data Transformation and load

    * Conversion of current Tables and Views Data Definition Languages(DDLs) to GCP BigQuery
    * Conversion of existing Data transformation/ processing jobs as-is to future state technology stack (refer: Architecture diagram)
    * Converted or migrated code will have the same business logic as the Legacy Environment. Data-type and schemas will be similar or compatible to the Legacy Environment production environment.

  * Orchestration and Scheduling \<Choose one of the options in Project SOW\>

    * **Option 1:** Setup Orchestration and Scheduling for converted workloads using GCP Cloud Composer. Cloud scheduler will follow the same schedule for jobs as in the Legacy Environment production environment.
    * **Option 2:** Setup Orchestration and Scheduling using enterprise scheduler and GCP Cloud Composer. Cloud scheduler will follow the same schedule for jobs as in the Legacy Environment production environment.
    * **Option 3:** Custom

  * Report Repointing [If applicable]

    * Onix will be responsible to do report repointing. Reporting Tool will be “abcde”
    * XX Tool configuration connection string modification of reports/queries to BigQuery environment
    * Onix will not be doing any code and report logic changes
    * Schema refresh from Cloud Data warehouse post repointing

### 2.5 Testing

**Development Testing**

  * Onix will conduct Testing in dev environment

**System testing**

  * Onix will conduct system testing in QA/UAT environment with production grade data provided by the Client OR planned GCP Production environment
  * One Successful Historical data validation of a set period to be defined during testing strategy
  * Pipeline Validation of the converted workflow, test data to be provided by customer
  * Two Successful Incremental Data validation Approach using Onix tool “Pelican” of data pipelines at consumption layer
  * Testing will be done using Onix tool “Pelican”

**User Acceptance Testing**

  * Client team will perform and complete the User Acceptance Testing(UAT) within 5 business days after delivery by Onix

**Performance validation (Add only if Estimated)**

  * Compare performance of queries/stored procedures between existing and future state implementation
  * Stress / Peak Load Testing is out of Scope

**Report Validation (Re-Pointing)**

  * Report Operational Testing (Estimated based number of reports in Repointing)
    * Test to ensure the reports are able to connect to BigQuery successfully in Production Environment
    * Schema refresh in reporting tool from Cloud Data warehouse for operational running of reports
    * XX reports operational validation with legacy reports will be done by DM.
    * YY Report Data validation with legacy will be done by customer

  * Report Data and Performance Validation (Needs to be Estimated based on number of Reports/Complexity)
    * Benchmark performance Report against Legacy and Cloud data, tune the report or data warehouse
    * Compare Report Metrics Data against against Legacy and Cloud, identify issues for migration team to identity anomalies
  * Report Load Testing (Needs to be Estimated based on number of times executed)
    * One Time Run Reports load testing with extrapolated users and reports to determine how many slots are required during holiday / peak season. Automated Load testing functionality/capability should be available in the BI Tool for executing the load testing.

### 2.6 Production Deployment - Please select the right option between 1 or 2

**Option 1: Client will Deploy, Onix will support**

  * Onix is responsible to deploy code onto lower environment
  * Client is responsible for production deployment
    * Onix team will provide required support in investigation of issues and fixes for defects if any in Onix developed code.

**Option 2: Onix will deploy, Client will support**

  * Onix will deploy the converted/ developed code into production environment
    * Client will provide access to the production environment and existing code deployment tools (i.e Bitbucket, GIT, etc)
    * Client will provide walkthrough of current deployment process

### 2.7 Parallel Run in Production [Optional]

  Onix or Client will validate the data between Legacy Environment production environment and Future State production Environment for 2 iterations using Onix’s IP Pelican
  * Legacy Environment production environment and Future State Production environment must be connecting to same source systems
  * Client is responsible for executing Legacy Environment code onto the Legacy Environment production environment
  * **Assumption** - Legacy Environment and Google Cloud Environment will have up and running production environments and both are pointing towards the same source and consuming data.
  * Handshake with Client Operations support team.

### 2.8 Project Handover

  * Knowledge transfer sessions for 2 weeks, after production deployment, covering:
    * Scope performed, tools and technology walkthrough
    * Design documentation
    * Reverse KT and shadow support as applicable
  * Provide runbooks(limited to scope performed by Onix)
  * DM team will not be responsible to fill-in the SLA/source team/downstream consumers details. That has to be provided/added by the existing operations team only.
  * Customer will ensure Operation Support teams available from 2 weeks prior of UAT till Go-Live for KT and Cloud Data Warehouse Application/Infrastructure Operation Setup

### 2.9 Hypercare Warranty Support

Onix will provide 4 weeks of warranty support (post production deployment) and will cover bugs/ error related to the following (limited to scope performed by Onix)

  * Future State Environment pipeline/ Jobs failures
  * Data Mismatch, if any
  * Converted codes and scripts
  * Orchestration and Scheduling failures

**Please note:**

  * Clients will be responsible for 24/7 monitoring and engaging Onix in case of failures (even during the 4 weeks of hypercare).
  * Client internal support team will be fully responsible to support the workstream after 4 weeks of warranty support.
  * Clients can choose to engage for additional managed support services, which will be above and beyond this Statement of Work and will be estimated separately.

-----

## 3\. Out of Scope - Please modify as per Scope of Work

**General**

  * Any report related activities such as Migration/ Repointing/ Enhancement of reports
  * Production deployment
  * Encryption or Decryption of any data
  * Development / Enhancement of any AI/ ML models
  * Performance testing
  * Any software upgrades or patching
  * Any changes and/ or defect fixing of Legacy environment codes
  * User Onboarding
  * L1, L2, L3 Managed service support
  * Integration with 3rd party applications other than mentioned in scope
  * Decommissioning of any existing environment
  * PII Data Implementation (Tagging, Encryption, etc)

**Project Specific**

  * TBD

-----

## 4\. Client Dependencies - Please refine the statements as per project requirements

**General Dependencies**

  * Client will be responsible to provide the following to the Onix team for Discovery, Analysis and design at project start:

      * Necessary Security approval and access rights (ID, LDAP, etc) for Onix team
      * Access to the confluence or similar portal
      * Data/ document related to the in-scope Platforms
        * Design documentation
        * Data Model/ Schema and Lineage
        * Jobs Scheduling, dependencies documentation
        * Business rules, transformation documents
        * Key NFR documents
      * Walkthrough of current state environment
        * Business Overview and priorities
        * Data Model/ Schema and Lineage
        * Source Systems/ Data Ingestion patterns
        * Data Transformation patterns
        * End to end pipeline run
        * Orchestration and Scheduling
        * Google Cloud Footprints, if any
        * Special case scenarios
        * Consumptions patterns
        * Deployment process and Standard operating procedure
      * *Please note - Onix team will provide detailed discovery topics and plan at the project kick-off*

  * Client will be responsible to provide the following to the Onix team before 1 week before the start of 1st migration Wave/ Sprint:

      * Access to the Legacy environment
      * Access to the in-scope Source systems
      * All the in-scope Codes / Scripts / DDLs etc
      * Necessary security approval and access rights for Onix accelerators (Pelican)
      * Infrastructure (VM) for the Onix Pelican tool installation
      * Existing code deployment tools (i.e Bitbucket, GIT, etc)
      * Resolution to issues and coordination matters related to any other vendor/business partner associated with the project
      * Point of contacts (technical and functional SME) who can be contacted throughout the project duration, as and when required
      * Any software (Libraries, ODBC Drivers, Connectors, etc.) required for this engagement
      * Provisioning of the identical Target systems for RDBMS (new instances of Oracle/SQL Server/MySQL) to facilitate parallel execution
    * Once Onix provide the final migration design and plan, Client is responsible to provide sign-off within 2 Weeks
    * If any other dependencies are identified during project execution, client will fulfill such dependencies within the mutually agreed timeline
    * After the mentioned timeline for client sign off, the deliverable will be considered deemed approved
    * Client will run existing Legacy environment code on same datasets in the Legacy environment for data validation purpose

**Project Specific topics**

  * Google Cloud Foundation is already setup and access to the same will be provided to Onix team at the project kickoff
  * Historical Data will be selected option
  * Access to the Future State production environment

-----

## 5\. Assumptions

**General Assumptions**

  * Migration strategy will be lift and shift migration, hence, legacy environment along with its associated workloads will be migrated to Future State Environment with the same data model and business logic
  * **Onix IP Pelican**
      * Pelican will be installed for the duration of this project only
      * Prerequisite mentioned in the Appendix D will be provided by client before project start
      * Pelican will be used to validate data only between Legacy environment and Future state environment
      * Infrastructure (VM) for the Onix Pelican tool installation will be provided by Client and cost associated with the environment will be borne by Client
      * Data validation services for additional other sources can be handled through a change request
  * Client team will freeze the code for mutually agreed period of Legacy environment covering all end-to-end pipeline, including data ingestion feeds, any ETL/ELT designs/code and export / data feeds before the start of each migration sprints
    * Any changes in the code after ‘code freeze period’ and ‘SIT phase’ will be handled through a Change Request
  * Onix will provide 4 weeks of support post deployment of each release
    * Onix team will conduct knowledge transfer session and handover the runbooks to Client team for that particular release
    * Client team will perform monitoring of jobs/ pipelines and identified issues will raised to Onix team
    * Onix will fix the raised issues based on priorities/ criticality defined by Client
  * Client team will setup the alerting and monitoring for the production environment based on Client enterprise standard
  * Client is responsible for monitoring the production environment
  * Client is responsible for setting up and handling CI/CD for this project

**Project Specific Assumptions**

  * Deployment into production environment will be done by Client team
  * The Future State Environment foundation and projects are already in place and any gaps identified by Onix team during project execution will be filled by Client team

-----

## 6\. Deliverables

| Particulars | Deliverables |
| :--- | :--- |
| **Discovery, Analysis and Design** | Migration planning and documentation |
| | Migration strategy (Milestone and Approach) |
| | Migration inventory (database objects, code, use cases) |
| | Sprint Plan/ Release Plan |
| | Cutover plan |
| | Communication plan including Project governance and cadence |
| | Solution Architecture diagram (Future State environment) |
| | Technical design document |
| | Testing Strategy |
| **Google Cloud Foundation Setup** | GCP Infrastructure Design Document |
| | Terraform Infrastructure Automation Scripts |
| | CI/CD Pipeline for GCP Infra Provisioning and Application Code Deployment |
| | Execution of the Terraform Scripts to build and Configure GCP Infrastructure. |
| **Historical Data Migration** | Historical Migration Scripts |
| | One Time execution of Historical Migration Scripts to load data into Production Bigquery Tables followed by Data Validation. |
| **Code Conversion** | Legacy Environment Tables/ Views DDLs converted to Future State environment |
| | Incremental data pipelines |
| | Legacy Environment code converted to Future State Environment |
| | Orchestrated and scheduled jobs |
| **Testing** | SIT test results |
| | Pelican report - Data Validation |
| **Production Deployment** | All the converted code and workloads deployed onto Future State production environment |
| **Parallel Run** | Parallel run test reports |
| **Project Handover** | Knowledge transfer sessions |
| | Runbooks |
| **Hypercare Warranty Support** | Hypercare warranty support(4 weeks) and Resolution to identified Bugs and errors (limited to the scope performed by Onix) |


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