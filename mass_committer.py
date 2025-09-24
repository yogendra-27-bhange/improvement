import os
import subprocess

FILENAME = "dummy_commits.txt"
NUM_COMMITS = 100

# Ensure the file exists
def ensure_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w") as f:
            f.write("Initial commit\n")

def make_commits():
    for i in range(1, NUM_COMMITS + 1):
        with open(FILENAME, "a") as f:
            f.write(f"Commit number {i}\n")
        subprocess.run(["git", "add", FILENAME], check=True)
        subprocess.run(["git", "commit", "-m", f"Commit #{i}"], check=True)
        print(f"Committed: Commit #{i}")

if __name__ == "__main__":
    ensure_file()
    make_commits() 