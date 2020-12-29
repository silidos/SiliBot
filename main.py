import discord
import config
import requests
import json
import datetime
import random

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

guild = client.get_guild('enter guild id')

#method to add to JSON
def write_json(data, filename='attendance.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

#gets random quotes from API
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def get_attendance(userId):
    with open('attendance.json', 'r') as f:
        inDatabase = False
        # make sure file reads from beginning
        f.seek(0)
        data = json.load(f)
        for user in data['users']:
        # check if user is in database    
            if (str(user['id']) == str(userId.id)):
                inDatabase = True
                if(userId.nick != None and userId.nick != user['nick']):
                    user['nick'] = userId.nick
                    write_json(data)
                # convert iso to datetime
                coolDownDate = datetime.datetime.strptime(user['cooldownDate'], '%Y-%m-%d')
                # convert datetime to date
                coolDownDate = coolDownDate.date()
                # check if user is eligible for attendance
                if(coolDownDate == datetime.date.today() or coolDownDate > datetime.date.today()):
                    return -2
            
            # user is eligible for attendance points
                elif(coolDownDate < datetime.date.today()):
                    user['cooldownDate'] = datetime.date.today().isoformat()
                    user['points'] = user['points'] + 10
                    write_json(data)
                    return user['points']

                else:
                    return -2        

    # user is not in database, add entry
    if(inDatabase == False):
        jsonobj = {
                    "id": userId.id,
                    "name": userId.name,
                    "points": 10,
                    "cooldownDate": datetime.date.today().isoformat(),
                    "nick": userId.nick   
                  }

        with open("attendance.json") as q:
            data = json.load(q)
            temp = data['users'] 
            temp.append(jsonobj)
    
        write_json(data)
        return -1

def get_points(userId):
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for user in data['users']:
        # check if user is in database    
            if (user['id'] == userId):
                return user['points']

    return -1

def deduct_points(userId, points):
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for user in data['users']:
        # check if user is in database    
            if (user['id'] == userId):
                user['points'] = user['points'] - points

    write_json(data)            

def check_database(user):
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for userDB in data['users']:
            if (str(userDB['name']).lower() == str(user).lower()):
                return True
            if (str(userDB['nick']).lower() == str(user).lower()):
                return True    

    return False        

async def move_user(user):
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for userDB in data['users']:
        # check if user is in database    
            if (str(userDB['name']).lower() == str(user[1]).lower()):
                userId = userDB['id']
            if (str(userDB['nick']).lower() == str(user[1]).lower()):
                userId = userDB['id']    

    member = client.get_guild('enter guild id').get_member(userId)
    for channel in client.get_guild('enter guild id').channels:
        if(str(channel) == 'Quarantine'):
            thisChannel = channel
    await member.edit(voice_channel=thisChannel)

async def kick_user(user):
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for userDB in data['users']:
        # check if user is in database    
            if (str(userDB['name']).lower() == str(user[1]).lower()):
                userId = userDB['id']
            if (str(userDB['nick']).lower() == str(user[1]).lower()):
                userId = userDB['id']    
        
    member = client.get_guild('enter guild id').get_member(userId)
    await member.edit(voice_channel=None)    

def get_leaderboard():
    namePoints = {}
    with open('attendance.json', 'r') as f:
        data = json.load(f)
        for userDB in data['users']:
            if (userDB['nick'] == None):
                namePoints.update({userDB['name']: userDB['points']})
            else:
                namePoints.update({userDB['nick']: userDB['points']})    

    return namePoints            
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send('Current commands are:\n$help\n$climb\n$el alfa\n$tin\n$bud\n$ape1\n$pce\n$attendance\n$inspire\n$points\n$shop\n$leaderboard')

    if message.content.startswith('$commands'):
        await message.channel.send('Current commands are:\n$help\n$climb\n$el alfa\n$tin\n$bud\n$ape1\n$pce\n$attendance\n$inspire\n$points\n$shop\n$leaderboard')    

    if message.content.startswith('$attendance'):
        points = get_attendance(message.author)
        if (points == -1):
            await message.channel.send(' First attendance logged. You now have 10 points.')
            return

        if (points == -2):
            await message.channel.send('Attendance already logged for today.')
            return      
        await message.channel.send('Attendance logged. You now have ' + str(points) + ' points.')        

    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if message.content.startswith('$points'):
        points = get_points(message.author.id)
        if (points == -1):
            await message.channel.send('Could not find user. Use $attendance to claim your points for the day')  
            return
        if (points == 1):
            await message.channel.send('You have 1 point.')
            return

        await message.channel.send('You have ' + str(points) + ' points.')

    if message.content.startswith('$shop'):
        await message.channel.send('List of shop commands:\n' + '$move _user (10 points)\n' + '$kick _user (20 points)\n')   

    if message.content.startswith('$move'):
        points = get_points(message.author.id)
        if("_" in message.content):
            user = message.content.split("_", 1)
            if (check_database(user[1]) == True):
                if (points >= 10):
                    deduct_points(message.author.id, 10)
                    await move_user(user)
                    await message.channel.send('User moved')
                else:
                    await message.channel.send('Insufficient points')
            else: await message.channel.send('Could not find user to move.')
        else: await message.channel.send('Incorrect syntax. Use $move _user')            

    if message.content.startswith('$kick'):
        points = get_points(message.author.id)
        if("_" in message.content):
            user = message.content.split("_", 1)
            if (check_database(user[1]) == True):
                if (points >= 20):
                    deduct_points(message.author.id, 20)
                    await kick_user(user)
                    await message.channel.send('User kicked')
                else:
                    await message.channel.send('Insufficient points')
            else: await message.channel.send('Could not find user to kick.')
        else: await message.channel.send('Incorrect syntax. Use $kick _user')              

    if message.content.startswith('$leaderboard'):
        scores = get_leaderboard()
        leaderboard_string = ''
        for player, value in scores.items():
            newString = player + ': ' + str(value) + '\n'
            leaderboard_string += newString
        await message.channel.send('Current Leaderboard: ' + '\n' + leaderboard_string)                                    




client.run(config.token)