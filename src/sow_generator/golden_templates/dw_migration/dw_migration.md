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