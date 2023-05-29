#!/opt/example/bin/python3
import schedule
import time
import backup

def job():
    backup.main()

schedule.every().day.at('01:00').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)