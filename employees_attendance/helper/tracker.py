# import os
# import time
# import random
# import json
# import requests
# import pyautogui
# import tempfile
# import sys
# import platform
# import socket
# import subprocess
# from datetime import datetime, timezone, timedelta
# from PIL import Image
# import threading

# # ---------------- CONFIG ----------------
# # Get API URL from command line or use default
# API_URL = sys.argv[3] if len(sys.argv) > 3 else None

# THRESHOLD_SECONDS = 10 * 60  # max delay between screenshots
# MAX_GAP_SECONDS = 15 * 60    # treat any gap longer than this as idle
# RETRY_LIMIT = 3
# RETRY_BACKOFF = 10
# OFFLINE_QUEUE_DIR = os.path.join(os.path.expanduser('~'), '.universal_hrms', 'offline_screenshots')
# os.makedirs(OFFLINE_QUEUE_DIR, exist_ok=True)
# # ----------------------------------------

# ATTENDANCE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else None
# CHECK_IN_ISO = sys.argv[2] if len(sys.argv) > 2 else None

# if not ATTENDANCE_ID:
#     print("❌ Attendance ID required")
#     sys.exit(1)

# if CHECK_IN_ISO:
#     print(f"🕒 Using provided check-in time: {CHECK_IN_ISO}")

# print(f"🌐 API Endpoint: {API_URL}")

# LAST_SCREENSHOT_TS = None
# SYSTEM = platform.system().lower()
# TRACKER_STARTED = False

# def get_local_ip():
#     """Get local IP address"""
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         ip = s.getsockname()[0]
#         s.close()
#         return ip
#     except:
#         return "unknown"

# def get_machine_info():
#     """Get machine information for heartbeats"""
#     return {
#         'hostname': platform.node(),
#         'platform': platform.platform(),
#         'ip_address': get_local_ip(),
#         'python_version': platform.python_version(),
#         'system': platform.system(),
#         'processor': platform.processor()
#     }

# def send_heartbeat():
#     global TRACKER_STARTED
#     while True:
#         try:
#             if ATTENDANCE_ID:
#                 ts = datetime.now(timezone.utc).isoformat()
                
#                 data = {
#                     'attendance_id': str(ATTENDANCE_ID),
#                     'timestamp': ts,
#                     'is_heartbeat': 'true',
#                     'tracker_status': 'STARTED' if TRACKER_STARTED else 'STOPPED',
#                     'machine_info': json.dumps(get_machine_info())
#                 }
                
#                 resp = requests.post(API_URL, data=data, timeout=10)
#                 if resp.status_code == 200:
#                     print(f"❤️ Heartbeat sent at {ts} | Status: {'STARTED' if TRACKER_STARTED else 'STOPPED'}")
#                 else:
#                     print(f"⚠️ Heartbeat failed: {resp.status_code} - {resp.text}")
#         except Exception as e:
#             print(f"❌ Heartbeat failed: {e}")

#         time.sleep(30)  # every 30 seconds

# # ---------- Platform Detection ----------
# def is_windows():
#     return SYSTEM == 'windows'

# def is_macos():
#     return SYSTEM == 'darwin'

# def is_linux():
#     return SYSTEM == 'linux'

# # ---------- Time Synchronization Check ----------
# def check_time_sync():
#     """Check if system time is synchronized and show current time"""
#     current_time = datetime.now()
#     current_utc = datetime.now(timezone.utc)
    
#     print(f"🕐 Local System Time: {current_time}")
#     print(f"🌐 UTC Time: {current_utc}")
    
#     if CHECK_IN_ISO:
#         try:
#             # Parse check-in time (handle both with and without timezone)
#             if 'T' in CHECK_IN_ISO:
#                 if CHECK_IN_ISO.endswith('Z') or '+' in CHECK_IN_ISO:
#                     # Has timezone info
#                     check_in_dt = datetime.fromisoformat(CHECK_IN_ISO.replace('Z', '+00:00'))
#                 else:
#                     # No timezone, assume local time
#                     check_in_dt = datetime.fromisoformat(CHECK_IN_ISO)
#             else:
#                 # Just time, assume today
#                 today = datetime.now().date()
#                 check_in_dt = datetime.combine(today, datetime.strptime(CHECK_IN_ISO, '%H:%M:%S').time())
            
#             print(f"📅 Check-in Time: {check_in_dt}")
            
#             # Calculate time difference
#             time_diff = (current_time - check_in_dt).total_seconds() / 60  # in minutes
            
#             if time_diff < -5:  # Check-in time is more than 5 minutes in the future
#                 print(f"⚠️ WARNING: Check-in time appears to be {abs(time_diff):.1f} minutes in the future!")
#                 print("💡 This will cause productive time calculation issues.")
#                 return False
#             elif time_diff > 1440:  # More than 24 hours ago
#                 print(f"⚠️ WARNING: Check-in time was {time_diff/60:.1f} hours ago")
#             else:
#                 print(f"✅ Time sync OK - Check-in was {time_diff:.1f} minutes ago")
#                 return True
                
#         except Exception as e:
#             print(f"⚠️ Time sync check error: {e}")
    
#     return True

# # ---------- Simple Linux Idle Detection ----------
# def get_idle_seconds_linux_simple():
#     """Simple but reliable Linux idle detection"""
#     try:
#         # Method 1: Check if we can interact with X server
#         try:
#             # Try to get mouse position - if this works, X server is responsive
#             result = subprocess.run(
#                 ['xdotool', 'getmouselocation'], 
#                 capture_output=True, text=True, timeout=2
#             )
#             if result.returncode == 0:
#                 # If we can get mouse position, assume not idle
#                 return 0.0
#         except:
#             pass
        
#         # Method 2: Check for recent user activity files
#         try:
#             # Check last access time of various user activity indicators
#             user = os.getenv('USER')
#             activity_files = [
#                 f'/home/{user}/.bash_history',
#                 f'/home/{user}/.xsession-errors',
#                 '/var/log/auth.log'
#             ]
            
#             current_time = time.time()
#             latest_activity = 0
            
#             for file_path in activity_files:
#                 if os.path.exists(file_path):
#                     try:
#                         last_access = os.path.getatime(file_path)
#                         if last_access > latest_activity:
#                             latest_activity = last_access
#                     except:
#                         continue
            
#             if latest_activity > 0:
#                 idle_seconds = current_time - latest_activity
#                 # Cap at reasonable value
#                 return min(idle_seconds, 3600)  # Max 1 hour
#         except:
#             pass
        
#         # Method 3: Check running processes for user activity
#         try:
#             result = subprocess.run(
#                 ['ps', 'aux'], 
#                 capture_output=True, text=True, timeout=2
#             )
#             if result.returncode == 0:
#                 lines = result.stdout.split('\n')
#                 # Look for interactive applications
#                 interactive_keywords = ['chrome', 'firefox', 'code', 'nautilus', 'terminal', 'gnome-terminal']
#                 for line in lines:
#                     if any(keyword in line.lower() for keyword in interactive_keywords):
#                         # Found interactive app, assume active
#                         return 0.0
#         except:
#             pass
        
#         # If all methods fail, assume active (better than assuming idle)
#         return 0.0
        
#     except Exception as e:
#         print(f"⚠️ Simple idle detection error: {e}")
#         return 0.0

# def get_idle_seconds_linux():
#     """Main Linux idle detection with fallbacks"""
#     # Try traditional methods first
#     try:
#         # Try xprintidle
#         try:
#             result = subprocess.run(['xprintidle'], capture_output=True, text=True, timeout=3)
#             if result.returncode == 0:
#                 idle_ms = int(result.stdout.strip())
#                 idle_seconds = idle_ms / 1000.0
#                 print(f"🔍 Idle (xprintidle): {idle_seconds:.1f}s")
#                 return idle_seconds
#         except:
#             pass
        
#         # Try xdotool
#         try:
#             result = subprocess.run(['xdotool', 'getidletime'], capture_output=True, text=True, timeout=3)
#             if result.returncode == 0:
#                 idle_ms = int(result.stdout.strip())
#                 idle_seconds = idle_ms / 1000.0
#                 print(f"🔍 Idle (xdotool): {idle_seconds:.1f}s")
#                 return idle_seconds
#         except:
#             pass
        
#     except Exception as e:
#         print(f"⚠️ Traditional idle detection failed: {e}")
    
#     # Fall back to simple method
#     return get_idle_seconds_linux_simple()

# def get_idle_seconds_windows():
#     try:
#         import ctypes
#         class LASTINPUTINFO(ctypes.Structure):
#             _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
#         lastInputInfo = LASTINPUTINFO()
#         lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
#         ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
#         millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
#         return millis / 1000.0
#     except Exception:
#         return 0.0

# def get_idle_seconds_macos():
#     try:
#         result = subprocess.run(['ioreg', '-c', 'IOHIDSystem'], capture_output=True, text=True, timeout=5)
#         if result.returncode == 0:
#             for line in result.stdout.split('\n'):
#                 if 'HIDIdleTime' in line:
#                     parts = line.split('=')
#                     if len(parts) > 1:
#                         nanoseconds = int(parts[1].strip(), 16)
#                         return nanoseconds / 1_000_000_000
#     except Exception as e:
#         print(f"⚠️ macOS idle detection error: {e}")
#     return 0.0

# def get_idle_seconds():
#     """Wrapper with timeout protection and sanity checks"""
#     try:
#         idle_sec = 0.0
#         if is_windows():
#             idle_sec = get_idle_seconds_windows()
#         elif is_macos():
#             idle_sec = get_idle_seconds_macos()
#         elif is_linux():
#             idle_sec = get_idle_seconds_linux()
#         else:
#             print(f"⚠️ Unsupported platform: {SYSTEM}")
#             return 0.0
        
#         # Sanity check: idle time shouldn't be more than a few hours
#         if idle_sec > 36000:  # 10 hours max
#             print(f"⚠️ Suspicious idle time {idle_sec}s, resetting to 0")
#             return 0.0
            
#         return idle_sec
#     except Exception as e:
#         print(f"⚠️ Idle detection failed: {e}")
#         return 0.0

# def is_online(check_url="https://www.google.com", timeout=5):
#     try:
#         requests.get(check_url, timeout=timeout)
#         return True
#     except Exception:
#         return False

# def get_active_window_linux():
#     """Improved Linux window detection"""
#     try:
#         # Try xdotool first
#         try:
#             result = subprocess.run(
#                 ['xdotool', 'getwindowfocus', 'getwindowname'], 
#                 capture_output=True, text=True, timeout=3
#             )
#             if result.returncode == 0 and result.stdout.strip():
#                 window_title = result.stdout.strip()
#                 return window_title if window_title else "Active Application"
#         except:
#             pass
        
#         # Fallback: Use environment variables or basic detection
#         desktop_session = os.getenv('XDG_CURRENT_DESKTOP', '').lower()
#         if 'gnome' in desktop_session or 'ubuntu' in desktop_session:
#             return "GNOME Desktop"
#         elif 'kde' in desktop_session:
#             return "KDE Desktop"
#         elif 'xfce' in desktop_session:
#             return "XFCE Desktop"
#         else:
#             return "Linux Desktop"
            
#     except Exception as e:
#         print(f"⚠️ Linux window detection error: {e}")
#         return "Active Application"

# def get_active_window():
#     if is_linux():
#         return get_active_window_linux()
#     else:
#         return "Active Application"

# # ----------- Offline Storage ------------
# def save_offline(image_path, meta):
#     dest_dir = os.path.join(OFFLINE_QUEUE_DIR, str(ATTENDANCE_ID))
#     os.makedirs(dest_dir, exist_ok=True)

#     ts = meta.get('timestamp', datetime.now(timezone.utc).isoformat())
#     safe_ts = ts.replace(':', '-').replace('+', '_').replace('.', '_')
#     base = f"screenshot_{safe_ts}"
#     img_name = f"{base}.png"
#     meta_name = f"{base}.meta.json"

#     dest_img = os.path.join(dest_dir, img_name)
#     dest_meta = os.path.join(dest_dir, meta_name)

#     try:
#         os.replace(image_path, dest_img)
#     except Exception:
#         import shutil
#         shutil.copyfile(image_path, dest_img)
#         try:
#             os.remove(image_path)
#         except Exception:
#             pass

#     with open(dest_meta, 'w', encoding='utf-8') as f:
#         json.dump(meta, f, ensure_ascii=False)
#     print(f"📥 Saved offline: {dest_img}")
#     return dest_img, dest_meta

# def attempt_upload_file(img_path, meta):
#     for attempt in range(RETRY_LIMIT):
#         try:
#             with open(img_path, 'rb') as f:
#                 files = {'screenshot': f}
#                 data = {
#                     'attendance_id': str(ATTENDANCE_ID),
#                     'timestamp': meta.get('timestamp'),
#                     'window_title': meta.get('window_title', 'Unknown'),
#                     'is_idle': str(meta.get('is_idle', False)),
#                     'idle_duration_seconds': str(meta.get('idle_duration_seconds', 0)),
#                     'is_productive': str(meta.get('is_productive', False)),
#                     'productivity_score': str(meta.get('productivity_score', 0.0)),
#                     'productive_time_min': str(meta.get('productive_time_min', 0.0)),
#                     'tracker_status': 'ACTIVE',  # Screenshot indicates active tracker
#                     'machine_info': json.dumps(get_machine_info())
#                 }
#                 print(f"📩 Uploading {os.path.basename(img_path)} attempt {attempt+1}/{RETRY_LIMIT} ...")
#                 resp = requests.post(API_URL, files=files, data=data, timeout=30)
#             if resp.status_code in (200, 201):
#                 print(f"✅ Uploaded: {img_path}")
#                 return True
#             else:
#                 print(f"⚠️ Upload failed: {resp.status_code} - {resp.text}")
#         except Exception as e:
#             print(f"❌ Upload error: {e}")
#         time.sleep(RETRY_BACKOFF)
#     return False

# def flush_offline_queue():
#     dir_for_att = os.path.join(OFFLINE_QUEUE_DIR, str(ATTENDANCE_ID))
#     if not os.path.isdir(dir_for_att):
#         return
#     for fname in sorted(os.listdir(dir_for_att)):
#         if fname.endswith('.meta.json'):
#             meta_path = os.path.join(dir_for_att, fname)
#             try:
#                 with open(meta_path, 'r', encoding='utf-8') as f:
#                     meta = json.load(f)
#             except Exception:
#                 continue
#             base = fname.rsplit('.meta.json', 1)[0]
#             img_path = os.path.join(dir_for_att, f"{base}.png")
#             if not os.path.exists(img_path):
#                 continue
#             ok = attempt_upload_file(img_path, meta)
#             if ok:
#                 os.remove(img_path)
#                 os.remove(meta_path)
#                 print(f"🧹 Removed queued files: {base}")

# # ---------- Productivity Logic -------------
# def compute_productivity_score(idle_seconds):
#     """Calculate productivity score based on idle time"""
#     if idle_seconds <= 60:  # 1 minute
#         return 100.0
#     elif idle_seconds <= 180:  # 3 minutes
#         return 70.0
#     elif idle_seconds <= 600:  # 10 minutes
#         return 40.0
#     else:
#         return 0.0

# # ----------- Screenshot Handling ----------
# def parse_checkin_time(checkin_iso):
#     """Parse check-in time and handle timezone properly"""
#     try:
#         current_time = datetime.now()
        
#         if 'T' in checkin_ISO:
#             if checkin_ISO.endswith('Z') or '+' in checkin_ISO:
#                 # Has timezone info - convert to local time
#                 checkin_dt = datetime.fromisoformat(checkin_ISO.replace('Z', '+00:00'))
#                 checkin_dt = checkin_dt.astimezone().replace(tzinfo=None)
#             else:
#                 # No timezone, assume local time
#                 checkin_dt = datetime.fromisoformat(checkin_ISO)
#         else:
#             # Just time, assume today
#             today = current_time.date()
#             checkin_dt = datetime.combine(today, datetime.strptime(checkin_ISO, '%H:%M:%S').time())
        
#         return checkin_dt
#     except Exception as e:
#         print(f"⚠️ Check-in parse error: {e}")
#         return None

# def take_and_handle_screenshot():
#     global LAST_SCREENSHOT_TS
#     ts = datetime.now()
#     timestamp_iso = datetime.now(timezone.utc).isoformat()
    
#     # Get current activity info
#     active_window = get_active_window()
#     idle_seconds = get_idle_seconds()
#     is_idle = idle_seconds > 600  # Idle if more than 10 minutes
#     productivity_score = compute_productivity_score(idle_seconds)

#     # Calculate productive time
#     productive_seconds = 0
    
#     if LAST_SCREENSHOT_TS:
#         # Calculate time since last screenshot
#         gap_seconds = (ts - LAST_SCREENSHOT_TS).total_seconds()
        
#         # Productive time = gap time - idle time (minimum 0)
#         productive_seconds = max(0, gap_seconds - idle_seconds)
#         print(f"🧮 Time since last screenshot: {gap_seconds/60:.2f} min, Idle: {idle_seconds/60:.2f} min")
        
#     elif CHECK_IN_ISO:
#         # First screenshot - calculate from check-in time
#         check_in_dt = parse_checkin_time(CHECK_IN_ISO)
#         if check_in_dt:
#             gap_seconds = (ts - check_in_dt).total_seconds()
            
#             # Only count positive time (avoid negative gaps)
#             if gap_seconds > 0:
#                 productive_seconds = max(0, gap_seconds - idle_seconds)
#                 print(f"🧮 First screenshot - Time from check-in: {gap_seconds/60:.2f} min, Idle: {idle_seconds/60:.2f} min")
#             else:
#                 # If check-in is in future, use current session start
#                 print(f"ℹ️ Check-in time issue, using tracker start time")
#                 productive_seconds = 0
#         else:
#             productive_seconds = 0
#     else:
#         productive_seconds = 0

#     productive_time_min = round(productive_seconds / 60, 2)

#     # Take screenshot
#     temp_file = os.path.join(tempfile.gettempdir(), f"tracker_{ATTENDANCE_ID}_{int(time.time())}.png")
    
#     try:
#         pyautogui.screenshot(temp_file)
#         print(f"📸 Captured | Idle: {idle_seconds:.1f}s | Productive: {productive_time_min}min | Window: {active_window}")

#         meta = {
#             'timestamp': timestamp_iso,
#             'window_title': active_window,
#             'is_idle': is_idle,
#             'idle_duration_seconds': int(idle_seconds),
#             'is_productive': productivity_score >= 50,
#             'productivity_score': productivity_score,
#             'productive_time_min': productive_time_min
#         }

#         # Upload or save offline
#         if is_online():
#             try:
#                 flush_offline_queue()
#             except Exception as e:
#                 print(f"⚠️ Flush error: {e}")
#             if attempt_upload_file(temp_file, meta):
#                 os.remove(temp_file)
#             else:
#                 save_offline(temp_file, meta)
#         else:
#             save_offline(temp_file, meta)

#         LAST_SCREENSHOT_TS = ts
#         return True
        
#     except Exception as e:
#         print(f"❌ Screenshot failed: {e}")
#         return False

# # ----------- Tracker Loop -----------
# def start_tracker():
#     global TRACKER_STARTED
    
#     print(f"✅ Tracker started for attendance ID: {ATTENDANCE_ID}")
#     print(f"🌐 API Endpoint: {API_URL}")
    
#     # Set tracker status to started
#     TRACKER_STARTED = True
    
#     heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
#     heartbeat_thread.start()
    
#     print(f"🖥️ Platform: {platform.system()} {platform.release()}")
    
#     # Check time synchronization first
#     check_time_sync()
    
#     # Install required tools for Linux
#     if is_linux():
#         print("🔧 Linux environment detected")
#         # Check for required tools
#         tools = ['xprintidle', 'xdotool']
#         missing_tools = []
        
#         for tool in tools:
#             result = subprocess.run(['which', tool], capture_output=True, text=True)
#             if result.returncode != 0:
#                 missing_tools.append(tool)
        
#         if missing_tools:
#             print(f"⚠️ Missing tools: {', '.join(missing_tools)}")
#             print("💡 Install with: sudo apt install xprintidle xdotool")
#         else:
#             print("✅ All required tools available")
    
#     try:
#         while True:
#             next_delay = random.randint(1, THRESHOLD_SECONDS)
#             print(f"⏱ Next screenshot in {next_delay//60}m {next_delay%60}s")
#             time.sleep(next_delay)
#             take_and_handle_screenshot()
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("🛑 Tracker stopped by user.")
#         # Update tracker status to stopped
#         TRACKER_STARTED = False
#         # Send one final heartbeat with stopped status
#         time.sleep(1)  # Give time for final heartbeat
#         sys.exit(0)
#     except Exception as e:
#         print(f"🛑 Tracker crashed: {e}")
#         TRACKER_STARTED = False
#         time.sleep(1)  # Give time for final heartbeat
#         sys.exit(1)

# if __name__ == "__main__":
#     start_tracker()


import os
import time
import random
import json
import requests
import pyautogui
import tempfile
import sys
import platform
import socket
import subprocess
from datetime import datetime, timezone, timedelta
from PIL import Image
import threading
import logging
from logging.handlers import RotatingFileHandler
import ctypes
from ctypes import wintypes

# ---------------- CONFIG ----------------
# Get API URL from command line or use default
API_URL = sys.argv[3] if len(sys.argv) > 3 else None

SCREENSHOT_WINDOW = 10 * 60  # 10 minutes window for screenshots
SCREENSHOTS_PER_WINDOW = 2   # Max 2 screenshots per 10 minutes
MAX_GAP_SECONDS = 15 * 60    # treat any gap longer than this as idle
RETRY_LIMIT = 3
RETRY_BACKOFF = 10
OFFLINE_QUEUE_DIR = os.path.join(os.path.expanduser('~'), '.universal_hrms', 'offline_screenshots')
os.makedirs(OFFLINE_QUEUE_DIR, exist_ok=True)

# Logging configuration
LOG_DIR = os.path.join(os.path.expanduser('~'), '.universal_hrms', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'tracker_{datetime.now().strftime("%Y%m%d")}.log')

# Auto-stop configuration
AUTO_STOP_TIME = datetime.strptime("23:59:00", "%H:%M:%S").time()
# ----------------------------------------

ATTENDANCE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else None
CHECK_IN_ISO = sys.argv[2] if len(sys.argv) > 2 else None

if not ATTENDANCE_ID:
    print("❌ Attendance ID required")
    sys.exit(1)

if CHECK_IN_ISO:
    print(f"🕒 Using provided check-in time: {CHECK_IN_ISO}")

print(f"🌐 API Endpoint: {API_URL}")

# ---------------- LOGGING SETUP ----------------
logger = logging.getLogger('TrackerLogger')
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# File handler with rotation (max 5MB, keep 5 backups)
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=5*1024*1024, 
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Disable PIL debug logs
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.WARNING)

logger.info(f"Tracker started for attendance ID: {ATTENDANCE_ID}")
logger.info(f"API Endpoint: {API_URL}")
# ------------------------------------------------

LAST_SCREENSHOT_TS = None
TRACKER_STARTED = False
SCREENSHOT_TRACKER = []  # List to track screenshot timestamps in current window
SLEEP_DETECTED = False
LAST_ACTIVITY_TIME = datetime.now()

def log_error(error_msg, exc_info=False):
    """Helper function for error logging"""
    logger.error(error_msg, exc_info=exc_info)

def log_warning(warning_msg):
    """Helper function for warning logging"""
    logger.warning(warning_msg)

def log_info(info_msg):
    """Helper function for info logging"""
    logger.info(info_msg)

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        log_error(f"Failed to get local IP: {e}")
        return "unknown"

def get_machine_info():
    """Get machine information for heartbeats"""
    return {
        'hostname': platform.node(),
        'platform': platform.platform(),
        'ip_address': get_local_ip(),
        'python_version': platform.python_version(),
        'system': platform.system(),
        'processor': platform.processor(),
        'windows_version': platform.win32_ver()
    }

def send_heartbeat():
    global TRACKER_STARTED, SLEEP_DETECTED
    while True:
        try:
            if ATTENDANCE_ID:
                ts = datetime.now(timezone.utc).isoformat()
                
                data = {
                    'attendance_id': str(ATTENDANCE_ID),
                    'timestamp': ts,
                    'is_heartbeat': 'true',
                    'tracker_status': 'STARTED' if TRACKER_STARTED else 'STOPPED',
                    'sleep_detected': str(SLEEP_DETECTED),
                    'machine_info': json.dumps(get_machine_info())
                }
                
                resp = requests.post(API_URL, data=data, timeout=10)
                if resp.status_code == 200:
                    log_info(f"Heartbeat sent | Status: {'STARTED' if TRACKER_STARTED else 'STOPPED'} | Sleep: {SLEEP_DETECTED}")
                else:
                    log_warning(f"Heartbeat failed: {resp.status_code} - {resp.text}")
        except requests.exceptions.RequestException as e:
            log_error(f"Heartbeat request failed: {e}")
        except Exception as e:
            log_error(f"Heartbeat unexpected error: {e}", exc_info=True)

        time.sleep(30)  # every 30 seconds

# ---------- Windows-specific functions ----------
def get_idle_seconds_windows():
    """Get idle time in seconds for Windows"""
    try:
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
        
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
        
        # Get last input time
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo))
        
        # Get current tick count
        current_tick = ctypes.windll.kernel32.GetTickCount()
        
        # Calculate idle time in milliseconds
        idle_ms = current_tick - lastInputInfo.dwTime
        
        # Convert to seconds
        idle_seconds = idle_ms / 1000.0
        
        return idle_seconds
        
    except Exception as e:
        log_error(f"Windows idle detection error: {e}")
        return 0.0

def get_active_window_windows():
    """Get active window title for Windows"""
    try:
        import win32gui
        import win32process
        import psutil
        
        def get_active_window_title():
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title if title else "Active Application"
        
        return get_active_window_title()
        
    except ImportError:
        # Fallback if win32gui is not available
        try:
            # Try using PowerShell to get active window
            ps_script = '''
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class ActiveWindow {
                [DllImport("user32.dll")]
                public static extern IntPtr GetForegroundWindow();
                [DllImport("user32.dll")]
                public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
            }
            "@
            $hwnd = [ActiveWindow]::GetForegroundWindow()
            $sb = New-Object System.Text.StringBuilder 256
            [ActiveWindow]::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
            $sb.ToString()
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                   capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return "Active Application"
            
        except Exception as e:
            log_error(f"Windows window detection error: {e}")
            return "Active Application"
    except Exception as e:
        log_error(f"Windows window detection error: {e}")
        return "Active Application"

def check_windows_sleep_state():
    """Check if Windows is in sleep state"""
    try:
        # Query power state using powercfg
        result = subprocess.run(
            ['powercfg', '/requests'], 
            capture_output=True, text=True, encoding='utf-8', timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout.lower()
            if 'system' in output and 'display' in output:
                # Check for active sleep requests
                lines = output.split('\n')
                for line in lines:
                    if 'system:' in line and 'none' not in line:
                        return True
        return False
        
    except Exception as e:
        log_error(f"Windows sleep state check error: {e}")
        return False

# ---------- Sleep/Hibernation Detection ----------
def detect_sleep_period():
    """Detect if system was in sleep/hibernation mode"""
    global SLEEP_DETECTED, LAST_ACTIVITY_TIME
    
    current_time = datetime.now()
    time_diff = (current_time - LAST_ACTIVITY_TIME).total_seconds()
    
    # Get current idle time
    idle_seconds = get_idle_seconds_windows()
    
    # Check Windows sleep state using powercfg (more reliable)
    is_sleeping = check_windows_sleep_state()
    
    # Only detect sleep if:
    # 1. Windows reports sleep state, OR
    # 2. Very long gap (15+ minutes) with low idle
    if is_sleeping:
        SLEEP_DETECTED = True
        sleep_duration = time_diff  # Assume all time was sleep
        log_warning(f"Windows sleep state detected! Duration: {sleep_duration:.1f}s")
        return sleep_duration
    elif time_diff > 900 and idle_seconds < 60:  # 15 min gap with low idle
        SLEEP_DETECTED = True
        sleep_duration = time_diff - idle_seconds
        log_warning(f"Possible sleep detected! Duration: {sleep_duration:.1f}s")
        return sleep_duration
    
    SLEEP_DETECTED = False
    LAST_ACTIVITY_TIME = current_time
    return 0

# ---------- Time Synchronization Check ----------
def check_time_sync():
    """Check if system time is synchronized and show current time"""
    current_time = datetime.now()
    current_utc = datetime.now(timezone.utc)
    
    log_info(f"Local System Time: {current_time}")
    log_info(f"UTC Time: {current_utc}")
    
    # Check Windows time service
    try:
        result = subprocess.run(
            ['w32tm', '/query', '/status'], 
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            log_info("Windows Time Service: Active")
    except:
        log_warning("Windows Time Service check failed")
    
    if CHECK_IN_ISO:
        try:
            # Parse check-in time (handle both with and without timezone)
            if 'T' in CHECK_IN_ISO:
                if CHECK_IN_ISO.endswith('Z') or '+' in CHECK_IN_ISO:
                    # Has timezone info
                    check_in_dt = datetime.fromisoformat(CHECK_IN_ISO.replace('Z', '+00:00'))
                else:
                    # No timezone, assume local time
                    check_in_dt = datetime.fromisoformat(CHECK_IN_ISO)
            else:
                # Just time, assume today
                today = current_time.date()
                check_in_dt = datetime.combine(today, datetime.strptime(CHECK_IN_ISO, '%H:%M:%S').time())
            
            log_info(f"Check-in Time: {check_in_dt}")
            
            # Calculate time difference
            time_diff = (current_time - check_in_dt).total_seconds() / 60  # in minutes
            
            if time_diff < -5:  # Check-in time is more than 5 minutes in the future
                log_warning(f"WARNING: Check-in time appears to be {abs(time_diff):.1f} minutes in the future!")
                log_warning("This will cause productive time calculation issues.")
                return False
            elif time_diff > 1440:  # More than 24 hours ago
                log_warning(f"WARNING: Check-in time was {time_diff/60:.1f} hours ago")
            else:
                log_info(f"Time sync OK - Check-in was {time_diff:.1f} minutes ago")
                return True
                
        except Exception as e:
            log_error(f"Time sync check error: {e}")
    
    return True

def is_online(check_url="https://www.google.com", timeout=5):
    try:
        requests.get(check_url, timeout=timeout)
        return True
    except requests.exceptions.RequestException as e:
        log_warning(f"Network check failed: {e}")
        return False
    except Exception as e:
        log_error(f"Network check unexpected error: {e}")
        return False

# ----------- Offline Storage ------------
def save_offline(image_path, meta):
    dest_dir = os.path.join(OFFLINE_QUEUE_DIR, str(ATTENDANCE_ID))
    os.makedirs(dest_dir, exist_ok=True)

    ts = meta.get('timestamp', datetime.now(timezone.utc).isoformat())
    safe_ts = ts.replace(':', '-').replace('+', '_').replace('.', '_')
    base = f"screenshot_{safe_ts}"
    img_name = f"{base}.png"
    meta_name = f"{base}.meta.json"

    dest_img = os.path.join(dest_dir, img_name)
    dest_meta = os.path.join(dest_dir, meta_name)

    try:
        os.replace(image_path, dest_img)
    except Exception as e:
        import shutil
        log_warning(f"Replace failed, copying instead: {e}")
        shutil.copyfile(image_path, dest_img)
        try:
            os.remove(image_path)
        except Exception as e:
            log_warning(f"Failed to remove temp file: {e}")

    with open(dest_meta, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    log_info(f"Saved offline: {dest_img}")
    return dest_img, dest_meta

def attempt_upload_file(img_path, meta):
    for attempt in range(RETRY_LIMIT):
        try:
            with open(img_path, 'rb') as f:
                files = {'screenshot': f}
                data = {
                    'attendance_id': str(ATTENDANCE_ID),
                    'timestamp': meta.get('timestamp'),
                    'window_title': meta.get('window_title', 'Unknown'),
                    'is_idle': str(meta.get('is_idle', False)),
                    'idle_duration_seconds': str(meta.get('idle_duration_seconds', 0)),
                    'is_productive': str(meta.get('is_productive', False)),
                    'productivity_score': str(meta.get('productivity_score', 0.0)),
                    'productive_time_min': str(meta.get('productive_time_min', 0.0)),
                    'sleep_detected': str(meta.get('sleep_detected', False)),
                    'sleep_duration': str(meta.get('sleep_duration', 0)),
                    'tracker_status': 'ACTIVE',
                    'machine_info': json.dumps(get_machine_info())
                }
                log_info(f"Uploading {os.path.basename(img_path)} attempt {attempt+1}/{RETRY_LIMIT} ...")
                resp = requests.post(API_URL, files=files, data=data, timeout=30)
            if resp.status_code in (200, 201):
                log_info(f"Uploaded: {img_path}")
                return True
            else:
                log_warning(f"Upload failed: {resp.status_code} - {resp.text}")
        except requests.exceptions.RequestException as e:
            log_error(f"Upload request error: {e}")
        except Exception as e:
            log_error(f"Upload unexpected error: {e}")
        time.sleep(RETRY_BACKOFF)
    return False

def flush_offline_queue():
    dir_for_att = os.path.join(OFFLINE_QUEUE_DIR, str(ATTENDANCE_ID))
    if not os.path.isdir(dir_for_att):
        return
    for fname in sorted(os.listdir(dir_for_att)):
        if fname.endswith('.meta.json'):
            meta_path = os.path.join(dir_for_att, fname)
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
            except Exception as e:
                log_warning(f"Failed to load meta file {fname}: {e}")
                continue
            base = fname.rsplit('.meta.json', 1)[0]
            img_path = os.path.join(dir_for_att, f"{base}.png")
            if not os.path.exists(img_path):
                log_warning(f"Image file not found: {img_path}")
                continue
            ok = attempt_upload_file(img_path, meta)
            if ok:
                os.remove(img_path)
                os.remove(meta_path)
                log_info(f"Removed queued files: {base}")

# ---------- Screenshot Scheduling ----------
def should_take_screenshot():
    """Check if we should take a screenshot based on 10-minute window with max 2 screenshots"""
    global SCREENSHOT_TRACKER
    
    current_time = time.time()
    
    # Remove screenshots older than 10 minutes from tracker
    SCREENSHOT_TRACKER = [ts for ts in SCREENSHOT_TRACKER if current_time - ts < SCREENSHOT_WINDOW]
    
    # If we already have 2 screenshots in the last 10 minutes, don't take another
    if len(SCREENSHOT_TRACKER) >= SCREENSHOTS_PER_WINDOW:
        oldest = datetime.fromtimestamp(SCREENSHOT_TRACKER[0]).strftime('%H:%M:%S')
        newest = datetime.fromtimestamp(SCREENSHOT_TRACKER[-1]).strftime('%H:%M:%S')
        next_possible = datetime.fromtimestamp(SCREENSHOT_TRACKER[0] + SCREENSHOT_WINDOW).strftime('%H:%M:%S')
        log_info(f"Screenshot limit reached ({len(SCREENSHOT_TRACKER)}/{SCREENSHOTS_PER_WINDOW}) in last 10min. Next possible at {next_possible}")
        log_info(f"Recent screenshots: {oldest} to {newest}")
        return False
    
    # Add current timestamp to tracker
    SCREENSHOT_TRACKER.append(current_time)
    return True

# ---------- Productivity Logic -------------
def compute_productivity_score(idle_seconds, sleep_duration=0):
    """Calculate productivity score based on idle and sleep time"""
    total_inactive = idle_seconds + sleep_duration
    
    if total_inactive <= 60:  # 1 minute
        return 100.0
    elif total_inactive <= 180:  # 3 minutes
        return 70.0
    elif total_inactive <= 600:  # 10 minutes
        return 40.0
    else:
        return 0.0

# ----------- Screenshot Handling ----------
def parse_checkin_time(checkin_iso):
    """Parse check-in time and handle timezone properly"""
    try:
        current_time = datetime.now()
        
        if 'T' in checkin_iso:
            if checkin_iso.endswith('Z') or '+' in checkin_iso:
                # Has timezone info - convert to local time
                checkin_dt = datetime.fromisoformat(checkin_iso.replace('Z', '+00:00'))
                checkin_dt = checkin_dt.astimezone().replace(tzinfo=None)
            else:
                # No timezone, assume local time
                checkin_dt = datetime.fromisoformat(checkin_iso)
        else:
            # Just time, assume today
            today = current_time.date()
            checkin_dt = datetime.combine(today, datetime.strptime(checkin_iso, '%H:%M:%S').time())
        
        return checkin_dt
    except Exception as e:
        log_error(f"Check-in parse error: {e}")
        return None

def take_and_handle_screenshot():
    global LAST_SCREENSHOT_TS
    
    # Check if we should take screenshot based on 10-minute window
    if not should_take_screenshot():
        return False
    
    ts = datetime.now()
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    
    # Detect sleep/hibernation periods
    sleep_duration = detect_sleep_period()
    
    # Get current activity info
    active_window = get_active_window_windows()
    idle_seconds = get_idle_seconds_windows()
    is_idle = idle_seconds > 600  # Idle if more than 10 minutes
    
    # Calculate productivity with sleep consideration
    productivity_score = compute_productivity_score(idle_seconds, sleep_duration)

    # Calculate productive time (subtract idle and sleep time)
    productive_seconds = 0
    
    if LAST_SCREENSHOT_TS:
        # Calculate time since last screenshot
        gap_seconds = (ts - LAST_SCREENSHOT_TS).total_seconds()
        
        # Productive time = gap time - (idle time + sleep time) (minimum 0)
        productive_seconds = max(0, gap_seconds - idle_seconds - sleep_duration)
        log_info(f"Time since last screenshot: {gap_seconds/60:.2f} min, Idle: {idle_seconds/60:.2f} min, Sleep: {sleep_duration/60:.2f} min")
        
    elif CHECK_IN_ISO:
        # First screenshot - calculate from check-in time
        check_in_dt = parse_checkin_time(CHECK_IN_ISO)
        if check_in_dt:
            gap_seconds = (ts - check_in_dt).total_seconds()
            
            # Only count positive time (avoid negative gaps)
            if gap_seconds > 0:
                productive_seconds = max(0, gap_seconds - idle_seconds - sleep_duration)
                log_info(f"First screenshot - Time from check-in: {gap_seconds/60:.2f} min, Idle: {idle_seconds/60:.2f} min, Sleep: {sleep_duration/60:.2f} min")
            else:
                # If check-in is in future, use current session start
                log_info(f"Check-in time issue, using tracker start time")
                productive_seconds = 0
        else:
            productive_seconds = 0
    else:
        productive_seconds = 0

    productive_time_min = round(productive_seconds / 60, 2)

    # Take screenshot
    temp_file = os.path.join(tempfile.gettempdir(), f"tracker_{ATTENDANCE_ID}_{int(time.time())}.png")
    
    try:
        pyautogui.screenshot(temp_file)
        log_info(f"Captured | Idle: {idle_seconds:.1f}s | Sleep: {sleep_duration:.1f}s | Productive: {productive_time_min}min | Window: {active_window}")

        meta = {
            'timestamp': timestamp_iso,
            'window_title': active_window,
            'is_idle': is_idle,
            'idle_duration_seconds': int(idle_seconds),
            'sleep_detected': sleep_duration > 0,
            'sleep_duration': int(sleep_duration),
            'is_productive': productivity_score >= 50,
            'productivity_score': productivity_score,
            'productive_time_min': productive_time_min
        }

        # Upload or save offline
        if is_online():
            try:
                flush_offline_queue()
            except Exception as e:
                log_error(f"Flush error: {e}")
            if attempt_upload_file(temp_file, meta):
                os.remove(temp_file)
            else:
                save_offline(temp_file, meta)
        else:
            save_offline(temp_file, meta)

        LAST_SCREENSHOT_TS = ts
        return True
        
    except pyautogui.PyAutoGUIException as e:
        log_error(f"Screenshot capture failed: {e}")
        return False
    except Exception as e:
        log_error(f"Screenshot handling failed: {e}", exc_info=True)
        return False

def check_auto_stop_time():
    """Check if current time is past the auto-stop time (11:59 PM)"""
    current_time = datetime.now().time()
    
    # Check if current time is 11:59 PM or later
    if current_time >= AUTO_STOP_TIME:
        log_info(f"Auto-stop time reached: {current_time}")
        return True
    
    # Also check if it's past midnight (next day)
    # This handles cases where the tracker runs past midnight
    if current_time.hour == 0 and current_time.minute < 1:
        log_info(f"Past midnight, auto-stopping")
        return True
    
    return False

# ----------- Tracker Loop -----------
def start_tracker():
    global TRACKER_STARTED
    
    # Check if platform is Windows
    if platform.system() != 'Windows':
        log_error(f"Unsupported platform: {platform.system()}. This tracker only works on Windows.")
        sys.exit(1)
    
    log_info(f"Windows Tracker started for attendance ID: {ATTENDANCE_ID}")
    
    # Set tracker status to started
    TRACKER_STARTED = True
    
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()
    
    log_info(f"Windows Version: {platform.win32_ver()}")
    
    # Check time synchronization first
    check_time_sync()
    
    # Display auto-stop information
    log_info(f"Tracker will auto-stop at: {AUTO_STOP_TIME}")
    
    try:
        while True:
            # Check if it's time to auto-stop
            if check_auto_stop_time():
                log_info("Auto-stopping tracker as per schedule (11:59 PM)")
                TRACKER_STARTED = False
                
                # Send final heartbeat with stopped status
                try:
                    ts = datetime.now(timezone.utc).isoformat()
                    data = {
                        'attendance_id': str(ATTENDANCE_ID),
                        'timestamp': ts,
                        'is_heartbeat': 'true',
                        'tracker_status': 'STOPPED',
                        'sleep_detected': str(SLEEP_DETECTED),
                        'machine_info': json.dumps(get_machine_info()),
                        'auto_stopped': 'true'
                    }
                    requests.post(API_URL, data=data, timeout=10)
                except Exception as e:
                    log_error(f"Final heartbeat failed: {e}")
                
                # Flush any remaining offline screenshots
                try:
                    flush_offline_queue()
                except Exception as e:
                    log_error(f"Final flush failed: {e}")
                
                log_info("Tracker auto-stopped successfully")
                time.sleep(2)  # Give time for final logs
                sys.exit(0)
            
            # Calculate delay for next check (random between 1-5 minutes)
            next_delay = random.randint(60, 300)  # 1-5 minutes
            
            # Calculate time until auto-stop for logging
            current_time = datetime.now()
            stop_datetime = datetime.combine(current_time.date(), AUTO_STOP_TIME)
            
            # If current time is already past auto-stop time, use next day
            if current_time.time() >= AUTO_STOP_TIME:
                stop_datetime = datetime.combine(current_time.date() + timedelta(days=1), AUTO_STOP_TIME)
            
            time_until_stop = (stop_datetime - current_time).total_seconds()
            hours_until = int(time_until_stop // 3600)
            minutes_until = int((time_until_stop % 3600) // 60)
            
            log_info(f"Next check in {next_delay//60}m {next_delay%60}s")
            log_info(f"Screenshots in last 10min: {len(SCREENSHOT_TRACKER)}/{SCREENSHOTS_PER_WINDOW}")
            log_info(f"Auto-stop in: {hours_until}h {minutes_until}m")
            
            time.sleep(next_delay)
            
            # Take screenshot if within limits
            take_and_handle_screenshot()
            
    except KeyboardInterrupt:
        log_info("Tracker stopped by user.")
        # Update tracker status to stopped
        TRACKER_STARTED = False
        # Send one final heartbeat with stopped status
        time.sleep(1)  # Give time for final heartbeat
        sys.exit(0)
    except Exception as e:
        log_error(f"Tracker crashed: {e}", exc_info=True)
        TRACKER_STARTED = False
        time.sleep(1)  # Give time for final heartbeat
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Verify Windows platform
        if platform.system() != 'Windows':
            print("❌ This tracker only works on Windows")
            sys.exit(1)
            
        start_tracker()
    except KeyboardInterrupt:
        log_info("Tracker interrupted")
        sys.exit(0)
    except Exception as e:
        log_error(f"Fatal error in main: {e}", exc_info=True)
        sys.exit(1)