# wake-me-up

A Python based application that runs on a standalone Raspberry Pi to alert users about a milestone or an event happening in a Sports game based on the rules set by the them.

Currently the Application supports for Cricket, taking in input form users to alert them if a batsman of their choice is near to a milestone, or whenever the match is tied and superover is about to start. The user is alerted through Speaker with a predefined sound or a custom Text to Speech input form user.

## Instructions to Run the Code 

Create a virtualenv: ```virtualenv venv```

Activate the virtualenv: ``` source venv/bin/activate```

Install the Python requirements: ```pip install -r requirements.txt``` 

Run the main file: ```python main.py```

Enter your inputs for the player you want to be alerted for and the score. 
