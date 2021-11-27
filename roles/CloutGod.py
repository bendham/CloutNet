from roles.SkeletonRole import SkeletonRole
from discord import Color

class CloutGod(SkeletonRole):

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
        self.name = "Clout God"
        self.price=1000
        self.buycommand = "cloutgod"
        self.description = "Who dares to bark at the God of all Clout. Bow down and become one."
        self.attributes = "Extra 5% \odds to gamble."
        

        
