import re, gc, psutil, time, signal
from typing import Optional, Tuple
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException


def _kill_process_tree(pid: int) -> None:
    """Forcefully kill a process and all its children"""
    try:
        if not psutil.pid_exists(pid):
            return
        
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        # Kill children first
        for child in children:
            try:
                child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Kill parent
        try:
            parent.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Wait for processes to die
        gone, alive = psutil.wait_procs(children + [parent], timeout=3)
        
        # Force kill any survivors
        for p in alive:
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
    except Exception as e:
        print(f"⚠️ Error killing process tree {pid}: {e}")


def _cleanup_driver(driver) -> None:
    """Aggressively cleanup Chrome driver and processes"""
    if not driver:
        return
    
    pid = None
    try:
        if driver.service and driver.service.process:
            pid = driver.service.process.pid
    except Exception:
        pass
    
    # Try graceful quit first
    try:
        driver.quit()
    except Exception:
        pass
    
    # Force kill process tree
    if pid:
        _kill_process_tree(pid)
    
    # Cleanup any orphaned chrome/chromedriver processes
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                if ('chrome' in name or 'chromedriver' in name) and \
                   ('--headless' in cmdline or '--test-type' in cmdline):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass


def fetch_coordinates_from_google_maps(address: str) -> Optional[Tuple[float, float]]:
    """
    Fetch coordinates from Google Maps with aggressive resource management.
    Optimized for low-memory environments (<4GB RAM).
    """
    driver = None
    
    try:
        # Check available memory before starting
        mem = psutil.virtual_memory()
        if mem.available < 200 * 1024 * 1024:  # Less than 200MB available
            print(f"⚠️ Low memory ({mem.available // 1024 // 1024}MB), skipping: {address}")
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
        
        # Single process mode (risky but saves RAM)
        # chrome_options.add_argument("--single-process")
        
        # Window size minimal
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
        if "Chrome failed to start" in str(e) or "DevToolsActivePort" in str(e):
            print(f"❌ Chrome startup failed (likely OOM): {address}")
        else:
            print(f"❌ WebDriver error for {address}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching coordinates for {address}: {e}")
        return None
    finally:
        _cleanup_driver(driver)
        gc.collect()
        time.sleep(0.2)  # Give system time to cleanup
