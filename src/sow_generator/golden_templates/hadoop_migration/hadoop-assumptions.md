### **Golden Content Framework: Standardized Assumptions for Hadoop to GCP Migration Projects**

These assumptions are logically organized into categories, reflecting the multifaceted nature of large-scale data migrations.

---

#### **I. Technical Assumptions**
These assumptions pertain to the migration approach, architectural components, code conversion, and functional parity expectations.

*   **Migration Strategy Adherence**: The migration will primarily follow a **lift-and-shift approach**, ensuring **minimal or no changes to the existing data model, business logic, or data types**. Data type mappings will be adjusted solely for GCP compatibility without altering the underlying business logic.
*   **Code Conversion Parity**: All converted code and workflows are assumed to retain the **same business logic and possess similar or compatible data types and schemas** as their legacy Hadoop counterparts.
*   **Source Workload Characteristics**: Specific source workload components are assumed to be handled in a predefined manner in GCP. For instance:
    *   A defined number of tables (e.g., 500) that are direct copies of existing source (WS) tables will be implemented as 1:1 views in GCP.
    *   Tables (e.g., 750) created within the target environment (SA) and sourcing data from other domain tables are assumed to follow existing patterns.
    *   A specific count of tables (e.g., 200) with existing data ingestion pipelines (e.g., Connexio or FTAAS) will require setup in GCP, either through a pointing change or parallel pipelines.
    *   Data ingestion or transformation logic written in Bash scripts, Python, or Java for a specified number of tables (e.g., 50) will be ported "as-is" to GCP.
*   **Orchestration Tooling**: Legacy orchestration (e.g., Apache Airflow, Oozie) in the source environment is assumed to be fully convertible to **Cloud Composer** in the target GCP environment.
*   **Developed Pipelines Compatibility**: All newly developed pipelines are assumed to be compatible with any existing frameworks previously developed by the customer.

---

#### **II. Operational Assumptions**
These cover project management, client-side processes, approvals, User Acceptance Testing (UAT), deployment responsibilities, and collaborative working.

*   **Client Responsiveness**: The client is assumed to provide **timely responses** (e.g., within 5 business days) for change requests, approvals, feedback, clarifications, and sign-offs on designs and deliverables.
*   **Client Participation & Approvals**: The client will **actively participate** in all key project meetings, workshops, and reviews, providing essential feedback and ensuring alignment with business objectives. Formal **validation and approval of deliverables at key milestones** by the client are assumed.
*   **Testing & Validation Responsibility**: The client's team is responsible for **executing and completing testing and validation** of migrated workloads within the agreed-upon scoped environments.
*   **Production Deployment Responsibility**: The client will **assume ultimate responsibility for executing production deployments** of migrated workloads.
*   **Post-Migration Management**: The client will **manage and oversee ongoing technical support and maintenance** of the migrated environment post-engagement.
*   **Code Review and Approval**: Established code review and pull request (PR) approval processes will be adhered to.

---

#### **III. Data Assumptions**
These assumptions address the quality, availability, and provisioning of data, as well as validation processes.

*   **Data Quality & Accuracy**: The data residing in the Hadoop environment (or other legacy systems) is assumed to be **complete, accurate, and suitable for migration and subsequent testing**, with no significant data quality issues that would impede the migration or testing efforts.
*   **Test Data Provision**: The client will provide **production-grade test data** (sanitized as necessary) for use in lower environments to facilitate historical data migration and comprehensive testing.
*   **Source Data Integrity**: The client is responsible for the **accuracy, completeness, and correctness of data** in their source tables (e.g., WS tables) that feed new target jobs/tables. The vendor will not be held accountable for issues arising from incorrect or incomplete data originating from these source tables. Any data quality issues identified in source (WS) tables impacting target (SA) tables are assumed to be resolved by the client.
*   **Compressed Data Provision**: Data will be provided in a **compressed format** to optimize load times and prevent adverse impacts on project timelines.
*   **Historical Data Integrity**: Any data corruption identified post-loading and validation will be addressed, but on-premise data changes due to business reasons are explicitly outside the scope of vendor responsibility.
*   **Inactive Objects Handling**: For inactive objects, the vendor will perform an "as-is" migration, limiting validation to row-count testing.

---

#### **IV. Infrastructure Assumptions**
These delineate the readiness, setup, connectivity, and ongoing management of the GCP environment and supporting infrastructure.

*   **GCP Cloud Foundation Readiness**: The **GCP Cloud Foundation environment is assumed to be already established, provisioned, and fully accessible** to the vendor's team for the execution of all in-scope activities. Any identified gaps in the infrastructure will be addressed and filled by the client.
*   **Client Provisioning of GCP Resources**: The client is responsible for **provisioning all necessary GCP projects, IAM roles, service accounts, and VPC connectivity**. This includes the pre-creation and configuration of GCS buckets.
*   **Network Connectivity**: **Sufficient network connectivity is assumed to exist and be operational between the on-premises Hadoop environment and GCP**. Furthermore, there will be **no disruption** in the provision of critical resources or infrastructure (e.g., VDI, access, network bandwidth) essential for project execution.
*   **Pelican Installation**: The vendor's proprietary data validation tool, Pelican, will be **installed and operational within the customer's GCP environment**.
*   **Required Infrastructure for Vendor Tools**: The client will provide all necessary infrastructure (e.g., VMs) and security approvals for the vendor's accelerators (e.g., Pelican) at no additional cost.

---

#### **V. Security Assumptions**
These address access management, data privacy, and compliance-related responsibilities.

*   **Access Provisioning**: The client will provide all **necessary security approvals and access rights** for vendor resources and accelerators required for project execution.
*   **IAM & Security Policies**: The vendor will **not be responsible for designing or implementing the client's comprehensive IAM, RBAC, or enterprise-wide security policies**, limiting their scope to the access directly required for the migration project.
*   **PII/Sensitive Data Handling**: The client is responsible for providing mappings of tables to portfolios and classifications into secure/unsecure zones, particularly for sensitive data.

---

#### **VI. Dependencies & Resources Assumptions**
These cover client-provided resources, access, subject matter expertise, and external system readiness.

*   **Access Provisioning**: The client will provide **all necessary access** to their existing Hadoop environment, GCP environment, in-scope tools/technologies, GIT repository, and relevant project documentation.
*   **SME Availability**: The client will ensure the availability of **dedicated subject matter experts (SMEs)**, including system administrators, technical and functional SMEs, database experts, and application owners, to actively support working sessions, clarify requirements, and resolve issues throughout the project lifecycle.
*   **Documentation Provision**: The client will furnish essential documentation, such as system architecture diagrams, data lineage information, and ETL/ELT job scripts.
*   **External Coordination**: The client will proactively facilitate decision-making and ensure the timely resolution of issues involving other vendors or business partners.
*   **Source Version Agreement**: The client and vendor will mutually agree upon the source version of the code (encompassing the entire end-to-end pipeline) at the inception of each migration phase. Any changes introduced to the code after the conversion process begins will fall outside the scope of this migration.
*   **Code Freeze**: The client will implement a **code freeze** in the legacy environment for a mutually agreed-upon period, covering all end-to-end pipelines, prior to the commencement of each migration sprint. Any changes introduced after this code freeze period will necessitate a formal Change Request.
*   **Connectivity Details**: The client will provide comprehensive source and target connection details for all relevant pipelines (e.g., Connexio and FTaaS).
*   **Generic Credentials**: Generic credentials will be established within the FTaaS framework.

---

#### **VII. Governance & Scope Management Assumptions**
These address change management, project boundaries, and overall project governance structures.

*   **Change Control**: Any modifications to the defined **scope or volumetrics** beyond agreed-upon thresholds will necessitate a formal change request process and are considered outside the initial scope.
*   **Move Group Agreement**: The classification and prioritization of move groups will be jointly reviewed and agreed upon by the client and Google, with any subsequent changes requiring mutual agreement.
*   **No Changes to Findings**: There will be **no changes in the discovery findings** after the move group delivery activities have commenced.
