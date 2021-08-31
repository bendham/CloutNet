import boto3
import json
import random
import settings

def getUserFromDb(guildId, memberId,dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

  table = dynamodb.Table(settings.AWS_TABLE)

  try:
      response = table.get_item(
          Key={'GuildID': guildId},
          ProjectionExpression="#usr.#id",
          ExpressionAttributeNames={
              '#usr':'Users',
              '#id': f'{memberId}'
          })
  except ClientError as e:
      print("e.response['Error']['Message']")
  else:
      if returnDynamodb:
        return dynamodb, response.get('Item')
      else:
        return response.get('Item')

def getGuildFromDb(guildId,dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

  table = dynamodb.Table(settings.AWS_TABLE)

  try:
      response = table.get_item(Key={'GuildID': guildId})
  except ClientError as e:
      print("e.response['Error']['Message']")
  else:
      if returnDynamodb:
        return dynamodb, response.get('Item')
      else:
        return response.get('Item')

def setGuildWithUser(guildId,userId, coins, dynamodb=None, returnDynamodb=False):
  if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

  table = dynamodb.Table(settings.AWS_TABLE)

  response = table.put_item(
       Item={
            'GuildID': guildId,
            'Users': {
              f"{userId}" : coins
            }
        }
    )
  if returnDynamodb:
    return dynamodb, response
  else:
    return response

def setUserCoins(guildId, memberId, amount=1, dynamodb=None, returnDynamodb=False ):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

    table = dynamodb.Table(settings.AWS_TABLE)

    response = table.update_item(
        Key={
            'GuildID': guildId,
        },
        UpdateExpression="set #usr.#id = :val",
        ExpressionAttributeNames={
            '#usr':'Users',
            '#id': f'{memberId}',
        },
        ExpressionAttributeValues={
            ':val': amount
        },
        ReturnValues="UPDATED_NEW"
    )

    if returnDynamodb:
      return dynamodb, response
    else:
      return response

def addUserCoins(guildId, memberId, increaseAmount=1, dynamodb=None, returnDynamodb=False ):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='ca-central-1')

    table = dynamodb.Table(settings.AWS_TABLE)

    response = table.update_item(
        Key={
            'GuildID': guildId,
        },
        UpdateExpression="set #usr.#id = #usr.#id + :val",
        ExpressionAttributeNames={
            '#usr':'Users',
            '#id': f'{memberId}',
        },
        ExpressionAttributeValues={
            ':val': increaseAmount
        },
        ReturnValues="UPDATED_NEW"
    )

    if returnDynamodb:
      return dynamodb, response
    else:
      return response

def getCoinsFromUser(userData):
    return list(userData["Users"].values())[0]

def get_name(username):
  if username.nick:
    return username.nick
  else:
    return username.name

def at_user(id):
  return "<@!{0}>".format(id)

def set_user(guildId, id, coins, dynamoDB=None):
  guild = getGuildFromDb(guildId, dynamoDB)
  if(guild):
    setUserCoins(guildId, id, coins, dynamoDB)
  else:
    setGuildWithUser(guildId, id, coins, dynamoDB)


def get_losing_text():

  with open("words.json", 'r') as f:
    losing_array = json.load(f)["lost"]
  
  return random.choice(losing_array)

"""
def del_cloutnet(context):
  guildId = context.guild.id
  if guild_in_db(guildId):
    del db[guildId]
"""