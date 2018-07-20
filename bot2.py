import discord
import asyncio
import sys
import re
from enum import Enum
from random import randint
import json
	
class messageLog:
	def __init__(self):
		self.msg = ""
		self.log = ""
		
	def logMessage(self, msg):
		self.log += msg + '\n'
	
	def discordMessage(self, msg):
		self.msg += msg + '\n'
	
	def logMessagePrint(self):
		print(self.log)
		self.log = ""
	
	def discordMessageRead(self):
		msg = self.msg
		self.msg = ""
		return msg

class commandType(Enum):
	invalid = 0
	pick = 1
	captains = 2
	veto = 3
	exit = 4

class playerData:
	def __init__(self, name = "unnamed", id = "NOID", isCaptain = False):
		self.name = name
		self.id = id
		self.isCaptain = isCaptain

class teamData:
	def __init__(self, pos):
		self.players = [playerData(), playerData(), playerData(), playerData(), playerData()]
		self.pos = pos
		self.totalPicks = 0
	
	def addPlayer(self, player):
		self.players[self.totalPicks].name = player
		self.totalPicks += 1
	
	def getCaptainID(self):
		return self.players[0].id
	
	def getCaptain(self):
		return self.players[0]
	
	def getTeamNameString(self):
		return "Team " + self.getCaptain().name
	
	def getTeamString(self):
		return (self.getTeamNameString() + ": " + self.players[0].name + ''.join((", " + str(player.name)) for player in self.players[1:self.totalPicks]) if self.getCaptain().name != "unnamed" else "Team " + str(self.pos))

class gameData:
	def __init__(self):
		self.teams = [teamData(0), teamData(1)]
		self.pickInfo = {'team' : 0, 'picksRemaining' : 1, 'totalPicks' : [0, 0]}
		self.vetoInfo = {'team' : 1, 'vetosRemaining' : 1, 'totalVetos' : [0, 0]}
		self.mapInfo = 	{
						'Dust 2' : {'terms' : ['dust 2', 'd2', 'dii', 'dust ii', 'dust'], 	'remaining' : True},
						'Mirage' : {'terms' : ['mirage'], 									'remaining' : True},
						'Overpass' : {'terms' : ['overpass', 'ovp'], 						'remaining' : True},
						'Cache' : {'terms' : ['cache', 'caiche'], 							'remaining' : True}, # <3 Spunj
						'Inferno' : {'terms' : ['inferno', 'inf'], 							'remaining' : True},
						'Nuke' : {'terms' : ['nuke', 'chris'], 								'remaining' : True},
						'Train' : {'terms' : ['train', 'choo choo'], 						'remaining' : True},
						}
	def reset(self):
		for mapName in self.mapInfo.keys():
			self.mapInfo[mapName]['remaining'] = True
		self.pickInfo = {'team' : 0, 'picksRemaining' : 1, 'totalPicks' : [0, 0]}
		self.vetoInfo = {'team' : 1, 'vetosRemaining' : 1, 'totalVetos' : [0, 0]}
			
		
	def vetoMaps(self, vetos):
		allowedVetos = vetos[0:self.vetoInfo['vetosRemaining']]
		for veto in allowedVetos:
			for mapName, mapData in self.mapInfo.items():
				if(veto in mapData['terms']):
					self.mapInfo[mapName]['remaining'] = False
					self.vetoInfo['totalVetos'][self.vetoInfo['team']] += 1
					self.vetoInfo['vetosRemaining'] -= 1
					print("Vetoing " + mapName)
		
		if(self.vetoInfo['vetosRemaining'] == 0):
			self.vetoInfo['team'] = 1 - self.vetoInfo['team']
			self.vetoInfo['vetosRemaining'] = 2 if self.vetoInfo['totalVetos'][self.vetoInfo['team']] < 2 else 3 - self.vetoInfo['totalVetos'][self.vetoInfo['team']]
				
	def getCaptainIDs(self):
		return [team.getCaptainID() for team in self.teams]
		
	def addPlayers(self, picks):
		allowedPicks = picks[0:self.pickInfo['picksRemaining']]
		for pick in allowedPicks:
			self.teams[self.pickInfo['team']].addPlayer(pick) 
			self.pickInfo['totalPicks'][self.pickInfo['team']] += 1
			self.pickInfo['picksRemaining'] -= 1
			print("Added " + str(pick) + " to team " + str(self.pickInfo['team']))

		if(self.pickInfo['picksRemaining'] == 0):
			self.pickInfo['team'] = 1 - self.pickInfo['team']
			print(self.pickInfo['totalPicks'][self.pickInfo['team']])
			self.pickInfo['picksRemaining'] = 2 if self.pickInfo['totalPicks'][self.pickInfo['team']] < 3 else 4 - self.pickInfo['totalPicks'][self.pickInfo['team']]
	
	def setCaptains(self, ids, names):
		for counter, id in enumerate(ids):
			self.teams[counter].players[0].id = id
			self.teams[counter].totalPicks = 1
			self.teams[counter].totalVetos = 0
			print("Setting team " + str(counter) + " captain ID to " + str(id))
			
		for counter, name in enumerate(names):
			self.teams[counter].players[0].name = name
			print("Setting team " + str(counter) + " captain name to " + str(name))
			
	def printTeams(self):
		return self.teams[0].getTeamString() + '\n' + self.teams[1].getTeamString()
	
	def printMaps(self):
		mapString = ""
		first = True
		for mapName, mapInfo in self.mapInfo.items():
			
			if(mapInfo['remaining'] == True):
				if(not first):
					mapString += ", "
				mapString += str(mapName)
				first = False
		return mapString
	def printNextPick(self):
		return self.teams[self.pickInfo['team']].players[0].name + " can make " + str(self.pickInfo['picksRemaining']) + " pick" + ("s" if self.pickInfo['picksRemaining'] != 1 else "")
		
	def printNextVeto(self):
		return self.teams[self.vetoInfo['team']].players[0].name + " can make " + str(self.vetoInfo['vetosRemaining']) + " veto" + ("s" if self.vetoInfo['vetosRemaining'] != 1 else "")
		
	def printState(self):
		return "```" + self.printTeams() + '```\n```' + self.printMaps() + "```\n```" + self.printNextPick() + "```\n```" + self.printNextVeto() + "```"

def parseInputCommand(inputCommand):
	tokens = re.split('\W+', inputCommand.content[1:].lower())
	if(tokens[0] not in commandType.__members__):
		print("Invalid command token: " + tokens[0])
		tokens[0] = 'invalid'
		logStore.discordMessage("```Invalid command: " + tokens[0] + "```")
	command = {'senderID' : inputCommand.author.id, 'type' : commandType[tokens[0]], 'vars': tokens [1:]}
	return command

def pickCommand(senderID, picks):
	team = -1
	if(senderID in game.getCaptainIDs()):
		team = game.getCaptainIDs().index(senderID)
	else:
		logStore.discordMessage("```You are not a captain```")
		return
	if(game.pickInfo['team'] != team):
		log.discordMessage("```It's not your turn to pick```")
		return
	maxPicks = game.pickInfo['picksRemaining']
	game.addPlayers(picks[0:maxPicks])
	
def captainsCommand():
	v_channel = client.get_channel(config['voiceServer'])
	v_members = list(v_channel.voice_members)
	max_id = len(v_members)-1
	if max_id > 0:
		game.reset()
		captains = [''] * 2
		captains[0]=randint(0,max_id)
		captains[1]=randint(0,max_id-1)
		if captains[1] == captains[0]:
			captains[1] += 1
		captainnames = [v_members[captain].name for captain in captains]
		captainids = [v_members[captain].id for captain in captains]
		game.setCaptains(captainids, captainnames)
		IDs = game.getCaptainIDs()
		print(IDs)
	else:
		logStore.discordMessage("```Too few players in the channel " + v_channel.name + "```")

def vetoCommand(senderID, vetos):
	team = -1
	if(senderID in game.getCaptainIDs()):
		team = game.getCaptainIDs().index(senderID)
	else:
		logStore.discordMessage("```You aren't a captain```")
		return
	if(game.vetoInfo['team'] != team):
		logStore.discordMessage("```It's not your turn to ban```")
		return
	maxVetos = game.vetoInfo['vetosRemaining']
	game.vetoMaps(vetos[0:maxVetos])
	

def parseCommand(command):
	if(command['type'] == commandType.pick):
		pickCommand(command['senderID'], command['vars'])
	if(command['type'] == commandType.captains):
		captainsCommand()
	if(command['type'] == commandType.veto):
		vetoCommand(command['senderID'], command['vars'])
	if(command['type'] == commandType.exit and command['senderID'] == ownerID):
		logStore.logMessage("Exit command from user " + str(command['senderID']))
		client.logout()
		exit()

config = {}
with open('config.json', 'r') as configFile :
	config = json.load(configFile)	
game = gameData()	
logStore = messageLog()
client = discord.Client()


@client.event
async def on_ready():
	global HELP
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')


@client.event
async def on_message(message):
	if (message.channel.id in config['vetoID']) and (message.author != client.user) and (message.content[0] == config['commandChar']):
		command = parseInputCommand(message)
		parseCommand(command)
		await client.send_message(message.channel, game.printState())
		await client.send_message(message.channel, logStore.discordMessageRead())
		print(logStore.logMessagePrint())
client.run(config['botID'])
