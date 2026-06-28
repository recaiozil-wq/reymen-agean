---
skill_id: 62880d777aa6
usage_count: 1
last_used: 2026-06-16
---
# Function scope (default) - runs for each test
@pytest.fixture
def temp_file():
    with open("temp.txt", "w") as f:
        yield f
    os.remove("temp.txt")