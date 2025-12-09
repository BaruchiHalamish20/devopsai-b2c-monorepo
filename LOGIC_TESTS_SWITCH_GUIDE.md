# Logic Tests Switch Guide

## 🎛️ Overview

Your CI pipeline now has **3 ways** to control when logic bug tests run:

1. **Repository Variable** - Persistent toggle (stays enabled until you turn it off)
2. **Manual Workflow Run** - One-time execution via GitHub UI
3. **Commit Message Trigger** - One-time trigger using `[test-logic]` in commit message

By default, **logic tests are DISABLED** so your normal CI runs pass.

---

## 📋 Quick Reference

### Enable Logic Tests (Persistent)

```bash
./toggle-logic-tests.sh
# Select option 2
```

### Disable Logic Tests

```bash
./toggle-logic-tests.sh
# Select option 3
```

### One-Time Test (Commit Message)

```bash
git commit -m "Test: price calculation bug [test-logic]"
git push
```

---

## 🎯 Method 1: Repository Variable (Recommended for Testing Sessions)

**Use when:** You want to test multiple bugs in a row

### Enable via Script

```bash
chmod +x toggle-logic-tests.sh
./toggle-logic-tests.sh
# Select option 2: Enable logic tests
```

### Enable Manually

1. Go to your GitHub repository
2. Navigate to: **Settings → Secrets and variables → Actions → Variables tab**
3. Click **New repository variable**
4. Name: `ENABLE_LOGIC_TESTS`
5. Value: `true`
6. Click **Add variable**

### Check Status

```bash
./toggle-logic-tests.sh
# Select option 1: Show current status
```

### Using GitHub CLI

```bash
# Enable
gh variable set ENABLE_LOGIC_TESTS -b "true"

# Disable
gh variable set ENABLE_LOGIC_TESTS -b "false"

# Check
gh variable list | grep ENABLE_LOGIC_TESTS
```

### ⚠️ Important

- Once enabled, **EVERY push** to master will run logic tests
- Tests will **FAIL** if you have introduced bugs (intentionally or not)
- **Always disable when done testing!**

---

## 🎯 Method 2: Manual Workflow Run (Best for One-Time Tests)

**Use when:** You want to test once without enabling it for all pushes

### Via Script

```bash
./toggle-logic-tests.sh
# Select option 4: Run workflow manually
```

### Via GitHub UI

1. Go to: **Actions** tab in your repository
2. Select workflow: **Build & Push changed services (GHCR)**
3. Click **Run workflow** button (on the right)
4. Check the box: ☑️ **Enable logic bug tests (normally disabled)**
5. Click green **Run workflow** button

### Via GitHub CLI

```bash
gh workflow run ci.yml -f enable_logic_tests=true
```

### Watch the Run

```bash
# Watch in terminal
gh run watch

# Or open in browser
gh run view --web
```

---

## 🎯 Method 3: Commit Message Trigger (Easiest for Quick Tests)

**Use when:** You want logic tests for just one commit

### How It Works

Add `[test-logic]` **anywhere** in your commit message:

```bash
# Example 1
git commit -m "Test: authentication bug [test-logic]"

# Example 2
git commit -m "[test-logic] Testing price calculation"

# Example 3
git commit -m "Fix user service

This commit introduces a test bug [test-logic]"
```

Then push:

```bash
git push
```

### ✅ Advantages

- No need to enable/disable variables
- No need to use GitHub UI
- Clear in git history which commits were test runs
- Automatic - just include the tag

### Example Workflow

```bash
# 1. Introduce bug
./trigger-logic-bug.sh
# Select option 4 (price calculation bug)

# 2. Commit with trigger
git add .
git commit -m "Test: price calculation logic bug [test-logic]"
git push

# 3. Wait for CI to run (~1 min) and fail
# 4. Wait for AI analysis (~5 mins)
# 5. Check email

# 6. Revert
git revert HEAD --no-edit
git push  # This push won't run logic tests (no [test-logic])
```

---

## 🔄 Complete Testing Workflows

### Workflow A: Quick Single Test

```bash
# Use commit message trigger (no setup needed)
./trigger-logic-bug.sh  # Select a bug
git add .
git commit -m "Test: bug scenario [test-logic]"
git push

# Wait ~6 minutes
# Check email

# Revert
git revert HEAD --no-edit && git push
```

### Workflow B: Multiple Tests in Session

```bash
# 1. Enable via variable
./toggle-logic-tests.sh  # Select option 2

# 2. Test bug #4
./trigger-logic-bug.sh  # Select 4
git add . && git commit -m "Test: price bug" && git push
# Wait ~6 min, check email

# 3. Revert
git revert HEAD --no-edit && git push

# 4. Test bug #8
./trigger-logic-bug.sh  # Select 8
git add . && git commit -m "Test: data leak" && git push
# Wait ~6 min, check email

# 5. Revert
git revert HEAD --no-edit && git push

# 6. Disable tests
./toggle-logic-tests.sh  # Select option 3
```

### Workflow C: Manual One-Time Run

```bash
# Useful when you want to test without committing

# 1. Introduce bug locally (don't commit yet)
./trigger-logic-bug.sh  # Select a bug

# 2. Commit
git add . && git commit -m "Test: logic bug"
git push

# 3. Trigger manual run with logic tests
./toggle-logic-tests.sh  # Select option 4

# 4. Wait for results
gh run watch

# 5. Revert
git revert HEAD --no-edit && git push
```

---

## 📊 What Happens When Enabled?

### CI Flow (Normal)

```
Push → Lint ✅ → Tests ✅ → Build ✅ → Deploy ✅
```

### CI Flow (With Logic Tests Enabled)

```
Push → Lint ✅ → Tests ✅ → Logic Tests 🔬 → Build → Deploy

If logic test fails: ❌
  → Build SKIPPED
  → n8n triggered
  → AI analyzes
  → Email sent
```

### GitHub Actions Output

When logic tests are enabled, you'll see:

```
🔬 Running LOGIC BUG TESTS for user-service...
⚠️  These tests check for business logic failures.

✓ Enabled via: Repository variable ENABLE_LOGIC_TESTS

tests/test_user_auth_logic.py::test_wrong_password_rejected FAILED
```

---

## 🚨 Troubleshooting

### Tests Don't Run When Enabled

**Check:**
1. Did you enable the correct repository variable?
   ```bash
   gh variable list | grep ENABLE_LOGIC_TESTS
   ```

2. Is it set to `true` (not `"true"` with quotes)?

3. Are you pushing to the master branch?

4. Did you remove `@pytest.mark.skip` from the test?

### Tests Pass But Should Fail

**Check:**
1. Did you introduce the bug in the code?
   ```bash
   git diff services/*/app.py
   ```

2. Did you commit AND push both files (test + app)?
   ```bash
   git log -1 --stat
   ```

3. Is the service that changed being detected?
   Check the GitHub Actions log for "detect-changes"

### Variable Not Working

**Option 1: Use commit message trigger instead**
```bash
git commit -m "Test [test-logic]"
```

**Option 2: Use manual workflow run**
```bash
gh workflow run ci.yml -f enable_logic_tests=true
```

**Option 3: Check permissions**
- Make sure you have admin access to the repository
- Check if GitHub CLI is authenticated: `gh auth status`

---

## 🎓 Best Practices

### 1. **Always Disable After Testing**

```bash
# At end of testing session
./toggle-logic-tests.sh  # Select option 3: Disable
```

Otherwise every push will fail!

### 2. **Use Commit Message Trigger for One-Offs**

Quickest way to test:
```bash
git commit -m "Your message [test-logic]"
```

### 3. **Use Repository Variable for Testing Sessions**

When testing multiple bugs:
```bash
# Start of session
./toggle-logic-tests.sh  # Enable

# ... test multiple bugs ...

# End of session
./toggle-logic-tests.sh  # Disable
```

### 4. **Check Status Before Pushing**

```bash
./toggle-logic-tests.sh  # Option 1: Show status
```

### 5. **Clear Indicators in Commit Messages**

```bash
# Good
git commit -m "Test: authentication bypass [test-logic]"

# Bad
git commit -m "fix [test-logic]"
```

### 6. **Document Your Test Results**

Keep track:
```
Test Session 2024-01-15
- Bug #4 (Price): ✅ AI identified correctly
- Bug #8 (Data Leak): ✅ AI found root cause
- Bug #1 (Auth): ⚠️ AI analysis generic
```

---

## 📖 Examples

### Example 1: Test Authentication Bug

```bash
# Using commit message trigger
./trigger-logic-bug.sh
# Select: 1 (Authentication bypass)

git add .
git commit -m "Test: wrong password accepted bug [test-logic]"
git push

# Wait ~6 minutes
# Email arrives with AI analysis

git revert HEAD --no-edit
git push
```

### Example 2: Test Multiple Bugs in One Session

```bash
# Enable tests for session
./toggle-logic-tests.sh
# Select: 2 (Enable)

# Test bug #4
./trigger-logic-bug.sh && git add . && git commit -m "Test: price bug" && git push
sleep 360  # Wait 6 min
git revert HEAD --no-edit && git push
sleep 180  # Wait for clean build

# Test bug #8
./trigger-logic-bug.sh && git add . && git commit -m "Test: data leak" && git push
sleep 360
git revert HEAD --no-edit && git push

# Disable tests
./toggle-logic-tests.sh
# Select: 3 (Disable)
```

### Example 3: Manual Workflow Run

```bash
# Introduce bug but don't enable tests in config
./trigger-logic-bug.sh
git add . && git commit -m "Test: logic bug" && git push

# Now manually trigger with tests
gh workflow run ci.yml -f enable_logic_tests=true

# Watch
gh run watch

# Revert when done
git revert HEAD --no-edit && git push
```

---

## 🔍 Checking What's Enabled

### Script

```bash
./toggle-logic-tests.sh
# Select option 1
```

### GitHub CLI

```bash
gh variable list | grep ENABLE_LOGIC_TESTS
```

### GitHub UI

1. Go to: **Settings → Secrets and variables → Actions**
2. Click **Variables** tab
3. Look for `ENABLE_LOGIC_TESTS`

### In CI Logs

When logic tests run, they show which trigger was used:

```
✓ Enabled via: Repository variable ENABLE_LOGIC_TESTS
# or
✓ Enabled via: Manual workflow dispatch
# or
✓ Enabled via: Commit message contains [test-logic]
```

---

## 🎉 Summary

| Method | Best For | Enable | Disable | Scope |
|--------|----------|--------|---------|-------|
| **Repository Variable** | Multiple tests | Script/UI | Script/UI | Every push |
| **Manual Run** | One-time | GitHub UI | Automatic | Single run |
| **Commit Message** | Quick test | `[test-logic]` | Automatic | Single commit |

**Recommended workflow:**
1. Start: Use commit message `[test-logic]` for first test
2. Multiple tests: Enable variable for session
3. Always: Disable variable when done!

---

## 📚 Related Files

- [`toggle-logic-tests.sh`](./toggle-logic-tests.sh) - Interactive toggle script
- [`trigger-logic-bug.sh`](./trigger-logic-bug.sh) - Bug introduction script
- [`LOGIC_BUG_TESTING_GUIDE.md`](./LOGIC_BUG_TESTING_GUIDE.md) - Complete testing guide
- [`QUICK_BUG_REFERENCE.md`](./QUICK_BUG_REFERENCE.md) - Quick reference card
- [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) - CI workflow with switch

---

**Ready to test? Start with the commit message trigger - it's the easiest!**

```bash
./trigger-logic-bug.sh  # Select a bug
git commit -m "Test: bug name [test-logic]" && git push
```

🚀
