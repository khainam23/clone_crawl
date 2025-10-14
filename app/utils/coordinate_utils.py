import re, gc, psutil, time, atexit
from typing import Optional, Tuple
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException


# ==================== ZOMBIE PROCESS KILLER ====================
def _kill_all_chrome_zombies() -> int:
    """
    Kill tất cả Chrome zombie processes (headless only).
    Trả về số lượng processes đã kill.
    """
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name']
                if not name:
                    continue
                    
                name_lower = name.lower()
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline).lower() if cmdline else ''
                
                # Chỉ kill Chrome headless, KHÔNG kill Chrome browser thường của user
                is_chrome = 'chrome' in name_lower or 'chromedriver' in name_lower
                is_headless = '--headless' in cmdline_str or '--test-type' in cmdline_str
                
                if is_chrome and is_headless:
                    proc.kill()
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"⚠️ Error scanning processes: {e}")
    
    return killed_count


def _cleanup_driver(driver) -> None:
    """
    Đóng Chrome driver và đảm bảo process được kill hoàn toàn.
    """
    if not driver:
        return
    
    # Lưu PID trước khi quit
    pid = None
    try:
        if driver.service and driver.service.process:
            pid = driver.service.process.pid
    except Exception:
        pass
    
    # Bước 1: Graceful quit
    try:
        driver.quit()
        time.sleep(0.1)  # Đợi driver.quit() hoàn tất
    except Exception:
        pass
    
    # Bước 2: Force kill process tree nếu còn sống
    if pid:
        try:
            if psutil.pid_exists(pid):
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                # Kill children trước
                for child in children:
                    try:
                        child.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Kill parent
                try:
                    parent.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
        except Exception:
            pass
    
    # Bước 3: Scan và kill mọi Chrome zombie còn sót lại
    _kill_all_chrome_zombies()


# Đăng ký cleanup khi thoát chương trình
@atexit.register
def _cleanup_on_exit():
    """Kill tất cả Chrome processes khi chương trình thoát"""
    killed = _kill_all_chrome_zombies()
    if killed > 0:
        print(f"🧹 Cleaned up {killed} Chrome zombie processes on exit")


def fetch_coordinates_from_google_maps(address: str) -> Optional[Tuple[float, float]]:
    driver = None
    
    try:
        # Kiểm tra RAM khả dụng (tăng threshold lên 300MB để an toàn hơn)
        mem = psutil.virtual_memory()
        available_mb = mem.available // 1024 // 1024
        
        if mem.available < 300 * 1024 * 1024:  # Less than 300MB available
            print(f"⚠️ Low memory ({available_mb}MB), cleaning zombies...")
            killed = _kill_all_chrome_zombies()
            if killed > 0:
                print(f"🧹 Killed {killed} zombie processes")
                gc.collect()
                time.sleep(1)  # Đợi OS giải phóng RAM
                
                # Kiểm tra lại
                mem = psutil.virtual_memory()
                available_mb = mem.available // 1024 // 1024
                if mem.available < 300 * 1024 * 1024:
                    print(f"❌ Still low memory ({available_mb}MB), skipping: {address}")
                    return None
            else:
                print(f"❌ Low memory ({available_mb}MB), skipping: {address}")
                return None
        
        encoded_address = quote(address)
        url = f"https://www.google.co.jp/maps/place/{encoded_address}"

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.binary_location = "/usr/local/bin/chrome/chrome"
        
        # Aggressive memory optimization for low-RAM systems
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument("--disable-javascript")  # Maps URL doesn't need JS
        chrome_options.add_argument("--disable-features=VizDisplayCompositor,AudioServiceOutOfProcess")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-web-resources")
        
        # Memory limits
        chrome_options.add_argument("--max-old-space-size=128")  # Limit V8 heap
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--window-size=800,600")

        service = Service("/usr/bin/chromedriver")
        service.log_path = "/dev/null"  # Disable logging
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(10)  # Reduced timeout
        
        driver.get(url)

        # Wait for URL to contain coordinates
        WebDriverWait(driver, 8).until(
            lambda d: re.search(r'@-?\d+\.\d+,-?\d+\.\d+', d.current_url)
        )

        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None

    except TimeoutException:
        print(f"⏱️ Timeout fetching: {address}")
        return None
        
    except WebDriverException as e:
        error_str = str(e)
        if "Chrome failed to start" in error_str or "DevToolsActivePort" in error_str:
            print(f"❌ Chrome startup failed (OOM): {address}")
            # Aggressive cleanup khi gặp OOM
            _kill_all_chrome_zombies()
            gc.collect()
            time.sleep(1)  # Đợi lâu hơn để OS recover
        else:
            print(f"❌ WebDriver error for {address}: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching coordinates for {address}: {e}")
        return None
        
    finally:
        # QUAN TRỌNG: Đóng Chrome ngay sau khi trích xuất xong
        if driver:
            _cleanup_driver(driver)
            driver = None  # Đảm bảo không còn reference
        
        # Force garbage collection
        gc.collect()
        
        # Tăng delay lên 0.5s để OS có thời gian giải phóng RAM
        time.sleep(0.5)
