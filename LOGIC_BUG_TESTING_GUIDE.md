# Logic Bug Testing Guide

This guide explains how to test your CI/CD monitoring system with **business logic failures** (not just syntax errors).

## ⚡ Quick Start

```bash
# 1. Introduce a bug
./trigger-logic-bug.sh
# Select option 4 (price calculation bug)

# 2. Commit with [test-logic] to enable tests for this commit only
git add .
git commit -m "Test: price calculation bug [test-logic]"
git push

# 3. Wait ~6 minutes for AI analysis email
# 4. Revert when done
git revert HEAD --no-edit && git push
```

**That's it!** The `[test-logic]` in your commit message enables logic tests for just that one push.

## 🎛️ Test Control Switch

Logic tests are **DISABLED by default** so normal CI passes. Enable them:

- **Option A (Easiest)**: Add `[test-logic]` to commit message (one-time)
- **Option B**: Use `./toggle-logic-tests.sh` to enable variable (persistent)
- **Option C**: Manual workflow run via GitHub Actions UI (one-time)

📖 **See [LOGIC_TESTS_SWITCH_GUIDE.md](./LOGIC_TESTS_SWITCH_GUIDE.md) for complete switch documentation**

---

## 🎯 What's Different About Logic Bugs?

Unlike syntax errors:
- ✅ Code is syntactically correct
- ✅ Linting passes
- ❌ Tests fail due to incorrect business logic
- 🤖 AI must understand business requirements to diagnose

## 📁 Test Files Overview

We've created three test files with **10 different logic bug scenarios**:

### `tests/test_user_auth_logic.py`
- Authentication bypass (wrong password accepted)
- Input validation failures (empty username)
- Token validation issues

### `tests/test_order_pricing_logic.py`
- Price calculation errors (wrong totals)
- Business rule violations (negative quantities)
- Edge cases (empty cart, zero quantity)

### `tests/test_order_authorization_logic.py`
- Authorization bypasses (access other users' data)
- Missing authentication checks
- Data isolation failures

## 🚀 Quick Start

### Method 1: Using the Interactive Script (Recommended)

```bash
# Make the script executable
chmod +x trigger-logic-bug.sh

# Run the interactive menu
./trigger-logic-bug.sh
```

This will show you a menu where you can select which bug to trigger.

### Method 2: Manual Testing

Follow the 2-step process:

#### Step 1: Enable the Test

Edit the test file and remove `@pytest.mark.skip`:

```python
# BEFORE (test disabled - CI will pass):
@pytest.mark.skip(reason="Enable this test to check authentication logic")
def test_wrong_password_rejected():
    ...

# AFTER (test enabled - CI will run this test):
def test_wrong_password_rejected():
    ...
```

#### Step 2: Introduce the Bug

Follow the instructions in the test's docstring. For example:

```python
"""
TO TRIGGER THIS TEST FAILURE:
In services/user-service/app.py, line 74, change:
    if not user or user["password_hash"] != hash_pw(password):
To:
    if not user:  # BUG: Removed password check!
"""
```

#### Step 3: Commit and Push

```bash
git add .
git commit -m "Test: authentication bypass bug"
git push
```

## 📋 Available Test Scenarios

### 1️⃣ Authentication Bypass

**Test:** `test_wrong_password_rejected`
**File:** `tests/test_user_auth_logic.py`
**Bug Location:** `services/user-service/app.py:74`

**What it tests:** Any password is accepted for valid usernames

**Expected AI Analysis:**
```
Root Cause: Authentication logic flaw - password validation bypassed.
Summary: Critical security vulnerability allowing unauthorized access.
Suggestion: Restore password validation check.
Impact: CRITICAL - Complete authentication bypass
```

**Quick trigger:**
```bash
./trigger-logic-bug.sh
# Select option 1
```

---

### 2️⃣ Empty Username Accepted

**Test:** `test_empty_username_rejected`
**File:** `tests/test_user_auth_logic.py`
**Bug Location:** `services/user-service/app.py:50`

**What it tests:** Input validation for username field

---

### 3️⃣ Invalid Token Accepted

**Test:** `test_invalid_token_rejected`
**File:** `tests/test_user_auth_logic.py`
**Bug Location:** `services/user-service/app.py:86`

**What it tests:** Token validation doesn't check user existence

---

### 4️⃣ Wrong Order Total (Most Realistic!)

**Test:** `test_order_total_calculation_with_quantity`
**File:** `tests/test_order_pricing_logic.py`
**Bug Location:** `services/order-service/app.py:78`

**What it tests:** Order total calculation with quantities

**Scenario:**
- Order 3 mice at $19.99 each
- Expected: $59.97
- Bug causes: $19.99 (only single item price added)

**Expected AI Analysis:**
```
Root Cause: Price calculation error - quantity not applied to total.
Summary: When ordering multiple items, only single item price counted.
Suggestion: Change line 78 to use line_total instead of prod["price"]
Impact: HIGH - Financial loss on multi-quantity orders
Test: Expected $59.97 but got $19.99
```

**Quick trigger:**
```bash
./trigger-logic-bug.sh
# Select option 4
```

---

### 5️⃣ Negative Quantity Allowed

**Test:** `test_negative_quantity_rejected`
**File:** `tests/test_order_pricing_logic.py`
**Bug Location:** `services/order-service/app.py:75`

**What it tests:** Business rule - quantities must be positive

---

### 6️⃣ Zero Quantity Allowed

**Test:** `test_zero_quantity_rejected`
**File:** `tests/test_order_pricing_logic.py`
**Bug Location:** Same as #5

**What it tests:** Cannot order zero items

---

### 7️⃣ Empty Cart Allowed

**Test:** `test_empty_cart_rejected`
**File:** `tests/test_order_pricing_logic.py`
**Bug Location:** `services/order-service/app.py:66-67`

**What it tests:** Orders must have at least one item

---

### 8️⃣ User Can See All Orders (Data Leak!)

**Test:** `test_user_order_isolation`
**File:** `tests/test_order_authorization_logic.py`
**Bug Location:** `services/order-service/app.py:122`

**What it tests:** Users should only see their own orders

**Scenario:**
- Alice creates 1 order
- Bob creates 1 order
- Bug: Alice sees both orders (should only see hers)

**Expected AI Analysis:**
```
Root Cause: Authorization bypass - user isolation not enforced.
Summary: Data leak allowing users to view other users' orders.
Suggestion: Filter orders by username
Impact: CRITICAL - Privacy violation, data leak
Test: Alice should see 1 order but sees 2
```

**Quick trigger:**
```bash
./trigger-logic-bug.sh
# Select option 8
```

---

### 9️⃣ Access Other User's Order by ID

**Test:** `test_cannot_access_other_users_order`
**File:** `tests/test_order_authorization_logic.py`
**Bug Location:** `services/order-service/app.py:106`

**What it tests:** Direct order access requires ownership check

---

### 🔟 Missing Token Allowed

**Test:** `test_missing_token_rejected`
**File:** `tests/test_order_authorization_logic.py`
**Bug Location:** `services/order-service/app.py:57`

**What it tests:** Authentication is required

---

## 🎮 Usage Patterns

### Pattern 1: Test One Bug at a Time

```bash
# Trigger bug #4 (price calculation)
./trigger-logic-bug.sh
# Select option 4

# Commit and push
git add .
git commit -m "Test: price calculation bug"
git push

# Wait for CI to fail and AI to analyze (~5 minutes)
# Check your email for AI analysis

# Revert
./trigger-logic-bug.sh
# Select option 11 (Revert All)
git add .
git commit -m "Fix: revert price bug"
git push
```

### Pattern 2: Test Multiple Bugs in Sequence

```bash
#!/bin/bash
# test-all-bugs.sh

bugs=(1 4 8)  # Test authentication, pricing, and authorization

for bug in "${bugs[@]}"; do
    echo "Testing bug #$bug..."

    # Trigger bug
    echo "$bug" | ./trigger-logic-bug.sh

    # Commit
    git add .
    git commit -m "Test: bug scenario $bug"
    git push

    # Wait for CI + AI analysis
    sleep 300  # 5 minutes

    # Revert
    git revert HEAD --no-edit
    git push

    # Wait for successful build
    sleep 180  # 3 minutes
done

echo "All tests complete! Check your email."
```

### Pattern 3: Quick Manual Test

```bash
# 1. Edit test file - remove @pytest.mark.skip
vim tests/test_order_pricing_logic.py
# Remove skip decorator from test_order_total_calculation_with_quantity

# 2. Edit app file - introduce bug
vim services/order-service/app.py
# Line 78: Change "line_total" to "prod['price']"

# 3. Commit and push
git add .
git commit -m "Test: price calculation logic bug"
git push

# 4. Watch GitHub Actions
gh run watch

# 5. Wait for email with AI analysis
```

## 🔍 How to Run Tests Locally

Before pushing, test locally:

```bash
# Run all tests (skipped tests won't run)
pytest tests/ -v

# Run only enabled tests (skip the @pytest.mark.skip ones)
pytest tests/ -v

# Run a specific test (even if marked skip)
pytest tests/test_order_pricing_logic.py::test_order_total_calculation_with_quantity -v

# Run with more detail
pytest tests/ -vv --tb=short
```

## 🎯 Testing Best Practices

### 1. Test One Bug at a Time
- Easier to understand AI analysis
- Clear cause and effect
- Simpler to revert

### 2. Use Descriptive Commit Messages
```bash
# Good:
git commit -m "Test: authentication bypass - wrong password accepted"

# Bad:
git commit -m "test"
```

### 3. Wait for Complete CI Pipeline
- Tests run (~30-60 seconds)
- N8n detects failure (~1-2 minutes)
- AI analyzes logs (~2-3 minutes)
- Email sent (~1 minute)
- **Total: ~5-7 minutes**

### 4. Document Results
Keep track of which bugs the AI successfully identified:

```
Bug #1 (Auth Bypass): ✅ AI correctly identified
Bug #4 (Price Calc): ✅ AI found root cause and suggested fix
Bug #8 (Data Leak): ⚠️ AI identified issue but suggestion unclear
```

### 5. Clean Up After Testing
```bash
# Always revert test bugs
git revert HEAD --no-edit
git push

# Or reset if you have multiple test commits
git reset --hard origin/master
git push --force  # Be careful with force push!
```

## 📊 Expected CI/CD Flow

```
Push with Logic Bug
    ↓
detect-changes (10s) ✅
    ↓
lint-and-test (30-60s)
    ├─ Lint with flake8 ✅
    ├─ Validate Python syntax ✅
    ├─ Check imports ✅
    └─ Run tests ❌ TEST FAILED
    ↓
build-push ⏭️ SKIPPED
    ↓
N8n Workflow Triggered (1-2 min)
    ├─ Fetch job logs
    ├─ Trigger AI analysis
    └─ Send email notification
    ↓
Email Received with AI Analysis! 📧
```

## 🧪 Verification Checklist

After triggering a logic bug:

- [ ] GitHub Actions shows test failure (not syntax/lint error)
- [ ] Error message shows assertion failure with business context
- [ ] N8n workflow executes
- [ ] AI analysis received via email
- [ ] AI correctly identifies:
  - [ ] Root cause
  - [ ] Business impact
  - [ ] Suggested fix
  - [ ] Affected code location

## 🚨 Troubleshooting

### Issue: Tests still pass after introducing bug

**Check:**
1. Did you remove `@pytest.mark.skip` from the test?
2. Did you save both files (test + app code)?
3. Did you commit both changes?

```bash
# Verify changes are staged
git status
git diff --cached
```

### Issue: Tests fail but for wrong reason

**Check:**
1. Make sure you introduced the EXACT change specified
2. Line numbers might be different - search for the code pattern
3. Previous tests might be interfering - revert all first

### Issue: AI analysis is generic

**This is expected sometimes!** Logic bugs are harder to analyze than syntax errors. Try:
- Using bugs with clearer business impact (#4, #8)
- Adding more context in commit messages
- Checking if test output is being captured

### Issue: Script doesn't work on Windows

Use Git Bash or WSL:
```bash
# In Git Bash
bash trigger-logic-bug.sh

# Or use Python version
python trigger-logic-bug.py
```

## 📈 Advanced Usage

### Create Custom Logic Bugs

1. Write a test that asserts business requirements
2. Mark it with `@pytest.mark.skip`
3. Add clear instructions in docstring
4. Commit with tests disabled
5. Use for future testing

Example:
```python
@pytest.mark.skip(reason="Enable to test discount calculation")
def test_discount_applied_correctly():
    """
    Test that 10% discount is applied to orders over $100

    TO TRIGGER:
    In app.py, remove the discount calculation logic
    """
    # Your test here
    pass
```

### Measure AI Analysis Quality

Track these metrics:
- **Detection Rate**: % of bugs where AI sent analysis
- **Accuracy**: % where AI identified correct root cause
- **Usefulness**: % where suggestion was actionable
- **Time**: Average time from push to email

### Integration with Monitoring

Add custom metrics:
```python
# In CI workflow
- name: Record test failure type
  if: failure()
  run: |
    if grep -q "AssertionError" test-output.log; then
      echo "LOGIC_FAILURE" >> $GITHUB_ENV
    fi
```

## 🎉 Success Metrics

Your AI analysis system is working well when:

✅ Receives email within 5-7 minutes of push
✅ AI correctly identifies it's a logic error (not syntax)
✅ Root cause mentions the business rule violated
✅ Suggestion includes specific code change or investigation step
✅ Impact/severity is assessed correctly

## 📚 Additional Resources

- [TEST_SCENARIOS_QUICK_REF.md](./TEST_SCENARIOS_QUICK_REF.md) - Syntax error tests
- [CI_TESTING_GUIDE.md](./CI_TESTING_GUIDE.md) - CI pipeline setup
- [GitHub Actions Logs](https://github.com/YOUR_ORG/YOUR_REPO/actions)
- [N8n Workflow Executions](http://your-n8n-instance/executions)

---

**Ready to test? Run `./trigger-logic-bug.sh` and select a scenario!** 🚀
