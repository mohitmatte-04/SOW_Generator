### **Golden Content Framework: Standardized Assumptions for Teradata to GCP Migration Projects**

These assumptions are logically organized into categories, reflecting the multifaceted nature of large-scale data migrations.

---

#### **I. Technical Assumptions**
These assumptions pertain to the migration approach, architectural components, code conversion, and functional parity expectations of the migrated solution.

*   **Migration Strategy**: The migration will primarily follow a **lift-and-shift approach with minimal or no changes to the existing data model, business logic, or data types/schemas**. Data type mappings will be adjusted solely for target platform compatibility without altering underlying business logic.
*   **Code Conversion Parity**: All converted code and workflows are assumed to retain the **same business logic and possess similar or compatible data types and schemas** as their legacy Teradata counterparts.
*   **Orchestration Tooling**: Legacy orchestration (e.g., Apache Airflow, Control-M, Autosys, Oozie) in the source environment is assumed to be fully convertible to **Cloud Composer** or other native cloud orchestration services.
*   **Source Workload Characteristics**: Specific source workload components are assumed to be handled in a predefined manner in the target platform, with certain tables implemented as 1:1 views or undergoing specific porting/conversion based on their original scripting languages.
*   **Reporting/BI Tool Compatibility**: The client is responsible for ensuring their BI reporting tools (e.g., MicroStrategy, Tableau, SAP BO) are **compatible with BigQuery/target platform**. Any required upgrades for these tools are the client's responsibility. If a specific tool (e.g., Microstrategy) is being considered for migration to the cloud, it needs to be handled either prior to project start or after project completion to avoid delays.
*   **Peripheral System Behavior**: Peripheral systems (e.g., Java Web Apps, Python ML Apps, R Shiny Applications, Self Service Datalabs) will generally continue to run on their existing infrastructure, with the vendor's scope limited to providing information on access setup for connection between the target platform and these systems. Any changes to the codebase or jobs of these peripheral systems are out of scope.
*   **Performance Optimization**: Performance tuning or query cost optimization in BigQuery/target platform will be considered a post-migration optimization activity and is **out of scope for the migration itself**, with acceptance criteria strictly based on data parity and query equivalence, not performance benchmarking. Non-BI reporting BigQuery SQL will be performance tuned to perform as well as or better than Teradata.
*   **Data Encryption**: Encryption or decryption of data is not included beyond publicly available cloud service functionality.

---

#### **II. Operational Assumptions**
These cover project management, client responsibilities in supporting project activities, UAT, deployment, and post-migration handovers.

*   **Client Responsiveness**: The client will provide **timely responses** (e.g., within 3 or 5 business days) to change order requests, approvals, feedback, clarifications, and sign-offs on designs and deliverables. Delays will extend project timelines.
*   **User Acceptance Testing (UAT)**: The client team is responsible for **performing and completing UAT** within an agreed-upon timeframe (e.g., 3 or 5 business days) after delivery by the vendor. The vendor will provide necessary support during UAT.
*   **Production Deployment**: The client is ultimately **responsible for executing production deployments** of code and reports, with the vendor providing remote support for bug fixing. The vendor is not responsible for the client's internal change management or release approvals.
*   **Remote Work**: Development activities will be performed from offshore (e.g., Datametica, India Office).
*   **Client Project Management**: The client is responsible for assigning a dedicated project manager and handling all project management and change management duties between the contractor and the end customer. Client steering committee or similar body for timely decision-making and issue resolution.
*   **Post-Migration Management**: The client will **manage and oversee ongoing technical support and maintenance** of the migrated environment post-engagement.
*   **Warranty Scope**: Warranty coverage applies only to objects/workloads delivered in the engagement; issues arising from out-of-scope workloads, upstream data quality, or post-migration changes by the client are excluded.
*   **Code Review and Approval**: Converted code will be reviewed with the client team (up to 2 reviews), and client will provide sign-off within 3 business days.

---

#### **III. Data Assumptions**
These focus on the characteristics and availability of data, as well as validation processes.

*   **Data Quality & Accuracy**: The data in the Teradata environment (or other legacy systems) is assumed to be **complete, accurate, and fit for migration and testing**, with no significant data quality issues that could impact the migration or testing. The client is responsible for fixing any issues or errors found in source/legacy data within a defined timeframe (e.g., 2 business days).
*   **Test Data Provision**: The client will provide **production-grade test data** (sanitized if required) for use in lower environments (e.g., UAT) to support historical data migration and testing. Test data availability in lower environments for the EM team is assumed.
*   **Metadata & Lineage**: Lineage and optimization analysis relies on metadata, schema definitions, query logs, and system usage statistics provided by the client.
*   **Inactive Objects Handling**: For inactive objects, the vendor will perform an "as-is" migration, limiting validation to row-count testing.
*   **Source Data Integrity**: The client is responsible for the accuracy, completeness, and correctness of data in their source tables that feed new target jobs/tables.
*   **Data Cleansing**: In-scope datasets are assumed to already exist and be accessible within the client's environment and **do not require data cleansing, remediation, or restructuring**.

---

#### **IV. Infrastructure Assumptions**
These cover the readiness and configuration of the target cloud environment and connectivity.

*   **Cloud Foundation Setup**: The **GCP Cloud Foundation environment is assumed to be already in place, provisioned, and accessible** to the vendor's team for execution of all in-scope activities. Any identified gaps will be filled by the client. For Databricks migrations, the Databricks environment setup is assumed to be handled by the client.
*   **GCP Project & Service Provisioning**: The client is responsible for **provisioning necessary GCP projects, IAM roles, service accounts, and VPC connectivity**. Required APIs and services will be enabled prior to project kickoff.
*   **Network Connectivity**: **Sufficient network connectivity is assumed to exist and be operational between the legacy environment (e.g., on-premises Teradata) and GCP**, including any dedicated interconnects required for historical data transfer. The client is responsible for ensuring optimal connectivity and managing any performance issues arising from network bottlenecks. A minimum sustained network bandwidth (e.g., 100 GBPS) between source and target environments is often assumed for efficient historical data migration.
*   **Pelican Installation**: The vendor's proprietary data validation tool, Pelican, will be **installed and operational within the customer's GCP environment**. The client is responsible for provisioning the necessary infrastructure (e.g., VMs) and security approvals for Pelican installation.
*   **CI/CD Management**: The client is responsible for **setting up and handling CI/CD infrastructure and processes** for the project. Delays due to incomplete CI/CD environment readiness or insufficient permissions will extend the project timeline. The vendor will comply with the client's existing code deployment process and tools.
*   **Client Provisioning of Source Data**: The client will make historical and incremental data available in GCS buckets. For 3rd party file-based systems, client provides files into GCS, and file formats will be BQLoad supported.

---

#### **V. Security Assumptions**
These address access management, data privacy, and compliance.

*   **Access Management**: Access granted to the vendor will be **governed by the client's security policies, identity management systems, and approval processes**. The client will provide necessary security approvals and access rights for vendor resources and accelerators.
*   **IAM Design**: The vendor will **not design or implement the client's IAM, RBAC, or enterprise security policies** beyond the access necessary for the migration project.
*   **Data Privacy Compliance**: The client is responsible for ensuring **compliance with all data privacy and regulatory frameworks** (e.g., GDPR, CCPA). The vendor will not handle classification or remediation of PII/PCI data. Client is responsible for providing details on redacted columns to enable testing.

---

#### **VI. Dependencies & Resources Assumptions**
These relate to client-provided resources, access, and subject matter expertise.

*   **Access Provisioning**: The client will provide **necessary access** to their GCP environment, legacy Teradata environment (Dev/QA/Prod-readonly), in-scope tools (e.g., Informatica, Datastage, Alteryx, BI Tools, Python Apps), incident management systems (e.g., JIRA), document portals (e.g., Confluence), VPN/VDI, dedicated interconnect, all in-scope codes/scripts/DDLs, and existing code deployment tools (e.g., Bitbucket, GIT).
*   **SME Availability**: The client will provide **dedicated subject matter experts (SMEs)** (e.g., system admins, technical and functional SMEs, database experts, application owners, architects) with sufficient business hours to support working sessions, provide clarifications, and resolve issues throughout the project duration.
*   **Extraction Utilities**: The client will execute vendor-provided extraction utilities and share extracted metadata outputs.
*   **Upstream/Downstream Dependencies**: The client is responsible for ensuring that all **upstream systems and downstream consumers are available and compatible** for the migration timeline. Delays arising from external dependencies will trigger a Change Request. The client will resolve issues and coordinate matters related to any other vendor/business partner.
*   **Third-Party Tool Licensing**: The client is responsible for ensuring that any third-party tools (e.g., Fivetran) have **valid licenses and sufficient capacity** to support reconfiguration. The client procures any additional licenses required for data encryption, tokenization, or other security tools.
*   **Source Version Agreement**: The client and vendor will mutually agree on the source version of the code (all end-to-end pipelines) to be considered at the start of each phase. Any changes to code after conversion starts will not be covered.
*   **Code Freeze Policy**: The client will implement a **code freeze** for a mutually agreed period in the legacy environment, covering all end-to-end pipelines, before the start of each migration sprint. Any changes after the code freeze period will be handled through a change request process.

---

#### **VII. Governance & Scope Management Assumptions**
These address how changes are managed, project scope defined, and overall project governance.

*   **Change Control**: Any change in the described scope, an increase in volumetrics beyond a defined threshold (e.g., 10%), additional requirements, or changes to assumptions will be treated as a **formal Change Request (CR)** and priced separately.
*   **Scope Volumetrics**: The vendor's estimates and activities are based on the **volumetrics provided by the client** in the SOW appendices. Any increase in these volumetrics beyond the agreed scope will trigger a Change Request.
*   **Project Timelines**: The client is expected to **adhere to critical dates and timelines** for resource onboarding, access provision, design approval, cross-cloud interconnect, and historical data extract. Delays will result in project timeline adjustments via Change Management.
*   **Parallel Development**: Any parallel development or overlapping changes by client teams to in-scope code or models during migration will void parity guarantees unless mutually agreed upon in writing.
*   **Communication**: All project communication and documentation will be carried out in a mutually agreed language (e.g., English).
*   **Program Oversight**: A client steering committee or similar body will be responsible for driving timely decision-making and providing resolution to critical issues within a defined timeframe (e.g., 48 hours).
*   **Vendor's IP Usage**: The vendor's proprietary tools (e.g., Pelican, Raven) will be used for specific activities (e.g., code conversion, data validation). Access to these tools may require a separate subscription or may be limited to the duration of the SOW.