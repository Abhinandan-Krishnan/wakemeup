
"""
Author: Abhinandan Krishnan
Description: This script contains utility functions to take in inputs from user and generate an audio link if user wants the notification in audio format.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import yaml

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
  

def take_user_input():
	# Load existing data from the file if it exists
	try:
		with open('rules.yaml', 'r') as file:
			data = yaml.safe_load(file)
	except FileNotFoundError:
		data = []

	# Get input from the user
	alert_id = len(data) + 1
	alert_type = input("Enter alert type (1: HighScoreAlert, 2: SuperOverAlert): ")
	if alert_type=='1':
		alert_type="HighScoreAlert"

	player = input("Enter player Name: ")
	runs = int(input("Enter runs: "))
	playsound = int(input("Enter playsound (0 or 1): "))
	playtext = int(input("Enter playtext (0 or 1): "))
	if playtext==1:
		text = input("Enter text: ")
	else:
		text=" "
	print("\n\n")

	# Create alert dictionary
	alert = {
		'id': alert_id,
		'alert': {
			'type': alert_type,
			'player': player,
			'runs': runs,
			'playsound': playsound,
			'playtext': playtext,
			'text': text
		}
	}

	# Append the new alert to the data
	data.append(alert)

	# Save the updated data to the file
	with open('rules.yaml', 'w') as file:
		yaml.dump(data, file)

	print(f"Alert with id {alert_id} added successfully.")

	

	