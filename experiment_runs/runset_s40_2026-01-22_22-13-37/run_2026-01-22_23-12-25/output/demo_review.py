#!/usr/bin/env python3
"""
Demo of the Contextual Code Review Assistant

This shows the kind of feedback our intelligent code review tool would provide
on various code patterns, demonstrating context awareness and constructive guidance.
"""

# Import the review assistant (would be the completed version)
# from smart_review_assistant import SmartReviewAssistant, format_review_report

def demo_review_scenarios():
    """Demonstrate different review scenarios with expected feedback"""

    # Test case 1: Generic function name in complex context
    problematic_code_1 = '''
def process(user_data, validation_rules, output_format, logging_config, retry_settings):
    """Process user data according to validation rules."""
    try:
        if validation_rules.strict_mode:
            if user_data.requires_verification:
                if output_format.include_metadata:
                    if logging_config.verbose:
                        if retry_settings.max_attempts > 3:
                            print(f"Processing {user_data}")
                            result = validate_and_transform(user_data, validation_rules)
                            if result.success:
                                return format_output(result, output_format)
                        else:
                            return None
    except:
        pass
    return True
    '''

    # Test case 2: Boolean function with poor naming
    problematic_code_2 = '''
def validate_user_input(data):
    if data.age > 18 and data.email and '@' in data.email:
        return True
    return False
    '''

    # Test case 3: Mutable default argument bug
    problematic_code_3 = '''
def create_user_profile(name, permissions=[]):
    permissions.append('read')  # Bug: modifies shared default
    return {'name': name, 'permissions': permissions}
    '''

    # Test case 4: Performance anti-pattern
    problematic_code_4 = '''
def find_matching_users(users, target_criteria):
    matches = []
    for user in users:                    # Outer loop
        for criterion in target_criteria: # Nested loop
            if user.matches(criterion):   # Potential N*M complexity
                database.log_match(user, criterion)  # DB call in loop
                matches.append(user)
                break
    return matches
    '''

    print("🔍 Contextual Code Review Demo\n")
    print("This demo shows the kind of intelligent feedback our review assistant provides:\n")

    # Simulate what our tool would output for each scenario
    scenarios = [
        {
            "title": "Generic Function Names",
            "code": problematic_code_1,
            "feedback": [
                "⚠️  SUGGESTION - Line 1: Function name 'process' is quite generic",
                "    💭 Consider a name like 'validate_and_process_user_data' that describes the specific operation",
                "    📝 Generic function names make code harder to understand and navigate",
                "",
                "💡 SUGGESTION - Line 5: Deep nesting detected in 'process' (depth: 5)",
                "    💭 Consider extracting nested logic into separate functions or using early returns",
                "    📝 Deep nesting increases cognitive load and makes code harder to follow",
                "",
                "⚠️  WARNING - Line 12: Bare 'except:' clause catches all exceptions",
                "    💭 Specify the exception type(s) you want to catch",
                "    📝 Bare except clauses can hide programming errors and make debugging difficult"
            ]
        },
        {
            "title": "Boolean Function Naming",
            "code": problematic_code_2,
            "feedback": [
                "ℹ️  INFO - Line 1: Function 'validate_user_input' returns boolean but doesn't follow convention",
                "    💭 Consider renaming to 'is_user_input_valid' or 'has_valid_user_input'",
                "    📝 Boolean-returning functions are clearer when named as questions"
            ]
        },
        {
            "title": "Mutable Default Arguments",
            "code": problematic_code_3,
            "feedback": [
                "⚠️  WARNING - Line 1: Function 'create_user_profile' uses mutable default argument",
                "    💭 Use None as default and create the list inside the function",
                "    📝 Mutable defaults are shared between calls, causing unexpected behavior",
                "",
                "    Example fix:",
                "    def create_user_profile(name, permissions=None):",
                "        if permissions is None:",
                "            permissions = []"
            ]
        },
        {
            "title": "Performance Concerns",
            "code": problematic_code_4,
            "feedback": [
                "💡 SUGGESTION - Line 3: Nested loops detected - consider optimizing algorithm complexity",
                "    💭 Could this be solved with a hash map or set lookup instead?",
                "    📝 O(N*M) complexity can become problematic with larger datasets",
                "",
                "⚠️  WARNING - Line 6: Database operations in loop - consider batch operations",
                "    💭 Collect matches first, then log them in a single batch operation",
                "    📝 Database calls in loops can significantly impact performance"
            ]
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"## Scenario {i}: {scenario['title']}")
        print("```python")
        print(scenario['code'].strip())
        print("```")
        print("\n**Review Feedback:**")
        for line in scenario['feedback']:
            print(line)
        print("\n" + "="*60 + "\n")

def demo_context_awareness():
    """Show how the tool understands when to apply rules contextually"""

    print("🧠 Context Awareness Demo\n")
    print("Our tool understands when common 'rules' should be relaxed:\n")

    examples = [
        {
            "title": "Appropriate Generic Names in Iterator Context",
            "code": '''
# This would NOT be flagged as problematic:
for i, item in enumerate(data_points):
    process_item(item, i)
            ''',
            "explanation": "Single-letter variables like 'i' are acceptable in iteration contexts"
        },
        {
            "title": "Intentional Complexity in Performance-Critical Code",
            "code": '''
def fast_matrix_multiply(a, b):
    """Optimized matrix multiplication - complexity is intentional."""
    # Complex nested loops here would be flagged as "acceptable"
    # when performance is explicitly mentioned in docstring
            ''',
            "explanation": "High complexity is acceptable when explicitly justified for performance"
        },
        {
            "title": "Bare Except in Cleanup Code",
            "code": '''
def cleanup_resources():
    try:
        resource.cleanup()
    except:  # This might be flagged as INFO rather than WARNING
        pass  # Cleanup should never fail the main operation
            ''',
            "explanation": "Bare except might be downgraded when used in cleanup scenarios"
        }
    ]

    for example in examples:
        print(f"### {example['title']}")
        print("```python")
        print(example['code'].strip())
        print("```")
        print(f"**Context Understanding**: {example['explanation']}\n")

if __name__ == "__main__":
    demo_review_scenarios()
    demo_context_awareness()

    print("🎯 Key Benefits of This Approach:")
    print("- Reduces false positives by understanding context")
    print("- Provides actionable suggestions with explanations")
    print("- Learns from team patterns and preferences")
    print("- Focuses on high-impact issues that humans care about")
    print("- Explains the 'why' behind each recommendation")