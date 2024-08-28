import time
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

load_dotenv()

driver_path = os.getenv('driver_path')
email = os.getenv('email')
password = os.getenv('password')
meet_url = os.getenv('meet_url')

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-popup-blocking")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-save-password-bubble")

options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.notifications": 1
})

driver = uc.Chrome(options=options, use_subprocess=True)

def start_ffmpeg_recording(output_file):
    command = [
        'ffmpeg',
        '-y',  # Overwrite output files without asking
        '-f', 'x11grab',  # For Linux; use 'gdigrab' for Windows
        '-s', '1920x1080',  # Screen resolution
        '-i', ':0.0',  # Display address (':0.0' for Linux; on Windows you might use the window ID)
        '-c:v', 'libx264',
        '-r', '30',  # Frames per second
        output_file
    ]
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def stop_ffmpeg_recording(process):
    process.terminate()

def join_google_meet(meet_url):
    driver.get(meet_url)
    time.sleep(10)
    
    driver.execute_script('''
        const micButton = document.querySelector('[aria-label="Turn off microphone"]');
        const cameraButton = document.querySelector('[aria-label="Turn off camera"]');
        if (micButton) micButton.click();
        if (cameraButton) cameraButton.click();
    ''')

    try:
        meeting_name = driver.find_element(By.XPATH, '//*[@aria-label="Your name"]')
        meeting_name.send_keys("Meeting Bot")
    except Exception as e:
        print("No name input required", e)
    
    time.sleep(2)
    
    try:
        join_button = driver.find_element(By.XPATH, '//*[text()="Ask to join"]')
        join_button.click()
    except Exception as e:
        print("Join button not found", e)
    
    time.sleep(5)

def check_participants():
    participants_xpath = '//*[@aria-label="Show everyone"]'
    driver.find_element(By.XPATH, participants_xpath).click()
    time.sleep(2)
    participants_list_xpath = '//*[@role="listitem"]'
    participants = driver.find_elements(By.XPATH, participants_list_xpath)
    driver.find_element(By.XPATH, participants_xpath).click()
    return len(participants)

join_google_meet(meet_url)
ffmpeg_process = start_ffmpeg_recording("meeting_recording.mp4")

try:
    while True:
        participants_count = check_participants()
        print(f"Participants: {participants_count}")
        if participants_count <= 1:
            break
        time.sleep(10)
finally:
    stop_ffmpeg_recording(ffmpeg_process)
    driver.quit()
