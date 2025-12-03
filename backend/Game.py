"""
========================================================================================================================
Package
========================================================================================================================
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

from Shoe import Shoe
from Hand import Hand
from Utils import *


"""
========================================================================================================================
Dealer Hit Rule
========================================================================================================================
"""
def dealer_play(shoe: Shoe, dealer_hand: Hand) -> Hand:

    while True:

        total, is_soft = dealer_hand.values()
        
        if total < 17:
            dealer_hand.add_card(shoe.draw_one())
            continue

        if total == 17 and is_soft:
            dealer_hand.add_card(shoe.draw_one())
            continue

        break

    return dealer_hand


"""
========================================================================================================================
Game Rules
========================================================================================================================
"""
def settle_hand(player_hand: Hand, dealer_hand: Hand, blackjack_payout: float = 1.5) -> float:

    # Cards Value
    player_total, _ = player_hand.values()
    dealer_total, _ = dealer_hand.values()

    # Check Black Jack
    player_is_blackjack = (len(player_hand.cards) == 2 and player_hand.best_value() == 21 and not player_hand.doubled)
    dealer_is_blackjack = (len(dealer_hand.cards) == 2 and dealer_hand.best_value() == 21)

    # Player vs Dealer
    if player_is_blackjack:
        # Push
        if dealer_is_blackjack:
            return 0.0
        # Win
        return blackjack_payout * player_hand.bet
    
    # Bet
    bet = player_hand.bet * (2.0 if player_hand.doubled else 1.0)
        
    # w/ Busts
    if player_total > 21:
        return -bet
    if dealer_total > 21:
        return +bet
    
    # w/o Busts
    if player_total > dealer_total:
        return +bet
    if player_total < dealer_total:
        return -bet
    
    # Push
    return 0.0

"""
========================================================================================================================
Main Function
========================================================================================================================
"""
if __name__ == "__main__":

    pass