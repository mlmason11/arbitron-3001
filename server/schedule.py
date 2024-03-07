from crontab import CronTab

cron = CronTab(user='maxmason')
job = cron.new(command='python3 seed.py')
job.minute.on(0, 15, 30, 45)
cron.write()