def process_user_data(data):
    """A function with various code quality issues for demonstration."""
    f = open("results.txt", "w")  # Should use context manager
    results = []

    try:
        for i in range(len(data)):  # Could use enumerate
            x = data[i]  # Single letter variable
            if x > 0:
                if x < 1000:
                    if x % 2 == 0:
                        if x not in results:
                            # Magic number and eval usage
                            processed = eval(f"{x} * 3.14159")  # Security issue
                            f.write(str(processed))
                            results.append(x)
    except:  # Bare except clause
        print("Something went wrong")

    max_items = 50  # Magic number
    return results[:max_items]

def build_list_manually(items):
    """Example of a loop that could be a list comprehension."""
    result = []
    for item in items:
        if item.startswith('test'):
            result.append(item.upper())
    return result