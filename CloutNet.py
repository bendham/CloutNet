import boto3
import discord
import random
import math
import aiocron

from asyncio import *
from botocore.exceptions import ClientError
from discord.ext.commands import Bot, Cog
from discord.ext import tasks
from discord import FFmpegPCMAudio
from discord.ext.commands.core import guild_only
from helpers import *
from tabulate import tabulate
from youtube_dl import YoutubeDL
from settings import COMMAND_SIGN
from discord.utils import get

from roles.CloutGod import CloutGod

from update_messages import updateMsg3

bot = Bot(command_prefix=COMMAND_SIGN)

role_shop = {"cloutgod" : ["Clout God", "The god of all of CloutNet", 30],
            "cloutphosopher" : ["Clout Phosopher", "The wisest of all the clout",  20],
            "cloutteusmaximus": ["Cloutteus Maximus", "The big booty of the CloutNet",  10]}

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
  await context.channel.send(embed=await leaderboard(context))

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

@bot.command(name='update', help="Message CloutNet the new update. Only Void has these privlidges.")
async def on_message(context):
  if(context.author.id == 197808116962820096):
    await updateFunction(updateMsg3)

# @bot.command(name='stimmy', help="papa gov gives mun")
# async def on_message(context):
#   stimmy(context)
#   await context.channel.send("The Population has been stimmied.")

@bot.command(name="finalcountdown", help="costs 5 CC but plays music")
async def on_message(context):
  await context.channel.send(await music_request(context))

# @bot.command(name="test", help="costs 5 CC but plays music")
# async def on_message(context):
#   guild = context.guild
#   member = context.author

#   cGod = CloutGod(guild)
#   await cGod.addToMemberInGuild(member)
  
#   await context.channel.send("Became a CloutGod Made")

@bot.command(name="refund", help="refund roles")
async def on_message(context):
  if(context.author.id == 197808116962820096):
    await refund()

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

  guessCorrectAmount = 4

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
    return f"You do not contain the knowhow of playing music. Joing the net, CloutNet: {settings.COMMAND_SIGN}join."

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
    users = dataSet["current"]
    sortedUsers = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))
  
    for idx, user in enumerate(sortedUsers.keys()):
        size = len(users)
        threshHold = math.floor(size*0.8)

        posn = idx+1

        increment = 1 if posn <= threshHold else 2

        sortedUsers[user] = sortedUsers[user] + increment
    
    dataSet["current"] = sortedUsers

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

        hasRole = isRoleInGuild(roleName, guild)
        if(not hasRole):
          await createRoleInGuild(roleName, guild)

        await addExistingRole(guild, member, roleName, reason="Bought some clout")

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
        msg = "{0} has lost all {1} CloutCoins\n{2}".format(at_user(usernameId), coins, get_losing_text())
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
    

# async def leaderboard(context):
#   guildId = context.guild.id
#   guildName = context.guild.name
#   msg = "==== CloutNet Public Ledger ===="


#   guild = getGuildFromDb(guildId)
#   if(guild):
#     sorted_dict = dict(sorted(guild["current"].items(), key=lambda item: item[1], reverse=True))
#     pos = 1
#     for userID in sorted_dict:
#       user = await bot.fetch_user(int(userID))
#       msg = msg + "\n+{0} - {1}CC {2}".format(pos, sorted_dict[userID], user.name)
#       pos = pos + 1
#   else:
#     msg=GUILD_NOT_ON_NET(guildName)
#   return msg

async def leaderboard(context):
  guildId = context.guild.id
  guildName = context.guild.name

  guild = getGuildFromDb(guildId)
  if(guild):
    sorted_dict = dict(sorted(guild["current"].items(), key=lambda item: item[1], reverse=True))
    pos = 1
    msg=""
    for userID in sorted_dict:
      user = await bot.fetch_user(int(userID))
      msg = msg + "\n{0} - {1}CC {2}".format(pos, sorted_dict[userID], user.name)
      
      pos = pos + 1
    embed=discord.Embed(title="==== CloutNet Public Ledger ====", color=0xa9ce46, description=msg)
  else:
    embed=discord.Embed(title=GUILD_NOT_ON_NET(guildName), color=0xa9ce46)
  return embed

@aiocron.crontab('0 12 * * 6')
async def send_weekly_recap_cron():

  database = getDb()

  for entry in database:
    id = int(entry['GuildID'])
    textChannel= getGuildTextChannel(id)
    if(textChannel):
      await textChannel.send(embed=await weekly_recap(entry))

      setPrevious(id,entry['current'])

async def weekly_recap(guild):
  embed=discord.Embed(title="==== CloutNet Weekly Recap ====", color=0xa9ce46)
  current_sorted_dict = dict(sorted(guild["current"].items(), key=lambda item: item[1], reverse=True))
  previous_sorted_dict = dict(sorted(guild["previous"].items(), key=lambda item: item[1], reverse=True))

  biggestLoser = {"user": "Nobody", "amount": 0}
  biggestGainer = {"user": "Nobody", "amount": 0}

  positionString=""

  pos = 1
  for userID in current_sorted_dict:
    user = await bot.fetch_user(int(userID))

    change, amountChange = getUserChangeDetails(current_sorted_dict,previous_sorted_dict,userID, pos)

    if amountChange > biggestGainer["amount"]:
      biggestGainer['user'] = user.name
      biggestGainer['amount'] = amountChange
    elif amountChange < biggestLoser['amount']:
      biggestLoser['user'] = user.name
      biggestLoser['amount'] = amountChange

    
    positionString = positionString + f"\n{pos} - {change['placeChange']} {change['moneyChange']}CC {user.name}"
    pos = pos + 1

  
  embed.add_field(name="--- Position & Clout Changes ---", value=positionString, inline=False)

  gainerMsg = ""
  if(biggestGainer["amount"] == 0):
    gainerMsg+= "\nThere are no biggest gainers for this week"
  else:
    gainerMsg += f"\n{biggestGainer['user']} was the biggest weekly gainer, gaining {biggestGainer['amount']}CC"

  if(biggestLoser["amount"] == 0):
    gainerMsg+= "\nThere are no biggest losers for this week. You all did great."
  else:
    gainerMsg += f"\n{biggestLoser['user']} was the biggest weekly loser, losing {biggestLoser['amount']}CC"


  embed.add_field(name="--- Gainers & Losers ---", value=gainerMsg, inline=False)

  return embed

def getSpan(text, color="white"):
  return f"<span style='color:{color}; display:block'>{text}</span>"
  
def getUserChangeDetails(current, prev, userId, currentPos):
  posCount=1
  for id in prev:
    if(id == userId):
      previousPos = posCount
      break
    else:
      posCount+=1

  placeChange = currentPos-previousPos
  absPlaceChange = abs(placeChange)

  placeChangeSymbol = "⇒"
  color="white"
  if(placeChange < 0):
    placeChangeSymbol = "▲"
    color="green"
  elif(placeChange > 0):
    placeChangeSymbol = "▼"
    color="red"

  moneyChange = current[userId]-prev[userId]
  absMoneyChange = abs(moneyChange)

  moneyChangeSymbol = "+"
  if(moneyChange < 0):
    moneyChangeSymbol = "-"

  change_details = {
    "placeChange" : placeChangeSymbol+str(absPlaceChange),
    "moneyChange" : moneyChangeSymbol+str(absMoneyChange),
    "color":color
  }

  return change_details, moneyChange

def flip():
  flip = random.randint(0, 1)
  if(flip == 1):
    return "Heads"
  else:
    return "Tails"


def getGuildTextChannel(guildId):

  guild = bot.get_guild(guildId)
  textChannelList = guild.text_channels

  txtChannel = None

  for item in textChannelList:
    if(item.name.lower() == settings.TEXT_CHANNEL):
      txtChannel = item
      break
    
  return txtChannel

async def refund(database=None):
  if(not database):
    database = getDb()

  for entry in database:
    await iterateUsersInGuild(entry)

async def iterateUsersInGuild(entry):
  users = entry['current']

  guildId = int(entry['GuildID'])
  guild = bot.get_guild(guildId)

  guildTxt = getGuildTextChannel(guildId)
  if(guildTxt):
       
    for userid in users.keys():
      member = await guild.fetch_member(int(userid))

      refundableRoles = userHasRoles(member)
      if refundableRoles:
        moneyRefund = 0
        for roleName in refundableRoles:
          commandName = roleName.lower().replace(" ", "")
          moneyRefund += role_shop[commandName][2]
          


        #addUserCoins(guildId, userid, moneyRefund)

        roleString = ""
        idx = 0
        for role in refundableRoles:
          roleString += role
          if(idx+1 != len(refundableRoles)):
            roleString += ", "
          idx += 1

        #await guildTxt.send(f"{at_user(userid)} has been refunded {moneyRefund} for their roles of: {roleString}")
    
      for roleName in refundableRoles:
          role = get(guild.roles, name=roleName)  
          await role.delete()

def userHasRoles(member):
  cloutRoles = ["Clout God", "Clout Phosopher", "Cloutteus Maximus"]
  memberRoleNameList = [memberRole.name for memberRole in member.roles]

  hasRole = []

  for role in memberRoleNameList: 
    if(role in cloutRoles):
      hasRole.append(role)

  return hasRole

async def updateFunction(updateMsg):
  if(updateMsg):
    await messageGuilds(buildUpdateMessage(updateMsg))

async def messageGuilds(embedAnouncement, database=None):
  if(not database):
    database = getDb()

  for entry in database:
    id = int(entry['GuildID'])

    if(embedAnouncement):
      textChannel = getGuildTextChannel(id)
      if(textChannel):
        await textChannel.send(embed=embedAnouncement)

def isRoleInGuild(roleName, guild):
  roleNameList = [guildRole.name for guildRole in guild.roles]

  if(roleName not in roleNameList):
    return False
  else:
    return True

async def createRoleInGuild(roleName, guild):
  await guild.create_role(name=roleName)

async def addExistingRole(guild, member, roleName, reason="Just cause"):
  for potentialRole in guild.roles:
    if potentialRole.name == roleName:
      await member.add_roles(potentialRole,reason=reason, atomic=True)
      break

# ERRORS

def GUILD_NOT_ON_NET(guildName):
  return f"{guildName} is not on the CloutNet! Be the first to join! Use !join to get started."

def NOT_ON_NET(usernameId):
 return "{0} is not on the CloutNet. Use {1}join to get started!".format(at_user(usernameId), settings.COMMAND_SIGN)

bot.run(settings.BOT_TOKEN)