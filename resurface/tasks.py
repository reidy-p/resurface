from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(daemon=True)
sched.start()
