import requests

r = requests.get("https://codeforces.com/api/problemset.problems?tags=trees")

problems = r.json()['result']['problems']
statistic = r.json()['result']['problemStatistics']

for p in problems:
    print(p)

for s in statistic:
    print(s)