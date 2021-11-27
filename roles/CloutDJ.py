from roles.SkeletonRole import SkeletonRole
from discord import Color
from settings import COMMAND_SIGN

class CloutDJ(SkeletonRole):

    def __init__(self):
        self.initilizeAttributes()

    def __init__(self, guild):
        self.initilizeAttributes()

        super().__init__(
            name=self.name, 
            guild=guild, 
            colour=Color.gold(), 
            hoist=True, 
            reason=f"The role of {self.name} did not exist, so it was created."
        )

    def initilizeAttributes(self):
        self.name = "Clout DJ"
        self.price=50
        self.buycommand = "cloutdj"
        self.description = ""
        self.attributes = "Ability to play only the fatest of beats. {COMMAND_SIGN}play <music name>, to play."
        

        
