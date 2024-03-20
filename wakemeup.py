import requests
import bs4
import re
import json
from collections import defaultdict
from googlehomepush import GoogleHome
from utils import get_audio_link
import logging
import os
import traceback
import azure.cosmos.exceptions as exceptions

import time
import config
from azure.cosmos import CosmosClient, PartitionKey

# Initialize your Cosmos DB client
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

client = CosmosClient(HOST, credential=MASTER_KEY)
database = client.get_database_client(DATABASE_ID)
container = database.get_container_client(CONTAINER_ID)

class MatchData:
	def __init__(self,url,PATH):
		self.score_url=url
		self.score_res=requests.get(self.score_url)
		self.score_dump=bs4.BeautifulSoup(self.score_res.text,'lxml')
		self.PATH=PATH
		self.card_url=url.replace('scores','scorecard')
		self.card_res=requests.get(self.card_url)
		self.card_dump=bs4.BeautifulSoup(self.card_res.text,'html.parser')
		self.match=defaultdict(dict)
		#self.match={'MatchInfo':{'Teams':[],'Toss':[], 'Players':{}}}

		self.names = {}
		with open(os.path.join(self.PATH,"teamnames.json"), "r") as config_file:
			self.names = json.load(config_file)
		#Call all necessary functions
		self.PATH=PATH

	def extract_data(self,pattern,string):
		extract = re.search(pattern, string)
		if extract:
			res=extract.groups()
		else:
			res="Not found."
		return res

	def get_match_info(self):
		data=self.card_dump.select('.cb-col .cb-col-100 .cb-font-13')[-1].getText()
		

		#Extract team self.names
		team1,team2=self.extract_data(r'\b([A-Z]{2,4})\svs\s([A-Z]{2,4})\b',data)
		self.match['MatchInfo']['Teams']=[team1,team2]

		#Extract Toss
		toss=self.extract_data(r"Toss\s\s(.*?)\swon the toss and opt to (bowl|bat)", data)
		self.match['MatchInfo']['Toss']=[toss[0],toss[1]]

		#Extract Player self.names
		team1_players=self.extract_data(r"{}\sSquad  Playing(.*?)Bench".format(self.names[team1]),data)[0].split(',')
		team2_players=self.extract_data(r"{}\sSquad  Playing(.*?)Bench".format(self.names[team2]),data)[0].split(',')
		self.match['MatchInfo']['Players']={team1:[player.strip() for player in team1_players],team2:[player.strip() for player in team2_players]}


		#Extract Match Type
		if "ODI" in data:
			match_type="ODI"
		if "T20I" in data:
			match_type="T20"
		if "Ranji" in data:
			match_type="Test"
		if "Test" in data:
			match_type="Test"
		if "Bash" in data:
			match_type="T20"
		if "IPL" in data:
			match_type="T20"
		if "Ford" in data:
			match_type="T20"
		else:
			match_type="Test"

		self.match['MatchInfo']['Format']=match_type


	def current_status(self):
		classes = [value for element in self.score_dump.find_all(class_=True) for value in element["class"]]
		if 'cb-text-complete' in classes:
			result = self.score_dump.select('.cb-text-complete')
			status='complete'
		elif 'cb-text-inprogress' in classes:
			result = self.score_dump.select('.cb-text-inprogress')
			status='inprogress'
		elif 'cb-text-stumps' in classes:
			result = self.score_dump.select('.cb-text-stumps')
			status='stumps'
		else:
			result='N/A'
			status='N/A'
		try:
			self.match["MatchStatus"]={"Status":status,"Description":result[-1].getText()}
		except:
			self.match["MatchStatus"]={"Status":status,"Description":result}


	def get_player_scores(self):
		pass


	#Still in dev. Need to generalise well
	def get_current_scores(self):
		if self.match["MatchStatus"]["Status"]=="inprogress":
			data=self.score_dump.select('.cb-col .cb-col-100 .cb-col-scores')[0].getText()
			#res=re.search(r'\b([A-Z]{2,3})\s(\d+)/(\d+)\s\((.*?)\)\s([A-Z]{2,3})\s(\d+)/(\d+)\s\((.*?)\)',data)
			res=re.search(r'\b([A-Z]{2,4})(.*?)([A-Z]{2,4})(.*?)\)',data)		
			scores=res.groups()
			#self.match["Scores"]={scores[0]:{"Score":float(scores[1]),"Wickets":float(scores[2]),"Overs":float(scores[3])},scores[4]:{"Score":float(scores[5]),"Wickets":float(scores[6]),"Overs":float(scores[7])}}
			self.match["Scores"]={scores[0]:{"Score":scores[1]},scores[2]:{"Score":scores[3]}}
		else:
			self.match["Scores"]="Match not in Progress"


	def get_current_batsmen_scores(self):
		if self.match["MatchStatus"]["Status"]=="inprogress":
			data=self.score_dump.find("div",class_='cb-col-67 cb-col').find("div",class_='cb-min-inf cb-col-100').find_all("div",class_='cb-col cb-col-100 cb-min-itm-rw')
			current_scores=defaultdict(dict)
			for batsman in data: 
				info=[]
				for div in batsman.find_all("div", class_="cb-col"):
					info.append(div.text.strip())
				current_scores[info[0]]={"Runs":info[1],"Balls":info[2],"4s":info[3],"6s":info[4]}
				self.match["CurrentBatsmanScore"]=current_scores
		else:
			self.match["CurrentBatsmanScore"]="Match not in Progress"

	
	def print(self):
		j=json.dumps(self.match,indent=4)
		with open(os.path.join(self.PATH,"match_data.json"),'w') as f:
			json.dump(self.match,f,indent=4)
		print(j)

	def push_to_cosmos(self):
    	# Convert the match data to JSON
		self.match['partitionKey'] = 'key'
		self.match['id'] = '1'

		# Convert the match data to JSON
		match_data = json.dumps(self.match, indent=4)

		# Convert the JSON string back to a Python dictionary
		match_data_dict = json.loads(match_data)

		# Push the JSON data to Azure Cosmos DB
		try:
			db = client.create_database(id=DATABASE_ID)
			print('Database with id \'{0}\' created'.format(DATABASE_ID))
		
		except exceptions.CosmosResourceExistsError:
			db = client.get_database_client(DATABASE_ID)
			print('Database with id \'{0}\' was found'.format(DATABASE_ID))

		try:
			container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
			print('Container with id \'{0}\' created'.format(CONTAINER_ID))
		except exceptions.CosmosResourceExistsError:
			container = db.get_container_client(CONTAINER_ID)
			print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

		try:
			container.upsert_item(match_data_dict)
			print("Data pushed to Azure Cosmos DB successfully.")
		except exceptions.CosmosResourceExistsError:
			print(f"Item already exists")
			traceback.print_exc()


	
class alert(MatchData):
	def __init__(self,url,PATH,mode):
		self.PATH=PATH

		if mode=="prod":
			super().__init__(url,PATH)
			#Call necessary functions in MatchData class to get match information (only in prod mode)
			self.get_match_info()
			self.current_status()
			#self.get_current_scores()
			self.get_current_batsmen_scores()

		elif mode=="dev":
			#Get saved data from file
			with open(os.path.join(self.PATH,"match_data.json"),"r") as f:
				data = json.load(f)
			self.match=data
			#self.push_to_cosmos()

		self.highscore_flag=0

	def send_alert(self,playsound,playtext,text):
		if playsound==True:
			for i in range(0,3):
				GoogleHome(host="192.168.0.134").play("https://audio.jukehost.co.uk/7Xie70tvsMrcUa37nhujjaLvmXRPYHJ0")
				time.sleep(20)
		if playtext==True:
			link=get_audio_link(text)
			if link:
				for i in range(0,3):
					GoogleHome(host="192.168.0.134").play(link)
			else:
				logging.warning("Text message not played")
				print("Text message not played")


	def highscore_alert(self,player=None,runs="90",playsound=True,playtext=False,text=None):
		runs=int(runs)
		if self.match["MatchStatus"]["Status"]=="inprogress":
			if player!="ALL":
				try:
					score=self.match["CurrentBatsmanScore"][player]
					if float(score["Runs"])>=runs:
						self.highscore_flag=1
						logging.info("Player {} on {}. Alert created".format(player,score["Runs"]))
						print("Player {} on {}. Alert created".format(player,score["Runs"]))
						self.send_alert(playsound,playtext,text)
					else:
						logging.info("Player {} on {}. No Alert created".format(player,score["Runs"]))
						print("Player {} on {}. No Alert created".format(player,score["Runs"]))

				except KeyError:
					logging.warning("Player not playing currently")
					print("Player not playing currently")
			elif player=="ALL":
				for player in self.match["CurrentBatsmanScore"].keys():
					score=self.match["CurrentBatsmanScore"][player]
					if float(score["Runs"])>=runs:
						self.highscore_flag=1
						logging.info("Player {} on {}. Alert created".format(player,score["Runs"]))
						print("Player {} on {}. Alert created".format(player,score["Runs"]))
						self.send_alert(playsound,playtext,text)
					else:
						logging.info("Player {} on {}. No Alert created".format(player,score["Runs"]))
						print("Player {} on {}. No Alert created".format(player,score["Runs"]))


		else:
			logging.warning("Match not in Progress")
			print("Match not in Progress")


