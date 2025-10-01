"""
APScheduler setup
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from app.core.config import settings
import logging
# Import jobs package to ensure all jobs are registered
import app.jobs
from app.jobs.index import job_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler configuration
jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# Create scheduler instance
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=settings.scheduler_timezone
)

def start_scheduler():
    """Start the scheduler"""
    try:        
        job_registry.add_jobs(scheduler)
        
        scheduler.start()
        logger.info("Scheduler started successfully")
        logger.info(f"Registered {len(job_registry.jobs)} jobs")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

def stop_scheduler():
    """Stop the scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")

def get_scheduler():
    """Get scheduler instance"""
    return scheduler