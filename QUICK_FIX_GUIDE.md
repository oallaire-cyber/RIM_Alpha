# Quick Fix Guide - Type & Path Errors v1.0.1

## 🚨 If You're Seeing These Errors

You're experiencing data type issues and Windows path problems in your application. Here's how to fix it:

**Common Errors:**
- `TypeError: unsupported operand type(s) for //: 'NoneType' and 'int'`
- `TypeError: unsupported operand type(s) for /: 'str' and 'int'`
- `FileNotFoundError: [Errno 2] No such file or directory: '/home/claude/risk_network.html'`

## 🔧 Immediate Solution

### Step 1: Update app.py
Replace your current `app.py` with the fixed version (included in these files).

### Step 2: Clean Your Database (Choose One)

**Option A: Quick Fix (Recommended)**
1. Open Neo4j Browser: http://localhost:7474
2. Copy and paste this query:

```cypher
// Quick fix - convert all string numbers to integers
MATCH (r:Risk)
SET r.probability = toInteger(r.probability),
    r.impact = toInteger(r.impact),
    r.score = toInteger(r.score);

MATCH ()-[i:INFLUENCES]->()
SET i.strength = toInteger(i.strength);
```

3. Press ▶ (Play button) or Ctrl+Enter

**Option B: Complete Cleanup**
1. Open the file `data_cleanup.cypher`
2. Copy all contents
3. Paste into Neo4j Browser
4. Execute

### Step 3: Restart Streamlit
```bash
# Stop the current app (Ctrl+C)
# Restart
streamlit run app.py
```

## 🐛 What Was Wrong?

Your application had **three issues**:

### Issue 1: String Numbers
```cypher
// Wrong - numbers stored as strings
{probability: '7', impact: '9', strength: '5'}

// Right - numbers stored as integers  
{probability: 7, impact: 9, strength: 5}
```

### Issue 2: NULL Values
```cypher
// Missing or NULL values caused crashes
{probability: null, impact: null, score: null}
```

### Issue 3: Windows Path Error
```python
# Wrong - hardcoded Linux path
net.save_graph("/home/claude/risk_network.html")  # Doesn't exist on Windows!

# Right - cross-platform temporary directory
temp_file = os.path.join(tempfile.gettempdir(), "risk_network.html")
net.save_graph(temp_file)
```

## ✅ What's Fixed Now?

The new `app.py` has multiple improvements:

**1. safe_int() function** that handles:
- ✅ String numbers → Converts '5' to 5
- ✅ NULL values → Converts to default (0 or 5)
- ✅ Missing values → Uses defaults
- ✅ Invalid values → Uses defaults

**2. Cross-platform paths**:
- ✅ Works on Windows (C:\Users\...\AppData\Local\Temp\)
- ✅ Works on Linux (/tmp/)
- ✅ Works on macOS (/var/folders/...)

**3. Better imports**:
```python
import tempfile  # Added for cross-platform temp directory
```

## 🎯 How to Prevent This?

When creating risks in the future, use **integers not strings**:

**In Python (create_risk function):**
```python
# Already fixed in new app.py - uses int() conversion
probability = int(probability_slider)  # Good
```

**In Neo4j Browser:**
```cypher
// Good - use numbers directly
CREATE (r:Risk {
    probability: 7,
    impact: 9,
    score: 63
})

// Bad - don't use quotes for numbers
CREATE (r:Risk {
    probability: '7',    // ❌ String!
    impact: '9',         // ❌ String!
    score: '63'          // ❌ String!
})
```

**When using CSV import, use toInteger():**
```cypher
LOAD CSV WITH HEADERS FROM 'file:///risks.csv' AS row
CREATE (r:Risk {
    name: row.name,
    probability: toInteger(row.probability),  // Convert!
    impact: toInteger(row.impact),            // Convert!
    score: toInteger(row.score)               // Convert!
})
```

## 🧪 Test Your Fix

After updating, create a test risk:

```cypher
// This should now work without crashing the app
CREATE (r:Risk {
    name: 'Test Fix',
    category: 'Cyber',
    probability: '7',    // String - will be converted
    impact: 9,           // Integer - already correct
    score: null,         // NULL - will use default
    status: 'Active'
})
```

Refresh the Streamlit app - it should display without errors!

## 📋 Verification Checklist

- [ ] Updated to new `app.py`
- [ ] Ran data cleanup query in Neo4j
- [ ] Restarted Streamlit
- [ ] Tested visualization tab
- [ ] No more type errors in console
- [ ] Graph displays correctly

## 🆘 Still Having Issues?

1. **Check Neo4j is running**: Visit http://localhost:7474
2. **Check your data**: 
   ```cypher
   MATCH (r:Risk) 
   RETURN r 
   LIMIT 5
   ```
3. **View Streamlit logs**: Look at the terminal where you started Streamlit
4. **Restart everything**:
   ```bash
   docker-compose restart
   streamlit run app.py
   ```

## 📚 Additional Resources

- **Full bugfix details**: See `BUGFIX_v1.0.1.md`
- **Data cleanup script**: See `data_cleanup.cypher`
- **Change log**: See `CHANGELOG.md`

---

**Version**: 1.0.1  
**Issue**: Type conversion errors  
**Status**: Fixed ✅  
**Date**: January 2025
