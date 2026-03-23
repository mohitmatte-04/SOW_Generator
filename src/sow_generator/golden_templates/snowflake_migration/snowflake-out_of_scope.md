### **Golden Content Framework: "Out of Scope" for Snowflake to GCP Migration Projects**

#### **I. Project Initiation & Governance**
These exclusions underscore the importance of disciplined project management and define limits on evolving requirements and administrative overhead.

*   **Activities Not Explicitly Mentioned in Scope**: Any activities or deliverables not specifically enumerated within the "Scope of Services" are considered out of scope.
*   **Changes in Scope or Volumetrics**: Any alterations in the project's defined scope or an increase in volumetrics beyond mutually agreed-upon thresholds will necessitate a formal change request and are explicitly out of scope.
*   **General Third-Party Licensing/Integration (Unspecified)**: Activities related to any 3rd party licensing or general integration not specifically detailed within the in-scope deliverables are excluded.

#### **II. Discovery & Assessment (Post-Assessment Engagements)**
For SOWs detailing migration post-initial assessment, further broad assessment efforts are typically excluded.

*   **Assessment of Non-Scoped Platforms/Technologies**: Assessment of platforms, tools, or technologies other than those specifically mentioned as in-scope is excluded.
*   **Analysis/Change in Legacy System**: Any general analysis or change in the legacy system (Snowflake on Azure) is out of scope.
*   **Proof of Concept (POC)/Value Implementation**: Any proof of concept or value implementation is excluded.

#### **III. Infrastructure & Platform Management**
The provisioning, configuration, and ongoing management of the underlying cloud environment are consistently designated as the client's responsibility.

*   **Cloud Foundation Setup**: The establishment, configuration, and provisioning of the core Google Cloud Platform (GCP) environment (e.g., foundational services, VM provisioning, service enablement, network security, IAM, creation of databases, VPCs) are explicitly out of scope.
*   **CI/CD & DevOps Activities**: The implementation of CI/CD pipelines or broader DevOps activities is typically excluded, beyond specifically defined scope or required GitHub Actions setup.
*   **Software Upgrades/Patching/Enhancements**: Any software upgrades, patching, or general enhancements to existing systems are out of scope.
*   **Infrastructure-Related Setups**: Any infrastructure-related setups or activities are excluded.
*   **Maintenance/Operation of Non-GCP Products**: Maintaining, enabling, or operating any code or non-GCP products, tools, and services is excluded.
*   **Implementation of GCP Environment Changes**: Implementing any changes to the Customer’s Google Cloud environment is out of scope.
*   **Migration of Data Source Systems**: The migration of the actual data source systems themselves is excluded.

#### **IV. Data Ingestion & Integration**
Specific patterns or broad integration work with external systems is often excluded to maintain project focus.

*   **Integration with Unspecified Applications**: Integration with any upstream, downstream, peripheral, or 3rd party applications not explicitly mentioned in the scope is excluded. For Albertsons, Alation, Denodo, Databricks, and ICEDQ are specifically in scope, making others out of scope.
*   **Data Ingestion from Source to GCS (Client Responsibility)**: Data ingestion from source systems to Google Cloud Storage (GCS) is typically a client responsibility.
*   **Kafka-to-BigQuery Connectivity Setup (Client Responsibility)**: Establishing connectivity for Kafka to BigQuery is the client's responsibility.
*   **Integrating Source Systems (General)**: General integration of source systems is out of scope.
*   **Customization to Data Ingestion Framework**: Any customization or modification to the Data Ingestion framework after the completion of the SOW is excluded.
*   **Historical Data Extraction (Client Responsibility)**: Historical Data Extraction from the source system is often a client responsibility.
*   **Refactoring of Downstream Applications**: Refactoring of downstream applications is out of scope.

#### **V. Code Conversion & Transformation**
While code translation is central, deep re-engineering, new development, and responsibility for source system defects are consistently excluded, preserving the "lift-and-shift" focus.

*   **Business Logic/Data Model Changes**: Modifications to the core business logic, existing data models, or transformation rules of the objects being migrated are not within the migration scope, emphasizing a lift-and-shift approach. Data model optimization for Snowflake is out of scope unless absolutely necessary.
*   **Legacy Code Issues**: Any analysis and enhancement/development to determine Legacy code issues during the data validation process is explicitly excluded.
*   **Data Classification/PII Handling**: Data classification, handling, or identification concerning "Personally Identifiable Information (PII)" is typically out of scope.
*   **AI/ML Models Development/Enhancement**: The development or enhancement of any AI/ML models is excluded.
*   **Ad-Hoc Query Conversion**: The conversion of ad-hoc queries developed by end-users is out of scope.
*   **Consolidation Efforts**: Consolidation of markets, platforms, schemas, or code is out of scope.
*   **Migration of Historical Jupyter Notebooks**: Migration of historical Jupyter notebooks is excluded.
*   **Migration of Other Technologies**: Migration of any technology not explicitly mentioned in the scope (e.g., Aurora DB) is out of scope.
*   **Snowflake Marketplace Integrations**: Migration of Snowflake Marketplace Shared Dataset integrations (B2B) is out of scope.
*   **Encryption/Decryption of Data (Beyond Native)**: Encryption or decryption of data is not included beyond publicly available Snowflake and BigQuery functionality.
*   **Modernization of Ab Initio Software Suite**: Modernization of the Ab Initio software suite beyond the migration scope is explicitly out of scope.

#### **VI. Reporting & Application Repointing**
Repointing of existing reports is usually specific, while broader integration, new report development, and deep application changes are excluded.

*   **New Report Development/Redesign**: Creating new reports/dashboards, or reconfiguration of child or linked reports, is out of scope.
*   **Report Optimization/Redesign**: Redesign or optimization of Looker semantic models or dashboards beyond connectivity and repointing is out of scope.
*   **Report Comparison**: Direct report comparison between legacy and GCP is out of scope.
*   **Functional Validation of Reports**: Functional validation for the reports is out of scope.
*   **Specific Report Volumetrics**: Repointing of any Looker objects not mentioned in the volumetrics is out of scope.
*   **Development of New Dashboards**: Development of new dashboards beyond the defined POC scope is excluded.
*   **Downstream Reporting Integration**: General downstream reporting integration is out of scope.
*   **Integration with Realteo and Collibra**: Integration with these specific systems is excluded.

#### **VII. Testing & Validation**
Boundaries for who performs extensive testing and for which types of issues are clearly set to ensure efficiency and accountability.

*   **Production Deployment/Testing and UAT Testing**: Production Deployment/testing and UAT testing are out of scope for the vendor.
*   **Extended Validation Cycles**: Validation beyond two agreed incremental cycles will require a Change Request.
*   **Bug Fixing in Third-Party SaaS Platforms**: The vendor is not responsible for bug fixing in third-party SaaS platforms (e.g., Fivetran, Looker, Prefect).
*   **Advanced Optimization (Cost/Performance)**: Any advanced optimization (cost tuning, slot reservations, re-modeling) is out of scope. This also includes performance, reliability, and security testing, and configuring monitoring or spend alerts.
*   **Non-Production Data Migration**: Migration of data not captured in volumetrics or in non-production environments is excluded to avoid costs.

#### **VIII. Deployment**
The final stages of production readiness and legacy system retirement are often client-led responsibilities, with vendor support typically being limited to bug fixes.

*   **Production Deployment Execution**: While support and guidance are provided, the actual execution of production deployments is frequently the client's responsibility. For Albertsons, Datametica will support, but Albertsons is responsible for the production deployment.
*   **Decommissioning/Cutover**: Decommissioning and cutover activities for existing systems or environments are generally the client's responsibility.

#### **IX. Post-Migration Support & Knowledge Transfer**
Ongoing operational support, extensive user training, and long-term advisory services are typically outside the migration SOW.

*   **User Training & Onboarding**: User training and onboarding beyond the knowledge transfer and documentation associated with the work are excluded.
*   **Long-term Advisory/Troubleshooting**: Long-term advisory and troubleshooting beyond the duration of the project engagement are out of scope.
*   **Managed Support Services**: Managed support services (L1, L2, L3) are typically separate agreements.
*   **Instructor-led Training/Certification**: Instructor-led training on Google Cloud fundamentals or Google Professional Cloud Architect certification is excluded.
*   **Cloud Observability/Operations**: Implementing cloud observability solutions (beyond specified scope) and general operations of the DWH/GCP environments are out of scope.

#### **X. Data Quality & Governance**
Broad data governance frameworks, extensive data quality remediation, and specific data privacy handling are generally separate responsibilities or engagements.

*   **Data Classification/Handling/PII**: Data classification, handling, or identification concerning "Personally Identifiable Information (PII)" is out of scope.
*   **Full-Scale Governance Implementation**: Full-scale governance implementation is out of scope.
*   **Custom Data Quality Rules**: Custom rules/check setup for data quality is out of scope.
*   **Data Governance Assessments/Recommendations**: Providing data governance assessments, recommendations, or leading practices is out of scope.
*   **Lifecycle Management, BCP & DR & DQ Solutions**: Implementation of lifecycle management, Business Continuity Planning (BCP), Disaster Recovery (DR), and Data Quality (DQ) solutions is out of scope.
*   **Post-Load Data Quality Controls**: Post-load data quality controls are out of scope.

#### **XI. Modernization Specific Exclusions (If Not Core to Migration)**
For projects that are primarily migration-focused, advanced features or deep modernization efforts are typically out of scope.

*   **FinOps Implementation/Reports**: Implementation of FinOps or related reports is out of scope.
*   **Machine Learning Operations (MLOps)**: Delivering any Machine Learning Operations initiatives (MLOps) is out of scope.
*   **Custom Schemas**: Customizations to the current schema beyond what is necessary for target platform compatibility are excluded.