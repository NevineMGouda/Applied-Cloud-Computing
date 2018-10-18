import pronouns
from celery import Celery

app = Celery('pronounstasks', broker='pyamqp://guest@localhost//', backend='rpc://')


@app.task
def add(x,y):
    return x+y


def count_swedish_pronouns():
    return str(pronouns.count_pronouns())
