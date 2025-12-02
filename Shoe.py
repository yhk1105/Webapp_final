"""
========================================================================================================================
Package
========================================================================================================================
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

import random
from typing import Dict

from Utils import *


"""
========================================================================================================================
Shoe Manager
========================================================================================================================
"""
class Shoe():

    """
    ====================================================================================================================
    Initialization
    ====================================================================================================================
    """
    def __init__(self, num_decks: int = 6, rng: random.Random = None) -> None:

        self.num_decks = num_decks
        self.rng = rng or random.Random()

        # Counts of Every Rank
        self.counts: Dict[Rank, int] = {r: 4 * num_decks for r in RANKS}

        return

    """
    ====================================================================================================================
    Number of Remaining Cards
    ====================================================================================================================
    """
    def remaining(self) -> int:

        return sum(self.counts.values())

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def remove_card(self, rank: Rank) -> None:
        
        # Check Validity
        if self.counts.get(rank, 0) <= 0:
            raise ValueError("No card {} left to remove".format(rank))
        
        # Remove Specific Rank
        self.counts[rank] -= 1

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def draw_one(self) -> Rank:

        total = self.remaining()
        if total == 0:
            raise ValueError("Shoe is empty")
        
        # 
        r = self.rng.randint(1, total)
        cum = 0
        for rank in RANKS:
            cum += self.counts.get(rank, 0)
            if r <= cum:
                self.remove_card(rank)
                return rank
    
        # 
        raise RuntimeError("draw_one failed")

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def clone(self) -> 'Shoe':

        shoe_temp = Shoe(self.num_decks, rng = random.Random(self.rng.randint(0, 2**31-1)))
        shoe_temp.counts = dict(self.counts)

        return shoe_temp
    

"""
========================================================================================================================
Main Function
========================================================================================================================
"""
if __name__ == "__main__":

    shoe = Shoe(num_decks = 8)

    temp = shoe.clone()

    print()
    print(temp.draw_one())
    print(temp.draw_one())
    print(temp.draw_one())
    print(temp.draw_one())
    print()

    print()
    print(shoe.counts)
    print(temp.counts)
    print()