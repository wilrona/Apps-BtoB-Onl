
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger


class Config(object):
    JOBS = [
        # {
        #     'id': 'job1',
        #     'func': 'application.modules.utilities.views:job1',
        #     'args': (1, 2),
        #     'trigger': IntervalTrigger(seconds=10)
        # }
    ]

    SCHEDULER_API_ENABLED = True


def job1(a, b):
    print(str(a) + ' ' + str(b))
