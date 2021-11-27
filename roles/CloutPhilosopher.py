from roles.SkeletonRole import SkeletonRole
from discord import Color

class CloutPhilosopher(SkeletonRole):

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
        self.name = "Clout Philosopher"
        self.price=500
        self.buycommand = "cloutphil"
        self.description = "Thy is thy wisest of them all."
        self.attributes = "Forsee the next gamble once a day. But costs 50 CC to do so."
        

        
