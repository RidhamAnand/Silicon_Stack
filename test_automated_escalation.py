"""
Script to test escalation flow automatically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simulate user inputs for testing
test_inputs = [
    "I received defective item",  # Initial complaint
    "john.doe@test.com",          # Provide email
    "no order",                   # Skip order
    "quit"                        # Exit
]

input_index = 0

# Monkey patch input() to use our test inputs
original_input = input
def mock_input(prompt=""):
    global input_index
    if input_index < len(test_inputs):
        user_input = test_inputs[input_index]
        input_index += 1
        print(f"{prompt}{user_input}")
        return user_input
    return "quit"

__builtins__.input = mock_input

# Now run main
from src.main import CustomerSupportCLI

cli = CustomerSupportCLI()
cli.print_header()

for test_input in test_inputs[:-1]:  # Exclude 'quit'
    cli.process_query(test_input)

print("\n" + "="*80)
print("AUTOMATED TEST COMPLETE")
print("="*80)
