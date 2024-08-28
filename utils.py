import time
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os

load_dotenv()

driver_path = os.getenv('driver_path')
email = os.getenv('email')
password = os.getenv('password')
meet_url = os.getenv('meet_url')

options = uc.ChromeOptions()

# options.add_argument("--headless")  # Uncomment if you want headless mode
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x1080")

options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_camera": 2,  # Disable camera
    "profile.default_content_setting_values.media_stream_mic": 2,     # Disable microphone
    "profile.default_content_setting_values.notifications": 2         # Disable notifications
})


driver = uc.Chrome(options=options, driver_executable_path=driver_path)

def login_to_google(email, password):
    driver.get("https://accounts.google.com/signin")
    email_field = driver.find_element(By.ID, "identifierId")
    email_field.send_keys(email)
    email_field.send_keys(Keys.RETURN)
    time.sleep(5)
    password_field = driver.find_element(By.NAME, "Passwd")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)

def join_google_meet(meet_url):
    driver.get(meet_url)
    time.sleep(2)

    # driver.find_element(By.XPATH, '//*[@aria-label="Turn off microphone"]').click()
    # driver.find_element(By.XPATH, '//*[@aria-label="Turn on camera"]').click()
    meeting_name = driver.find_element(By.ID, 'c16')
    meeting_name.send_keys("Meeting Bot")
    time.sleep(2)
    join_button = driver.find_element(By.XPATH, '//*[text()="Ask to join"]')
    join_button.click()
    time.sleep(5)

def start_ffmpeg_recording(output_file="meeting_recording.mp4"):
    command = [
        'ffmpeg', '-y', '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99.0',
        '-f', 'pulse', '-i', 'default', '-c:v', 'libx264', '-preset', 'fast', output_file
    ]
    return subprocess.Popen(command)

def stop_ffmpeg_recording(process):
    process.terminate()

# ffmpeg_process = start_ffmpeg_recording("meeting_recording.mp4")

# login_to_google(email, password)
join_google_meet(meet_url)
time.sleep(3600)
# stop_ffmpeg_recording(ffmpeg_process)
driver.quit()
