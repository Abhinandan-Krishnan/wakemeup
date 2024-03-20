
"""
Author: Abhinandan Krishnan
Description: This script sets up alerts for cricket matches based on predefined rules.
"""

import logging
import os
import argparse
from datetime import datetime
import yaml
from utils import take_user_input
from wakemeup import alert


# URL of the desired match
URL = r'https://www.cricbuzz.com/live-cricket-scores/60009/aus-vs-ind-1st-test-australia-tour-of-india-2023'
PATH = "./"  # Update with appropriate path

logging.basicConfig(
    filename=os.path.join(PATH, "logfile.log"),
    filemode='a',
    format='[%(asctime)s,%(msecs)d] [%(levelname)s]: %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)

'''
alert.highscore_alert(player=None,runs=90,playsound=True,playtext=False,text=None)

Parameters: Player: string
					Player full name for alert. 
					Default: creates alert for all players on strike 
			runs: string
				  run threshold for alert
				  Default: 90 runs
			playsound: Bool
					   if True: alarm sounds play
					   if False: alarm does not play
			playtext: Bool
					  if True: text audio sounds play
					  if False: text audio does not play
			text: String
				  Text to play on google home						

Returns: No returns. Creats a alert flag for given conditions
'''

def parse_rules(rule):
    alert_id = rule["id"]
    alert_type = rule["alert"]["type"]

    if alert_type == "HighScoreAlert":
        player = rule["alert"]["player"]
        playsound = rule["alert"]["playsound"]
        runs = rule["alert"]["runs"]
        playtext = rule["alert"]["playtext"]
        text = rule["alert"]["text"]
        params = [player, runs, playsound, playtext, text]
        return alert_id, alert_type, params


def run_alerts(mode):
    logging.info('Running script at: {}'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    alerter = alert(url=URL, path=PATH, mode=mode)
    take_user_input()

    with open(os.path.join(PATH, 'rules.yaml')) as f:
        rules = yaml.safe_load(f)

    for rule in rules:
        alert_id, alert_type, params = parse_rules(rule)
        if alert_type == "HighScoreAlert":
            try:
                alerter.highscore_alert(params[0], params[1], params[2], params[3], params[4])
            except Exception as e:
                logging.error(f"Alert ID: {alert_id} failed. Error: {str(e)}")

    logging.info("Alert jobs finished")
    logging.info("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", help="set mode (dev or prod)", choices=['prod', 'dev'], nargs='?', default="dev")
    args = parser.parse_args()
    run_alerts(args.mode)
