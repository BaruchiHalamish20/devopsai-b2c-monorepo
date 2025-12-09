# Quick Logic Bug Reference Card

## 🚀 Fastest Way to Test (with Switch)

```bash
# Step 1: Enable a bug
./trigger-logic-bug.sh
# Select a number (e.g., 4 for price bug)

# Step 2: Commit with [test-logic] trigger
git add .
git commit -m "Test: price bug [test-logic]"
git push

# That's it! CI will run logic tests for this commit only.
```

## 🎛️ Switch Control

Logic tests are **DISABLED by default**. Enable them in 3 ways:

### Option A: Commit Message (Easiest - One-Time)
```bash
git commit -m "Your message [test-logic]"
```

### Option B: Repository Variable (For Multiple Tests)
```bash
./toggle-logic-tests.sh  # Select: Enable
# Now ALL pushes run logic tests until you disable
```

### Option C: Manual Run (Via GitHub UI)
- Actions → Run workflow → ☑️ Enable logic tests

## 📝 Most Realistic Test Scenarios

### #4: Price Calculation Bug ⭐⭐⭐
**Why:** Very common in real e-commerce systems
**Test:** Order 3 items, get charged for 1
**Impact:** Financial loss
```bash
./trigger-logic-bug.sh  # Select 4
```

### #8: Data Leak Bug ⭐⭐⭐
**Why:** Critical privacy violation
**Test:** Users can see each other's orders
**Impact:** Security breach
```bash
./trigger-logic-bug.sh  # Select 8
```

### #1: Authentication Bypass ⭐⭐⭐
**Why:** Critical security vulnerability
**Test:** Any password works
**Impact:** Unauthorized access
```bash
./trigger-logic-bug.sh  # Select 1
```

## 🎯 Manual Testing (2 Steps)

### Step 1: Remove Skip Decorator
```python
# In tests/test_*.py
-@pytest.mark.skip(reason="...")
 def test_something():
```

### Step 2: Introduce Bug
Follow the docstring instructions:
```python
"""
TO TRIGGER:
In app.py line X, change:
    OLD CODE
To:
    NEW CODE (with bug)
"""
```

### Step 3: Push
```bash
git add .
git commit -m "Test: describe the bug"
git push
```

## ⚡ Super Quick Commands

### Test Price Bug
```bash
# Remove skip from test
sed -i '/@pytest.mark.skip.*order total/d' tests/test_order_pricing_logic.py

# Introduce bug
sed -i 's/total = money(total + line_total)/total = money(total + prod["price"])/' services/order-service/app.py

# Push
git add . && git commit -m "Test: price calc bug" && git push
```

### Test Data Leak
```bash
# Remove skip
sed -i '/@pytest.mark.skip.*user order isolation/d' tests/test_order_authorization_logic.py

# Introduce bug
sed -i 's/user_orders = \[o for o in ORDERS if o\["user"\] == username\]/user_orders = ORDERS/' services/order-service/app.py

# Push
git add . && git commit -m "Test: data leak bug" && git push
```

### Revert Everything
```bash
git revert HEAD --no-edit && git push
# OR
git checkout services/*/app.py tests/
```

## 📋 All 10 Scenarios at a Glance

| # | Name | Severity | File | Line |
|---|------|----------|------|------|
| 1 | Auth Bypass | 🔴 CRITICAL | user-service/app.py | 74 |
| 2 | Empty Username | 🟡 MEDIUM | user-service/app.py | 50 |
| 3 | Invalid Token | 🔴 HIGH | user-service/app.py | 86 |
| 4 | **Wrong Price** | 🔴 **HIGH** | **order-service/app.py** | **78** |
| 5 | Negative Qty | 🟡 MEDIUM | order-service/app.py | 75 |
| 6 | Zero Qty | 🟡 MEDIUM | order-service/app.py | 75 |
| 7 | Empty Cart | 🟡 MEDIUM | order-service/app.py | 66 |
| 8 | **Data Leak** | 🔴 **CRITICAL** | **order-service/app.py** | **122** |
| 9 | Access Control | 🔴 HIGH | order-service/app.py | 106 |
| 10 | No Auth Check | 🔴 CRITICAL | order-service/app.py | 57 |

⭐ = Recommended for first test

## 🕐 Timing

- Commit → Tests fail: **~1 minute**
- Tests fail → Email: **~5 minutes**
- **Total**: **~6 minutes** from push to AI analysis

## ✅ Success Checklist

After pushing:
1. ⏰ Wait 1-2 min → Check GitHub Actions (should be red ❌)
2. ⏰ Wait 5-7 min → Check Email 📧
3. ✅ Email contains:
   - Root cause identified
   - Business impact explained
   - Code fix suggested
4. 🔄 Revert and push fix

## 🎯 Pro Tips

1. **Start with #4 or #8** - Most realistic business bugs
2. **Test locally first**: `pytest tests/test_*.py::test_name -v`
3. **Use descriptive commits**: Help AI understand context
4. **One bug at a time**: Easier to analyze
5. **Always revert**: Don't leave bugs in code!

## 🚨 If Something Goes Wrong

```bash
# Check what's modified
git status
git diff

# Undo everything
git checkout .
git clean -fd

# Start fresh
git pull origin master
```

## 📖 Full Documentation

See [LOGIC_BUG_TESTING_GUIDE.md](./LOGIC_BUG_TESTING_GUIDE.md) for complete details.

---

**Ready? Run `./trigger-logic-bug.sh` now!** 🚀
