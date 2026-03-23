### **Golden Content Framework: Standardized Assumptions for Snowflake to GCP Migration Projects**

These assumptions are logically organized into categories, reflecting the multifaceted nature of large-scale data migrations.

---

#### **I. Technical Assumptions**
These assumptions pertain to the migration approach, architectural components, code conversion, and functional parity expectations of the migrated solution.

*   **Migration Strategy**: The migration will primarily follow a **lift-and-shift approach with minimal or no changes to the existing data model, business logic, or data types/schemas**. Data type mappings will be adjusted solely for target platform compatibility without altering underlying business logic.
*   **Code Conversion Parity**: All converted code and workflows are assumed to retain the **same business logic and possess similar or compatible data types and schemas** as their legacy Snowflake counterparts.
*   **Snowflake-Specific Feature Handling**: Non-standard Snowflake features (e.g., Tasks, Streams) may require re-design or re-implementation in compliance with BigQuery and GCP-native capabilities and will be addressed in collaboration with the client.
*   **Snowflake DDL Conversion**: Only Snowflake base table DDLs will be converted to BigQuery equivalents; it is assumed that dbt will recreate transient and dynamic tables during model execution as per existing transformations.
*   **Source System Stability**: Any upgrades, patching, or changes to source systems (e.g., Kafka-0) will **not require changes in the Data/file format and interfaces** in the target GCP environment. Similarly, there will be no changes to the structures of existing elements/tags in XML/JSON.
*   **Peripheral System Behavior**: Any upgrades or patching of peripheral systems will **not require a change in the Data/file format and interfaces**. Enhancements or modifications to code/framework/Data model/feature of any peripheral system are considered out of scope.
*   **Reporting/BI Tool Compatibility**: The client is responsible for ensuring their BI reporting tool versions (e.g., Power BI, Crystal, ThoughtSpot, Tableau, MicroStrategy) are **compatible with BigQuery**. Any required upgrades for these tools are the client's responsibility. Changes in existing reports and/or BI tools will not require a change in the Data format and interfaces.
*   **Performance Optimization**: Performance tuning or query cost optimization in BigQuery/target platform will be considered a post-migration optimization activity and is **out of scope for the migration itself**, with acceptance criteria strictly based on data parity and query equivalence. Non-BI reporting BigQuery SQL will be performance tuned to perform as well as or better than Teradata.
*   **Data Encryption**: Encryption or decryption of data is not included beyond publicly available Snowflake and BigQuery functionality.
*   **Ab Initio Workload Replatforming**: The replatforming and/or modernization of Ab Initio infrastructure is excluded beyond what is covered in the scope.
*   **SSIS Workload Handling**: It is assumed that SSIS is only used for data transformation and is not connected to any direct source system.
*   **Databricks Instance Sizing**: The number of Databricks instances is assumed by considering 1 instance for Snowflake, 1 for Redshift, and 1 for other warehouses.
*   **Lambda Ingestion Jobs**: A specific number of Lambda Ingestion jobs (e.g., 100) are being considered for the migration scope.
*   **Data Quality Rule Location**: All the Data quality rules/checks are assumed to be written in Informatica, Lightup, and Collibra only.

---

#### **II. Operational Assumptions**
These cover project management, client responsibilities in supporting project activities, UAT, deployment, and post-migration handovers.

*   **Client Responsiveness**: The client will provide **timely responses** (e.g., within 3 or 5 business days) for change requests, approvals, feedback, clarifications, and sign-offs on designs and deliverables. Delays will extend project timelines.
*   **User Acceptance Testing (UAT)**: The client team is responsible for **performing and completing UAT** within an agreed-upon timeframe (e.g., 3, 5, or 10 business days) after delivery by the vendor. The vendor will provide necessary support during UAT.
*   **Production Deployment**: The client is ultimately **responsible for executing production deployments** of code and reports. The vendor will provide remote support for bug fixing. The vendor is not responsible for the client's internal change management or release approvals.
*   **Vendor Accountability**: The vendor is not responsible for bug fixing in third-party SaaS platforms (e.g., Fivetran, Looker, Prefect).
*   **Client Bug Fixing**: The client will perform investigation activity on tickets/defects raised in production and provide detailed analysis to the vendor for defect fixing.
*   **Code Review and Approval**: Converted code will be reviewed with the client team (up to 2 reviews), and the client will provide sign-off within 3 business days.
*   **Client Project Management**: The client is responsible for business change management (Communication, Coordination, Identification & Execution).
*   **Vendor Reliance on Client Data/Information**: The vendor may rely upon the data and information provided by the customer and its agents and shall not have any responsibility for independently verifying its accuracy or completeness. The customer will promptly resolve any problems or issues identified by the vendor regarding existing applications, software, systems, and hardware.
*   **Warranty Scope**: Warranty coverage applies only to objects/workloads delivered in the engagement; issues arising from out-of-scope workloads, upstream data quality, or post-migration changes by the client are excluded.

---

#### **III. Data Assumptions**
These focus on the quality, availability, and provisioning of data, as well as validation processes.

*   **Data Quality & Accuracy**: The data in the Snowflake environment (or other legacy systems) is assumed to be **complete, accurate, and fit for migration and testing**, with no significant data quality issues that could impact the migration or testing. In-scope datasets already exist and are accessible, requiring **no data cleansing, remediation, or restructuring**.
*   **Test Data Provision**: The client will provide **production-grade test data** (sanitized if required) for use in lower environments to support historical data migration and testing.
*   **Historical Data Validation**: Historical data validation of a set period is to be defined during testing strategy discussions. Pelican will be used to validate two agreed incremental cycles; extended validation cycles require a Change Request.
*   **Volumetric Adherence**: The vendor's estimates are based on the volumetrics provided by the client. The engagement scope is limited to the defined volumetric boundaries. Any data not captured in volumetrics or in non-production environments is excluded to avoid costs.
*   **Metadata Accuracy**: Lineage and optimization analysis will rely on metadata, schema definitions, query logs, and system usage statistics provided by the client.
*   **Source Data Issues**: Any issues or errors in the legacy data can delay the timelines of the project. The client is responsible for triaging and fixing any errors caused by the legacy data within a defined timeframe (e.g., 2 business days).

---

#### **IV. Infrastructure Assumptions**
These cover the readiness, setup, connectivity, and ongoing management of the GCP environment and supporting infrastructure.

*   **Cloud Foundation Readiness**: The **GCP Cloud Foundation environment is assumed to be already in place, provisioned, and accessible** to the vendor's team for execution of all in-scope activities. Any identified gaps will be filled by the client.
*   **Client Provisioning of GCP Resources**: The client is responsible for **provisioning necessary GCP projects, IAM roles, service accounts, and VPC connectivity**. Required APIs and services (e.g., BigQuery, GCS, Dataflow, Datastream) will be enabled prior to project kickoff. The client is responsible for provisioning and maintaining the required Google Cloud environments.
*   **Network Connectivity**: **Sufficient network connectivity is assumed to exist and be operational between the legacy environment (e.g., AWS/Snowflake) and GCP**, including any dedicated interconnects required for historical data transfer. The client is responsible for ensuring optimal connectivity and managing any performance issues arising from network bottlenecks. A minimum sustained network bandwidth (e.g., 1 Gbps) is assumed.
*   **Pelican Installation**: The vendor's proprietary data validation tool, Pelican, will be **installed and operational within the customer's GCP environment**. The client is responsible for provisioning the necessary infrastructure (e.g., VMs) and security approvals for Pelican installation.
*   **CI/CD Management**: The client will provision and maintain the CI/CD infrastructure. Delays arising from incomplete CI/CD environment readiness or insufficient permissions will extend the project timeline.
*   **Client Provisioning of Source Data**: For 3rd party file-based systems, the client will provide files into GCS, and file formats will be BQLoad supported. Data ingestion from source systems to GCS will be the client’s responsibility (e.g., using an Octopus framework).
*   **Kafka Connectivity**: Establishing connectivity between Kafka and GCP for data ingestion (e.g., Kafka-0 to GCP BigQuery) is typically the client's responsibility.

---

#### **V. Security Assumptions**
These address access management, data privacy, and compliance-related responsibilities.

*   **Access Management**: Access granted to the vendor will be **governed by the client's security policies, identity management systems, and approval processes**. The client will provide necessary security approvals and access rights for vendor resources and accelerators.
*   **IAM Design**: The vendor will **not design or implement the client's IAM, RBAC, or enterprise security policies** beyond the access necessary for the migration project.
*   **Data Privacy Compliance**: The client is responsible for ensuring **compliance with all data privacy and regulatory frameworks** (e.g., GDPR, CCPA). The vendor will not handle classification or remediation of PII/PCI data. The client will procure any additional licenses required for data encryption, tokenization, or other security tools not already provisioned. No extra security or compliance implementations beyond the Customer’s existing standards.

---

#### **VI. Dependencies & Resources Assumptions**
These relate to client-provided resources, access, subject matter expertise, and external system readiness.

*   **Access Provisioning**: The client will provide **necessary access** to their GCP environment, legacy Snowflake environment (Dev/QA/Prod-readonly), in-scope tools (e.g., dbt, Looker, Streamlit, Fivetran), incident management systems (e.g., JIRA), document portals (e.g., Confluence), VPN/VDI, dedicated interconnect, all in-scope codes/scripts/DDLs, and existing code deployment tools (e.g., Bitbucket, GIT).
*   **SME Availability**: The client will provide **dedicated subject matter experts (SMEs)** (e.g., system admins, technical and functional SMEs, database experts, application owners, architects) with sufficient business hours to support working sessions, provide clarifications, and resolve issues throughout the project duration.
*   **Upstream/Downstream Dependencies**: The client is responsible for ensuring that all **upstream systems and downstream consumers are available and compatible** for the migration timeline. Delays arising from external dependencies are outside the vendor’s control and will warrant a Change Request.
*   **Third-Party Tool Licensing**: The client is responsible for ensuring that any third-party tools (e.g., Fivetran) have **valid licenses and sufficient capacity** to support reconfiguration to BigQuery.
*   **Code Freeze Policy**: The client will implement a **code freeze** for a mutually agreed period in the legacy environment, covering all end-to-end pipelines, before the start of each migration sprint. Any changes after the code freeze period will be handled through a change request process.
*   **Code Versioning**: The client will provide the code version (e.x. GIT repository).
*   **Parallel Development**: Any parallel development or overlapping changes by client teams to in-scope code or dbt models during migration will void parity guarantees unless mutually agreed in writing.
*   **Client Provision of System Stats**: The client will provide the stats of the legacy system in case stats need to be compared with converted code execution on Google Cloud.
*   **Key Critical Dates**: The client is expected to adhere to critical dates and timelines for resource onboarding, access to infrastructure, design/migration plan approval, and historical data extraction. Delays will result in project timeline adjustments.
*   **No Production Outages**: It is assumed that no production outages or scheduled maintenance windows will impact data availability during migration windows.

---

#### **VII. Governance & Scope Management Assumptions**
These address how changes are managed, project scope defined, and overall project governance structures.

*   **Change Control**: Any change in the described scope, an increase in volumetrics beyond a defined threshold (e.g., 10%), additional requirements, or changes to assumptions will be treated as a **formal Change Request (CR)** and priced separately.
*   **Scope Volumetrics**: The vendor's estimates and activities are based on the **volumetrics provided by the client** in the SOW appendices. Any increase in these volumetrics beyond the agreed scope (e.g., >10%) will trigger a Change Request.
*   **Project Timelines**: The client is expected to **adhere to critical dates and timelines** for resource onboarding, access provision, design approval, cross-cloud interconnect, and historical data extract. Delays will result in project timeline adjustments via Change Management.
*   **Advanced Optimization Out of Scope**: Any advanced optimization (cost tuning, slot reservations, re-modeling) is out of scope.
*   **No Changes to Discovery Findings**: There will be no changes in the discovery findings after the move group delivery activities start.
*   **Code Freeze Adherence**: Any changes in the code/scripts of the use case/data domain on Legacy Environment, post agreed code freeze dates for the sprint, will be considered out of scope.