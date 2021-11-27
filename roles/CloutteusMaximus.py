from roles.SkeletonRole import SkeletonRole
from discord import Color

class CloutteusMaximus(SkeletonRole):

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
        self.name = "Cloutteus Maximus"
        self.price=350
        self.buycommand = "cloutmax"
        self.description = "Strongest muscle in the net."
        self.attributes = "Ability to kick someone out of a voice channel once a day."
        

        
