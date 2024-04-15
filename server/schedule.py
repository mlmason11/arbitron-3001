from crontab import CronTab

cron = CronTab()
job = cron.new(command='python3 /Users/maxmason/Development/code/phase-5/arbitron-3001/server/seed.py')
job.minute.on(0, 15, 30, 45)
cron.write()