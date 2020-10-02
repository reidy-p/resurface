from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from resurface import application

jobstore = {
    'default': SQLAlchemyJobStore(url=application.config['SQLALCHEMY_DATABASE_URI'])
}

sched = BackgroundScheduler(daemon=True, jobstores=jobstore)
sched.start()
