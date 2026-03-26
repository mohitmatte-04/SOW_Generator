scope
Discovery and Analysis: Deep dive of current Teradata Vantage environment and provide appropriate architectural design and recommendations.
Foundation Setup: Google Foundation Setup as per project requirements.
Data Ingestion: Build incremental ingestion pipeline from S3 to GCS for continuous data synchronization.
Data Migration: One-time historical data migration from Teradata Vantage to Google Cloud Platform.
Code Conversion: Conversion of Teradata tables & views DDLs, Stored Procedures, and BTEQs to GCP native.
ETL Repointing: Repointing Datastage and Alteryx to GCP native.
Orchestration: Set up Orchestration & Scheduling with Cloud Composer.
BI Tool Setup: Setup connectivity with in-scope BI tools to GCP BigQuery.
Reporting Repointing: Repoint SAP BO, Tableau, Periscope, and Power BI reports to GCP BigQuery.
Testing and Validation: Validation of converted code and data synchronization.
Warranty: Warranty support post-deployment.
In-Scope Volumetrics:
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
out_of_scope
Any Software upgrades or patching.
User onboarding.
Decommissioning and cut over of existing systems/environments.
Migration of Snowflake environment.
Phase 2 Target Architecture features (Source System Integration directly to GCP, replacing ETL with GCP native Dataflow) are mapped as Future Scope of Work / Proposal TBD.
success_criteria
100% Guaranteed Conversion: Successful, one-shot conversion of native code to GCP technologies.
Data Accuracy: 100% validated & matching reconciled data at the cell level between legacy and cloud databases.
Accelerated Migration Timeline: Faster ramp on GCP, building confidence to achieve early Teradata retirement by Phase 1 end (October 2024).
User Acceptance: Successful UAT sign-off before moving to PROD.
assumptions
Migration strategy will be a lift and shift migration with minimal or no data model changes.
Customer (Sony) will provide the following to Onix:
Access to GCP and Teradata environment (Dev/Test/QA/Prod) and in-scope tools and technology (e.g., Datastage, Alteryx, BI Tools, etc.).
Access to required Sony’s incident management and ticketing systems (e.g., JIRA) and documents portal (e.g., Confluence) related to the in-scope platform.
VPN/VDI and dedicated interconnect.
All the in-scope Codes, Scripts, DDLs, and any other applicable software.
Existing Code deployment tools (i.e. Bitbucket, GIT, etc.).
Infrastructure and Necessary Security approval and access rights for Onix accelerators and resources at no cost.
Required knowledge transfer around current architecture, data model, codebase, and other associated information, as and when required.
Resolution to issues and coordination matters related to any other vendor/business partner associated with the project.
Point of contact (technical and functional SME) who can be contacted throughout the project duration, as and when required.
Any software, hardware, infrastructure, and interfaces (Licenses, Libraries, ODBC Drivers, Connectors, etc.) required for this engagement.
In the event of a need to re-platform ETL/BI tools to GCP due to performance issues or other factors, Sony will take responsibility for procuring and setting up these tools on GCP infrastructure.
Alteryx ETL will be hosted on AWS and not be migrated to GCP.
Sony team to ensure optimal connectivity between GCP and Teradata Vantage; any performance issues arising due to network bottlenecks will be handled by the Sony team.
Any issues or errors in the legacy data can delay the timelines of the project.
Sony team will perform the User Acceptance Testing (UAT) after sprint delivery by the Onix team.
deliverables
Discovery & Assessment Materials: End-to-End Lineage, Data Model Discovery, Workload Breakdown, Complexity/Dependency Analysis, and Volumetric Analysis.
Migration Strategy & Plan: Detailed migration strategy with step-by-step sprint details, move groups, prioritization, target state solution architecture, and cutover strategy.
Fully Converted Code: Translated BTEQ, SQL dialects, ETL mappings, reports, and ad-hoc workloads native to GCP.
Cloud Foundation Setup: Configured Platform (Dev, QA, PreProd & Prod), Security, and DevOps environments.
Reconciled Data: Automated cell-level data validation reports highlighting 100% reconciled data with no duplicate/missing records.
Documentation: Runbooks and Technical documents around implementation.
Optimization Recommendations: Cloud utilization analysis identifying tuning opportunities for data models, queries, and costs.
solution_overview
Executive Overview: Sony’s current data ecosystem is anchored by Teradata and Snowflake, supported by ETL processes driven by Datastage and Alteryx, with AWS S3 for storage. Sony aims to transition its Teradata environment to a scalable cloud platform (GCP BigQuery) in an accelerated timeframe.
Migration Approach Recommendation (Option B):
The project will follow an "Early Teradata Retirement" model to allow Teradata to be fully migrated and retired by the end of Phase 1 (October 2024).
This involves migrating Teradata to BigQuery, building an incremental pipeline for continuous sync from AWS S3 to GCS, and repointing existing ETL scripts (Datastage will be repointed & rehosted on GCP; Alteryx will be repointed but remain on AWS).
BI Tools (SAP BO, Tableau, Periscope, Power BI) will be migrated/hosted onto GCP and repointed to BigQuery.
Delivery Methodology:
The project will be delivered using Agile methodology.
A "Sprint Wise" approach will be utilized to avoid "Big Bang" risks. Sprints will include extended parallel running with cell-level data synchronization and validation between new GCP and Teradata environments prior to cutover.
Automation Technologies (Bird Automation Suite):
Eagle (The Planner): Utilized for granular, automated workload discovery, assessing dependencies, planning move groups, and architecting the migration strategy.
Raven (The Transformer): An automated code convertor used to translate legacy EDW ETL components and SQL Objects (BTEQ, Views, Stored Procedures) into native GCP code (BigQuery SQL) rapidly with consistent syntactical translation.
Pelican (The Validator): Automates cell-level data validation, reconciliation, and comparison across the heterogeneous systems without moving data to the cloud, ensuring high confidence for decommissioning the legacy solution.