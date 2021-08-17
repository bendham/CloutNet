import boto3
import discord
import random
import math

from asyncio import *
from botocore.exceptions import ClientError
from discord.ext.commands import Bot, Cog
from discord.ext import tasks
from discord import FFmpegPCMAudio
from helpers import *
from tabulate import tabulate
from youtube_dl import YoutubeDL

client = discord.Client()
COMMAND_SIGN = "#"
bot = Bot(command_prefix=COMMAND_SIGN)

role_shop = {"cloutgod" : ["Clout God", "The god of all of CloutNet", 30],
            "cloutphosopher" : ["Clout Phosopher", "The wisest of all the clout",  20],
            "cloutteusmaximus": ["Cloutteus Maximus", "The big booty of the CloutNet",  10]}

NET_NAME = "FartNet"


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    #stimmy_the_net.start()

@bot.command(name='join', help="Get started on the CloutNet")
async def on_message(context):
  await context.channel.send(init_user(context))

@bot.command(name='balance', help="View your CloutCoin balance")
async def on_message(context):
  await context.channel.send(get_balance(context))

@bot.command(name='transfer', help="Move your coins to another individual: !transer amount @user")
async def on_message(context):
  await context.channel.send(transfer_coin(context))

@bot.command(name='gamble', help="Gamble your CloutCoins in a double or nothing scenario...it's a 50/50!")
async def on_message(context):
  await context.channel.send(gamble(context))

@bot.command(name='ledger', help="View the CloutNet public ledger")
async def on_message(context):
  await context.channel.send(await leaderboard(context))

@bot.command(name='buy', help="purchase some clout")
async def on_message(context):
  await context.channel.send(await buy_clout(context))

@bot.command(name='shop', help="view all clout available")
async def on_message(context):
  await context.channel.send(clout_shop(context))

@bot.command(name='flip', help="flip a coin")
async def on_message(context):
  await context.channel.send(flip())

@bot.command(name='alive', help="check if CloutNet is alive.")
async def on_message(context):
  await context.channel.send("CloutNet never dies.")

@bot.command(name='highlow', help="Play the classic higher or lower game!")
async def on_message(context):
  await highlow(context)

# @bot.command(name='stimmy', help="papa gov gives mun")
# async def on_message(context):
#   stimmy(context)
#   await context.channel.send("The Population has been stimmied.")

@bot.command(name="finalcountdown", help="costs 5 CC but plays music")
async def on_message(context):
  await context.channel.send(await music_request(context))

"""
@bot.command(name='del', help="papa delete clout")
async def on_message(context):
 del_cloutnet(context)
 print("Deleted.")
"""

async def highlow(ctx):
  channel = ctx.channel
  guildId = ctx.guild.id
  memberId = ctx.author.id

  def check(m):
    contentLC = m.content.lower()
    return ("hi" in contentLC or "lo" in contentLC) and ctx.author == m.author



  dynamoDB, user = getUserFromDb(guildId, memberId, None, True)

  if(not user):
    return "Hold the PHONE. You are trying to play a game that's on CloutNet...yet you're not on CloutNet: !join."

  guessCorrectAmount = 5

  correctGuess = True
  numberOfCorrectGuesses = 0

  hiNum = 10
  loNum = 1
  

  coins = getCoinsFromUser(user)

  if(coins >= 1):

    await channel.send(f"{at_user(memberId)} you must get {guessCorrectAmount} correct to double your Clout. The range is [{loNum}, {hiNum}]. You have {coins} CC.")
    beforeFlip = random.randint(loNum, hiNum)
    while(correctGuess and numberOfCorrectGuesses < guessCorrectAmount):
      nextFlip = random.randint(loNum, hiNum)
      await sleep(0.3)
      await ctx.channel.send(f"{beforeFlip}, {at_user(memberId)} higher or lower? #{numberOfCorrectGuesses+1}")

      try:
          msg  = await bot.wait_for('message', timeout=60.0, check=check)
          msgContent = msg.content
      except TimeoutError:
          await channel.send(f'Sorry {at_user(memberId)}. Too slow. You lose by default.')
          setUserCoins(guildId, memberId, 0)

      if(nextFlip == beforeFlip):
        await channel.send("You got a freebie! The number was the same.")
      elif("hi" in msgContent.lower() and nextFlip > beforeFlip):
        await channel.send("Bingo.")
        numberOfCorrectGuesses += 1
      elif("lo" in msgContent.lower() and nextFlip < beforeFlip):
        await channel.send("Bingo.")
      else:
        correctGuess = False
      
      numberOfCorrectGuesses += 1
      beforeFlip = nextFlip

    
    if(correctGuess):
      await channel.send(f"{at_user(memberId)} is a CloutGod with numbers.")
      await channel.send(f"{at_user(memberId)} has doubled their coins from {coins} to {2*coins}!")
      setUserCoins(guildId, memberId, coins*2)
    else:
      await channel.send(f"The number was {nextFlip}. {at_user(memberId)} is very bad with numbers.")
      await channel.send(f"{at_user(memberId)} has lost all {coins} CC. Go back to school.")
      setUserCoins(guildId, memberId, 0)
  else:
    await channel.send(f"{at_user(memberId)} is so poor they cant even play with numbers.")





async def music_request(ctx):

  price = 0

  guild = ctx.guild
  guildId = guild.id
  member = ctx.author
  memberId = member.id

  voiceStatus = ctx.author.voice
  guild = ctx.message.guild 
  video_link="https://www.youtube.com/watch?v=MvXUZKEkhDA"

  
  dynamoDB, user = getUserFromDb(guildId, memberId, None, True)

  if(not user):
    return f"You do not contain the knowhow of playing music. Joing the net, CloutNet: {COMMAND_SIGN}join."

  coins = getCoinsFromUser(user)
  
  if coins >= price+1:
    

    if voiceStatus:

      channel = voiceStatus.channel
      
      try:
        await channel.connect()
      except:
        return "Songs already playing bro, take a chill pill."
        
      voice_client = guild.voice_client

      YDL_OPTIONS = {'noplaylist':'True'}
      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

      if not voice_client.is_playing():
          setUserCoins(guildId, memberId, coins - price)

          with YoutubeDL(YDL_OPTIONS) as ydl:
              info = ydl.extract_info(video_link, download=False)
          URL = info['formats'][0]['url']
          voice_client.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
          voice_client.is_playing()

          while voice_client.is_playing():
            await sleep(5)
          return await autoGamble(voice_client, guildId, memberId, user)
      else:
        return "Songs already playing bro, take a chill pill."
    else: 
      return "{0} before using this command join a voice channel!".format(at_user(memberId))
  else:
    return "You have such little clout you don't even know what music is. Get some Clout."


async def autoGamble(voice_client, guildId, memberId, userData):
  await voice_client.disconnect()
  return gambleLogic(userData, guildId, memberId)

def stimmy(context, dynamodb=None):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name="ca-central-1")

  table = dynamodb.Table('CloutNet')

  response = table.scan()
  data = response['Items']
  
  while 'LastEvaluatedKey' in response:
      response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
      data.extend(response['Items'])
  
  for dataSet in data:
    users = dataSet["Users"]
    sortedUsers = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))
  
    for idx, user in enumerate(sortedUsers.keys()):
        size = len(users)
        threshHold = math.floor(size*0.8)

        posn = idx+1

        increment = 1 if posn <= threshHold else 2

        sortedUsers[user] = sortedUsers[user] + increment
    
    dataSet["Users"] = sortedUsers

    table.put_item(Item=dataSet)
 
def clout_shop(context):
  header = ["Buy command", "Role Name", "Description", "Price"]
  table = []
  for idx, key in enumerate(role_shop):
    table.insert(idx, [key] + role_shop[key])

  return "```"+tabulate(table, header, tablefmt="orgtbl")+"```"

async def buy_clout(context):
  guild = context.guild
  guildId = guild.id
  member = context.author
  memberId = member.id
  content = context.message.content

  dynamoDB,user = getUserFromDb(guildId, memberId, None, True)

  if(not user):
    return "You are not on cloutnet. Use !help to learn how to join."

  if(len(content.split()) <= 2):
    role = content.split()[1]

    if(role in role_shop.keys()):
      
      userCoins = getCoinsFromUser(user)
      price = role_shop[role][2]
      roleName = role_shop[role][0]

      memberRoleNameList = [memberRole.name for memberRole in member.roles]

      if(roleName in memberRoleNameList):
        return "{} is already a {}. Leave some clout for the rest of us.".format(at_user(memberId),roleName)

      if(userCoins >= price):
        setUserCoins(guildId, memberId, userCoins - price, dynamoDB)

        roleNameList = [guildRole.name for guildRole in guild.roles]

        if(roleName not in roleNameList):
          await guild.create_role(name=roleName)

        for potentialRole in guild.roles:
            if potentialRole.name == roleName:
              await member.add_roles(potentialRole,reason="Bought some clout.", atomic=True)
              break

        msg = "{} is now a {}".format(at_user(memberId),roleName)

      else:
        msg = "{0} does not have enough clout to purchase {1}. They also smell bad.".format(at_user(memberId), roleName)
    else:
      msg = "{}, that type of clout does not exist".format(at_user(memberId))
  else:
    msg = "{} is trying to scam the system...not going to work, this is CloutNet".format(at_user(memberId))
    

  return msg

def init_user(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id


  dynamoDB, userDb = getUserFromDb(guildId, usernameId, None,True)

  if userDb:
    return "{0} already exists on the CloutNet".format(at_user(usernameId))
  else:
    starting_coins = 5
    set_user(guildId, usernameId, starting_coins, dynamoDB)
    return "-- CloutNet has initialized {0} with {1} CloutCoins --".format(at_user(usernameId), starting_coins)

def get_balance(context):
  username = context.author
  usernameId = username.id
  guildId = context.guild.id

  userDb = getUserFromDb(guildId, usernameId)

  if userDb:
    return get_name(username) + " has " + str(getCoinsFromUser(userDb)) + " CloutCoins"
  else:
    return NOT_ON_NET(usernameId)

def gamble(context):
  usernameId = context.author.id
  guildId = context.guild.id

  user = getUserFromDb(guildId, usernameId)

  return gambleLogic(user, guildId, usernameId)

def gambleLogic(userData, guildId, usernameId):
  if userData:
    coins = getCoinsFromUser(userData)
    flip = random.randint(0, 1)
    if(coins > 0):
      if(flip):
        setUserCoins(guildId, usernameId, 2*coins)
        msg = "{0} has doubled their CloutCoins from {1} to {2}".format(at_user(usernameId), str(coins), str(2*coins))
      else:
        setUserCoins(guildId, usernameId, 0)
        msg = "{0} has lost all {1} CloutCoins\nYou pushed it too far".format(at_user(usernameId), coins)
    else:
      msg = "{0} is too poor to gamble".format(at_user(usernameId))
  else:
    msg = "CloutCoins could not be gambled"

  return msg

def transfer_coin(context):
  usernameId = context.author.id
  msg = context.message.content
  guildId = context.guild.id


  splitMsg = msg.split()
  if len(splitMsg) != 3:
    return "CloutNet could not transfer CloutCoins"
  
  coins = int(splitMsg[1])
  payee = splitMsg[2]
  payeeId = payee.replace("@",'').replace("!",'').replace("<",'').replace(">",'')

  dynamoDB, sender = getUserFromDb(guildId, usernameId, None, True)
  senderCoins = getCoinsFromUser(sender)

  if senderCoins - coins < 0:
    return "HAHAHA {0} doesn't have sufficient CloutCoins!".format(at_user(usernameId))
  elif not getUserFromDb(guildId, payeeId):
    return "That payee is not on the CloutNet"
  else:
    setUserCoins(guildId, usernameId, senderCoins - coins, dynamoDB)
    addUserCoins(guildId, payeeId, coins, dynamoDB)
    return "{0} has transfered {1} CloutCoins to {2}".format(at_user(usernameId), coins, at_user(payeeId))
    

async def leaderboard(context):
  guildId = context.guild.id
  guildName = context.guild.name
  msg = "==== CloutNet Public Ledger ===="


  guild = getGuildFromDb(guildId)
  if(guild):
    sorted_dict = dict(sorted(guild["Users"].items(), key=lambda item: item[1], reverse=True))
    pos = 1
    for userID in sorted_dict:
      user = await bot.fetch_user(int(userID))
      msg = msg + "\n{0} - {1}CC {2}".format(pos, sorted_dict[userID], user.name)
      pos = pos + 1
  else:
    msg=GUILD_NOT_ON_NET(guildName)
  return msg

def flip():
  flip = random.randint(0, 1)
  if(flip == 1):
    return "Heads"
  else:
    return "Tails"


# ERRORS

def GUILD_NOT_ON_NET(guildName):
  return f"{guildName} is not on the CloutNet! Be the first to join! Use !join to get started."

def NOT_ON_NET(usernameId):
 return "{0} is not on the CloutNet. Use {1}join to get started!".format(at_user(usernameId), COMMAND_SIGN)


bot.run("ODY2MDY3ODkyNDAzNDM3NTY4.YPNKlA.5DUKwmggya_lZjhR1MtHH2RTB8Q")
#client.run("ODIwMzkwMDUyNDk1ODg0MzA1.YE0dxg.oda2MS-Gv4OxyuovsJgvkrGq8zM")