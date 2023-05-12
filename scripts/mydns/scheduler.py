#!/opt/example/bin/python3
import schedule
import time
import autoupdate

def job():
    autoupdate.main()

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)