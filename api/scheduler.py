from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def sample_job():
    print("Scheduler is working!")

def start_scheduler():
    scheduler.add_job(sample_job, 'interval', seconds=30, id='test_job')
    scheduler.start()
    print("✓ Scheduler started")

def shutdown_scheduler():
    scheduler.shutdown()
    print("✓ Scheduler stopped")
