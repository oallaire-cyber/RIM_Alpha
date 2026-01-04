# Bugfix: Type Conversion & Path Errors - v1.0.1

## Issue Description

**Error Types**: 
1. `TypeError: unsupported operand type(s) for //: 'NoneType' and 'int'`
2. `TypeError: unsupported operand type(s) for /: 'str' and 'int'`
3. `FileNotFoundError: [Errno 2] No such file or directory: '/home/claude/risk_network.html'`

**Location**: `app.py`, various lines in `visualize_risk_network()` function

**Cause**: The application crashed when:
1. Risks had `None` (NULL) values in database fields
2. Numeric fields were stored as **strings** instead of integers in Neo4j
3. Running on Windows with hardcoded Linux paths

## Root Causes

### Issue 1: None/NULL Values
When retrieving risks from Neo4j, if any risk node was missing properties or had NULL values:

```python
# Original problematic code
score = risk.get('score', 0)  # Returns None if score exists but is NULL
size = max(10, min(50, score // 2))  # Crashes if score is None
```

### Issue 2: String vs Integer Types  
Neo4j can store numbers as strings, especially when data is imported from CSV or created with string values:

```cypher
// This creates strength as a string!
CREATE ()-[:INFLUENCES {strength: '5'}]->()
```

Then in Python:
```python
strength = influence.get('strength')  # Returns '5' (string)
width = max(1, strength / 2)  # Crashes: can't divide string by int
```

### Issue 3: Hardcoded Linux Paths
The code used `/home/claude/risk_network.html` which doesn't exist on Windows:

```python
# Original problematic code
net.save_graph("/home/claude/risk_network.html")  # Crashes on Windows!
```

The issue: `.get('score', 0)` returns the default `0` only if the key doesn't exist, but returns `None` if the key exists with a NULL value in the database.

## Solution Applied

### 1. Added Safe Type Conversion Function (Line ~70-90)
```python
def safe_int(value, default: int = 0) -> int:
    """
    Safely convert a value to integer, handling None, strings, and invalid types.
    
    Args:
        value: Value to convert (can be int, str, None, etc.)
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
```

### 2. Fixed Risk Node Handling (Line ~350-360)
```python
# Fixed code - uses safe_int for all numeric fields
score = safe_int(risk.get('score'), 0)
probability = safe_int(risk.get('probability'), 0)
impact = safe_int(risk.get('impact'), 0)
```

This handles:
- ✅ None values → converts to 0
- ✅ String values like '5' → converts to 5
- ✅ Invalid values → converts to default (0)

### 3. Fixed Influence Strength (Line ~390)
```python
# Fixed code  
strength = safe_int(influence.get('strength'), 5)
```

### 4. Fixed Cross-Platform Path Handling (Line ~8, ~408-410)
```python
# Import tempfile module
import tempfile

# Use temporary directory for cross-platform compatibility
temp_file = os.path.join(tempfile.gettempdir(), "risk_network.html")
net.save_graph(temp_file)

with open(temp_file, "r", encoding="utf-8") as f:
    html_content = f.read()
```

This works on:
- ✅ Windows (uses `C:\Users\...\AppData\Local\Temp\`)
- ✅ Linux (uses `/tmp/`)
- ✅ macOS (uses `/var/folders/...`)

### 5. Improved Statistics Calculation (Line ~190-210)
```python
# Added WHERE clause to exclude NULL scores
query_avg = """
MATCH (r:Risk)
WHERE r.score IS NOT NULL
RETURN avg(r.score) as avg_score
"""
# Added additional None check
avg_score = result[0]['avg_score'] if result and result[0]['avg_score'] is not None else 0
```

## Testing

The fix handles these scenarios:
- ✅ Risks with missing `score`, `probability`, or `impact` properties
- ✅ Risks with NULL values in these properties  
- ✅ Risks with **string values** in numeric fields (e.g., '5' instead of 5)
- ✅ Influences with missing or NULL `strength` values
- ✅ Influences with **string strength** values
- ✅ Empty database (no risks)
- ✅ Mixed data (some risks complete, some incomplete, some with wrong types)

## How to Verify the Fix

### Test Case 1: Create Risk with Missing Values
```cypher
// In Neo4j Browser, create a risk without score
CREATE (r:Risk {
    name: 'Test Risk - Missing Values',
    category: 'Cyber',
    description: 'Testing null handling'
})
```

Expected: Application should display the risk with default values (score=0, size=10)

### Test Case 2: Create Risk with String Numbers
```cypher
// Create a risk with string values instead of integers
CREATE (r:Risk {
    name: 'Test Risk - String Numbers',
    category: 'Cyber',
    probability: '7',
    impact: '9',
    score: '63',
    status: 'Active',
    description: 'Testing string number handling'
})
```

Expected: Application converts strings to integers and displays correctly

### Test Case 3: Create Influence with String Strength
```cypher
// Create an influence with string strength
MATCH (r1:Risk), (r2:Risk)
WHERE r1.name <> r2.name
WITH r1, r2 LIMIT 1
CREATE (r1)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: '8',
    description: 'Test string strength'
}]->(r2)
```

Expected: Application converts '8' to 8 and displays edge with correct width

### Test Case 4: Update Existing Risk to NULL
```cypher
MATCH (r:Risk {name: 'Some Risk'})
SET r.score = null, r.probability = null, r.impact = null
```

Expected: Application should not crash and should handle the risk gracefully

## Prevention

To prevent similar issues in the future:

1. **Use safe_int() Everywhere**: Apply the utility function to all numeric conversions
2. **Type Enforcement in Cypher**: Use `toInteger()` when creating data
   ```cypher
   CREATE (r:Risk {
       probability: toInteger($prob),
       impact: toInteger($imp),
       score: toInteger($score)
   })
   ```
3. **Data Validation**: Ensure `create_risk()` validates and converts types
4. **Database Constraints**: Consider adding Neo4j property existence constraints
5. **Input Sanitization**: Validate user input before database insertion
6. **Unit Tests**: Add test coverage for type edge cases
7. **Documentation**: Warn users about string/integer type issues in user guide

## Quick Fix for Existing Data

If you have existing data with string values, run this in Neo4j Browser:

```cypher
// Convert all string numbers to integers
MATCH (r:Risk)
WHERE r.probability IS NOT NULL
SET r.probability = toInteger(r.probability),
    r.impact = toInteger(r.impact),
    r.score = toInteger(r.score);

// Convert influence strengths
MATCH ()-[i:INFLUENCES]->()
WHERE i.strength IS NOT NULL
SET i.strength = toInteger(i.strength);
```

## Files Modified

- ✅ `app.py` - Main application logic
- ✅ `CHANGELOG.md` - Documented the fix
- ✅ `REPOSITORY_SUMMARY.md` - Added to recent fixes section

## Version Impact

- **From**: v1.0.0 (initial release)
- **To**: v1.0.1 (bugfix release)
- **Severity**: High (application crash)
- **Impact**: All installations with incomplete data

## Rollout

No database migration required. Simply replace the `app.py` file and restart the application.

---

**Fixed**: January 4, 2025  
**Reporter**: User testing  
**Severity**: High  
**Status**: Resolved ✅
