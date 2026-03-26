# Opportunity

The Client, Bell Canada, is embarking on Phase 2 of its comprehensive Hadoop transformation journey, intended to seamlessly migrate active, mission-critical workloads from a legacy on-premise Hadoop ecosystem to Google Cloud Platform (GCP).
This crucial modernization initiative is primarily focused on rigorously refactoring the existing Extract, Transform, and Load (ETL) and orchestration stack, validating massive datasets dynamically at scale, and establishing robust frameworks to enable seamless downstream data consumption across the organization.
By executing a transition to a fully managed, enterprise-grade GCP architecture that utilizes highly scalable native services such as BigQuery, Dataproc, and Cloud Composer, the Client strategically aims to substantially reduce accumulated technical debt.
Furthermore, this strategic migration will ensure equal or superior performance parity compared to the legacy environment, ultimately empowering the Client's Business Intelligence (BI) team with fully self-sufficient, modern reporting capabilities.
To facilitate this complex transformational program, the Provider, Onix, shall strategically leverage its proprietary suite of automation accelerators.
These tailored tools are meticulously designed to guarantee a highly secure, mathematically accurate, and significantly accelerated migration execution process from initial discovery through final deployment.
#

# Solution Overview

### Migration Approach The Provider shall execute and deliver the engagement utilizing an industry-standard Agile methodology.
The project implementation will be systematically segmented into modular "Move Groups," which represent distinct, logical collections of Hadoop workloads designed to be migrated together.
Project execution will occur throughout strictly time-boxed execution cycles, utilizing iterative sprints lasting between 4 and 6 weeks.
The overall sequence of delivery transitions seamlessly from Initial Discovery and Design, proceeding to rigorous Code Conversion and Historical Data Migration, and is subsequently followed by Integration and Orchestration, comprehensive Validation (Quality Assurance and Parallel runs), Report Repointing, and concluding with a formal Handover phase.
### Technology Mapping (Target State Architecture) The modernization effort actively shifts current operational workloads from an on-premise Hadoop and NetApp ecosystem to a fully managed, scalable Google Cloud stack.
The Provider shall implement the following component replacements:
* **Batch Ingestion:** Implementation of scalable Dataflow to fully replace legacy systems including Sqoop, Kafka, Streamsets, and Apache Spark.
* **ETL/ELT Processing:** Deployment of Serverless Dataproc and BigQuery architectures to replace Apache Spark on Hadoop, Hive, Trino, and Impala pipelines.
* **SQL Query Engine:** Utilization of BigQuery to natively replace existing Hive, Trino, and Impala querying capabilities.
* **Orchestration:** Configuration of Cloud Composer (Airflow) to successfully replace all existing Oozie scheduling and orchestration.
* **Data Storage:** Migration to Cloud Storage (GCS) to natively replace HDFS and NetApp S3 infrastructure, alongside BigQuery to successfully replace Hive Native and External Tables.
* **Reporting & BI:** Retention of the existing MicroStrategy footprint, which shall be thoroughly repointed to BigQuery as the new primary analytical data source.
* **Streaming:** Implementation of robust Kafka and Dataflow streams to seamlessly replace legacy Kafka and Streamsets infrastructure.
* **Monitoring/Visualization:** Active retention and seamless integration of all existing ELK and Grafana instances.
### Automation & Accelerators (Onix Birds Suite) The migration timeline and overall accuracy will be heavily accelerated by deploying the Provider's proprietary automation tooling, designed specifically to validate massive quantities of data with zero data movement required during the core validation phase:
* **Eagle (The Planner):** The Provider will utilize this diagnostic tool to conduct comprehensive architecture assessments, perform detailed lineage extraction, analyze system volumetrics, and logically facilitate Move Group planning.
* **Raven (The Transformer):** This tool shall automate and aggressively optimize the direct translation of underlying code (including ETL frameworks, SQL, and specific Scripts) from their native source languages directly to GCP-native technologies (e.g., automatically converting Hive logic to BigQuery SQL, and transitioning existing Spark logic directly to Dataproc).
* **Pelican (The Validator):** The Provider will perform sophisticated AI-powered, automated data validation and reconciliation.
This includes exhaustive cell-level and row-level comparisons natively executed between the legacy Hadoop data stores and the newly established GCP target stores, executed entirely without requiring cross-environment data movement.
* **Condor (The Transporter):** This specific accelerator shall be extensively utilized to rapidly generate automated, scalable ingestion pipelines operating natively on Dataflow.
### Change Management & Ongoing Sync The Provider and Client shall implement a strict code freeze for all legacy codebase elements associated with upcoming, scheduled Move Groups, explicitly excluding any mutually agreed business-critical operational changes.
Any such business-critical legacy changes introduced by the Client during the freeze will be formally logged, systematically tracked, and subsequently manually retrofitted into the new GCP environment.
Following the post-deployment phase, the Client's internal technical team will formally assume full ownership of making any corresponding, ongoing adjustments to the GCP codebase if the legacy on-premise systems are necessarily altered prior to their final operational sunset.
### Project Governance To ensure total alignment, risk mitigation, and continuous transparency, the engagement includes the following stringent governance routines:
* Conducting formal weekly status reporting and iterative sprint planning sessions.
* Hosting detailed sprint reviews and continuous retrospective meetings at the explicit conclusion of each execution cycle.
* Facilitating dedicated joint steering committee meetings intended for critical path decision-making and continuous risk mitigation strategy deployment.
#

# Activities

The Provider shall perform the following specific tasks and activities throughout the execution of this engagement:
* **Project Initiation & Discovery:** The Provider shall conduct a formal project kickoff, precisely validate all volumetrics provided by the Client, systematically establish necessary technical access credentials, and comprehensively finalize the formal Move Group sprint plan.
* **Environment Preparation:** The Provider will thoroughly validate its network access to the source Hadoop and NetApp ecosystems, and subsequently provision the targeted GCP environments along with the necessary Foundation configurations.
* **Source System Integration:** The Provider shall design, build, and set up continuous incremental data ingestion pipelines routing from established legacy source systems—including robust RDBMS architectures, flat files, and APIs—directly into the target GCP environment.
* **Code Conversion & Refactoring:**
* The Provider shall carefully convert in-scope database structural objects, encompassing all necessary tables and views, directly to robust BigQuery-compatible schemas and operational formats.
* The Provider will programmatically convert and refactor legacy native scripts (encompassing legacy Sqoop imports, Scala routines, Spark SQL frameworks, Hive/Impala SQL scripts, and deep Trino queries) directly into highly scalable GCP-native services such as Dataproc, Dataflow, and BigQuery logic.
* The Provider will effectively reutilize existing non-SQL Spark workloads by successfully shifting their execution execution directly to Dataproc or functionally equivalent GCP analytical frameworks.
* The Provider will systematically migrate and strategically reuse the existing legacy Python, Java, and Shell scripts natively within GCP wherever technically applicable.
* **Historical Data Migration:** The Provider shall orchestrate and safely execute a comprehensive, one-time migration of existing historical data assets spanning directly from the legacy Hadoop (HDFS/S3) environments over to the target GCP environment (specifically optimizing for Cloud Storage and BigQuery).
* **Orchestration & Scheduling:** The Provider will design and fundamentally implement robust execution orchestration mechanisms for all successfully migrated workloads utilizing Cloud Composer (Airflow).
Resulting schedulers shall be deeply engineered to accurately mirror the exact cadence and dependency chains of the existing Oozie schedules currently operating in the legacy on-premise environment.
* **End-to-End Pipeline Testing & Data Validation:** The Provider shall conduct rigorous technical testing phases encompassing isolated unit testing of all newly converted workloads, exhaustive historical data parity validation, and intensive concurrent parallel testing cycles to ensure absolute operational integrity.
* **Report Repointing & Enablement:**
* The Provider shall carefully repoint designated MicroStrategy reports from their original legacy Hadoop sources to target BigQuery endpoints, scaling this effort specifically targeting the “wireline access” project or structurally similar initiatives.
* The Provider shall conduct deeply thorough enablement sessions meticulously designed to walk the Client's internal BI team through the entirety of the system repointing process, comprehensively covering core administrative best practices and successfully outlining common situational reporting scenarios.
* **Support & Handover:** The Provider shall proactively deliver comprehensive User Acceptance Testing (UAT) deployment support, enforce a robust 4-week post-deployment defect warranty period, and seamlessly furnish all necessary structural technical documentation alongside dedicated platform knowledge transfer sessions.
#

# Deliverables

The Provider shall produce and systematically deliver the following specific artifacts during the engagement:
- Formal Project Kickoff Presentation and fully finalized Sprint Plan tracking document
- Quality Assurance (QA) Validated Code base
- Pelican Validation Results delivered as comprehensive, systematic automated reports
- Documentation of Closed Bug Jira(s) resulting from testing cycles, if any are produced
- Production Deployed Code, consisting of fully functional Pipelines and newly repointed MicroStrategy Projects
- Comprehensive Report Validation Report ensuring BI functionality
- Detailed Parallel Run Validation Report
- Systematic Pipeline Execution Runtime Comparison Report strictly measuring legacy Hive PROD metrics against newly established BQ PROD metrics
- MicroStrategy Report Performance Comparison Report specifically analyzing targeted business-critical reports
- Extensive Operational Runbooks, foundational Technical Design Documents (TDDs), and actionable Operational Management Guides
- A Packaged Enablement Kit specifically designed and tailored for the Client's BI team, encompassing operational playbooks, essential QA checklists, and robust validation templates
- Highly reusable architectural utilities, structural enablement frameworks, and scalable validation assets designed to rapidly assist future internal BI repointing efforts
- Formally published database connection templates, detailed dataset structures, and strict naming standards mapping schemas
- Recurring Weekly Project Status Reports effectively capturing current progress sprint, dependencies, risks, and sequential next steps
- A Final Migration Sign-off Document signaling the formal completion of the migration engagement delivery #

# Out of Scope

The following operational activities, technical systems, and professional deliverables are strictly and explicitly out of scope for this SOW:
- Any activity, task, milestone, or technological component not explicitly and purposefully mentioned within this approved Scope of Work document.
- The execution of any active software upgrades, preventative maintenance, or system patching upon the legacy on-premise infrastructure environments.
- The systematic repointing or alteration of any MicroStrategy projects other than the explicitly designated “wireline access” reporting project or those strictly identical to it in structure.
- The architectural design, structural formulation, or functional development of any net-new business intelligence reports or net-new dashboard functionality.
- The operational reconfiguration or structural modification of any linked, deeply integrated, or dependent child reports within the greater MicroStrategy ecosystem.
- Implementing any core architectural, underlying structural code, or configuration changes within the existing legacy source environments.
- Broad corporate end-user onboarding, credentialing, and direct organizational enablement beyond the strictly defined internal BI team knowledge transfer sessions.
- The physical hardware decommissioning, architectural teardown, and ultimate cutover of the existing legacy on-premise systems and underlying environments.
- Any third-party software licensing acquisition, subscription management, structural auditing, or associated corporate procurement efforts.
- Advanced data cleansing, extensive deduplication routines, or complex structural data quality remediation of the legacy source data either prior to or actively during the migration transition.
- The explicit provision of measurable Service Level Agreement (SLA) operational guarantees mapping to the availability, latency, or underlying performance of external legacy upstream source systems.
#

# Limitations

The Provider's successful execution and delivery of this stated SOW engagement are explicitly subject to the following technical constraints, environmental factors, and operational limitations:
- The overall project migration velocity and sprint timeline adherence are inherently strictly dependent upon the continued operational stability, systemic availability, and broad performance of the Client's legacy Hadoop environment.
- The automated data validation processes functionally performed by the Pelican toolset are categorically explicitly limited solely to the specific data types, structural formatting, and data structures organically supported natively by the intended target GCP architectural technologies.
- The projected project execution timelines inherently assume absolutely no artificial system throttling, API rate limit caps, or fundamental network bandwidth transmission constraints will be actively enforced by legacy source IT systems during the critical historical data extraction and transfer phases.
- Any outlined performance parity or latency improvement guarantees categorically and explicitly exclude fundamentally poorly optimized, legacy queries that would mandatorily require comprehensive functional architectural redesigns falling far outside the boundaries of the agreed-upon codebase refactoring scope.
#

# Success Criteria

The overall engagement will be deemed successful and structurally complete upon the verified achievement of the following distinct operational criteria:
* **Data Validation:** The Provider successfully establishes strictly verifiable data parity linking the legacy Hadoop systems to the target BigQuery environment.
Successful total data validation must be conclusively proven and signed off via the Pelican accelerator for both massive historical data loads and all subsequent Day 1 & Day 2 ongoing incremental data loads.
* **Performance Validation:** The newly migrated GCP system must clearly and consistently demonstrate equivalent or definitively superior performance capabilities regarding all mutually designated business-critical dashboards.
The total execution pipeline runtime in GCP must perform measurably better than, or strictly at parity with, the baselined legacy Hive pipeline runtimes.
Furthermore, total report and dashboard refresh lag times must directly meet or explicitly exceed the latency baselines currently established on the Hive ecosystem.
* **Reporting Parity:** Absolute report and dashboard-level structural rendering parity is successfully established, and complete underlying row-and-column data parity is verified against the foundational base tables currently supporting both Business Critical and operationally Relevant reporting elements.
* **Acceptance:** Comprehensive parallel run functional validation reports must be formally reviewed and systematically approved by the Client's designated Technical Subject Matter Experts (SMEs).
Moreover, formal User Acceptance Testing (UAT) sequences must be signed off by authorized internal UAT users.
Any resulting technical deviations or verified minor data mismatches discovered present in the final Pelican validation results must be explicitly reviewed, contextually understood, and approved by the Client’s SMEs prior to progression.
* **Enablement:** The Client’s internal BI reporting team is structurally proven to be totally self-sufficient regarding all future MicroStrategy-to-BigQuery repointing exercises, ultimately demonstrating a reliable 60–70% faster structural repointing turnaround time and establishing a near-zero vendor technical dependency baseline for all remaining, ongoing operational reporting projects.
* **Security Compliance:** The completely deployed target GCP operational environment must formally and rigorously conform to Bell Canada's internal pre-approved security frameworks and rigorous modern Identity and Access Management (IAM) technical standards prior to receiving any authorization for production live deployment.
#

# Technical Assumptions

The proposed architectural solution, project methodology, and estimated delivery timelines are directly based upon the following critical foundational assumptions:
- The primary structural migration strategy will purely utilize a lift-and-shift methodology, actively ensuring absolutely no fundamental functional changes will be made to the underlying business logic or core data models.
- The legacy Hadoop infrastructure footprint and all associated operational source system environments will remain functionally highly stable for the entire active duration of the project; explicitly, no major platform upgrades, major changes, or structural modifications will be independently introduced by the Client.
- The designated Client internal team will diligently perform and effectively conclude User Acceptance Testing (UAT) phases within exactly 5 business days following the delivery of each iterative sprint module by the Provider's team.
- The Client will unequivocally remain fully technically and administratively responsible for any business end-user onboarding processes and the establishment of functional integration setups for any specific third-party managed upstream or downstream platform systems touching this scope.
- The required mandatory MicroStrategy repointing activities are explicitly constrained and functionally limited exclusively to the “wireline access” operational project or structurally similar elements; any and all other distinct reporting architectural requirements are strictly and explicitly out of scope for this engagement.
- Any unforeseen complex technical issues, underlying data corruption, or systematic foundational errors existing securely within the legacy environment or source data pipelines carry the inherent potential to significantly delay the project's ultimate delivery timelines.
- Any necessary, discovered, or requested material deviations in project activity tracking, core technology architectural components, or the directly outlined data volumetrics within this scope will mandatorily strictly undergo a formal written Change Request (CR) assessment process before potential adoption.
- The Provider shall proactively deliver the baseline operational Wireline Access repointing project (or a directly structurally equivalent project) strictly functioning as a core foundational reference implementation for the Client to mirror.
- The Client shall aggressively proactively increase and administratively manage GCP tenant quotas and structural pipeline limits to appropriately handle and support the anticipated massive volume of active migration workloads.
- Customer dependencies require that the Client will proactively provide the Provider with the following explicit materials, network accesses, and personnel availability:
- Unrestricted direct access to all in-scope technical tools, requisite foundational technologies, and underlying infrastructure environments fundamentally required to actively execute the migration sequence.
- Comprehensive delivery of all in-scope legacy original source codes, foundational automation scripts, Data Definition Languages (DDLs), and any other applicable underlying dependent software logic (including Sqoop frameworks, Hive/Impala SQL text, Trino queries, Spark jobs, Python processes, Java elements, Shell scripts, etc.).
- Complete operational access to and provision of existing legacy enterprise code deployment tools (e.g., active Bitbucket tenants, structural GIT repositories, etc.).
- Readily available GCP and legacy infrastructure seamlessly accompanied by all necessary security approvals and elevated service account access rights specifically mapped for the Provider's automation accelerators and technical engineering resources, supplied entirely at zero additional cost to the Provider.
- Timely, deep, and comprehensive technical knowledge transfer sessions proactively focusing on the current bespoke Hadoop architecture, complex operational data models, internal scheduling frameworks (such as Oozie), full codebase historical context, and all associated structural business processes as dynamically required.
- The formal assignment of a dedicated, highly responsive internal Bell Canada point of contact (expressly serving as both a technical operational and functional enterprise SME) readily available to rapidly address queries, effectively unblock technical access issues, and provide timely detailed clarifications.
- Immediate operational access to any ancillary enterprise software, physical hardware components, core supporting infrastructure, and functional API interfaces (explicitly including required operational Licenses, system software Libraries, necessary ODBC Drivers, custom data Connectors, etc.) mandatory for the total completion of the engagement scope.
#

# Payment Schedule

- Milestone 1: Project Kickoff and Discovery Sign-off ([X]%)
- Milestone 2: Completion of Environment Setup and Initial Move Group ([X]%)
- Milestone 3: Monthly Sprint Execution (Billed Monthly based on delivered Move Groups)
- Milestone 4: Final UAT Sign-off and Handover ([X]%) #

# Appendix Details

**In-Scope Volumetrics** The Provider and Client agree to the following baselined technical volumetrics which formally govern the comprehensive size and scale of this migration effort:
- Hadoop Instance: 1
- Historical Data Size: 3,798.85 TB
- Tables: 6,850 (External: 6,171 / Managed: 679)
- Views: 381
- SQL & HQL: 1,228
- Shell Scripts: 1,643
- Sqoop Job Scripts: 651
- Streamset: 124
- Scala: 1,094
- Python: 150
- Java: 43
- Oozie Jobs: 2,179
- MicroStrategy Objects: 754 (~20% of total) **Optional / Additional Scope Items** The following supplementary technical and administrative services are presented as explicitly optional scope enhancements and may be formally included subject to separate commercial agreement or a documented Change Request:
- Google Cloud Foundation Service (Optional): Comprehensive holistic project setup and structural organization mapping, implementing a robust Data Platform Foundation (inclusive of highly structured BigQuery datasets and dedicated GCS buckets), configuring a secure Development & Deployment Environment (leveraging Cloud Build pipelines), establishing deep Monitoring & Logging frameworks, ensuring strict Security & Compliance baselines (including DLP routines and tight IAM access protocols), and setting up comprehensive transparent Cost Visibility reporting and tracking.
- AI-Powered DataOps Managed Services (Optional): A comprehensive 12-month, 24x7 operational lifecycle coverage model encompassing continuous active Infrastructure Management, dedicated tier Data Pipeline Support, ongoing algorithmic Data Quality Monitoring, deep structural Data Observability, proactive active Cost Management, and strict ongoing Data Access Management oversight."
