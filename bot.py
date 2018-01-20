import discord
import asyncio
import sys
import random
from random import randint
import string
import csv

commandChar = '*'

voiceServer = ''

vetoID = ''

ownerID = ''

botID = ''

serverName = 'undefined server'

voiceChannelName = 'undefined channel'

HELP = 'undefined HELP'

maps = ['Cobble', 'Mirage', 'Overpass', 'Nuke', 'Train', 'Cache', 'Inferno']
captainids = [0,0]
captainnames = [' ', ' ']
teamA = [' ',' ',' ',' ']
teamB = [' ',' ',' ',' ']
bans = [0,0,0,0,0,0,0]
pick_order =   [0, 1, 1, 0, 0, 1, 1, 0]
pick_numbers = [0, 0, 1, 1, 2, 2, 3, 3]
pick_number = 0
ban_order = [1, 0, 0, 1, 1, 0]
ban_number = 0
popflash = ''

def loadConfig(config):
	global vetoID
	global voiceServer
	global ownerID
	global botID
	global serverName
	global HELP
	with open(config, 'r') as csvfile:
		configReader = csv.DictReader(csvfile)
		for row in configReader:
			ownerID = str(row['owner'])
			vetoID = str(row['bans_channel'])
			voiceServer = str(row['voice_channel'])
			botID = row['botID']
			serverName = row['serverName']
	
def get_popflash():
	if popflash == '':
		return '```No popflash yet```'
	else:
		return '```Popflash at: ```\n' + popflash +'\n'

def get_current_pick():
	tau_picked = 0
	recommend = '```'
	for i in range(0,4):
		if (teamA[i].lower() == 'tau' or teamA[i].lower() == 'will' or teamB[i].lower() == 'tau' or teamB[i] == 'will' or captainnames[int(i/2)].lower() == 'tau' or captainnames[int(i/2)].lower() == 'will'):
			tau_picked = 1
	if tau_picked == 0:
		recommend = ' VetoBot recommends his polar bear buddy tau ;)```'
	if pick_number >= 8:
		return '```All players picked```'
	if(captainnames[0] == ' ' or captainnames[1] == ' '):
		return ' '
	if(pick_order[pick_number]==0):
		return '```Team ' + captainnames[0] + ' to pick next.' + recommend
	else:
		return '```Team ' + captainnames[1] + ' to pick next.' + recommend

def get_current_ban():
	if ban_number >= 6:
		played_map = ''
		for i in range (0, 7):
			if bans[i] == 0:
				played_map = maps[i]
		return '```The map is ' + played_map + '```'
	else:
		if(captainnames[0] == ' ' or captainnames[1] == ' '):
			return ' '
		if ban_order[ban_number] == 0:
			return '```Team ' + captainnames[0] + ' to ban next```'
		else:
			return '```Team ' + captainnames[1] + ' to ban next```'

def get_captains():
	out = '```Captain A: ' + captainnames[0] + ' | Captain B: ' + captainnames[1] + '```'
	return out

def get_teams():
	out = '```'
	if captainnames[0] != ' ' and captainnames[1] != ' ':
		out += 'Team ' + captainnames[0] + ': ' + captainnames[0]
		for i in range(0, 3):
			if teamA[i] != ' ':
				out += ', ' + teamA[i]
		if teamA[3] != ' ':
			out += ', ' + teamA[3] + ' the fat kid :('
		out += '\nTeam ' + captainnames[1] + ': ' + captainnames[1]
		for i in range(0, 4):
			if teamB[i] != ' ':
				out += ', ' + teamB[i]
		out += '```'
		return out
	else:
		return '```Please enter \'captains\' to start```'
		

def get_maps():
	out = '``` - '
	for i in range(0,7):
		if bans[i] == 0:
			out = out + maps[i] + ' - '
	out += '```'
	return out

def pop_gen():
	global popflash
	popflash = 'https://popflash.site/scrim/' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(0,9))
	return '```new popflash generated```'
		
def get_instruction(message):
	global pick_number
	global captainids
	global teamA
	global teamB
	global bans
	global pick_order
	global maps
	global captainnames
	global popflash
	global ban_number
	global ban_order
	received = message.content
	sender = message.author
	if 'help' in received:
		return HELP
		
	if(received[0]=='-'):
		for i in range(0,7):
			if received.lower() == '-' + maps[i].lower():
				if ban_number >= 6:
					return 'Map picked'
				elif (sender.name == captainnames[ban_order[ban_number]] or sender.id == ownerID):
					bans[i] = 1
					ban_number+=1
					return '```Banned ' + maps[i] + '```'
				else:
					return '```You are not the captain of team ' + captainnames[ban_order[ban_number]] + ', ' + sender.name + '```'
	
	if 'ban' in received.lower() or 'veto' in received.lower(): 
		for i in range(0,7):
			if maps[i].lower() in received.lower():
				if ban_number >= 6:
					return 'Map picked'
				elif sender.name == captainnames[ban_order[ban_number]] or sender.id == ownerID:
					bans[i] = 1
					ban_number+=1
					return '```Banned ' + maps[i] + '```'
				else:
					return '```You are not the captain of team ' + captainnames[ban_order[ban_number]] + ', ' + sender.name + '```'
				
	if  'reset' in received.lower():
		for i in range(0,7):
			bans[i] = 0
		for i in range(0,4):
			teamA[i] = ' '
			teamB[i] = ' '
		captainids = [0,0]
		pick_number = 0
		captainnames = [' ', ' ']
		popflash = ''
		ban_number = 0
		return '```PUGBot has reset```'
		
	if  'captains' in received.lower():
		for i in range(0,4):
			teamA[i] = ' '
			teamB[i] = ' '
			pick_number = 0
		v_channel = client.get_channel(voiceServer)
		v_members = list(v_channel.voice_members)
		max_id = len(v_members)-1
		ban_number = 0
		print(max_id)
		if max_id > 0:
			captainids[0]=randint(0,max_id)
			captainids[1]=randint(0,max_id-1)
			if captainids[1] == captainids[0]:
				captainids[1] += 1
			captainnames = [v_members[captainids[0]].name, v_members[captainids[1]].name]
			return '```Captains chosen, to reselect just type captains again```'
		else:
			output = '```Too few players in ' + v_channel.name + '```'
			return output
		
	if '-captaina' in received.lower():
		for i in range(0,7):
			bans[i] = 0
		for i in range(0,4):
			teamA[i] = ' '
			teamB[i] = ' '
		pick_number = 0
		ban_number = 0
		captainnames[0]=received[10:]
		return '```Captain A is ' + captainnames[0] + '```'
	if '-captainb' in received.lower():
		for i in range(0,7):
			bans[i] = 0
		for i in range(0,4):
			teamA[i] = ' '
			teamB[i] = ' '
		pick_number = 0
		ban_number = 0
		captainnames[1]=received[10:]
		return '```Captain B is ' + captainnames[1] + '```'
		
	if 'pick' in received.lower():
		fat_kid = ''
		if pick_number == 7:
			fat_kid = 'fat kid '
		if (sender.name == captainnames[pick_order[pick_number]]): 
			if pick_number >= 8 :
				return '```All players picked```'
			if len(received)>21:
				return '```You\'re probably taking the piss```'
			else:
				if pick_order[pick_number]==0:
					teamA[pick_numbers[pick_number]] = received[5:]
					pick_number+=1
					return '```Team ' + captainnames[0] + ' picked ' +fat_kid + received[5:] + '```'
				else:
					teamB[pick_numbers[pick_number]] = received[5:]
					pick_number+=1
					return '```Team ' + captainnames[1] + ' picked ' + fat_kid + received[5:] + '```'
		else:
			return '```Fuck off, you are not the captain of team ' + captainnames[pick_order[pick_number]] + ', ' + sender.name + '.```'
				
				
	if 'https://popflash.site/scrim' in received.lower():
		popflash = received
		return '```popflash set```'
		
	if 'reban' in received.lower():
		ban_number=0
		for i in range (0,7):
			bans[i]=0
		return '```Bans reset```'	
		
	if 'popgen' in received.lower():
			return pop_gen()
		
	return ''

if len(sys.argv) > 1:		
	print('Loading config ' + sys.argv[1])	
	loadConfig(sys.argv[1])		
else:
	print('No config argument - loading from config.csv') 
	loadConfig('config.csv')

if len(sys.argv) > 2:
	commandChar = str(sys.argv[2])[0]
	print('commandChar is ' + commandChar)
		
client = discord.Client()


@client.event
async def on_ready():
	global HELP
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	voiceChannel = client.get_channel(voiceServer)
	print('getting channel ' + voiceServer)
	voiceChannelName = voiceChannel.name
	commandPrefixString = ''
	if commandChar != '*':
		commandPrefixString = 'It uses the command prefix ' + commandChar + ' which should be prepended to any command.\n\n'
	HELP = '```This bot is currently configured for ' + serverName + '.\n\n' + commandPrefixString + 'To begin you must select captains. \nIf multiple people are in the ' + voiceChannelName + ' voice channel, then type \ncaptains\nto select randomly from the people in the channel.\n\nTo manually set the captains, use \n-CaptainA [discord name] \nand\n-CaptainB [discord name]\nCaptains must use their discord name.\n\nTo pick players type \n\'pick [name]\'\nThis name doesn\'t have to be their discord name.\n\nTo veto maps type one of \n\'-[map]\'\n\'ban [map]\'\n\'veto [map]\'\n\nYou must use the map names as shown in remaining maps.\n\nTo generate a popflash type \n\'popgen\'\n\nTo reset type \n\'reset\'```'		

@client.event
async def on_message(message):
	if (message.channel.id in vetoID) and (message.author != client.user) and (message.content[0] == commandChar or commandChar == '*'):
		if 'exit' in message.content.lower() and ownerID in message.author.id:
			await client.send_message(message.channel, 'Goodbye :wave:')
			client.logout()
		response = get_instruction(message)
		if(len(response) > 0):
			await client.send_message(message.channel, get_instruction(message) + '\n' + get_popflash() + '\n' + get_teams() + '\n' + get_current_pick() + '\n' + get_current_ban() + '\n' + get_maps())
		
print('BOTID: ' + botID)
client.run(botID)
