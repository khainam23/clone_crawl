import logging

from app.jobs.tokyu_crawl_page.index import crawl_multi
from app.jobs.index import job_registry
from app.core.config import settings

logger = logging.getLogger(__name__)

async def crawl_tokyu():
    try:
        # Làm rỗng trước khi run
        # await SaveUtils.clean_db(constants.COLLECTION_NAME, auto_backup=True)
        
        await crawl_multi()
        return {"status": "success", "message": "👍 Crawl page tokyu success!"}
    except Exception as e:
        error_msg = f"Job failed: {e}"
        logger.error(error_msg)
        print(f"❌ ERROR: {error_msg}")
        return {"status": "error", "message": error_msg}

# Job config
crawl_tokyu_job_config = {
    'func': crawl_tokyu,
    'trigger': 'cron',
    'hour': settings.HOUR_TOKYO,
    'minute': settings.MINUTE_TOKYO,
    'id': 'crawl_tokyu_job',
    'replace_existing': True
}

# Job tự đăng ký vào hệ thống
job_registry.register(crawl_tokyu_job_config)
