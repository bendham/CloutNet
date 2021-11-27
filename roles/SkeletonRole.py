from ctypes import Array
from discord import Color, Permissions
from discord.member import Member

class SkeletonRole:

    def __init__(self, name, guild, colour=Color.default(), permissions=Permissions(), hoist=False, mentionable=True, reason="No reason ;)") -> None:
        self.name = name
        self.colour = colour
        self.permissions = permissions
        self.hoist = hoist
        self.mentionable = mentionable
        self.reason = reason
        self.guild = guild           

    async def getAndOrMakeRoleInGuild(self):
        for guildRole in self.guild.roles:
            roleName = guildRole.name
            
            if(roleName == self.name):
                self.id = guildRole.id
                return guildRole

        return await self._createRoleInGuild()
        
    async def _createRoleInGuild(self):#TODO: add permissions
        self.role = await self.guild.create_role( 
            name=self.name,
            colour=self.colour,
            hoist=self.hoist,
            mentionable=self.mentionable,
            reason=self.reason
            )
        self.id = self.role.id
        return self.role

    async def _addRoleToMember(self, member, memberRoleReason: str ="Bought some Clout"):
        role = await self.getAndOrMakeRoleInGuild()
        await member.add_roles(role, reason=memberRoleReason, atomic=True)

    async def addToMemberInGuild(self, member: Member):
        await self._addRoleToMember(member)

    async def addToMembersInGuild(self, memberList: Array):
        for member in memberList:
            await self._addRoleToMember(member)        