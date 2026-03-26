import re

file_path = "d:\\AI_ML\\SOW-Generator\\repo\\SOW_Generator\\src\\sow_generator\\prompts\\enrichment_agent_v4.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Structure Formats
content = content.replace(
'''### Format 1: String (Paragraph Format)
- **When used**: Field type is `string`
- **Structure**: Multiple items separated by `\\n` or `\\n\\n` (double newline)
- **Example**:
```json
"opportunity": "First paragraph text.\\n\\nSecond paragraph text.\\n\\nThird paragraph."
```

### Format 2: List of Objects with {point, subpoint}
- **When used**: Field type is `list[dict]` and content has hierarchy (nested items)
- **Structure**: `[{"point": "...", "subpoint": ["...", "..."]}]`
- **Key rule**: `subpoint` is ALWAYS an array (use `[]` if no sub-items)
- **Example**:
```json
"activities": [
  {
    "point": "Discovery and Analysis",
    "subpoint": ["Analyze current state", "Identify requirements"]
  },
  {
    "point": "Design",
    "subpoint": []
  }
]
```

### Format 3: Simple Array of Strings
- **When used**: Field type is `list[dict]` but content is flat (no hierarchy)
- **Structure**: `["item1", "item2", "item3"]`
- **Example**:
```json
"deliverables": ["Architecture Document", "Migration Plan", "Test Report"]
```''', 
'''### Format 1: Text Paragraphs
- **When used**: The content consists of continuous text/paragraphs.
- **Structure**: Multiple paragraphs separated by double newlines.
- **Example**:
```markdown
## Opportunity
First paragraph text.

Second paragraph text.

Third paragraph.
```

### Format 2: Hierarchical Lists
- **When used**: The content has hierarchy (points and sub-items).
- **Structure**: Markdown headers for points, followed by bulleted lists for sub-items.
- **Key rule**: Use `###` for main points and `-` for subpoints.
- **Example**:
```markdown
## Activities
### Discovery and Analysis
- Analyze current state
- Identify requirements

### Design
```

### Format 3: Simple Bulleted Lists
- **When used**: The content is a flat list of items (no hierarchy).
- **Structure**: A standard markdown bulleted list.
- **Example**:
```markdown
## Deliverables
- Architecture Document
- Migration Plan
- Test Report
```''')

# 2. Paths Decision
content = content.replace(
'''- Is it Format 1 (string)?
- Is it Format 2 ({point, subpoint})?
- Is it Format 3 (simple array)?''',
'''- Is it Format 1 (Text Paragraphs)?
- Is it Format 2 (Hierarchical Lists)?
- Is it Format 3 (Simple Bulleted Lists)?''')

content = content.replace(
'''**Step A4**: Determine format and convert
- Use Format Selection rules (see above)
- Convert adapted content to chosen format''',
'''**Step A4**: Determine format and convert
- Use Format Selection rules (see above)
- Format the adapted content to match the chosen format''')

content = content.replace(
'''**Step B4**: Adapt and convert
- Adapt missing items to proposal context
- Convert to match the format identified in B1''',
'''**Step B4**: Adapt and format
- Adapt missing items to proposal context
- Format to match the format identified in B1''')


# 3. Example 1
content = content.replace(
'''**Extractor Agent Output**:
```json
{
  "category": "teradata_migration",
  "sow_content": {
    "success_criteria": "NA"
  }
}
```

**Golden Template**:
```json
{
  "success_criteria": [
    {"metric": "Performance", "target": "Query response time < 2 seconds"},
    {"metric": "Data Quality", "target": "100% data accuracy"},
    {"metric": "User Adoption", "target": "80% team adoption within 3 months"}
  ]
}
```

**Decision Process**:
- Field is "NA" → PATH A
- Template has content → Proceed
- Content is relevant to migrations → Proceed
- No adaptation needed (generic metrics) → Proceed
- Format Selection: Content is hierarchical → Use Format 2

**Enriched Output**:
```json
{
  "success_criteria": [
    {
      "point": "Performance",
      "subpoint": ["Query response time < 2 seconds"]
    },
    {
      "point": "Data Quality",
      "subpoint": ["100% data accuracy"]
    },
    {
      "point": "User Adoption",
      "subpoint": ["80% team adoption within 3 months"]
    }
  ]
}
```''',
'''**Extractor Agent Output**:
```markdown
# Category
teradata_migration

# SOW Content
## Success Criteria
NA
```

**Golden Template**:
```markdown
## Success Criteria
### Performance
- Query response time < 2 seconds

### Data Quality
- 100% data accuracy

### User Adoption
- 80% team adoption within 3 months
```

**Decision Process**:
- Section is "NA" → PATH A
- Template has content → Proceed
- Content is relevant to migrations → Proceed
- No adaptation needed (generic metrics) → Proceed
- Format Selection: Content is hierarchical → Use Format 2

**Enriched Output**:
```markdown
## Success Criteria
### Performance
- Query response time < 2 seconds

### Data Quality
- 100% data accuracy

### User Adoption
- 80% team adoption within 3 months
```''')

# 4. Example 2
content = content.replace(
'''**Extractor Agent Output**:
```json
{
  "deliverables": [
    {
      "point": "Design Phase",
      "subpoint": ["Architecture Document", "Migration Plan"]
    }
  ]
}
```

**Golden Template**:
```json
{
  "deliverables": [
    "Architecture Document",
    "Data Migration Strategy",
    "Security Assessment Report",
    "Performance Optimization Plan"
  ]
}
```

**Decision Process**:
- Field has data → PATH B
- Current format: Format 2 ({point, subpoint})
- Semantic comparison:
  - ❌ "Architecture Document" - already present
  - ❌ "Data Migration Strategy" - semantically similar to "Migration Plan"
  - ✅ "Security Assessment Report" - missing, different aspect
  - ✅ "Performance Optimization Plan" - missing, different aspect
- Both are HIGH priority for migrations → Add
- Convert to Format 2 (add as subpoints)

**Enriched Output**:
```json
{
  "deliverables": [
    {
      "point": "Design Phase",
      "subpoint": ["Architecture Document", "Migration Plan", "Security Assessment Report", "Performance Optimization Plan"]
    }
  ]
}
```''',
'''**Extractor Agent Output**:
```markdown
## Deliverables
### Design Phase
- Architecture Document
- Migration Plan
```

**Golden Template**:
```markdown
## Deliverables
- Architecture Document
- Data Migration Strategy
- Security Assessment Report
- Performance Optimization Plan
```

**Decision Process**:
- Section has data → PATH B
- Current format: Format 2 (Hierarchical Lists)
- Semantic comparison:
  - ❌ "Architecture Document" - already present
  - ❌ "Data Migration Strategy" - semantically similar to "Migration Plan"
  - ✅ "Security Assessment Report" - missing, different aspect
  - ✅ "Performance Optimization Plan" - missing, different aspect
- Both are HIGH priority for migrations → Add
- Format as Format 2 (add as sub-items under the existing header)

**Enriched Output**:
```markdown
## Deliverables
### Design Phase
- Architecture Document
- Migration Plan
- Security Assessment Report
- Performance Optimization Plan
```''')

# 5. Example 3
content = content.replace(
'''**Extractor Agent Output**:
```json
{
  "category": "teradata_migration_etl",
  "sow_content": {
    "activities": [
      {
        "point": "Discovery",
        "subpoint": ["Analyze Teradata environment", "Assess ETL pipelines using Informatica"]
      }
    ],
    "technical_assumptions": [
      {
        "point": "Client will provide access to production Teradata system",
        "subpoint": []
      }
    ]
  }
}
```

**Golden Template**:
```json
{
  "activities": [
    {
      "point": "Discovery",
      "subpoint": ["Analyze source environment", "Review data models"]
    },
    {
      "point": "Design",
      "subpoint": ["Create target Snowflake schema", "Design data pipelines"]
    },
    {
      "point": "Migration",
      "subpoint": ["Migrate Snowflake tables", "Validate data accuracy"]
    }
  ],
  "technical_assumptions": [
    {
      "point": "Client will provide access to source systems",
      "subpoint": []
    },
    {
      "point": "Snowflake instance is provisioned and accessible",
      "subpoint": []
    }
  ]
}
```

**Analysis**:
- Extractor: Teradata → ? migration, uses Informatica
- Template: Assumes Snowflake (conflict!)
- Template has missing phases: "Design", "Migration" (relevant, HIGH priority)

**Decision Process**:

**For `activities` field** (PATH B):
- Semantic comparison in Discovery phase:
  - ❌ "Analyze source environment" - semantically similar to "Analyze Teradata environment"
  - ✅ "Review data models" - missing, different aspect
- Add "Review data models" to Discovery
- Add "Design" and "Migration" phases
- Adapt "Snowflake" references using Adaptation Matrix:
  - "Create target Snowflake schema" → "Create target schema" (generic term)
  - "Migrate Snowflake tables" → "Migrate tables" (remove conflicting tech)

**For `technical_assumptions` field** (PATH B):
- First assumption: semantically similar to extractor → Skip
- Second assumption: "Snowflake instance" conflicts with extractor
- Adapt to: "Target platform instance is provisioned and accessible"

**Enriched Output**:
```json
{
  "category": "teradata_migration_etl",
  "sow_content": {
    "activities": [
      {
        "point": "Discovery",
        "subpoint": ["Analyze Teradata environment", "Assess ETL pipelines using Informatica", "Review data models"]
      },
      {
        "point": "Design",
        "subpoint": ["Create target schema", "Design data pipelines"]
      },
      {
        "point": "Migration",
        "subpoint": ["Migrate tables", "Validate data accuracy"]
      }
    ],
    "technical_assumptions": [
      {
        "point": "Client will provide access to production Teradata system",
        "subpoint": []
      },
      {
        "point": "Target platform instance is provisioned and accessible",
        "subpoint": []
      }
    ]
  }
}
```''',
'''**Extractor Agent Output**:
```markdown
# Category
teradata_migration_etl

# SOW Content
## Activities
### Discovery
- Analyze Teradata environment
- Assess ETL pipelines using Informatica

## Technical Assumptions
### Client will provide access to production Teradata system
```

**Golden Template**:
```markdown
## Activities
### Discovery
- Analyze source environment
- Review data models

### Design
- Create target Snowflake schema
- Design data pipelines

### Migration
- Migrate Snowflake tables
- Validate data accuracy

## Technical Assumptions
### Client will provide access to source systems

### Snowflake instance is provisioned and accessible
```

**Analysis**:
- Extractor: Teradata → migration, uses Informatica
- Template: Assumes Snowflake (conflict!)
- Template has missing phases: "Design", "Migration" (relevant, HIGH priority)

**Decision Process**:

**For `activities` section** (PATH B):
- Semantic comparison in Discovery phase:
  - ❌ "Analyze source environment" - semantically similar to "Analyze Teradata environment"
  - ✅ "Review data models" - missing, different aspect
- Add "Review data models" to Discovery
- Add "Design" and "Migration" phases
- Adapt "Snowflake" references using Adaptation Matrix:
  - "Create target Snowflake schema" → "Create target schema" (generic term)
  - "Migrate Snowflake tables" → "Migrate tables" (remove conflicting tech)

**For `technical_assumptions` section** (PATH B):
- First assumption: semantically similar to extractor → Skip
- Second assumption: "Snowflake instance" conflicts with extractor
- Adapt to: "Target platform instance is provisioned and accessible"

**Enriched Output**:
```markdown
# Category
teradata_migration_etl

# SOW Content
## Activities
### Discovery
- Analyze Teradata environment
- Assess ETL pipelines using Informatica
- Review data models

### Design
- Create target schema
- Design data pipelines

### Migration
- Migrate tables
- Validate data accuracy

## Technical Assumptions
### Client will provide access to production Teradata system

### Target platform instance is provisioned and accessible
```''')

# 6. Example 4
content = content.replace(
'''**Extractor Agent Output**:
```json
{
  "out_of_scope": ["Data cleansing", "User training"]
}
```

**Golden Template**:
```json
{
  "out_of_scope": "Application development\\n\\nInfrastructure provisioning\\n\\nOngoing support and maintenance\\n\\nThird-party tool licensing"
}
```

**Decision Process**:
- Field has data → PATH B
- Current format: Format 3 (simple array)
- Semantic comparison:
  - ❌ "Data cleansing" - not in template
  - ❌ "User training" - not in template
  - ✅ "Application development" - missing, relevant
  - ✅ "Infrastructure provisioning" - missing, relevant
  - ✅ "Ongoing support and maintenance" - missing, relevant
  - ✅ "Third-party tool licensing" - missing, relevant
- All are MEDIUM priority → Add
- Template is Format 1 (string), must convert to Format 3 (simple array)

**Enriched Output**:
```json
{
  "out_of_scope": [
    "Data cleansing",
    "User training",
    "Application development",
    "Infrastructure provisioning",
    "Ongoing support and maintenance",
    "Third-party tool licensing"
  ]
}
```''',
'''**Extractor Agent Output**:
```markdown
## Out of Scope
- Data cleansing
- User training
```

**Golden Template**:
```markdown
## Out of Scope
Application development

Infrastructure provisioning

Ongoing support and maintenance

Third-party tool licensing
```

**Decision Process**:
- Section has data → PATH B
- Current format: Format 3 (Simple Bulleted Lists)
- Semantic comparison:
  - ❌ "Data cleansing" - not in template
  - ❌ "User training" - not in template
  - ✅ "Application development" - missing, relevant
  - ✅ "Infrastructure provisioning" - missing, relevant
  - ✅ "Ongoing support and maintenance" - missing, relevant
  - ✅ "Third-party tool licensing" - missing, relevant
- All are MEDIUM priority → Add
- Template is Format 1 (Text Paragraphs), must adapt into Format 3 (Simple Bulleted Lists)

**Enriched Output**:
```markdown
## Out of Scope
- Data cleansing
- User training
- Application development
- Infrastructure provisioning
- Ongoing support and maintenance
- Third-party tool licensing
```''')


# 7. Example 5
content = content.replace(
'''**Extractor Agent Output**:
```json
{
  "category": "eagle_assessment_eagle_modernization",
  "sow_content": {
    "activities": [
      {
        "point": "Assessment Phase",
        "subpoint": ["Analyze Eagle system performance", "Review existing configurations"]
      }
    ]
  }
}
```

**Golden Template** (from teradata_migration category - WRONG category used):
```json
{
  "activities": [
    {
      "point": "Assessment",
      "subpoint": ["Analyze Teradata environment", "Identify migration scope"]
    },
    {
      "point": "ETL Migration",
      "subpoint": ["Convert stored procedures", "Migrate ETL jobs"]
    },
    {
      "point": "Data Migration",
      "subpoint": ["Extract data from Teradata", "Load to target platform"]
    }
  ]
}
```

**Decision Process**:
- Field has data → PATH B
- Current format: Format 2
- Semantic comparison:
  - ❌ First point semantically similar
  - ✅ "ETL Migration" phase - missing
  - ✅ "Data Migration" phase - missing
- **Relevance check**:
  - This is an Eagle ASSESSMENT project, not a migration
  - "ETL Migration" and "Data Migration" are LOW priority (not applicable to assessment)
  - Skip both phases

**Enriched Output**:
```json
{
  "activities": [
    {
      "point": "Assessment Phase",
      "subpoint": ["Analyze Eagle system performance", "Review existing configurations"]
    }
  ]
}
```''',
'''**Extractor Agent Output**:
```markdown
# Category
eagle_assessment_eagle_modernization

# SOW Content
## Activities
### Assessment Phase
- Analyze Eagle system performance
- Review existing configurations
```

**Golden Template** (from teradata_migration category - WRONG category used):
```markdown
## Activities
### Assessment
- Analyze Teradata environment
- Identify migration scope

### ETL Migration
- Convert stored procedures
- Migrate ETL jobs

### Data Migration
- Extract data from Teradata
- Load to target platform
```

**Decision Process**:
- Section has data → PATH B
- Current format: Format 2
- Semantic comparison:
  - ❌ First point semantically similar
  - ✅ "ETL Migration" phase - missing
  - ✅ "Data Migration" phase - missing
- **Relevance check**:
  - This is an Eagle ASSESSMENT project, not a migration
  - "ETL Migration" and "Data Migration" are LOW priority (not applicable to assessment)
  - Skip both phases

**Enriched Output**:
```markdown
## Activities
### Assessment Phase
- Analyze Eagle system performance
- Review existing configurations
```''')

# Mapping fields replacements
content = content.replace("For each field in `sow_content`:", "For each section in the markdown structure:")
content = content.replace("- The enriched output MUST use the exact same structure format as the extractor output", "- The enriched output MUST use the exact same formatting structure as the extractor output")
content = content.replace("Check extractor field value", "Check section value")
content = content.replace("Field is \"NA\"", "Section is \"NA\"")
content = content.replace("Field type is `string`", "Section involves Text Paragraphs")
content = content.replace("Field type is `list[dict]` and content has hierarchy", "Section involves Hierarchical points")
content = content.replace("Field type is `list[dict]` but content is flat", "Section is a flat list of strings")


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated successfully!")
