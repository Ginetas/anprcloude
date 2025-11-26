#!/usr/bin/env python3
"""
Update TODO file with status information for all tasks
"""

import re

# Define all tasks with their statuses
tasks_info = {
    1: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-5 dienos", "dependencies": "Nėra"},
    2: {"status": "✅", "progress": "100%", "priority": "✅ BAIGTA", "estimation": "-", "dependencies": "Nėra"},
    3: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    4: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2 dienos", "dependencies": "Task #1"},
    5: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #1, #30"},
    6: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Task #1, #35"},
    7: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "3-4 dienos", "dependencies": "Task #1"},
    8: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    9: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Task #1"},
    10: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    11: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "1-2 dienos", "dependencies": "Task #1"},
    12: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    13: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Task #1, #34"},
    14: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    15: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    16: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2 dienos", "dependencies": "Task #1"},
    17: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "1-2 dienos", "dependencies": "Task #1"},
    18: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-5 dienos", "dependencies": "Task #2, #19, #30"},
    19: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Task #2"},
    20: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    21: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1, #22"},
    22: {"status": "🔄", "progress": "50%", "priority": "🟡 AUKŠTAS", "estimation": "1-2 dienos", "dependencies": "Task #2"},
    23: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "2 dienos", "dependencies": "Task #1, #22"},
    24: {"status": "🔄", "progress": "30%", "priority": "🟡 AUKŠTAS", "estimation": "2 dienos", "dependencies": "Task #2"},
    25: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    26: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1, #3"},
    27: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "1-2 dienos", "dependencies": "Task #1"},
    28: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1, #3"},
    29: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    30: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Nėra"},
    31: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    32: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2 dienos", "dependencies": "Task #1, #9"},
    33: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #2"},
    34: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "2 dienos", "dependencies": "Task #1, #13"},
    35: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Nėra"},
    36: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-4 dienos", "dependencies": "Task #30, #34, #35"},
    37: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "3-4 dienos", "dependencies": "Task #1"},
    38: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "2-3 dienos", "dependencies": "Task #19"},
    39: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "1-2 dienos", "dependencies": "Task #1, #19"},
    40: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "3-4 dienos", "dependencies": "Task #1, #4-#9"},
    41: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "1 diena", "dependencies": "Task #1"},
    42: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    43: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "2 dienos", "dependencies": "Task #2"},
    44: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "1 diena", "dependencies": "Task #1"},
    45: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2 dienos", "dependencies": "Task #1, #21"},
    46: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #2"},
    47: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    48: {"status": "🔄", "progress": "50%", "priority": "🟡 AUKŠTAS", "estimation": "1-2 dienos", "dependencies": "Task #2, #24"},
    49: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "3-4 dienos", "dependencies": "Task #1, #8"},
    50: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    51: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    52: {"status": "❌", "progress": "0%", "priority": "🟡 AUKŠTAS", "estimation": "3-4 dienos", "dependencies": "Task #2"},
    53: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "1 diena", "dependencies": "Task #1"},
    54: {"status": "❌", "progress": "0%", "priority": "🟢 ŽEMAS", "estimation": "1-2 dienos", "dependencies": "Task #22"},
    55: {"status": "❌", "progress": "0%", "priority": "🟡 VIDUTINIS", "estimation": "2-3 dienos", "dependencies": "Task #1"},
    56: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-5 dienos", "dependencies": "Task #2, visi backend"},
    57: {"status": "❌", "progress": "0%", "priority": "🔴 KRITINIS", "estimation": "3-5 dienos", "dependencies": "Task #1, visi frontend"},
}

# Read the file
with open('/home/user/anprcloude/docs/TODO_SMART_SETTINGS_DASHBOARD.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update each task (skip 1, 2, 3, 4, 5, 6, 7, 8 as already updated)
for task_num in range(9, 58):
    info = tasks_info.get(task_num, {})
    if not info:
        continue

    # Pattern to match task header
    pattern = rf'(#### [☐✅❌🔄] {task_num}\. [^\n]+)\n(\*\*Komponentas:\*\*|\*\*Backend:\*\*|\*\*Test:\*\*)'

    # Replacement with status info
    replacement = rf'\1\n**Statusas:** {info["progress"]} | **Prioritetas:** {info["priority"]} | **Estimacija:** {info["estimation"]}\n**Priklausomybės:** {info["dependencies"]}\n\2'

    # Replace
    content = re.sub(pattern, replacement, content)

    # Also update the checkbox symbol
    content = re.sub(rf'#### [☐✅❌🔄] {task_num}\.', rf'#### {info["status"]} {task_num}.', content)

# Write back
with open('/home/user/anprcloude/docs/TODO_SMART_SETTINGS_DASHBOARD.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ TODO file updated successfully!")
print(f"Updated {len(tasks_info)} tasks with status information.")
