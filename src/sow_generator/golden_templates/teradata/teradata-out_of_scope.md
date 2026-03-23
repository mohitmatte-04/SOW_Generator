### **Standardized "Golden Content" Framework: "Out of Scope" for Teradata Migration Projects**

The following activities and responsibilities are **explicitly outside the scope of services** for this Teradata migration engagement. This delineation is crucial to maintain focus, manage project boundaries, and ensure the efficient delivery of the agreed-upon services.

**Overarching Principle:**
*   **Any activity not explicitly mentioned** within the "Scope of Services" section of this SOW is considered out of scope.

#### **1. Core Infrastructure & Platform Management (Client Responsibility)**
These items typically fall under the client's operational responsibilities for their cloud environment, as the service provider's focus is on the data warehouse migration itself, not the underlying cloud platform's general administration.

*   **Cloud Platform Foundation Setup**: The initial establishment, configuration, and ongoing management of the Google Cloud Platform (GCP) or Azure foundation, including project provisioning, IAM roles and service accounts, VPC connectivity, networking configurations, and security approvals.
*   **General Infrastructure Assessment/Setup/Provisioning**: Any general infrastructure assessment, setup, or ongoing provisioning of platforms, tools, and underlying technologies not explicitly listed as a deliverable or activity within the "Scope of Services". This includes provision of project-specific hardware.
*   **Software Lifecycle Management**: Upgrades, patching, or enhancements of any existing systems (legacy or target), or any required third-party software/licenses. This also covers procurement and licensing of software.
*   **Managed Services & Ongoing Operations**: Day-to-day L1, L2, L3 managed support, or long-term advisory and troubleshooting beyond the defined engagement and warranty periods.
*   **Monitoring & Alerting/SRE Implementation**: Setup of comprehensive monitoring and alerting systems, Site Reliability Engineering (SRE) implementation, or Backup & Recovery strategies beyond basic connectivity/platform features.
*   **Cloud Observability Solutions**: Beyond basic connectivity or specified in-scope monitoring.
*   **FinOps Implementation**: Beyond the generation of FinOps reports if specifically included in scope.

#### **2. Legacy System & Data Management (Client Responsibility / Not Migration Partner's Scope)**
This category clarifies that the service provider's role is to migrate, not to remediate fundamental issues within the legacy environment or manage client-specific data complexities beyond migration.

*   **Legacy Code Analysis & Remediation**: Any in-depth analysis, modification, or defect fixing of **legacy system codes** or issues inherently arising from legacy data during the data validation process. This also includes changes to consumption applications beyond the legacy environment.
*   **Data Cleansing, Remediation, or Restructuring**: Any data cleansing, remediation, or restructuring of source data, as the migration assumes the quality of source systems.
*   **Data Classification & Handling**: Identification, classification, or handling of Personally Identifiable Information (PII) beyond standard platform functionality or client-defined frameworks.
*   **Data Encryption/Decryption**: Beyond standard platform functionality or client-specified security designs.
*   **Legacy System Decommissioning**: The decommissioning, cutover, or sunsetting of any existing legacy systems or environments.
*   **Historical Data Extraction**: The primary process of extracting historical data from source systems to an intermediate staging layer (e.g., GCS bucket), unless explicitly defined as a service provider's responsibility within the "Scope of Services".
*   **Consolidation & Restructuring**: Consolidation of markets, platforms, schema, or code beyond a direct lift-and-shift approach.
*   **Data Verification**: General verification of data beyond specific data validation reports included in deliverables.
*   **Code Freeze Violations**: Any changes to code after an agreed-upon code freeze period.

#### **3. New Development & Advanced Optimization**
The project typically focuses on migrating existing functionalities, not introducing entirely new capabilities or extensive re-engineering that goes beyond the lift-and-shift approach.

*   **AI/ML Model Development/Enhancement**: Development or enhancement of any new AI/ML models or data science activities, unless explicitly specified in scope. This includes migration of historical Jupyter notebooks.
*   **New Report/Dashboard Development**: Development of new reports, dashboards, or re-configuration of child/linked reports beyond repointing existing ones, or specific reports not mentioned in volumetrics.
*   **Business Logic Changes**: Any changes to existing data models or business logic beyond ensuring functional equivalence as part of a lift-and-shift migration strategy. This includes UI/UX or application/API business logic changes.
*   **Performance Optimization/Tuning**: Performance optimization or tuning beyond ensuring parity with the current system's performance or initial conversion.
*   **Conversion of Ad-Hoc Queries/User-Developed Scripts**: Conversion of ad-hoc user queries or scripts not part of defined, in-scope workloads.
*   **Custom Analytical Application Development**: Custom development of new analytical applications.
*   **Proof of Concept (POC)/Value Implementation**: Any proof of concept or value implementation not explicitly stated as in-scope.

#### **4. Integration & DevOps (Unless Explicitly In-Scope)**
These activities are generally broad enterprise concerns and are out of scope unless precisely defined for the migration project.

*   **Integration with External Applications**: Integration with any upstream or downstream application(s) or third-party applications other than those explicitly mentioned and detailed in the "Scope of Services" [12. 315, 344, 384, 409, 459, 545, 647, 669, 777]. This includes configuring and testing SSO.
*   **CI/CD & DevOps Implementation**: Setup, implementation, or enhancement of CI/CD pipelines or general DevOps activities.

#### **5. Training & Change Management (Client Responsibility)**
The service provider's role is to enable the client to manage the new platform, not to manage organizational adoption or broader training.

*   **User Onboarding & Training**: User onboarding or training beyond structured knowledge transfer sessions and provided documentation.
*   **Organizational Change Management**: Designing, redesigning, or managing the customer's functional organization or internal change management processes (e.g., ITIL, communication to internal stakeholders).

#### **6. Project-Specific Limitations & Exclusions**
These are project-specific boundaries that reinforce the SOW's contractual nature and guard against common expansion points.

*   **Assessment of non-in-scope platforms/tools**: Assessment of platforms, tools, or technologies other than those explicitly mentioned in-scope.
*   **No Development/Implementation/Migration (for assessment-only SOWs)**: For assessment-focused SOWs, no development, implementation, migration, or decommissioning efforts are included.
*   **Volumetric Changes**: Any increase or change in agreed-upon in-scope volumetrics will typically require a formal Change Request.
*   **Warranty Exclusions**: Warranty explicitly excludes issues arising from out-of-scope workloads, upstream data quality, post-migration changes made by the client, or outside the active warranty period.
*   **Specific Data/Domain Exclusions**: Migration of domains outside explicitly defined scope (e.g., Sales, Customer, Inventory, and Finance), or migration of any local databases at the market level.
*   **Production Deployment**: Deployment to production environment by the service provider may be out of scope, or limited to support, with client performing the actual deployment.
*   **Report Functional Validation/Comparison**: Functional validation for reports, or report comparison between legacy and target systems beyond defined limits.
*   **Non-Production Data Migration**: Migration of data not captured in volumetrics or in non-production environments.
*   **Real-time Streaming Implementation**: Automation or implementation of real-time streaming ingestion pipelines, unless explicitly in scope (e.g., Pub/Sub streaming implementation).
*   **Framework Enhancements**: Enhancements, modifications, or bug fixes to specific client frameworks (e.g., Cerebro, CDMNext, AbInitio).
*   **External Data Sources**: Any addition of new data sources, or new data source onboarding beyond existing source systems.
*   **Specific Technology Exclusions**: Migration of any other technology not explicitly mentioned in the scope.

---