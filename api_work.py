import requests


class Codeforces_API:
    r = requests.get("https://codeforces.com/api/problemset.problems?tags=trees")

    def get_problems(self):
        problems = self.r.json()['result']['problems']
        return problems

    def get_statistic(self):
        statistic = self.r.json()['result']['problemStatistics']
        return statistic

