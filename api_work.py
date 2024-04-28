import requests


class CodeforcesAPI:
    r = requests.get("https://codeforces.com/api/problemset.problems?lang=ru")

    def get_problems(self):
        problems = self.r.json()['result']['problems']
        return problems

    def get_statistic(self):
        statistic = self.r.json()['result']['problemStatistics']
        return statistic
