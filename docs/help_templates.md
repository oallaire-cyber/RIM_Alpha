### 📋 Risk Templates

**Generic Risk Templates** allow you to define reusable risk archetypes that can be
instantiated into specific risks. Templates are excluded from all exposure calculations
and from the graph canvas — they exist purely as a library of reusable definitions.

---

**What is a Template?**

A Generic Risk Template (`is_template = true`) is a risk definition that:
- Carries standard **likelihood, severity, subtype, and categories** as a starting point
- Is **excluded from exposure** — it has no effect on EL, TRI, or quadrant distribution
- Is **invisible on the canvas** — it does not appear in the graph view
- Can be **instantiated** to create specific risks pre-filled with its attribute values

---

**Creating a Template**

1. Go to **Data Management → Risks tab**
2. In the **Create New Risk** form, check ☑ **Mark as template (GenericRisk)**
3. Fill in standard fields (likelihood, severity, subtype, categories, description)
4. Save — the risk appears in the **📋 Risk Templates** section, not in the main risk list

---

**Using the Template Library**

In **Data Management → Risks tab**, expand **📋 Risk Templates** to:
- View all defined templates with their instance counts
- **Instantiate** a template: click **➕ Instantiate** next to any template
  - An inline form opens pre-filled with the template's attributes
  - Adjust name, description, and any other fields as needed
  - Save — a new specific risk is created and linked via `[:INSTANTIATES]` in Neo4j
- **Delete** a template: click 🗑️ (does not affect existing instances)

---

**Template Relationships (Node Property Panel)**

When you click a **template risk** in the property panel:
- A **📋 Template** section shows how many instances were created from it
- A list of instance names is shown for traceability

When you click an **instance risk**:
- The **📋 Template** section shows the parent template name
- A note indicates this risk was instantiated from a template

---

**Why Templates?**

In large programs, many risks follow the same pattern (e.g., "Supplier Delivery Delay" in
multiple workstreams). Templates let you:
- Define the archetype once with standard scoring guidance
- Instantiate it quickly for each context with minimal rework
- Trace which risks share a common origin via the INSTANTIATES relationship

---

> **Note:** Templates are an organizational tool, not a mathematical construct.
> All exposure math, influence propagation, and lifecycle logic applies only to instances.
