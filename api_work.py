import requests


class CodeforcesAPI:
    """Класс для работы с API"""
    r = requests.get("https://codeforces.com/api/problemset.problems?lang=ru")

    def get_problems(self):
        """Функция для получения списка проблем"""
        problems = self.r.json()['result']['problems']
        return problems

    def get_statistic(self):
        """Функция для получения статистики"""
        statistic = self.r.json()['result']['problemStatistics']
        return statistic
