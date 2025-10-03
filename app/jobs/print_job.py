"""
Simple print job for testing scheduler
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def hello_world_job():
    """Simple job that prints Hello World to the console"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello World! Current time: {current_time}"
        
        print(message)  # In ra console
        logger.info(message)  # Ghi vào log
        
        return {"status": "success", "message": message}
    except Exception as e:
        error_msg = f"Hello World job failed: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

# Import registry và tự đăng ký job
from app.jobs.index import job_registry

# Job config
hello_world_job_config = {
    'func': hello_world_job,
    'trigger': 'interval',
    'seconds': 10,
    'id': 'hello_world_job',
    'replace_existing': True
}

# Job tự đăng ký vào hệ thống
# job_registry.register(hello_world_job_config)
