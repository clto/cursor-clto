import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

menu_items = {
    0: "Exit Program",
    1: "Reset Machine ID",
    2: "Register New Cursor Account (Outdated)",
    3: "Register with Google Account (LIFETIME ACCESS ENABLED)",
    4: "Register with GitHub Account (LIFETIME ACCESS ENABLED)",
    5: "Register Cursor with Custom Email",
    6: "Temporary GitHub Register",
    7: "Close Cursor Application",
    8: "Change Language",
    9: "Disable Auto-Update",
    10: "Totally Reset Cursor",
    11: "Contribute to the Project",
    12: "Show Config",
    13: "Select Chrome Profile",
    14: "Delete Cursor Google Account",
    15: "Bypass Version Check",
    16: "Check User Authorized",
    17: "Bypass Token Limit"
}

print("\n" + "="*80)
print("Available Options:")
print("="*80)
for num, desc in sorted(menu_items.items()):
    print(f"  {num:2d}. {desc}")
print("="*80)
print("\nEnter your choice (0-17)")
