### **Golden Content Framework: "Out of Scope" for Teradata Migration Projects**

This framework categorizes typical exclusions across the project lifecycle, ensuring logical organization and alignment with standard project phases.

#### **I. Project Initiation & Governance**
These exclusions underscore the importance of disciplined project management and set boundaries on evolving requirements and administrative overhead.
*   **Changes in Scope or Volumetrics**: Any alterations to the project's defined scope or an increase in volumetrics beyond mutually agreed-upon thresholds are explicitly out of scope and require a formal change request process.
*   **General Third-Party Licensing/Integration**: Activities related to any 3rd party licensing or general integration not specifically detailed within the in-scope deliverables are excluded.
*   **Post-Deployment Legacy Code Merging**: Handling or merging of legacy code changes in the new environment post-deployment is out of scope.

#### **II. Infrastructure & Platform Management**
The provisioning, configuration, and ongoing management of the underlying cloud environment are consistently designated as the client's responsibility.
*   **GCP/Cloud Foundation Setup**: The establishment, configuration, and provisioning of the core Google Cloud Platform environment (e.g., foundational services, VM provisioning, service enablement) are explicitly out of scope. This includes basic Databricks environment setup for Teradata to Databricks migrations.
*   **CI/CD & DevOps Implementation**: Activities related to Continuous Integration/Continuous Deployment (CI/CD) or broader DevOps practices (e.g., Jenkins Pipeline enhancements) are typically excluded.
*   **Software Upgrades/Patching**: Any upgrades or patching of existing system software, whether in the source (legacy) or target (GCP/Databricks) environment, are outside the migration scope. This also extends to product upgrades, bugs, and DCRs for Microsoft products.
*   **Kafka-Specific Integration (Outbound/General)**: Ingestion from Kafka (if not specifically in scope) and configuring Kafka for outbound patterns or acting as a publisher for external consumption are out of scope.

#### **III. Code Conversion & Data Transformation**
While code translation is central, deep re-engineering, new development, and responsibility for source system defects are consistently excluded.
*   **Business Logic/Data Model Changes**: Modifications to the core business logic, existing data models, or transformation rules of the objects being migrated are not within the migration scope. The project primarily adheres to a "lift-and-shift" principle, preserving the logical structure.
*   **Legacy Code Analysis/Fixes**: Any analysis, enhancement, or development to address or fix issues found in the existing legacy (Teradata) code or to determine legacy code issues during the data validation process is explicitly excluded.
*   **Custom Framework/Proprietary Tool Enhancements**: Modifications or enhancements to the customer's existing proprietary data tools (e.g., Connexio, FTAS, CDMNext, AbInitio, Cerebro) are generally excluded.
*   **New Development (Generic)**: General development of new frameworks or Java & Python programs beyond specifically scoped conversions are out of scope.
*   **Advanced Data Security Coding**: Development or implementation of custom code for encryption, decryption, tokenization, de-tokenization, or masking of data is typically out of scope.
*   **Shell Script Modernization**: While shell script migration might be in scope (e.g., simple porting), the deeper *modernization* of shell scripts is often out of scope, indicating a focus on conversion rather than re-engineering.

#### **IV. Data Management & Quality**
These exclusions highlight that broader data governance, extensive data quality remediation, and specific data privacy handling are separate responsibilities or engagements.
*   **Data Quality/Cleansing**: Any data cleansing activities (e.g., fixing incorrect, corrupted, or incomplete data) are excluded. Post-load data quality controls are also typically out of scope.
*   **Data Governance Activities**: Broad data governance, security, and compliance activities (e.g., data quality solutions, metadata management, lineage, and policy enforcement) beyond technical metadata capture and integrations are generally out of scope.
*   **PII/Sensitive Data Handling (Beyond Defined Scope)**: Data classification, handling, or identification concerning "Personally Identifiable Information (PII)" beyond specific, defined solutions (e.g., CDMNext) is excluded.
*   **Inactive/Unscoped Data**: Migration, conversion, testing, or redevelopment of any inactive data, objects, or workflows not part of the active in-scope volumetrics is excluded. Any data not captured in volumetrics or in non-production environments is excluded to avoid costs.

#### **V. Data Ingestion & Integration**
Specific patterns or broad integration work with external systems is often excluded to maintain project focus.
*   **General Source System Integration**: Broad "Source System Integration" as an activity, especially if a dedicated ingestion framework is used, is out of scope.
*   **Integration with Unspecified Systems**: Integration with any upstream, downstream, peripheral, or 3rd party applications not explicitly mentioned in the SOW's scope is excluded.
*   **New Data Source Onboarding**: Any addition of new data sources or new data source onboarding beyond existing ones are out of scope.
*   **Real-time Streaming/CDC Implementation**: Automation or implementation of real-time streaming ingestion pipelines or CDC-based configuration to GCP are excluded.

#### **VI. Reporting & Application Repointing**
While repointing of specific reports is in scope, broader reporting activities, new report development, and deep application changes are usually separate engagements.
*   **New Report Development/Redesign**: Creating new reports/dashboards, or reconfiguring/redeveloping reports (e.g., child or linked reports) beyond simple repointing or specific re-development identified in scope, is excluded. Any kind of activity related to development, repointing and migration of reports.
*   **Report Repointing (Beyond Defined Scope)**: Repointing of MicroStrategy and Tableau reports outside the explicitly defined scope is excluded. Similarly, Looker report repointing beyond defined volumetrics is out of scope.
*   **Application UI/UX or Business Logic Changes**: UI/UX changes, or application/API business logic changes for consuming applications, are not covered.

#### **VII. Testing & Validation**
Boundaries around who performs what testing, and for what scope, are crucial to ensure efficiency and accountability.
*   **Performance Optimization (Beyond Parity)**: Performance enhancements or query optimization beyond ensuring the migrated system performs at parity with, or better than, the current system are out of scope.
*   **Ad-Hoc Query Conversion**: Conversion of ad-hoc queries from self-service environments is typically excluded.
*   **Extensive Environmental Data Testing**: Any general data validation and testing conducted within the customer’s environment, beyond the scope of migration tool validation (e.g., Pelican) is often excluded.

#### **VIII. Deployment & Decommissioning**
The final stages of moving to production and retiring legacy systems are often client-led responsibilities.
*   **Production Deployment**: While support and guidance are provided, the actual execution of production deployments is frequently the client's responsibility.
*   **Legacy Environment Decommissioning/Cutover**: Decommissioning and cutover activities for existing legacy environments are generally the client's responsibility.

#### **IX. Post-Migration Support & Knowledge Transfer**
Ongoing operational responsibilities, extensive training, and long-term advisory services are typically outside the migration SOW.
*   **User Training & Onboarding**: User training and onboarding beyond basic knowledge transfer and documentation associated with the migration scope are excluded.
*   **Managed Services/Long-term Support**: Ongoing L1, L2, L3 managed support services, or long-term advisory and troubleshooting beyond the project duration, are typically separate agreements. This also includes monitoring and triaging issues in the production environment.

#### **X. Advanced Capabilities / Modernization (Specific Exclusions)**
For projects that are primarily migration-focused, advanced features or deep modernization efforts are typically out of scope.
*   **AI/ML/Data Science Development**: Creation or enhancement of Artificial Intelligence/Machine Learning (AI/ML) models or general Data Science activities are separate engagements.
*   **FinOps Implementation**: Implementation of FinOps, DataOps, SSOT, or other integrated frameworks, or the implementation work related to FinOps reports, are out of scope.
*   **Custom Schemas**: Customizations on the current schema beyond what is necessary for the target platform's compatibility are excluded.