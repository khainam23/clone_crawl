import logging

from app.jobs.mitsui_crawl_page.index import crawl_multi
# from app.jobs.crawl_single.index import crawl_pages
from app.jobs.index import job_registry
from app.utils.save_utils import SaveUtils
from app.jobs.mitsui_crawl_page import constants

logger = logging.getLogger(__name__)

async def crawl_mitsui():
    try:
        # Làm rỗng trước khi run
        await SaveUtils.clean_db(constants.COLLECTION_NAME)
        
        await crawl_multi()
        # await crawl_pages(["https://www.mitsui-chintai.co.jp/rf/tatemono/4281/211"])
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
    'hours': 8,
    'id': 'crawl_mitsui_job',
    'replace_existing': True
}

# Job tự đăng ký vào hệ thống
job_registry.register(crawl_mitsui_job_config)
