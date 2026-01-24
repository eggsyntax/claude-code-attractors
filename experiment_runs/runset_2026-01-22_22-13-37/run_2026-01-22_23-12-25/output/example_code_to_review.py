# Example code with various issues for the intelligent code reviewer

def process_user_data(d):
    """Process some user data"""
    f = open("users.txt", "r")
    users = []

    try:
        for line in f:
            user_info = eval(line.strip())
            if user_info:
                if user_info.get("age"):
                    if user_info["age"] > 18:
                        if user_info.get("status") == "active":
                            if len(user_info.get("name", "")) > 0:
                                users.append({
                                    "id": user_info["id"],
                                    "name": user_info["name"],
                                    "age": user_info["age"],
                                    "timeout": 3600  # magic number
                                })
    except:
        pass

    return users


def calculate_score(data):
    """Calculate some kind of score"""
    total = 0
    for i in range(len(data)):
        total += data[i] * 2.5  # another magic number
    return total