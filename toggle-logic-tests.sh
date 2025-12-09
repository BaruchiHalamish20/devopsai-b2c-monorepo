#!/bin/bash
# Script to toggle logic bug tests in CI

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get repository info
REPO_OWNER=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\1#p')
REPO_NAME=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\2#p')

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Logic Bug Test Toggle Manager               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Repository: ${CYAN}${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

show_status() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Current Status:${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
        echo ""
        echo "To check the status, you need the GitHub CLI:"
        echo "  • Install: https://cli.github.com/"
        echo "  • Or check manually at: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/variables/actions"
        echo ""
        return
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}✗ Not authenticated with GitHub CLI${NC}"
        echo ""
        echo "Run: ${CYAN}gh auth login${NC}"
        echo ""
        return
    fi

    # Get current value
    CURRENT_VALUE=$(gh variable list -R "${REPO_OWNER}/${REPO_NAME}" 2>/dev/null | grep "ENABLE_LOGIC_TESTS" | awk '{print $2}' || echo "NOT_SET")

    if [ "$CURRENT_VALUE" = "NOT_SET" ]; then
        echo -e "  Repository Variable: ${YELLOW}NOT SET (tests disabled)${NC}"
    elif [ "$CURRENT_VALUE" = "true" ]; then
        echo -e "  Repository Variable: ${GREEN}ENABLED ✓${NC}"
        echo -e "  ${YELLOW}⚠️  Logic tests WILL RUN on every push!${NC}"
    else
        echo -e "  Repository Variable: ${RED}DISABLED ✗${NC}"
    fi

    echo ""
    echo -e "${CYAN}Ways to enable logic tests:${NC}"
    echo "  1. Repository variable (persistent until changed)"
    echo "  2. Manual workflow run (one-time)"
    echo "  3. Commit message with [test-logic] (one-time)"
    echo ""
}

enable_tests() {
    echo -e "${GREEN}Enabling logic bug tests...${NC}"
    echo ""

    if ! command -v gh &> /dev/null; then
        echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
        echo ""
        echo "Install GitHub CLI: https://cli.github.com/"
        echo ""
        echo -e "${YELLOW}Alternative: Enable manually${NC}"
        echo "1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/variables/actions"
        echo "2. Create variable: ENABLE_LOGIC_TESTS"
        echo "3. Set value: true"
        echo ""
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        echo -e "${RED}✗ Not authenticated${NC}"
        echo "Run: ${CYAN}gh auth login${NC}"
        exit 1
    fi

    # Set the variable
    gh variable set ENABLE_LOGIC_TESTS -b "true" -R "${REPO_OWNER}/${REPO_NAME}"

    echo -e "${GREEN}✓ Logic tests ENABLED${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Logic tests will now run on EVERY push to master!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Use ./trigger-logic-bug.sh to introduce a bug"
    echo "  2. Commit and push"
    echo "  3. CI will run and tests will fail"
    echo "  4. Check email for AI analysis"
    echo "  5. Don't forget to disable tests when done!"
    echo ""
}

disable_tests() {
    echo -e "${YELLOW}Disabling logic bug tests...${NC}"
    echo ""

    if ! command -v gh &> /dev/null; then
        echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
        echo ""
        echo -e "${YELLOW}Alternative: Disable manually${NC}"
        echo "1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/variables/actions"
        echo "2. Delete variable: ENABLE_LOGIC_TESTS (or set to false)"
        echo ""
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        echo -e "${RED}✗ Not authenticated${NC}"
        echo "Run: ${CYAN}gh auth login${NC}"
        exit 1
    fi

    # Delete or set to false
    gh variable set ENABLE_LOGIC_TESTS -b "false" -R "${REPO_OWNER}/${REPO_NAME}"

    echo -e "${GREEN}✓ Logic tests DISABLED${NC}"
    echo ""
    echo "Logic tests will NOT run on regular pushes."
    echo ""
}

run_manually() {
    echo -e "${CYAN}Running workflow manually with logic tests enabled...${NC}"
    echo ""

    if ! command -v gh &> /dev/null; then
        echo -e "${RED}✗ GitHub CLI (gh) not installed${NC}"
        echo ""
        echo -e "${YELLOW}Alternative: Run manually via GitHub UI${NC}"
        echo "1. Go to: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
        echo "2. Select 'Build & Push changed services (GHCR)'"
        echo "3. Click 'Run workflow'"
        echo "4. Check the 'Enable logic bug tests' checkbox"
        echo "5. Click 'Run workflow' button"
        echo ""
        exit 1
    fi

    gh workflow run ci.yml -R "${REPO_OWNER}/${REPO_NAME}" -f enable_logic_tests=true

    echo -e "${GREEN}✓ Workflow triggered!${NC}"
    echo ""
    echo "Watch it at: https://github.com/${REPO_OWNER}/${REPO_NAME}/actions"
    echo "Or run: ${CYAN}gh run watch${NC}"
    echo ""
}

commit_with_trigger() {
    echo -e "${CYAN}Commit with [test-logic] trigger${NC}"
    echo ""
    echo "When you add [test-logic] to your commit message,"
    echo "logic tests will run for that push only."
    echo ""
    echo -e "${YELLOW}Example:${NC}"
    echo '  git commit -m "Test: authentication bug [test-logic]"'
    echo ""
    echo "This is useful for one-time testing without enabling"
    echo "the repository variable."
    echo ""
}

show_menu() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}What would you like to do?${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  1) Show current status"
    echo "  2) Enable logic tests (persistent)"
    echo "  3) Disable logic tests"
    echo "  4) Run workflow manually (one-time)"
    echo "  5) How to use commit message trigger"
    echo "  0) Exit"
    echo ""
}

# Main
show_status

while true; do
    show_menu
    read -p "Select option: " choice
    echo ""

    case $choice in
        1)
            show_status
            ;;
        2)
            enable_tests
            ;;
        3)
            disable_tests
            ;;
        4)
            run_manually
            ;;
        5)
            commit_with_trigger
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac

    read -p "Press Enter to continue..."
    echo ""
done
