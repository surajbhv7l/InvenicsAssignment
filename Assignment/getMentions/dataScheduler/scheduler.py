import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


from getMentions.views import getSaveBlobData

start_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

def update():
    print(start_time)
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(getSaveBlobData, trigger=CronTrigger(hour=5, minute=47),replace_existing=True)
    
    
    scheduler.start()
     
