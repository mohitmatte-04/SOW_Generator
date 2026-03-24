### **Golden Content Framework: Recurring Activities for Snowflake to GCP Migration Projects**

#### **I. Initiation & Program Governance**
This foundational phase establishes the project's strategic alignment, operational framework, and clear communication channels to ensure a smooth transition and consistent oversight.

*   **Project Kick-off**: Conduct a comprehensive kick-off meeting to align on project goals, communication channels, and stakeholder responsibilities.
*   **Program Goals & Deployment Planning**: Define and gain agreement on project goals, expected outcomes, and a high-level deployment plan with the customer.
*   **Program Oversight & Reporting**: Oversee and coordinate program delivery planning and reporting, including periodic executive updates and weekly progress updates. This involves tracking risks, issues, dependencies, and changes.
*   **Change Management**: Oversee the implementation of program change management processes in coordination with customer stakeholders.
*   **Risk Management**: Develop and maintain a comprehensive risk management plan.
*   **Project Planning**: Develop a detailed program plan, encompassing business outcomes, success metrics, key execution milestones, and a granular project plan.
*   **Team Onboarding**: Onboard project teams (client, vendor, Google) and finalize the migration design and plan, building upon initial discovery findings.
*   **Program Governance Model**: Establish and implement a structured program governance model, including sprint-based execution, move group tracking, dependency management, and executive reporting.

#### **II. Discovery & Assessment**
A critical deep-dive into the existing Snowflake environment and its ecosystem, providing the essential insights for migration planning and target state design.

*   **Current State Understanding**: Comprehensively analyze the current landscape, including business overview (Key Business Areas/Domains), technical and data architecture, source systems, data ingestion pipelines/patterns/volumetrics, data quality rules, data flow between data layers, data tokenization rules/process flow, data transformation pipelines/patterns/volumetrics, peripheral systems integration, BI tools, data consumption processes/patterns/feeds, current challenges/gaps & future expectations, and current testing strategy/infrastructure.
*   **Snowflake Metadata Analysis**: Analyze Snowflake object counts, table sizes, active/inactive analysis, stored procedures, views, and SQL scripts.
*   **Workload Analysis**: Conduct a detailed workload distribution analysis, identify unused or redundant tables/views, and perform volumetrics and complexity analysis.
*   **Source System Analysis**: Identify and analyze all source systems feeding into Snowflake, including their integration patterns, dependencies, and access methods.
*   **Data Flow & Script Lineage**: Analyze end-to-end data flow lineage, Snowflake scripts lineage, and ETL/ELT patterns.
*   **Dependency Identification**: Meticulously identify all dependencies for associated workloads and database objects.
*   **Early Tiny Movers (ETM) Migration**: Perform migration of ETM units during the discovery and planning phase to assess feasibility and solidify the migration strategy.

#### **III. Architecture & Design**
Translating discovery findings into a concrete future-state vision and a detailed, actionable migration roadmap, which forms the blueprint for the entire project.

*   **Future State Design**: Define the comprehensive future state GCP solution and its technical architecture, including specific architectural changes for application migration.
*   **Technology Mapping**: Explicitly define technology mappings from the current Snowflake environment to the target GCP environment.
*   **Detailed Migration Strategy**: Develop a granular migration strategy encompassing data migration, code conversion, repointing, testing/validation, and cutover procedures.
*   **Migration Planning Recommendations**: Provide detailed migration planning recommendations, including a project plan, sprint roadmap, move group definition (based on Eagle outputs), and status reporting guidelines.
*   **Design Sign-off**: Obtain formal sign-off on the final design and migration plan from the client and Google/vendor.
*   **High-Level Clean Room Design**: Provide guidance on a high-level design for a clean room in BigQuery.
*   **Semantic Layer Modeling Approach**: Draft the semantic layer modeling approach for key metrics, for example, in Looker.
*   **DataPlex Taxonomy Design**: Design the DataPlex taxonomy, including Entry Groups, Entry Types, and Aspect Types, structured by data domain.
*   **Data Quality Rule Framework Design**: Design the data quality rule framework, encompassing rule categories, scoring thresholds, scheduling, and alerting architecture.
*   **Data Lineage Mapping**: Map data lineage to ensure clear understanding and traceability.
*   **Solution Design Document**: Develop a comprehensive Solution Design Document that adheres to a "lift-and-shift" approach while preserving the logical structure of the current environment.

#### **IV. Google Cloud Foundation Setup**
While often a client responsibility, the scope may include design and guidance for establishing a secure and compliant GCP environment ready for migration.

*   **Infrastructure & Platform Foundation**: Design the implementation of Data Platform Foundations components according to the Technical Design Document.
*   **Security Model & RBAC Automation**: Develop and implement standardized templates (scripts) to replicate BigQuery and related pipelines for new market launches.

#### **V. Data Ingestion & Integration**
Establishing robust and efficient pipelines to consistently bring data from various sources into the GCP environment, ensuring continuous data flow.

*   **Source System Connectivity**: Set up connectivity from current source systems to Google Cloud Platform, often leveraging a Data Ingestion Framework (DIF).
*   **Incremental Ingestion Pipelines**: Build incremental ingestion pipelines from source systems (e.g., GCS) to BigQuery for continuous data synchronization.
*   **File Watchers Capability**: Implement File Watchers equivalent capability on GCP to detect file landings in GCP storage and initiate ETL processes accordingly.
*   **Kafka Stream Integration**: Leverage Google Managed Kafka for all streaming workloads. This includes building pipelines from Kafka-0 to BigQuery using a DIF and establishing connectivity (client responsibility).
*   **Legacy Script Repurposing/Migration**: Repurpose Python scripts and migrate them to Google Datastream. Reconfigure AWS Lambda functions with Cloud Run functions to write data into GCP.
*   **Existing Connector Reconfiguration**: Reconfigure existing connectors (e.g., Fivetran) to point to BigQuery.
*   **Data Tokenization/Encryption**: Integrate with existing tokenization/encryption tools (e.g., Protegrity) for PII data handling.

#### **VI. Code Conversion & Transformation**
The core engineering effort to translate existing Snowflake-specific logic into a GCP-native, performant, and maintainable format, preserving business integrity.

*   **DDL Conversion**: Convert current Tables and Views Data Definition Languages (DDLs) to GCP BigQuery equivalent, often leveraging Raven technology.
*   **Snowflake-Specific Conversion**: Convert Data Transformation Jobs such as SnowSQL, Snow Pipe, and Snowflake Stored Procedures to Dataflow, BigQuery SQL, and BigQuery Stored Procedures, including equivalent solutions for Snowflake Streams and Task.
*   **ETL Tool Conversion**: Convert Talend ETL jobs to GCP native technologies (Dataflow/BQ). Convert Matillion & ADF jobs to GCP native. Migrate Domo’s Magic ETLs to BigQuery using equivalent transformation logic.
*   **Python/Shell Script Refactoring**: Refactor and rewrite existing Python-based transformation scripts to align with the GCP runtime environment.
*   **dbt Object Migration**: Reconfigure and migrate dbt objects to ensure compatibility with BigQuery SQL dialect.
*   **Business Logic/Schema Preservation**: Ensure converted or migrated code retains the same business logic/structure, data format, and schemas as the legacy environment.
*   **Ab Initio Workload Conversion**: Rewrite and/or transform aspects of Ab Initio (ABI_2) functionality and/or jobs to work with new BigQuery statements, especially where Snowflake SQL was originally used. Repoint Ab Initio (ABI_2) to BigQuery in cases where Snowflake SQL was not directly used.
*   **Open Format Storage**: Convert workloads into Open Format at storage.

#### **VII. Historical Data Migration**
The critical, one-time transfer of historical data from the legacy Snowflake data warehouse to the target GCP BigQuery environment, with robust validation.

*   **Historical Data Pipeline Build**: Build a Historical Data pipeline to load one-time historical data from Snowflake/Azure to GCP.
*   **Client Data Provision**: The client is responsible for providing the required access to extract historical data from the Snowflake environment. This includes extracting and landing historical data from Snowflake into GCS.
*   **Validation**: Validate migrated history using a mutually defined approach. This includes verified schema and record-level reconciliation, often using tools like Pelican.
*   **Incremental Data Sync**: Implement and maintain incremental data sync until User Acceptance Testing (UAT) procedures are completed for a specific sprint.

#### **VIII. Orchestration & Scheduling**
Migrating and establishing robust job scheduling and workflow orchestration using GCP-native services, ensuring operational continuity.

*   **Legacy Tool Conversion**: Convert Airflow, Cron, and Talend orchestration/scheduling workloads to Cloud Composer. Set up Orchestration and Scheduling for converted workloads using Stonebranch and Cloud Composer. Set up Orchestration & Scheduling with Prefect for migrated workflows.
*   **Schedule Mirroring**: Ensure migrated workflows faithfully mirror existing schedules in the legacy environment to maintain business continuity.
*   **Data Orchestration Workflows**: Configure data orchestration workflows using Control-M.
*   **Retail Data Model Orchestration**: Orchestrate and schedule pipelines for the Retail Data Model using Composer/Airflow.

#### **IX. Reporting & Application Repointing**
Addressing the crucial aspect of connecting business intelligence tools and downstream applications to the new GCP data environment, ensuring seamless data consumption.

*   **Report Repointing**: Repoint existing Tableau, MicroStrategy, Power BI, Crystal Reports, and ThoughtSpot to consume data from GCP BigQuery.
*   **Report SQL Changes**: Make required changes in report SQLs for source/target change/repointing.
*   **Report Unit Testing**: Perform unit testing of in-scope reports.
*   **Report Data Validation**: Conduct parallel runs for data validation of in-scope reports repointed to BigQuery.
*   **Application Repointing**: Repoint downstream applications to BigQuery and refactor jobs/pipelines to ensure compatibility.
*   **Application Rehosting**: Rehost in-scope applications (e.g., R shiny, MP Insights, Python-based ML applications) on GCP. Build required connections to ingest 3rd party datasets via GCP native tech stack.
*   **Looker Reports**: Migrate Power BI, Tableau, and Crystal Reports to Looker and enable self-service analytics. Build LookML models and self-service dashboards for defined metrics, and validate Looker metrics against BigQuery outputs.

#### **X. Testing & Validation**
A non-negotiable phase to ensure data integrity, functional correctness, and performance parity between the legacy and target systems, building confidence in the migrated solution.

*   **Unit Testing**: Conduct unit testing of converted workloads/code components.
*   **Historical Data Validation**: Perform historical data validation for a set period.
*   **System Integration Testing (SIT)**: Perform system integration testing in QA/UAT environments using production-grade data.
*   **Parallel Runs**: Conduct two successful incremental data validations, often using the Onix tool “Pelican,” of data pipelines at the consumption layer between the Snowflake and GCP environments.
*   **Data Reconciliation/Parity Validation**: Perform data reconciliation and parity validation. Validate migrated data using Pelican.
*   **UAT Support**: Provide full support to the client team during User Acceptance Testing (UAT), including defect resolution, clarification, and reruns as needed.
*   **Report Validation**: Validate report performance (ensuring similar or better performing queries in GCP BQ vs. Snowflake). Benchmark Report Performance for Business Critical Reports against the source system and perform optimizations if required.
*   **Bug Identification & Tracking**: Log and track all bugs/issues identified during testing and UAT.
*   **Data Validation (General)**: Validate data completeness and accuracy post-migration for correctness using defined tools and criteria.

#### **XI. Deployment**
The final technical execution phase, moving validated workloads to the production environment, often requiring close collaboration and support from the vendor.

*   **Production Deployment Support**: While the client is typically responsible for the final production deployment, the vendor provides crucial support for investigating and fixing issues.
*   **Vendor Direct Deployment**: The Onix team may directly deploy all workloads to the Production environment.
*   **Client Walkthrough/Access**: The client provides a walkthrough of the current deployment process and access to the production environment and existing code deployment tools.
*   **Cutover Approach Finalization**: Finalize the cutover approach for consumption layer tables.

#### **XII. Post-Migration Support & Knowledge Transfer**
Ensuring operational readiness and long-term success through comprehensive documentation, targeted training, and a period of warranty to stabilize the new environment.

*   **Knowledge Transfer (KT)**: Conduct extensive knowledge transfer sessions covering post-migration review, runbooks, and technical design documents.
*   **Documentation**: Provide comprehensive runbooks and technical design documentation explaining the scope of work performed.
*   **Warranty Support**: Provide a defined period of warranty support (e.g., 4 weeks, 3 months) for bugs/errors directly related to the scope of work performed. The client is typically responsible for investigating tickets and providing detailed analysis for defect fixing.
*   **Raven Conversion Service for User Queries**: Provide Raven Conversion Service for user query conversion for a defined period.
*   **Helpdesk Services**: Provide Helpdesk services for Strategy users, limited to assisting in restoring functionality of reports and questions about report repointing.

#### **XIII. Data Quality & Governance**
Activities aimed at establishing and maintaining data integrity and governance frameworks within the new cloud environment.

*   **DQ Rules Implementation**: Implement existing Data Quality (DQ) rules and checks to GCP native technology, and build a capability to apply DQ rules for Data in transit. This includes ensuring existing data quality rules are embedded into the Data Ingestion Framework (DIF).
*   **DataPlex Cataloging/Lineage/Policy Enforcement**: Implement Dataplex-based cataloging, lineage, and policy enforcement.
*   **Data Cleaning/Masking**: Implement data cleaning and masking capabilities using Technical Design Document specifications, pre-existing customer algorithms, and/or specifications for data moved out of the production environment.

#### **XIV. Data Science Enablement**
For projects with a modernization component, this includes adapting data science models to the cloud-native ecosystem.

*   **Model Reconfiguration**: Reconfigure Databricks-based models to the GCP native stack (e.g., Vertex AI, BigQuery ML).