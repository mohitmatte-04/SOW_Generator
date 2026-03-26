Statement of Work (SOW)
1. Solution Overview
Executive Overview Sony’s current data ecosystem is anchored by Teradata and Snowflake, supported by ETL processes driven by Datastage and Alteryx, with AWS S3 for storage. Sony aims to transition its Teradata environment to a scalable cloud platform (GCP BigQuery) in an accelerated timeframe.

Migration Approach Recommendation

Early Teradata Retirement: The project will follow an "Early Teradata Retirement" model to allow Teradata to be fully migrated and retired by the end of Phase 1 (October 2024).
Target Architecture: This involves migrating Teradata to BigQuery, building an incremental pipeline for continuous sync from AWS S3 to Google Cloud Storage (GCS), and repointing existing ETL scripts. Datastage will be repointed and rehosted on GCP; Alteryx will be repointed but remain on AWS.
BI Repointing: Existing BI Tools (SAP BO, Tableau, Periscope, Power BI) will be migrated/hosted onto GCP and repointed to BigQuery.
Delivery Methodology

Agile Framework: The project will be delivered using Agile methodology.
Sprint-Based Execution: A "Sprint Wise" approach will be utilized to avoid "Big Bang" risks. Sprints will include extended parallel running with cell-level data synchronization and validation between new GCP and Teradata environments prior to cutover.
Automation Technologies (Bird Automation Suite) To ensure rapid, accurate, and risk-mitigated delivery, the following proprietary automation tools will be leveraged:

Eagle (The Planner): Utilized for granular, automated workload discovery, assessing dependencies, planning move groups, and architecting the migration strategy.
Raven (The Transformer): An automated code converter used to translate legacy EDW ETL components and SQL Objects (BTEQ, Views, Stored Procedures) into native GCP code (BigQuery SQL) rapidly with consistent syntactical translation.
Pelican (The Validator): Automates cell-level data validation, reconciliation, and comparison across heterogeneous systems without moving data to the cloud, ensuring high confidence for decommissioning the legacy solution.
2. Project Scope
The scope of work for this engagement encompasses the following activities and defined volumetrics:

2.1. Project Management & Governance
Project initiation, kickoff, and ongoing project governance.
Sprint planning, backlog management, and regular status reporting.
Risk, issue, and dependency management throughout the project lifecycle.
2.2. Discovery and Analysis
Deep dive of current Teradata Vantage environment.
Provide appropriate target architectural design and recommendations on GCP.
Workload breakdown, dependency mapping, and sprint planning.
2.3. Foundation & Infrastructure Setup
Google Foundation Setup: Build and configure the GCP foundation (Dev, QA, PreProd, and Prod environments) as per project requirements, including networking, IAM, and security controls.
Orchestration Setup: Provision, configure, and set up Orchestration & Scheduling leveraging Google Cloud Composer.
2.4. Data Ingestion & Migration
Data Ingestion: Build an incremental ingestion pipeline from AWS S3 to GCS for continuous data synchronization.
Data Migration: Perform a one-time historical data migration from Teradata Vantage to Google Cloud Platform.
2.5. Code Conversion & ETL Repointing
Code Conversion: Automated and manual translation of Teradata tables, views (DDLs), Stored Procedures, and BTEQs to GCP-native formats (BigQuery SQL).
ETL Repointing: Repointing Datastage and Alteryx to interact natively with GCP.
2.6. BI Tool Setup & Repointing
BI Tool Setup: Set up connectivity with in-scope BI tools to GCP BigQuery.
Reporting Repointing: Repoint SAP BO, Tableau, Periscope, and Power BI reports to read from GCP BigQuery.
2.7. Testing, Validation & Warranty
Testing and Validation: Validation of converted code and strict cell-level data synchronization and reconciliation.
Warranty Support: Provision of post-deployment warranty support to address any migration-related defects.
2.8. In-Scope Volumetrics
The following bounds define the quantitative scope of the migration:

History Data Size: 21 TB
Tables: 9,118
Views: 3,858
BTEQ: 115
Stored Procedures: 67
Datastage Sequence Jobs: 940
DataStage Parallel Jobs: 3,969
Alteryx Workflows: 394
Python Scripts: 170
SAP BO Universe: 10
SAP BO Reports: 2,041
Tableau: 295
Periscope: 5
Power BI: 5
3. Out of Scope
The following items are expressly excluded from the scope of this engagement:

Any Software upgrades or patching of existing systems.
User onboarding, identity creation, or end-user workstation configuration.
Decommissioning and cutover of existing legacy systems/environments (Teradata hardware tear-down).
Migration or re-platforming of the existing Snowflake environment.
Phase 2 Target Architecture features (e.g., Source System Integration directly to GCP, replacing ETL with GCP native Dataflow). These are mapped as Future Scope of Work / Proposal TBD.
Procurement of third-party software licenses or hardware.
Organizational change management, enterprise-wide communications, or end-user training outside of project core-team Knowledge Transfer (KT).
Resolution of pre-existing performance or functionality issues within the legacy Teradata environment not related to the cloud migration.
4. Deliverables
The project team will provide the following deliverables:

Project Governance: Project Kickoff Deck, Weekly Status Reports, Sprint Planning documents, and Final Project Sign-off/Closure Report.
Discovery & Assessment Materials: End-to-End Lineage, Data Model Discovery, Workload Breakdown, Complexity/Dependency Analysis, and Volumetric Analysis.
Migration Strategy & Plan: Detailed migration strategy with step-by-step sprint details, move groups, prioritization, target state solution architecture, and cutover strategy.
Cloud Foundation Setup: Configured Platform (Dev, QA, PreProd & Prod), Security, and DevOps environments ready for workload deployment.
Fully Converted Code: Translated BTEQ, SQL dialects, ETL mappings, reports, and ad-hoc workloads natively executing on GCP.
Reconciled Data: Automated cell-level data validation reports highlighting 100% reconciled data with no duplicate/missing records.
Documentation: Comprehensive Runbooks and Technical design/implementation documents.
Optimization Recommendations: Cloud utilization analysis identifying tuning opportunities for data models, queries, and cost optimizations.
5. Assumptions
The successful execution of this project is based on the following assumptions. Deviation from these may impact project scope, timeline, and cost.

Migration & Technical Assumptions

Migration strategy will be a "lift and shift" migration with minimal or no data model changes.
Alteryx ETL will be hosted on AWS and will not be migrated to GCP; it will only be repointed.
In the event of a need to re-platform ETL/BI tools to GCP due to performance issues or other factors, Sony will take responsibility for procuring and setting up these tools on GCP infrastructure.
Any issues, corruptions, or errors present in the legacy data can delay the timelines of the project. Onix is not responsible for pre-existing legacy data quality issues.
All work will be performed during standard business hours (Monday-Friday) unless specifically agreed upon for cutover events.
Customer (Sony) Responsibilities Sony will provide the following to Onix in a timely manner:

Access to the GCP and Teradata environments (Dev/Test/QA/Prod) and in-scope tools and technology (e.g., Datastage, Alteryx, BI Tools, etc.).
Access to required Sony incident management and ticketing systems (e.g., JIRA) and documentation portals (e.g., Confluence) related to the in-scope platform.
Required VPN/VDI access and dedicated interconnect infrastructure.
Sony team to ensure optimal connectivity between GCP and Teradata Vantage; any performance issues arising due to network bottlenecks will be handled by the Sony team.
All the in-scope Codes, Scripts, DDLs, and any other applicable software/assets required for migration.
Access to existing Code deployment tools (i.e., Bitbucket, GIT, etc.).
Infrastructure and necessary Security approvals and access rights for Onix accelerators (Bird Suite) and resources at no cost to Onix.
Required knowledge transfer around current architecture, data models, codebase, and other associated information as and when required.
Resolution to issues and coordination matters related to any other vendor/business partner associated with the project.
A dedicated point of contact (technical and functional SME) who can be contacted throughout the project duration as required.
Any software, hardware, infrastructure, and interfaces (Licenses, Libraries, ODBC Drivers, Connectors, etc.) required for this engagement.
Sony team will perform the User Acceptance Testing (UAT) promptly after sprint delivery by the Onix team.
Review and approval of deliverables will be completed within an agreed-upon timeframe (typically 3-5 business days) to prevent schedule delays.
6. Success Criteria
The engagement will be considered successfully completed upon achieving the following criteria:

100% Guaranteed Conversion: Successful, one-shot conversion of native code to GCP technologies as defined in the volumetrics.
Data Accuracy: 100% validated and matching reconciled data at the cell level between the legacy Teradata environment and the new cloud databases.
Accelerated Migration Timeline: Faster ramp on GCP, building confidence to achieve early Teradata retirement by the end of Phase 1 (October 2024).
User Acceptance: Successful UAT sign-off by the Sony team before moving to the PROD environment.