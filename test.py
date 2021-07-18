import pytest
from helpers import *

user1 = 420
user2 = 42
user3 = 69
guildId = 123

def test_db_access():
    # Should get guild
    guild = getGuildFromDb(guildId)
    assert guild["GuildID"] == guildId
    
    # Should get all users in guild
    guildUsers = guild["Users"].keys()
    assert str(user1) in guildUsers
    assert str(user2) in guildUsers
    assert str(user3) in guildUsers

    # Should get user from a guild
    user = getUserFromDb(guildId, user1)["Users"]
    assert str(user1) in user.keys()

def test_coin_setting():
    # Should get user coins
    user = getUserFromDb(guildId, user1)
    coins = -1
    coins = getCoinsFromUser(user)
    assert coins != -1

    # Should add user coins
    value = 3
    addUserCoins(guildId, user1, value)
    newCoins = getCoinsFromUser(getUserFromDb(guildId, user1))
    assert (coins + value) == newCoins

    # Should set user coins
    value = 90
    setUserCoins(guildId, user1, value)
    newCoins = getCoinsFromUser(getUserFromDb(guildId, user1))
    assert newCoins == value


if __name__ == '__main__':
    test_db_access()
    test_coin_setting()
