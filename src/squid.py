from enum import Enum
from actor import Actor

class Squid(Actor):
    def __init__(self):
        super().__init__()

        self.health = 1
    
    # TODO Create and update where the squid simply walks left and right and turns around at walls
    # Should they care about ledges?

    # They can be taken out by being jumped on
    # They hurt the player if they run into their sides or they fall on the player (if they don't care about ledges)
    # Worth 100(?) points