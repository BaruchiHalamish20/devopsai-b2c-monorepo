#!/bin/bash
# Helper script to trigger specific logic bug scenarios

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_menu() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║    Logic Bug Test Scenario Trigger Menu          ║${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo -e "${YELLOW}Authentication Bugs (User Service):${NC}"
    echo "  1) Wrong Password Accepted (Authentication Bypass)"
    echo "  2) Empty Username Accepted (Input Validation)"
    echo "  3) Invalid Token Accepted (Token Validation)"
    echo ""
    echo -e "${YELLOW}Pricing Bugs (Order Service):${NC}"
    echo "  4) Wrong Order Total (Quantity Not Applied)"
    echo "  5) Negative Quantity Allowed"
    echo "  6) Zero Quantity Allowed"
    echo "  7) Empty Cart Allowed"
    echo ""
    echo -e "${YELLOW}Authorization Bugs (Order Service):${NC}"
    echo "  8) User Can See All Orders (Data Leak)"
    echo "  9) User Can Access Other's Orders (Authorization Bypass)"
    echo " 10) Missing Token Allowed"
    echo ""
    echo -e "${YELLOW}Control:${NC}"
    echo " 11) Revert All Changes"
    echo " 12) Show Current Status"
    echo "  0) Exit"
    echo ""
}

enable_test() {
    local file=$1
    local test_name=$2
    echo -e "${GREEN}Enabling test: $test_name${NC}"
    sed -i "s/@pytest.mark.skip(reason=\"Enable this test to check $test_name\")/@pytest.mark.skip_disabled  # Test enabled/" "$file" || \
    sed -i "s/@pytest.mark.skip.*$test_name.*/@pytest.mark.skip_disabled  # Test enabled/" "$file"
}

introduce_bug_1() {
    echo -e "${RED}Introducing Bug: Authentication Bypass${NC}"
    # Enable the test
    enable_test "tests/test_user_auth_logic.py" "authentication logic"

    # Introduce the bug
    sed -i 's/if not user or user\["password_hash"\] != hash_pw(password):/if not user:  # BUG: Removed password check!/' services/user-service/app.py

    echo -e "${GREEN}✓ Bug introduced in services/user-service/app.py${NC}"
    echo -e "${GREEN}✓ Test enabled in tests/test_user_auth_logic.py${NC}"
    echo ""
    echo -e "${YELLOW}Ready to commit and push!${NC}"
    echo "Run: git add . && git commit -m \"Test: authentication bypass bug\" && git push"
}

introduce_bug_2() {
    echo -e "${RED}Introducing Bug: Empty Username Accepted${NC}"
    enable_test "tests/test_user_auth_logic.py" "empty username handling"

    sed -i 's/if not username or not password:/if not password:  # BUG: Only checking password!/' services/user-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: empty username validation bug\" && git push"
}

introduce_bug_3() {
    echo -e "${RED}Introducing Bug: Invalid Token Accepted${NC}"
    enable_test "tests/test_user_auth_logic.py" "token validation"

    sed -i 's/if not username or username not in USERS:/if not username:  # BUG: Doesn'\''t check if user exists!/' services/user-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: token validation bug\" && git push"
}

introduce_bug_4() {
    echo -e "${RED}Introducing Bug: Wrong Order Total${NC}"
    enable_test "tests/test_order_pricing_logic.py" "order total calculation"

    sed -i 's/total = money(total + line_total)/total = money(total + prod["price"])  # BUG: Should add line_total!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: order total calculation bug\" && git push"
}

introduce_bug_5() {
    echo -e "${RED}Introducing Bug: Negative Quantity Allowed${NC}"
    enable_test "tests/test_order_pricing_logic.py" "negative quantity validation"

    sed -i 's/if not prod or qty <= 0:/if not prod:  # BUG: Removed qty check!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: negative quantity validation bug\" && git push"
}

introduce_bug_6() {
    echo -e "${RED}Introducing Bug: Zero Quantity Allowed${NC}"
    enable_test "tests/test_order_pricing_logic.py" "zero quantity validation"

    # Same bug as #5
    sed -i 's/if not prod or qty <= 0:/if not prod:  # BUG: Removed qty check!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: zero quantity validation bug\" && git push"
}

introduce_bug_7() {
    echo -e "${RED}Introducing Bug: Empty Cart Allowed${NC}"
    enable_test "tests/test_order_pricing_logic.py" "empty cart validation"

    sed -i 's/if not items:/# if not items:  # BUG: Commented out validation!/' services/order-service/app.py
    sed -i 's/return jsonify({"error":"items required"}), 400/#     return jsonify({"error":"items required"}), 400/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: empty cart validation bug\" && git push"
}

introduce_bug_8() {
    echo -e "${RED}Introducing Bug: User Can See All Orders${NC}"
    enable_test "tests/test_order_authorization_logic.py" "user order isolation"

    sed -i 's/user_orders = \[o for o in ORDERS if o\["user"\] == username\]/user_orders = ORDERS  # BUG: Exposes all users'\'' orders!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: order isolation bug\" && git push"
}

introduce_bug_9() {
    echo -e "${RED}Introducing Bug: User Can Access Other's Orders${NC}"
    enable_test "tests/test_order_authorization_logic.py" "specific order access control"

    sed -i 's/if o\["order_id"\] == order_id and o\["user"\] == username:/if o["order_id"] == order_id:  # BUG: Doesn'\''t check user ownership!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: order access control bug\" && git push"
}

introduce_bug_10() {
    echo -e "${RED}Introducing Bug: Missing Token Allowed${NC}"
    enable_test "tests/test_order_authorization_logic.py" "missing token handling"

    # This is trickier - need to find the right line in create_order
    sed -i '57s/if not auth.lower().startswith("bearer "):/if False:  # BUG: Always allows access!/' services/order-service/app.py

    echo -e "${GREEN}✓ Bug introduced${NC}"
    echo "Run: git add . && git commit -m \"Test: missing token bug\" && git push"
}

revert_all() {
    echo -e "${YELLOW}Reverting all changes...${NC}"
    git checkout services/user-service/app.py
    git checkout services/order-service/app.py
    git checkout tests/
    echo -e "${GREEN}✓ All changes reverted${NC}"
}

show_status() {
    echo -e "${BLUE}Current Status:${NC}"
    echo ""
    echo "Modified files:"
    git status --short
    echo ""
    echo "Recent commits:"
    git log --oneline --graph --decorate -5
}

# Main menu loop
while true; do
    show_menu
    read -p "Select option: " choice

    case $choice in
        1) introduce_bug_1 ;;
        2) introduce_bug_2 ;;
        3) introduce_bug_3 ;;
        4) introduce_bug_4 ;;
        5) introduce_bug_5 ;;
        6) introduce_bug_6 ;;
        7) introduce_bug_7 ;;
        8) introduce_bug_8 ;;
        9) introduce_bug_9 ;;
        10) introduce_bug_10 ;;
        11) revert_all ;;
        12) show_status ;;
        0) echo "Exiting..."; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done
