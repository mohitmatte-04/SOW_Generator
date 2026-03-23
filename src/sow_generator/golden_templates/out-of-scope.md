
### **Standardized "Golden Content" Framework: "Out of Scope" for Data Warehouse Migration Projects**

The following activities and responsibilities are **explicitly outside the scope of services** for this data warehouse migration engagement. This delineation is crucial to maintain focus, manage project boundaries, and ensure the efficient delivery of the agreed-upon services.

**Overarching Principle:**
*   **Any activity not explicitly mentioned** within the "Scope of Services" section of this SOW is considered out of scope.

#### **1. Core Infrastructure & Platform Management (Client Responsibility)**
These items typically fall under the client's operational responsibilities for their cloud environment.

*   **Cloud Platform Foundation Setup**: The initial establishment, configuration, and ongoing management of the Google Cloud Platform (GCP) or Azure foundation, including project provisioning, IAM roles and service accounts, VPC connectivity, networking configurations, and security approvals.
*   **General Infrastructure Provisioning & Assessment**: Any general infrastructure assessment, setup, or ongoing provisioning of platforms, tools, and underlying technologies not explicitly listed as a deliverable or activity within the "Scope of Services".
*   **Software Lifecycle Management**: Upgrades, patching, licensing, procurement, or enhancements of any existing systems (legacy or target), or any required third-party software/licenses.
*   **Managed Services & Ongoing Operations**: Day-to-day L1, L2, L3 managed support, long-term advisory and troubleshooting beyond the defined engagement and warranty periods. This also includes the establishment of comprehensive monitoring and alerting systems, Site Reliability Engineering (SRE) implementation, or Backup & Recovery strategies beyond basic connectivity/platform features.
*   **Cloud Observability Solutions**: Beyond basic connectivity or specified in-scope monitoring.
*   **FinOps Implementation**: Beyond the generation of FinOps reports if included in scope.

#### **2. Legacy System & Data Management (Client Responsibility / Not Migration Partner's Scope)**
This category clarifies that the service provider focuses on migration, not on fixing or rebuilding the legacy state or managing client-specific data governance.

*   **Legacy Code Analysis & Remediation**: Any in-depth analysis, modification, or defect fixing of **legacy system codes** or issues inherently arising from legacy data during the data validation process.
*   **Data Cleansing & Remediation**: Any data cleansing, remediation, or restructuring of source data, as the migration assumes data quality of source systems.
*   **Data Classification & Handling**: Identification, classification, or handling of Personally Identifiable Information (PII) beyond standard platform functionality or client-defined frameworks.
*   **Data Encryption/Decryption**: Beyond standard platform functionality or client-specified security designs.
*   **Legacy System Decommissioning**: The decommissioning, cutover, or sunsetting of any existing legacy systems or environments.
*   **Historical Data Extraction**: The primary process of extracting historical data from source systems to an intermediate staging layer (e.g., GCS bucket), unless explicitly defined as a service provider's responsibility within the "Scope of Services".
*   **Consolidation & Restructuring**: Consolidation of markets, platforms, schema, or code beyond a direct lift-and-shift approach.
*   **Data Verification**: General verification of data beyond specific data validation reports included in deliverables.

#### **3. New Development & Advanced Optimization**
The focus is on migration and modernization of *existing* capabilities, not introducing entirely new functionalities or extensive re-engineering.

*   **AI/ML Model Development**: Development, enhancement, or re-platforming of any new AI/ML models or data science activities, unless explicitly scoped for data science enablement.
*   **New Reporting Development**: Development of new reports, dashboards, or re-configuration of child/linked reports beyond repointing existing ones.
*   **Business Logic Changes**: Any changes to existing data models or business logic beyond ensuring functional equivalence as part of a lift-and-shift migration strategy.
*   **Performance Optimization**: Performance optimization or tuning beyond ensuring parity with the current system's performance or initial conversion. Further or advanced optimization typically requires a change request.
*   **Ad-Hoc Query Conversion**: Conversion of ad-hoc user queries or scripts not part of defined, in-scope workloads.

#### **4. Integration & DevOps (Unless Explicitly In-Scope)**
These activities are generally broad enterprise concerns and are out of scope unless precisely defined for the migration project.

*   **Third-Party Application Integration**: Integration with any upstream, downstream, or third-party application(s) other than those explicitly mentioned and detailed in the "Scope of Services".
*   **CI/CD & DevOps Implementation**: Setup, implementation, or enhancement of CI/CD pipelines or general DevOps activities.
*   **System Integration Interfaces**: General system integration and interfaces not directly tied to data warehouse migration.

#### **5. Training & Change Management (Client Responsibility)**
The service provider's role is to enable, not to manage organizational adoption.

*   **User Onboarding & Training**: User onboarding or training beyond structured knowledge transfer sessions and provided documentation.
*   **Organizational Change Management**: Designing, redesigning, or managing the customer's functional organization or internal change management processes.

#### **6. Specific Project Limitations & Exclusions**
These are project-specific boundaries that reinforce the SOW's contractual nature.

*   **Assessment-Specific Exclusions**: For assessment-only SOWs, no development, implementation, migration, or decommissioning efforts are included.
*   **Product Bugs & DCRs**: Remediation of product bugs, software defects, or design change requests (DCRs) for commercial software products (e.g., Microsoft products).
*   **Hardware Provision**: Provision of any project-specific hardware.
*   **Non-Production Data Migration**: Migration of data not in production or not explicitly captured within the defined in-scope volumetrics.
*   **Volumetric Changes**: Any increase or change in agreed-upon in-scope volumetrics will typically require a formal Change Request and will be priced and scheduled separately.
*   **Out-of-Scope Tooling**: Assessment of platforms, tools, or technologies other than those explicitly specified in the scope.

---

This framework, derived from analyzing numerous SOW documents, provides a robust baseline for crafting "Out of Scope" sections that are comprehensive, granular, and prevent potential misunderstandings. By clearly articulating these exclusions, we enhance the transparency and predictability of our data warehouse migration engagements, fostering stronger client relationships and more successful project outcomes.