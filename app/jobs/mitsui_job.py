import logging

from app.jobs.mitsui_crawl_page.index import crawl_multi
from app.jobs.index import job_registry
from app.core.config import settings

logger = logging.getLogger(__name__)

async def crawl_mitsui():
    try:
        # Làm rỗng trước khi run
        # await SaveUtils.clean_db(constants.COLLECTION_NAME, auto_backup=True)
        
        await crawl_multi()
        return {"status": "success", "message": "👍 Crawl page mitsui success!"}
    except Exception as e:
        error_msg = f"Job failed: {e}"
        logger.error(error_msg)
        print(f"❌ ERROR: {error_msg}")
        return {"status": "error", "message": error_msg}

# Job config
crawl_mitsui_job_config = {
    'func': crawl_mitsui,
    'trigger': 'cron',
    'hour': settings.HOUR_MITSUI,
    'minute': settings.MINUTE_MITSUI,
    'id': 'crawl_mitsui_job',
    'replace_existing': True
}

# Job tự đăng ký vào hệ thống
job_registry.register(crawl_mitsui_job_config)
