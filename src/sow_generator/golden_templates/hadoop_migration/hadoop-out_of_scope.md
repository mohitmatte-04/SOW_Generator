### **Golden Content Framework: "Out of Scope" for Hadoop to GCP Migration Projects**

#### **I. Project Initiation & Governance**
These exclusions underscore the importance of disciplined project management and define limits on evolving requirements.
*   **Scope and Volumetric Changes**: Any alterations in the project's defined scope or an increase in volumetrics beyond mutually agreed-upon thresholds are explicitly out of scope and require a formal change request process.

#### **II. Assessment & Planning (Post-Assessment Engagements)**
For SOWs detailing migration post-initial assessment, further broad assessment efforts are typically excluded.
*   **Non-Scoped Platform Assessments**: Assessment of platforms, tools, or technologies not specifically identified as in-scope for the migration engagement.

#### **III. Infrastructure & Platform Management**
The provisioning and ongoing management of the underlying cloud environment are consistently designated as client responsibilities.
*   **GCP Cloud Foundation Setup**: The establishment, configuration, and provisioning of the core Google Cloud Platform environment are not included in the migration scope.
*   **General Infrastructure Activities**: Any infrastructure-related activities, such as general setup, configuration, VM provisioning, or service enablement, are excluded.
*   **Kafka Infrastructure Setup**: Setting up Kafka infrastructure (beyond specific ingestion pipelines) falls outside the migration scope.
*   **Infrastructure Gaps**: The client is responsible for addressing and resolving any identified gaps in the infrastructure required for the migration.
*   **CI/CD or DevOps Implementation**: Activities related to Continuous Integration/Continuous Deployment (CI/CD) or broader DevOps practices are typically out of scope.
*   **Software Upgrades/Patching**: Any upgrades or patching of existing system software, whether in the source or target environment, are excluded from the migration scope.

#### **IV. Code Conversion & Data Transformation**
While code conversion is central, deep re-engineering or responsibility for source system defects is excluded.
*   **Business Logic/Data Model Changes**: Modifications to the core business logic, existing data models, or transformation rules of the objects being migrated are not within the migration scope. The project primarily adheres to a lift-and-shift principle.
*   **Proprietary Tool Enhancements**: Modifications or enhancements to the customer's existing proprietary data tools (e.g., Connexio or FTAS) are excluded.
*   **Advanced Data Security Coding**: Development or implementation of custom code for encryption, decryption, tokenization, de-tokenization, or masking of data is typically out of scope.
*   **Legacy Code Analysis/Fixes**: Any analysis, enhancement, or development to address or fix issues within the existing legacy code or to determine legacy code issues during the data validation process is explicitly excluded.
*   **AI/ML or Data Science Development**: Activities involving Artificial Intelligence, Machine Learning, or general Data Science development are not part of the migration scope.
*   **Third-Party Software Workload Translation**: Translation, validation, integration, and testing of jobs, queries, or workflows running on third-party software (e.g., Power BI/Alteryx) are excluded unless specifically scoped.

#### **V. Data Integration & Quality**
Responsibilities for source data integrity and broader Kafka patterns are typically with the client.
*   **Source Data Discrepancy Fixes**: Correcting discrepancies found in source tables (e.g., WS source tables) is the client's responsibility.
*   **Kafka Outbound/Publishing Patterns**: Configuring Kafka for outbound patterns or acting as a publisher for external consumption is out of scope.

#### **VI. Reporting & Application Integration**
Repointing of existing reports is usually specific, while broader integration and new report development are excluded.
*   **Comprehensive Report Management**: Any new report development, changes to existing reports, or general migration/repointing activities for reporting tools are not included.
*   **Unspecified Application Integration**: Integration with any upstream, downstream, or peripheral applications or interfaces not explicitly mentioned as in-scope is excluded.
*   **Peripheral System Modification**: Working with peripheral system providers to modify or enhance their systems to align with the target GCP architecture is out of scope.

#### **VII. Testing & Validation**
Boundaries for who performs extensive testing and for which types of issues are clearly set.
*   **Extensive Environmental Data Testing**: Any general data validation and testing conducted within the customer's environment, beyond the scope of migration tool validation (e.g., Pelican), is typically excluded.
*   **Performance Enhancements**: Performance enhancements beyond ensuring that the migrated system performs at parity with the current system are out of scope. This means while performance parity is a goal, additional optimization efforts are not.
*   **Vendor-Initiated Data Bug Fixes**: The vendor is typically not responsible for fixing general data-related bugs identified during testing in the customer's environment, especially if they stem from source system issues.

#### **VIII. Deployment & Decommissioning**
The final stages of production readiness and legacy system retirement are often client-led.
*   **Production Deployment Execution**: While support and guidance are provided, the actual execution of production deployments is typically the client's responsibility.
*   **Legacy Environment Decommissioning**: The decommissioning and cutover of any existing legacy systems or environments are excluded.

#### **IX. Post-Migration Support & Enablement**
Ongoing operational support and extensive user training are generally outside the migration scope.
*   **User Onboarding/Change Management**: User onboarding and broader business or technology change management activities during or post-migration are out of scope.
*   **Extended User Training**: User training and onboarding beyond the specific knowledge transfer and documentation provided as part of the project deliverables are excluded.

#### **X. Data Governance & Security (General)**
Broad data governance frameworks are often separate engagements.
*   **Comprehensive Data Governance**: General data governance, security, and compliance activities, beyond what is specifically integrated as part of the migration, are excluded.
