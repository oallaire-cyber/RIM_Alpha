# ⚙️ RIM Configuration Manager

A standalone Streamlit application for managing RIM application configuration through YAML schemas.

## 🏃 Quick Start

```bash
# From project root with venv activated
streamlit run app_config.py
```

Opens at: `http://localhost:8501`

---

## 📋 Purpose

The Configuration Manager enables administrators to:

1. **Manage YAML Schemas** - Edit risk levels, categories, and all configuration without code changes
2. **Database Administration** - View stats, check compatibility, manage data
3. **Data Operations** - Backup/restore, clear database, load demo data
4. **Health Monitoring** - Validate schemas and data integrity

---

## 🗂️ Schema System

### Schema Structure

Schemas are stored in `schemas/<schema_name>/schema.yaml` and define:

| Section | Contents |
|---------|----------|
| **entities.risk** | Levels, categories, statuses, origins, attributes, custom_attributes |
| **entities.tpo** | Clusters, attributes, custom_attributes |
| **entities.mitigation** | Types, statuses, attributes, custom_attributes |
| **entities.custom_entities** | User-defined entity types (e.g., Asset, Threat Actor) |
| **relationships** | Influence types/strengths, impact levels, effectiveness levels |
| **relationships.custom_relationships** | User-defined relationship types between any entities |
| **analysis** | Exposure formulas, decay rates, thresholds |
| **ui** | App title, layout, tabs, filter presets |

### Included Schemas

| Schema | Purpose |
|--------|---------|
| `default` | SMR nuclear project (Strategic/Operational levels) |
| `it_security` | Cybersecurity (Enterprise/Tactical, CIA-based TPOs) |

### Creating New Schemas

1. Open Configuration Manager
2. Go to **Schema Management** → **General** tab
3. Click **➕ New Schema** or **📋 Duplicate**
4. Configure all sections
5. Click **💾 Save Schema**

---

## 🖥️ Application Tabs

### 📋 Schema Management

Eight sub-tabs for comprehensive schema editing:

| Sub-tab | Contents |
|---------|----------|
| **⚙️ General** | Name, version, description, UI settings, save/duplicate/new |
| **🎯 Risk Config** | Levels (with color, shape, emoji), categories, statuses, origins |
| **🏆 TPO Config** | Cluster definitions with colors |
| **🛡️ Mitigation Config** | Types (with line styles), statuses |
| **🔗 Relationships** | Influence strengths, effectiveness levels, impact levels |
| **📦 Custom Entities** | Define custom node types (e.g., Asset, Threat Actor) with attributes |
| **🔀 Custom Relationships** | Define custom edge types connecting any entities |
| **📄 YAML Preview** | Raw YAML view/edit mode with validation |

**Editing Features:**
- Form-based editors with live preview
- Color pickers for all color properties
- Slider controls for numeric values (strengths, percentages)
- Add/remove items dynamically
- Validation before save

### 🗄️ Database

Database administration tools (requires Neo4j connection):

| Feature | Description |
|---------|-------------|
| **Statistics** | Node and relationship counts by type |
| **Breakdown** | Counts by level, category, cluster, type |
| **Compatibility Check** | Compare database values against schema |
| **Migration Detection** | Find orphaned values, suggest Cypher updates |

### 📊 Data Management

Data operations (requires Neo4j connection):

| Operation | Description |
|-----------|-------------|
| **Clear Database** | Delete all nodes/relationships (requires confirmation) |
| **Load Demo Data** | Insert sample data for testing |
| **Backup to JSON** | Export entire database to JSON file |
| **Restore from JSON** | Import JSON backup (replaces existing data) |

### 🔍 Health Check

System health validation:

| Check | Description |
|-------|-------------|
| **Schema Validation** | Required fields, minimum items |
| **Database Connection** | Connectivity status |
| **Data Integrity** | Orphan nodes, invalid values, missing fields |

---

## 🔧 Sidebar Controls

### 🔌 Database Connection

Connect to Neo4j for database-related features:
- URI, username, password inputs
- Connect/Disconnect buttons
- Connection status indicator

### 📋 Active Schema

Schema selection and quick stats:
- Dropdown to switch schemas
- Current schema info (name, version)
- Quick metrics (levels, categories, clusters, types)
- Unsaved changes indicator
- **🎯 Set as Default for Main App** button

---

## 📁 File Structure

```
schemas/
├── default/
│   └── schema.yaml       # SMR nuclear configuration
├── it_security/
│   └── schema.yaml       # Cybersecurity configuration
└── <custom>/
    └── schema.yaml       # Your custom schemas

config/
├── schema_loader.py      # Schema parsing and validation
└── settings.py           # Dynamically loads from active schema

.rim_schema                 # Active schema name (persists across restarts)
```

---

## 🔄 Schema Workflow

### 1. Plan Your Schema

Define your domain's risk management vocabulary:
- Risk levels (e.g., Strategic/Operational or Enterprise/Tactical)
- Categories relevant to your domain
- TPO clusters aligned with your objectives

### 2. Create Schema

Either duplicate an existing schema or start from template:

```bash
# Schemas are stored as YAML files
schemas/my_project/schema.yaml
```

### 3. Configure Via UI

Use the Configuration Manager for visual editing:
- Add/remove/reorder items
- Set colors and visual properties
- Define relationship strengths

### 4. Validate

Before using in production:
1. Run **Health Check** with schema validation
2. Check **Database Compatibility** if migrating
3. Generate migration scripts if needed

### 5. Deploy

Set the schema as default for the main RIM app:

**Option 1: Via Configuration Manager**
1. Select your schema from the dropdown
2. Click **🎯 Set as Default for Main App**
3. Restart the main RIM app

**Option 2: Manually**
```bash
# Create .rim_schema file with your schema name
echo "my_project" > .rim_schema
```

**Option 3: Environment Variable**
```bash
# Set RIM_SCHEMA environment variable
$env:RIM_SCHEMA = "my_project"  # PowerShell
set RIM_SCHEMA=my_project       # Windows CMD
export RIM_SCHEMA=my_project    # Bash
```

---

## 🎯 Common Use Cases

### Adapting to a New Domain

1. Duplicate the closest existing schema
2. Rename levels/categories to match your terminology
3. Adjust colors for your organization's branding
4. Add custom attributes if needed

### Migrating Existing Data

1. Create new schema with updated values
2. Run **Compatibility Check** to find mismatches
3. Use suggested Cypher scripts to update data
4. Validate with **Health Check**

### Backup Before Major Changes

1. Go to **Data Management** tab
2. Click **Create Backup** → download JSON
3. Make your changes
4. If issues occur, use **Restore from JSON**

---

## 🔗 Related Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Main RIM app features |
| [Methodology](docs/METHODOLOGY.md) | RIM concepts and formulas |
| [Architecture](docs/ARCHITECTURE.md) | Code structure |

---

## 📁 File Reference

| File | Lines | Description |
|------|-------|-------------|
| `app_config.py` | ~2,000 | Configuration Manager application |
| `config/schema_loader.py` | ~1,100 | Schema loading and validation |
| `config/settings.py` | ~350 | Dynamic settings from schema |
| `ui/legend.py` | ~400 | Dynamic legend from schema |
| `schemas/default/schema.yaml` | ~300 | Default SMR schema |
| `schemas/it_security/schema.yaml` | ~500 | IT Security schema with custom entities |
