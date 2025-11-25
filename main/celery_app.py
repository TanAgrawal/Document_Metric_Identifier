from celery import Celery

cel = Celery(
    'doc_reader',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)
