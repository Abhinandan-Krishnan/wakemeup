from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
from screeninfo import get_monitors
import logging

def get_audio_link(text):
	try:
		options = webdriver.FirefoxOptions()
		driver = webdriver.Firefox()

		driver.get("https://freetts.com")
		time.sleep(2)
		text_input = driver.find_element("name","TextMessage")
		time.sleep(2)
		text_input.send_keys(text)
		time.sleep(2)
		#voice = Select(driver.find_element("id","Voice"))
		#time.sleep(5)
		voice = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Voice")))
		voice=Select(voice)
		voice.select_by_visible_text("Matthew_Male")
		time.sleep(2)
		driver.find_element("id","btnAudio").click()
		time.sleep(2)
		audio_link_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div/div[2]/div[4]/div[3]/div/div/div[2]/audio/source")))
		audio_link=audio_link_element.get_attribute("src")
		#audio_link = driver.find_element("xpath","/html/body/div[2]/div[2]/div/div/div[2]/div[4]/div[3]/div/div/div[2]/audio/source").get_attribute("src")
		time.sleep(2)
	except:
		logging.warning("Could not retrive audio link for text")
		driver.quit()
		return False
	driver.quit()
	return audio_link
  