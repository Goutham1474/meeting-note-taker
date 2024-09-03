import asyncio
import os
import subprocess
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

load_dotenv()

driver_path = os.getenv('driver_path')
email = os.getenv('email')
password = os.getenv('password')

options = uc.ChromeOptions()
options.add_argument("--use-fake-ui-for-media-stream")
options.add_argument("--window-size=1920x1080")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-application-cache")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, use_subprocess=True)
driver.set_window_size(1920, 1080)

def record_audio_ffmpeg(output_filename, duration):
    command = [
        'ffmpeg',
        '-f', 'dshow',
        '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',
        '-t', str(duration),
        '-y',
        output_filename
    ]
    
    print("Starting audio recording...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"Error recording audio: {stderr.decode()}")
    else:
        print(f"Audio recording finished. Saved as {output_filename}.")

async def join_google_meet(meet_url):
    driver.get(meet_url)
    print("Joining Google Meet")
    await asyncio.sleep(6)

    driver.save_screenshot("screenshots/meet_page.png")
    driver.execute_script('''
        const micButton = document.querySelector('[aria-label="Turn off microphone"]');
        const cameraButton = document.querySelector('[aria-label="Turn off camera"]');
        if (micButton) micButton.click();
        if (cameraButton) cameraButton.click();
    ''')
    driver.save_screenshot("screenshots/after_mic_cam_disable.png")

    await asyncio.sleep(2)

    try:
        try:
            join_button = driver.find_element(By.XPATH, '//*[text()="Join now"]')
            join_button.click()
        except Exception as e:
            join_button = driver.find_element(By.XPATH, '//*[text()="Ask to join"]')
            join_button.click()
    except Exception as e:
        print("Join button not found:", e)

    driver.save_screenshot("screenshots/after_ask_to_join.png")
    await asyncio.sleep(5)

async def sign_in(email, password):
    driver.get("https://accounts.google.com")
    print("Signing In to Bot Account")

    await asyncio.sleep(1)
    email_field = driver.find_element(By.NAME, "identifier")
    email_field.send_keys(email)
    driver.save_screenshot("screenshots/email.png")

    await asyncio.sleep(2)
    driver.find_element(By.ID, "identifierNext").click()

    await asyncio.sleep(3)
    driver.save_screenshot("screenshots/password.png")

    password_field = driver.find_element(By.NAME, "Passwd")
    password_field.click()
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    await asyncio.sleep(5)
    driver.save_screenshot("screenshots/signed_in.png")

async def record_meeting(meet_url: str, duration: int, output_filename: str):
    try:
        await sign_in(email, password)
        await join_google_meet(meet_url)
        
        record_audio_ffmpeg(output_filename, duration)
    finally:
        cleanup()

def cleanup():
    try:
        if driver:
            driver.quit()
    except OSError as e:
        if "The handle is invalid" in str(e):
            pass
        else:
            raise
    except Exception as e:
        print(f"Error closing Chrome: {e}")

# if __name__ == "__main__":
#     asyncio.run(record_meeting("https://meet.google.com/wqq-eaji-kig", duration=15, output_filename="audio/meeting_audio.wav"))