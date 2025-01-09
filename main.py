import os
import re
from github import Github, BadCredentialsException, GithubException

# Get environment variables
repo_name = os.getenv('ORG_REPO')
pr_number = os.getenv('PR_details')
workspace_path = os.getenv('WORKSPACE')
print("in main : ",repo_name, int(pr_number), workspace_path)
github_token = os.getenv('GITHUB_TOKEN')
# Initialize GitHub client
g = Github(github_token)
repo = g.get_repo(repo_name)
prohibited_file = os.path.join(workspace_path, 'prohibited_source.txt')
# Get the prohibited names to check against each file in the PR
print("....Get the prohibited names to check against each file in the PR")
try:
    with open(prohibited_file, 'r') as f:
        prohibited_names = set(line.strip() for line in f)
        print("prohibited_names : ", prohibited_names)
except Exception as e:
    print(f"An unexpected error occurred....: {e}")

# Fetch the pull request by number
try:
    pr = repo.get_pull(int(pr_number))
except BadCredentialsException:
    print("Authentication failed. Please check your personal access token.")
except GithubException as e:
    print(f"GitHub API error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

commits = pr.get_commits()
commit_id = commits[0].sha
print(type(pr))
print(commits)
print(commits[0], commit_id)

# Check if any prohibited names are present in PR title or body
def check_for_prohibited_names(pr):
    flag = 0
    violations = []
    # Check PR title
    if any(name in pr.title for name in prohibited_names):
        return f"Prohibited name found in title: {pr.title}"
    
    for file in pr.get_files():
        print("********** file :", file.filename)
        with open(file.filename, "r") as fd:
            all_lines = fd.readlines()
            for i, line in enumerate(all_lines):
                try:
                    if line.strip() in prohibited_names or re.search("@gmail.com", line) or re.search("@yahoo.com",line):
                        flag = -1
                        print("Prohibited word found in line {0} of file {1}".format(i+1,file.filename))
                        pr.create_review_comment(body="Prohibited word found!", commit=commits[0],path=file.filename,position=i+1)
                        violations.append("Prohibited word found in line {0} of file {1}".format(i+1,file.filename))
                except GithubException as e:
                    print(f"Error on PR : {e}")
                      
    if flag!=-1:
        return "No prohibited names found in the PR."
    else:
        return violations
    
# Execute check
result = check_for_prohibited_names(pr)
print(result)
