import requests
import mplcursors
import matplotlib.pyplot as plt
import csv

# set API endpoint and parameters
api_endpoint = "https://api.github.com/repos/{owner}/{repo}/stats/contributors"
owner = "calcom"
repo = "cal.com"
params = {"per_page": 100}
username = "uvudatha"
api_token = "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"
auth = (username, api_token)
# make GET request to the API
response = requests.get(api_endpoint.format(owner=owner, repo=repo), params=params,auth=auth)
total_commits = {}
total_additions = {}
total_deletions = {}
total_review_comments={}

print(response.status_code)
# check for successful response
if response.status_code == 200:
    stats = response.json()
    # calculate total commits and additions/deletions for each contributor
    total_commits = {}
    total_additions = {}
    total_deletions = {}

    for contributor in stats:
        author = contributor["author"]["login"]
        total_commits[author] = sum(week["c"] for week in contributor["weeks"])
        total_additions[author] = sum(week["a"] for week in contributor["weeks"])
        total_deletions[author] = sum(week["d"] for week in contributor["weeks"])

    review_comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"
    review_comments_ = requests.get(review_comments_url, auth=auth)
    if review_comments_.status_code==200:
        review_comments_response = review_comments_.json()
        for comment in review_comments_response:
            comment_author = comment["user"]["login"]
            if comment_author in total_review_comments:
                total_review_comments[comment_author]+=1
            else:
                total_review_comments[comment_author]=1
    # print stats
    print(f"Total commits: {sum(total_commits.values())}")
    print(f"Total additions: {sum(total_additions.values())}")
    print(f"Total deletions: {sum(total_deletions.values())}")
    print(f"Total review comments: {sum(total_review_comments.values())}")
    print("Contributor stats:")

###PULL REQUESTS##
api_endpoint_pull = f"https://api.github.com/repos/{owner}/{repo}/pulls"
params = {"state": "all", "per_page": 100}

# make GET request to the API
pull_response = requests.get(api_endpoint_pull, params=params,auth=auth)
pull_requests = {}

# check for successful response
if pull_response.status_code == 200:
    data = pull_response.json()
    for item in data:
        author = item["user"]["login"]
        if author in pull_requests:
            pull_requests[author] += 1
        else:
            pull_requests[author] = 1    
    for contributor in sorted(total_commits, key=total_commits.get, reverse=True):
        print(f"{contributor}: {total_commits[contributor]} commits, {total_additions[contributor]} additions, {total_deletions[contributor]} deletions", end=" ")
        if contributor in pull_requests:
            print(f"{pull_requests[contributor]} pulls",end=" ")
        else:
            print("0 pulls",end=" ")
        if contributor in total_review_comments:
            print(f"{total_review_comments[contributor]} issues")
        else:
            print("0 issues")
else:
    print("Error: Could not retrieve contributor stats from GitHub API")

####ISSUES###

issues_api_endpoint = "https://api.github.com/repos/{owner}/{repo}/issues"

params = {"state": "all", "per_page": 100}
issue_stats={}
# make GET request to the API
issues_response = requests.get(issues_api_endpoint.format(owner=owner, repo=repo), params=params,auth=auth)

# check for successful response
if issues_response.status_code == 200:
    # get the API response in JSON format
    issues = issues_response.json()

    # dictionary to hold issue stats for each contributor
    issue_stats = {}

    # iterate through each issue
    for issue in issues:
        # get the username of the issue creator
        creator = issue["user"]["login"]
        # check if the creator is already in the dictionary
        if creator not in issue_stats:
            issue_stats[creator] = {"created": 0, "closed": 0}
        # increment the "created" count for the creator
        issue_stats[creator]["created"] += 1
        # check if the issue is closed
        if issue["state"] == "closed":
            # increment the "closed" count for the creator
            issue_stats[creator]["closed"] += 1

    # print the issue stats for each contributor
    for contributor, stats in issue_stats.items():
        print(f"{contributor}: {stats['created']} issues created, {stats['closed']} issues closed")
else:
    print(f"Error: {issues_response.status_code}")

# set the API endpoint and owner/repo values
# comments_api_endpoint = "https://api.github.com/repos/{owner}/{repo}/pulls/comments"

# # set the parameters for the API request
# params = {
#     "state": "all",
#     "per_page": 100
# }

### REVIEW COMMENTS ###

# send the API request and store the response
# comments_response = requests.get(comments_api_endpoint.format(owner=owner, repo=repo), params=params,auth=auth)

# create empty dictionaries to store the review comment stats
# total_review_comments = {}
# review_comments_by_user = {}

# # check for a successful response
# if response.status_code == 200:
#     review_comments = comments_response.json()

#     # calculate the total number of review comments and review comments by user
#     for review_comment in review_comments:
#         author = review_comment["user"]["login"]
#         if author not in total_review_comments:
#             total_review_comments[author] = 0
#             review_comments_by_user[author] = {}

#         total_review_comments[author] += 1

#         if review_comment["pull_request_url"] not in review_comments_by_user[author]:
#             review_comments_by_user[author][review_comment["pull_request_url"]] = 0

#         review_comments_by_user[author][review_comment["pull_request_url"]] += 1

#     # print the review comment stats for each contributor
#     for contributor in sorted(total_review_comments, key=total_review_comments.get, reverse=True):
#         print(f"{contributor}: {total_review_comments[contributor]} review comments")
#         for pull_request_url in review_comments_by_user[contributor]:
#             print(f"\tPull Request {pull_request_url}: {review_comments_by_user[contributor][pull_request_url]} review comments")
# else:
#     print(f"Error: {comments_response.status_code}")


output_file = 'output.csv'

# open the file for writing
with open(output_file, mode='w', newline='') as csvfile:
    # create a CSV writer object
    writer = csv.writer(csvfile)
    writer.writerow(['Username', 'Additions', 'Deletions', 'Commits','Pull Requests','Issues Created','Issues Closed','Review Comments'])

    # write the header row
    for contributor in sorted(total_commits, key=total_commits.get, reverse=True):
        row=[contributor, total_additions[contributor], total_deletions[contributor], total_commits[contributor], 0,0,0,0]
        if contributor in pull_requests:
            row[4]=pull_requests[contributor]
        if contributor in issue_stats.keys():
            row[5]=issue_stats[contributor]['created']
            row[6]=issue_stats[contributor]['closed']
        if contributor in total_review_comments:
            row[7]=total_review_comments[contributor]
        writer.writerow(row)


# # Sample data for users and their contributio
# # Create a scatter plot with deletions on the x-axis and additions on the y-axis
# fig, ax = plt.subplots()
# ax.scatter(deletions,additions, s=commits, alpha=0.5)

# cursor = mplcursors.cursor(ax)
# @cursor.connect("add")
# def on_add(sel):
#     user_index = sel.target.index
#     user = users[user_index]
#     deletion = deletions[user_index]
#     addition = additions[user_index]
#     sel.annotation.set_text(f'{user}\nDeletions: {deletion}\nAdditions: {addition}')

# # Set axis labels and title
# ax.set_xlabel('Additions')
# ax.set_ylabel('Deletions')
# ax.set_title('Contributions by User')

# plt.show()

