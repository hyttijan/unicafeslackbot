import datetime
import os
import json
import requests
from slackclient import SlackClient


class Unicafebot:

	def __init__(self):
		self.bot_name = 'unicafeslackbot'
		self.slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
		self.restaurants = {'Latin Market Metsatalo': 'http://messi.hyyravintolat.fi/json/fin/1',
			   'Olivia': 'http://messi.hyyravintolat.fi/json/fin/2',
			   'Paarakennus': 'http://messi.hyyravintolat.fi/json/fin/4',
			   'Physicum': "http://messi.hyyravintolat.fi/json/fin/12",
			   'Ylioppilasaukio':"http://messi.hyyravintolat.fi/json/fin/9",
			   'Chemicum':"http://messi.hyyravintolat.fi/json/fin/10"}

	def handleOutput(self,slack_rtm_output):
		output_list = slack_rtm_output
		if output_list and len(output_list) > 0:
			for output in output_list:
				if("content" in output.keys()):
					if(output.get("content")=="help"):
						return "Kirjoita ravintolan nimi saadaksesi tietaa paivan ruuat:"+",".join(self.restaurants.keys()),output.get("channel")
					else:
						answer,restaurant = self.fetchUnicafeLunches(output.get("content"))
					if("error" in answer):
						return answer.get("error"),output.get("channel")
					elif(answer.get("foods")==[]):
						message = "Tanaan ravintolassa "+restaurant+" ei ole tarjolla ruokaa"
						return message,output.get("channel")
					else:
						message = "Tanaan ravintolassa "+restaurant+" ruokana on "
						foods = ""
						message+=",".join([food.get('name')+" "+food.get("price")+" kuvaus:"+food.get("description") for food in answer.get("foods")])
						return message,output.get("channel")
			return (None,None)
		else:
			return (None, None)

	def fetchUnicafeLunches(self,restaurant):
		if(restaurant in self.restaurants.keys()):
			try:
				req = requests.get(self.restaurants[restaurant])
				menu = req.json()
				today = datetime.datetime.today().weekday()
				return (menu.get("week")[today],menu.get("title"))
			except Exception:
				return {"error":"Valitettavasti en onnistunut hakemaan ruokalistaa ravintolasta "+restaurant}
		else:
			return ({"error":"Valitettavasti en tieda ravintolaa "+restaurant+", jos tarvitset apua kirjoita help"},None)

	def mainLoop(self):

		if self.slack_client.rtm_connect():
			print("Slackbot connected")
			current = []
			while True:
				output = self.slack_client.rtm_read()
				if output!=[]:
					message,channel = self.handleOutput(output)
					if(message!=None):
						self.slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

if __name__ == '__main__':
	unicafeslackbot = Unicafebot()
	unicafeslackbot.mainLoop()





