### **Standardized "Golden Content" Framework for Teradata to GCP Migration SOWs**

This framework outlines the essential phases and granular activities that repeatedly appear in comprehensive SOWs for Teradata to Google Cloud Platform migrations.

---

### 1. Executive Summary & Introduction

*   **Opportunity/Problem Statement**: Clearly articulate the client's strategic objective to modernize their data platform by migrating from **Teradata (whether on-premise or cloud-hosted)** to **Google Cloud Platform (GCP)**. Highlight anticipated benefits such as **enhanced scalability, improved cost-efficiency, and strengthened data-driven decision-making capabilities**.
*   **Solution Overview**: Briefly describe the vendor's proposed solution approach, emphasizing the use of **automated migration tools (e.g., Eagle for assessment, Raven for code conversion, Pelican for data validation)** and **deep subject matter expertise**. Outline the high-level phases or tracks of the engagement (e.g., Discovery, Migration, Reporting Re-pointing).
*   **Project Schedule**: Provide **estimated project start and end dates**, along with the overall **duration** and a high-level breakdown of key phases or milestones.

### 2. Scope of Work (Detailed Activities)

This section is the core of any migration SOW, meticulously defining the contractual boundaries and ensuring crystal-clear expectations for all parties.

*   **2.1. Discovery, Analysis, and Design**:
    *   **Project Kick-off & Planning**: Conduct a formal **project kick-off meeting** to align all stakeholders on the **Assessment Scope, Objectives, Assumptions, Approach, Eagle Prerequisites, Reference Plan, Team & SME Requirements, and Communication Plan**.
    *   **Detailed Project Planning**: Develop a comprehensive **Project Plan** that includes **detailed tasks, activities, timelines, milestones, and dependencies**. Establish a **Sprint Roadmap** and define **Move Groups** based on a thorough analysis of technical dependencies and business priorities.
    *   **Current State Assessment**:
        *   Gain a deep understanding of the **Business Overview (Key Business Areas/Domains), Technical and Functional Requirements**, and the **Current State Architecture** of the Teradata environment.
        *   Identify and document **all Tools and Technologies currently in use** within the legacy environment.
        *   Analyze **Data Ingestion Patterns, Data Transformation Pipelines/Patterns/Volumetrics**, and the **Workload Distribution** across the Teradata ecosystem.
        *   Perform detailed **Teradata scripts/code lineage analysis (ETL/ELT patterns)**, covering **BTEQs, Macros, Stored Procedures, Functions, Triggers, and User-Defined Functions (UDFs)**.
        *   Identify **Unused or redundant tables and views** to optimize migration scope.
        *   Conduct comprehensive **Volumetrics and Complexity Analysis** of all in-scope objects and workloads.
        *   Document **Current Challenges, Gaps, and Future Expectations** of the client.
        *   Analyze **User Query Lineage**, perform **Active User Session Analysis**, and derive **Functional IDs/User IDs based on DBQL logs**.
    *   **Future State Design & Recommendations**:
        *   Design the **Future State Solution and Technical Architecture** on GCP.
        *   Define precise **Technology Mappings (current vs. future)**, specifying how Teradata components will transition to **BigQuery, Cloud Composer, Dataflow, and other GCP services**.
        *   Formulate a **Detailed Migration Strategy** that comprehensively covers **Data Migration, ETL Conversion, Testing & Validation, and Cutover Strategy**.
        *   Provide **Architectural Changes Recommendations for Application Migration** as necessitated by the new GCP environment.

*   **2.2. Code Conversion**:
    *   **Schema & Object Conversion**: Convert all **Teradata Tables, Views, and Data Definition Languages (DDLs)** to their **GCP BigQuery/Native DDL equivalents**, ensuring appropriate data type adaptation.
    *   **SQL & Script Conversion**: Translate **Teradata native scripts (SQL, BTEQs, Macros, Stored Procedures, Functions, Triggers, UDFs)** to **GCP BigQuery equivalent/native SQL**.
    *   **ETL Tool Conversion**: Convert **Informatica Mappings/Workflows** to **GCP native services (e.g., Dataflow/BigQuery)**. Similarly, convert **Datastage and Alteryx workflows** to their **GCP equivalents**. Implement conversions for **custom frameworks (e.g., Verizon's GLU/MGLU/PMF/Cron)**.
    *   **Script Re-platforming**: Reutilize and refactor existing **Python scripts** for compatibility and optimal performance within the **GCP runtime environment**. Adapt **legacy shell scripts** for **GCP compatibility**.
    *   **Orchestration Logic Conversion**: Convert **Airflow DAGs** (Directed Acyclic Graphs) to **Cloud Composer DAGs**.
    *   **Logic Preservation Guarantee**: Crucially, ensure that all **converted/migrated code strictly retains the same business logic, and maintains similar/compatible data types and schemas** as the original legacy environment.
    *   **Pre-Conversion Validation**: Conduct a thorough **code review** with the client and perform **unit testing (focusing on syntactical correctness and, where applicable, zero records output)** before initiating full-scale conversion efforts.

*   **2.3. Data Migration (Historical & Incremental)**:
    *   **Historical Data Migration**: Execute a **one-time historical data migration** from **Teradata (or associated source systems like S3)** to **GCP (Google Cloud Storage / BigQuery)**. This phase typically mandates **client responsibility for data extraction and provisioning** and **vendor responsibility for data loading into GCP and initial validation**.
    *   **Incremental Data Ingestion**: Design and implement **incremental ingestion/data synchronization pipelines** from various **source systems (e.g., RDBMS, Files, existing enterprise frameworks like CCI or CDMNext)** to **GCP (GCS/BigQuery)**. This includes mechanisms for handling **Change Data Capture (CDC) extracts** and ensuring **source files are readily available in GCS**.
    *   **Data Validation for Migration**: Conduct rigorous **historical and incremental data validation** using automated tools, most notably **Pelican**, to ensure **complete data parity and accuracy** between the source and target systems. Formal **client sign-off on all data validation reports** is a key milestone.

*   **2.4. Orchestration and Scheduling**:
    *   **Tool Transition**: Establish robust **orchestration and scheduling solutions** utilizing **GCP-native tools like Cloud Composer**, or integrate with **existing enterprise tools such as Control-M**, or seamlessly connect with **client-specific frameworks like Cerebro**.
    *   **Schedule Replication**: Ensure all **migrated workflows faithfully mirror their existing production schedules and dependencies** to guarantee uninterrupted business continuity.
    *   **DAG Development**: Develop and implement **Cloud Composer DAGs** to encapsulate translated BigQuery SQLs and manage complex, multi-step workflows effectively.

*   **2.5. Reporting Re-pointing/Re-development**:
    *   **BI Tool Connectivity**: Establish robust **connectivity between various Business Intelligence (BI) tools (e.g., MicroStrategy, Tableau, Power BI, SAP BO, Looker)** and **GCP BigQuery**. Specific configurations may remain a client responsibility.
    *   **Report Identification & Scope**: Collaboratively **identify, prioritize, and finalize the specific set of reports** for re-pointing or conversion, guided by business criticality and impact.
    *   **Report Re-pointing**: Modify existing reports to **directly consume data from BigQuery datasets**.
    *   **Report Re-development/Conversion**: **Rewrite or redevelop reports** (e.g., transitioning SAP BO/Tableau reports to Looker) or **convert the underlying SQL queries within reports** to ensure BigQuery compatibility.
    *   **Validation & Testing**: Perform **unit testing of all repointed/redeveloped reports**. Conduct **data validation (often leveraging Pelican)** specifically for reports containing embedded queries that undergo changes. The client is responsible for executing **Functional and User Acceptance Testing (UAT)**.
    *   **Enablement & Knowledge Transfer**: Provide comprehensive **documentation, walkthroughs, and specialized enablement sessions** on the report re-pointing process and the utilization of new BI tools/platforms.

*   **2.6. Testing and Validation**:
    *   **Test Planning & Strategy**: Develop a comprehensive **data validation test strategy**, including objectives for **performance testing and benchmarking** against the existing legacy system. Formulate a detailed **System Integration and User Acceptance Test Plan**.
    *   **Unit Testing**: Conduct **unit testing of all converted workloads, code, and components** within development environments, verifying **syntactical correctness** and (if applicable) ensuring **zero-record outputs** in test scenarios.
    *   **System Integration Testing (SIT)**: Execute **SIT in QA/UAT environments** utilizing **production-grade data** to validate the end-to-end functionality of all integrated pipelines.
    *   **Data Validation**: Perform extensive **historical and incremental data validation**. Critically, leverage **automated data validation tools (e.g., Pelican)** for **data parity and reconciliation** between the Teradata source and BigQuery target. Client **sign-off on all data validation reports** is mandatory.
    *   **Parallel Run**: Conduct **parallel runs** to validate data consistency and operational correctness in production environments, comparing the legacy and new GCP systems, often facilitated by **Pelican**. Define the **duration and scope** of parallel runs (e.g., focusing on final tables, specific applications) based on the criticality of the data (e.g., financial data).
    *   **UAT Support & Remediation**: Provide **advisory and hands-on support during client-led User Acceptance Testing (UAT)**. Manage the entire **bug identification, tracking, fixing, and retesting lifecycle**, including **triaging and remediation of issues related to data parity mismatches or application query performance degradation**.

*   **2.7. Deployment and Cutover**:
    *   **Deployment Planning**: Collaboratively agree on **production deployment methodologies**, ensure **runbook readiness, resource readiness, detailed scheduling plans, change request procedures**, and **communication strategies for end-users**.
    *   **Deployment Execution**: The vendor (e.g., Onix) typically **deploys workloads to the production environment** or provides **essential support during the client's own deployment efforts**. The client is expected to provide a **walkthrough of their current deployment processes** and grant **necessary access to production environments and associated tools (e.g., Bitbucket, GIT)**.
    *   **Issue Resolution**: The vendor is responsible for **fixing any bugs identified by the client during the production deployment phase**.
    *   **Cutover Strategy**: Develop a **detailed cutover strategy**, including comprehensive **rollback procedures**, designed to minimize downtime and mitigate operational risks.

*   **2.8. Change Management, Knowledge Transfer, and Warranty**:
    *   **Knowledge Transfer (KT) & Documentation**: Conduct formal **KT sessions** covering design principles, migration processes, specific tool usage (e.g., Looker), and walkthroughs of GCP services. Provide comprehensive **runbooks and technical design documents** detailing the scope of work, operational procedures on GCP, and adherence to industry best practices. Include **FAQs and best practices for GCP adoption**. Document **post-migration reviews** leveraging successful data validation reports.
    *   **Warranty Support**: Provide a clearly defined **warranty period (e.g., 4 weeks, 3 months, 90 days)** post-deployment or post-delivery of specific components for **bug/error resolution** related to the converted code and scripts. The client is responsible for performing initial investigation and providing detailed analysis to the vendor for issue resolution.
    *   **Ad-hoc Support**: Offer **ad-hoc query support/conversion** for new environment enablement or direct user requests. Provide **consumption acceleration services** to facilitate user adoption.
    *   **Change Management**: Facilitate the **identification of key users/stakeholders for organizational change management** and assist in **defining their roles and responsibilities** within the new data ecosystem.

### 3. Deliverables (Summary of Outputs)

A concise summary of the tangible outputs from the engagement:

*   **Assessment Reports**: Volumetric analysis, data flow/code lineage, workload distribution dashboards, migration plans, solution designs, and technical architecture documents.
*   **Code & Data Assets**: Converted DDLs, BigQuery-compatible SQL scripts, translated ETL jobs, orchestrated workflows, and successfully migrated historical and incremental data.
*   **Testing Reports**: Unit test results, detailed data validation reports (often from Pelican), parallel run reports, and UAT issue logs with resolution details.
*   **Documentation**: Comprehensive runbooks, technical design documents, KT session materials, migration strategy documents, and sprint roadmaps.
*   **Support & Services**: Formal warranty support agreements and delivered ad-hoc query conversion services.

### 4. Success Criteria

Clearly defined metrics for measuring project success:

*   **Functional Equivalence**: **100% data matching** between the legacy Teradata environment and GCP BigQuery, with **no changes to the core business logic**.
*   **Operational Readiness**: All **in-scope workloads operating successfully and reliably in the production environment on GCP**.
*   **Data Consumption**: All **in-scope BI reports and downstream applications seamlessly consuming data from GCP BigQuery**.
*   **Scalability & Cost-Efficiency**: Realization of the intrinsic benefits of cloud migration, such as **improved scalability and optimized cost-efficiency** (implied by the primary objective of migration).

### 5. Assumptions and Dependencies (Critical for Project Execution)

Crucial elements that must be met for the project to proceed successfully:

*   **Client Responsibilities (General)**: The client is responsible for providing **timely access** (to GCP environments, legacy systems, and required tools), allocating **dedicated Subject Matter Experts (SMEs)**, providing **comprehensive documentation**, facilitating **clarifications**, ensuring **prompt issue resolution**, and delivering **timely sign-offs** on deliverables and designs.
*   **Technical Environment Readiness**: The **GCP foundation (projects, IAM, networking, security configurations)** must be **already in place, configured, and fully accessible** to the project team. **Optimal network connectivity** between on-premise/legacy cloud environments and GCP is paramount.
*   **Data & Code Quality**: The **legacy Teradata data is assumed to be complete and accurate, free from significant data quality issues** that could impede migration and testing. A **code freeze** for all in-scope components is required during migration sprints. The client is responsible for **resolving any identified legacy code or data issues**.
*   **Tools & Accelerators**: Adequate **infrastructure and security approvals** for vendor accelerators (e.g., Pelican, Raven, Eagle) must be provided. **Pelican** (for data validation) is typically installed within the **client's GCP environment**.
*   **Deployment Accountability**: The **client is ultimately responsible for production deployment** (with vendor support and guidance).
*   **Scope Boundaries & Change Management**: The migration strategy is primarily defined as **lift-and-shift with minimal or no data model changes**. **Any changes to the defined scope or additional volumetrics will necessitate a formal Change Request (CR)**, which will be estimated and approved separately.

### 6. Out of Scope (Clear Exclusions)

Explicitly stating what is *not* included helps manage expectations and prevent scope creep:

*   **GCP Foundation Setup**: This is generally considered a **prerequisite** for the engagement and not part of the migration scope.
*   **Advanced Features Development**: **AI/ML model development or enhancement** is typically excluded.
*   **Legacy System Decommissioning**: **Decommissioning or sunsetting of legacy environments** is outside the scope, as are **software upgrades or patching** of legacy systems.
*   **Beyond Migration Activities**: **Performance tuning or optimization** beyond ensuring functional equivalence, **user training or onboarding** beyond the provided knowledge transfer, **custom application changes or modifications to business logic**, and **integration with unlisted third-party applications** are typically excluded.
*   **Specific Technology Exclusions**: Any technologies or platforms not explicitly listed in the in-scope sections are excluded from migration or assessment.

### 7. Roles and Responsibilities

While a full RACI matrix is often in an appendix, the main SOW outlines key roles:

*   **Vendor Roles**: Typically include **Technical Project Manager, Technical Architect, Technical Lead, Data Engineer, Data/Test Engineer, SRE/DevOps Lead/Engineer, and BI Lead/Engineer**.
*   **Client Roles**: Crucial client personnel generally include **Executive Leadership, Project Manager, Owners of Data Products/SMEs, Technical Architects, Database Administrators (DBAs), Application Owners, Functional/Technical Support Teams, and Cloud Administrators**.

### 8. Commercials

The financial terms of the engagement:

*   **Pricing Model**: Consistently structured as a **Fixed Bid/Fixed Fee** engagement.
*   **Resourcing Model**: Often employs an **Onshore-Offshore** delivery model to optimize cost and resource availability.
*   **Milestone Payment Schedule**: Payments are explicitly **tied to the completion and formal acceptance of specific deliverables or project milestones**.
*   **Expenses**: A clear delineation of **reimbursable expenses**, often requiring prior client approval, is typically included.