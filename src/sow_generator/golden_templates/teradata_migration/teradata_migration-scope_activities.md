### **Golden Content Framework: Recurring Activities for Teradata Migration Projects**

#### **I. Initiation & Program Governance**
This foundational phase establishes the project's strategic alignment, operational framework, and clear communication channels.

*   **Project Kick-off**: Conduct a comprehensive kick-off meeting to align on project goals, communication channels, and stakeholder responsibilities.
*   **Program Goals & Deployment Planning**: Define and gain agreement on project goals, expected outcomes, and a high-level deployment plan with the customer.
*   **Program Oversight & Reporting**: Oversee and coordinate program delivery planning and reporting, including periodic executive updates and weekly progress updates. This also involves overseeing the implementation of program change management processes. Define and agree on regular reporting processes, stakeholders, format, and weekly cadence.
*   **Risk Management**: Develop and maintain a comprehensive risk management plan.
*   **Project Planning**: Develop a detailed program plan, encompassing business outcomes, success metrics, key execution milestones, and a granular project plan.
*   **Status Meetings**: Conduct regular program status meetings with key stakeholders to assess progress, identify risks, and address issues.
*   **Team Onboarding & Design Finalization**: Facilitate pre-kick-off alignment, team onboarding, and finalization of the migration design and plan, building upon initial discovery findings.

#### **II. Discovery & Assessment**
A critical deep-dive into the existing Teradata environment and its ecosystem, providing the essential insights for migration planning.

*   **Current State Architecture Assessment**: Comprehensively assess the current Teradata or Hadoop architecture, associated workloads, and database objects.
*   **Technical & Functional Requirements Understanding**: Gather and understand both technical and functional requirements from the client.
*   **Pipeline & Volumetrics Analysis**: Analyze existing data ingestion and transformation pipelines, identifying patterns and understanding data volumetrics.
*   **Dependency Identification**: Meticulously identify dependencies for all associated workloads and database objects.
*   **Complexity & Volumetrics Analysis**: Conduct a detailed analysis of overall complexity and specific volumetrics within the Teradata environment.
*   **Orchestration & Scheduling Analysis**: Analyze existing job orchestration and scheduling patterns.
*   **Data Flow & Script Lineage**: Analyze data flow lineage and Teradata scripts lineage.
*   **Unused Object Analysis**: Identify and categorize unused tables and views to rationalize the migration scope.
*   **Challenges & Gaps**: Document current challenges, existing gaps, and client's future expectations from the target platform.
*   **Performance Benchmark**: Analyze any available performance benchmarks and non-functional requirements to set realistic targets for the migrated solution.
*   **Source System Analysis**: Understand the various source systems, tools, and technologies feeding into or interacting with Teradata.
*   **Data Quality Rules**: Understand existing data quality rules (relevant for migration but derived from a Snowflake SOW, broadly applicable).
*   **Legacy Code Issue Identification**: As part of data validation, identify potential issues or bugs in legacy code that might impact migration (can be in or out of scope, but identification is key).

#### **III. Architecture & Design**
Translating discovery findings into a concrete future-state vision and a detailed, actionable migration roadmap.

*   **Future State Design**: Define the comprehensive future state GCP solution and its technical architecture.
*   **Technology Mapping**: Explicitly define technology mappings from the current Teradata environment to the target GCP environment.
*   **Detailed Migration Strategy**: Develop a granular migration strategy encompassing data migration, code conversion, testing, validation, and cutover procedures.
*   **Connectivity Planning**: Plan connectivity for any unsupported sources, potentially leveraging JDBC or a dedicated ingestion framework.
*   **Migration Planning Recommendations**: Provide detailed migration planning recommendations, including a project plan, sprint roadmap, and status reporting guidelines.
*   **Design Sign-off**: Obtain formal sign-off on the final design and migration plan from the customer team.
*   **Data Modeling & Layers**: Design the data modeling strategy and define data layers for BigQuery, aligning with best practices.
*   **Low-Level Design (LLD)**: Produce Low-Level Design (LLD) documents, detailing technical specifications for implementation.
*   **GCP Foundation Design (Migration-Specific)**: Design the implementation of specific GCP services and utilities for data warehousing (storage, processing, analytical capabilities, business data management, self-service, cloning, time travel), ETL orchestration, Identity Management & Access Control (IAM roles, service accounts, OKTA integration), Organization Hierarchy (folder and project structure, labels), Networking, Cloud DLP API, and Infrastructure as Code (IaC) using Terraform for GCP component configuration and CI/CD.

#### **IV. Code Conversion & Transformation**
The core engineering effort to translate existing Teradata-specific logic into a GCP-native, performant, and maintainable format.

*   **DDL Conversion**: Convert in-scope Teradata / Hive table DDLs to their GCP Native DDL or BigQuery equivalents.
*   **SQL Conversion**: Convert in-scope Presto and Spark SQL to GCP native, existing HiveQL or Spark SQL scripts to BigQuery SQLs, and Teradata native scripts (SQL, Stored Procedures/BTEQs, Macros) to GCP native.
*   **ETL Pipeline & Script Conversion**: Convert existing ETL pipelines and data transformation jobs (e.g., Informatica, Datastage, Alteryx, Pentaho, Talend) to GCP-native technologies (e.g., BigQuery SQL, Dataflow, Cloud Functions, Connexio, Ftaas pipelines). Reutilize and adapt Shell and Python scripts for the GCP environment.
*   **Compatibility Assurance**: Ensure that all converted code and transformation jobs maintain the **same business logic** and possess **similar or compatible data types and schemas** as the legacy environment.
*   **Syntactical Validation & Unit Testing (Pre-data)**: Perform syntactical validation and unit testing of converted code, typically without live data, to confirm technical correctness and identify zero technical failures.
*   **Developed Pipelines Compatibility**: Ensure all newly developed pipelines are compatible with any existing frameworks previously developed by the customer.

#### **V. Data Ingestion & Integration**
Establishing robust and efficient pipelines to consistently bring data from various sources into the GCP environment.

*   **Incremental Pipeline Setup**: Set up incremental data ingestion pipelines from source systems to GCP. Build incremental ingestion pipelines from source systems to GCS for continuous data synchronization, leveraging proprietary Data Ingestion Frameworks. Develop continuous data sync pipelines from Teradata.
*   **Connectivity Planning**: Plan and implement connectivity for Connexio's unsupported sources using JDBC or a dedicated ingestion framework.
*   **Source Data Ingestion**: Ingest upstream source data into the target GCP data platform according to the future state architecture. This includes setting up ingestion for Hadoop-based pipelines and reconfiguring AWS Lambda functions to Cloud Functions.
*   **Kafka Stream Integration**: Leverage Google Managed Kafka for all streaming workloads.
*   **MFT Setup**: Prepare configuration for MFT (Managed File Transfer) setup and coordinate its deployment.

#### **VI. Historical Data Migration**
The critical, one-time transfer of historical data from the legacy Teradata data warehouse to the target GCP BigQuery environment.

*   **Extraction & Loading**: Extract historical data from the legacy Teradata environment and load it to GCP. This may involve using client's existing tools (e.g., Connexio).
*   **Tool Configuration**: Configure customer tools (e.g., Connexio) to facilitate historical data loading.
*   **Data Transfer**: Transfer historical data from the Teradata environment to GCP (e.g., into GCS buckets).
*   **Data Loading**: Load historical data from GCS into BigQuery.
*   **Write-Back Data Pipeline**: Create a data pipeline and mapping from GCP BigQuery to Teradata for write-back functionalities, including defining update frequencies and conducting data validation.
*   **Data Copy (Replication)**: Replicate data from Teradata to BigQuery for both historical and ongoing daily incremental updates, covering specified tables not in ETL modernization scope, and implementing continuous data synchronization pipelines for upstream sources.

#### **VII. Orchestration & Scheduling**
Migrating and establishing robust job scheduling and workflow orchestration using GCP-native services.

*   **Workload Orchestration**: Implement workload orchestration and scheduling for converted workloads using **Cloud Composer**.
*   **Legacy Tool Conversion**: Convert legacy orchestration tools such as Control-M, Autosys, Airflow, and Oozie to Cloud Composer.
*   **Schedule Mirroring**: Ensure migrated workflows faithfully mirror existing schedules in the legacy environment for business continuity.
*   **CI/CD Integration**: Utilize CI/CD pipelines to support Databricks workloads, ensuring the CI/CD framework is effectively leveraged.

#### **VIII. Reporting & Application Repointing**
Addressing the crucial aspect of connecting business intelligence tools and downstream applications to the new GCP data environment.

*   **Report Re-development**: Rewrite existing SAP BO and Tableau Reports into Looker, replicating underlying reporting views and redesigning features for compatibility.
*   **Report Repointing**: Re-point existing MicroStrategy & Tableau reports to BigQuery. This includes updating data source connections and re-pointing Looker reports.
*   **Application Migration/Rehosting**: Rehost in-scope applications (e.g., R shiny, MP Insights, Python-based ML applications) on GCP.
*   **Build Connections for 3rd Party Datasets**: Build necessary connections to ingest third-party datasets (e.g., ListenFirst, Brandwatch, NRG, Google Title/Talent Search) via the GCP native tech stack.
*   **SQL Refactoring for Applications**: Refactor underlying SQL scripts to be BigQuery compatible, specifically limiting changes to non-hardcoded SQL.
*   **Firewall Exceptions**: Implement existing firewall exceptions as mutually finalized during discovery.
*   **Validation**: Validate BigQuery tables against tools like Hibernate.
*   **Unit Testing of Reports**: Perform unit testing of in-scope reports.
*   **Data Validation of Reports**: Conduct data validation for in-scope reports.
*   **Manual Verification**: Perform manual verification of re-developed reports as needed.

#### **IX. Testing & Validation**
A non-negotiable phase to ensure data integrity, functional correctness, and performance parity between the legacy and target systems.

*   **Unit Testing**: Conduct unit testing of converted workloads.
*   **System Integration Testing (SIT)**: Perform system testing in QA/UAT environments using production-grade data.
*   **Historical Data Validation**: Conduct one successful historical data validation for a defined period. Validate historical data using Pelican.
*   **Pipeline Validation**: Utilize **Pelican** for data pipeline validation at the consumption layer.
*   **Data Validation (General)**: Perform end-to-end data validation between Teradata and GCP. This includes Pelican data validation between Teradata and Databricks.
*   **Parallel Runs**: Conduct **Pelican**-based parallel runs for data validation between source and target production environments. This includes two successful incremental data validations using Pelican.
*   **Bug Identification & Tracking**: Log and track all bugs/issues. Define bug categories and priorities. Manage defect logging, bug-fixing, and retesting.
*   **UAT Support**: Provide full support to the client team during User Acceptance Testing (UAT).
*   **Performance Parity Testing**: Ensure non-BI reporting BigQuery SQL performs as well as, or better than, Teradata.
*   **Data Revalidation**: Perform data revalidation, bug-fixing, and retesting as necessary.

#### **X. Deployment**
The final technical execution phase, moving validated workloads to the production environment, often with significant client involvement.

*   **Production Deployment Support**: While the client is often responsible for the final production deployment, the vendor provides crucial support for investigating and fixing issues. The vendor may also directly deploy converted code to production. The vendor provides build and release support for production deployment.
*   **Deployment Access & Walkthrough**: The client provides access to the production environment and existing code deployment tools, along with a walkthrough of their current deployment process.
*   **Cutover Planning**: Develop a detailed cutover plan and finalize the cutover approach.

#### **XI. Post-Migration Support & Knowledge Transfer**
Ensuring operational readiness and long-term success through comprehensive documentation, training, and a period of warranty.

*   **Knowledge Transfer Sessions**: Conduct extensive knowledge transfer sessions.
*   **Documentation**: Provide comprehensive runbooks and technical design documentation.
*   **Warranty Support**: Provide a defined period of warranty support (e.g., 4 weeks, 3 months) for bugs/errors directly related to the scope of work performed.
*   **Handover**: Formal project handover and associated documentation.

#### **XII. Data Quality & Governance**
Activities aimed at establishing and maintaining data integrity and governance frameworks within the new cloud environment.

*   **Data Governance Setup**: Set up data governance using **Dataplex**.
*   **Data Protection**: Integrate with existing tokenization/encryption tools for PII data handling (applicable from a Snowflake SOW, but broadly relevant).
*   **Data Quality Rules**: Implement existing data quality (DQ) rules and checks using GCP-native technologies.

#### **XIII. Consumption Acceleration Service (CAS)**
A specialized offering, identified in one SOW, focusing on enhancing data consumption capabilities post-migration.

*   **SQL Query Conversion**: Convert SQL queries originating from reports, ETL, or SAS.
*   **Query Testing**: Test converted queries against GCP BigQuery.
*   **Consultation**: Provide consultation to address legacy SQL functionality in GCP.
*   **Assisted Query Conversion**: Offer assisted query conversion for application or BI users, and for ad-hoc SQLs.
*   **Tracking Mechanism**: Define a robust request tracking mechanism (including category, execution life cycle, efforts, exceptions, activities, and cadence).
*   **Baseline Throughput**: Establish a baseline throughput for query conversion and resolution.