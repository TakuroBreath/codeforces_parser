from api_work import CodeforcesAPI

cf = CodeforcesAPI()


def test_get_problems():
    assert cf.get_problems() != []
    assert len(cf.get_problems()) > 1000


def test_get_statistic():
    assert cf.get_statistic != []
