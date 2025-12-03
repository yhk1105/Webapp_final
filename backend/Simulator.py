"""
========================================================================================================================
Package
========================================================================================================================
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))

import random
import math
from typing import List, Dict

from Shoe import Shoe
from Hand import Hand
from Game import *
from Utils import *


"""
========================================================================================================================
Monte Carlo Simulator
========================================================================================================================
"""
class Simulator():

    """
    ====================================================================================================================
    Initialization
    ====================================================================================================================
    """
    def __init__(self, base_shoe: Shoe, num_sim: int = 10000, blackjack_payout: float = 1.5, rng_seed: int = None) -> None:

        self.base_shoe = base_shoe

        self.num_sim = num_sim
        self.blackjack_payout = blackjack_payout
        self.rng = random.Random(rng_seed)

        return

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    # Simulator.py の _prepare_shoe_from_state メソッド内

    def _prepare_shoe_from_state(self, player_cards: List[Rank], dealer_cards: List[Rank]) -> Shoe:
        # Clone Shoe
        shoe = self.base_shoe.clone()

        # Remove Player's Cards
        #for card in player_cards[:]:
         #    if shoe.counts.get(card, 0) <= 0:
                 # シミュレーション中にカードが足りなくなる稀なケースは無視して続行させるか、エラーハンドリング
          #       continue 
           #  shoe.remove_card(card)

        # Remove Dealer's Cards
        #for card in dealer_cards[:]:
        #     if shoe.counts.get(card, 0) <= 0:
        #         continue
        #     shoe.remove_card(card)

        return shoe

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def simulate_action(self, player_cards: List[Rank], dealer_cards: List[Rank], action: str) -> Dict:

        payoffs = []
        for _ in range(self.num_sim):

            # 
            shoe = self._prepare_shoe_from_state(player_cards[:], dealer_cards[:])

            # 
            player_hand = Hand(player_cards[:])
            dealer_hand = Hand(dealer_cards[:] + [shoe.draw_one()])

            # 
            if action == 'STAND':
                final_player_hand = player_hand

            elif action == 'HIT':

                """
                # Hit
                player_hand.add_card(shoe.draw_one())

                # Settle
                dealer_play(shoe.clone(), dealer_hand)
                payoff = settle_hand(player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
                if player_hand.is_bust() or payoff > 0 or len(player_hand) >= 5:
                    payoffs.append(payoff)
                    continue

                # Hit
                player_hand.add_card(shoe.draw_one())

                # Settle
                dealer_play(shoe.clone(), dealer_hand)
                payoff = settle_hand(player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
                if player_hand.is_bust() or payoff > 0 or len(player_hand) >= 5:
                    payoffs.append(payoff)
                    continue
                    
                # Hit
                player_hand.add_card(shoe.draw_one())

                # Settle
                dealer_play(shoe.clone(), dealer_hand)
                payoff = settle_hand(player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
                if player_hand.is_bust() or payoff > 0 or len(player_hand) >= 5:
                    payoffs.append(payoff)
                    continue
                
                """
                while True:
                    # Hit
                    player_hand.add_card(shoe.draw_one())
                    # Settle
                    dealer_play(shoe.clone(), dealer_hand)
                    payoff = settle_hand(player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
                    if player_hand.is_bust() or payoff > 0:
                        payoffs.append(payoff)
                        break
                continue
            
            elif action == 'DOUBLE':
                player_hand.doubled = True
                player_hand.add_card(shoe.draw_one())
                final_player_hand = player_hand

            # 
            dealer_play(shoe, dealer_hand)

            # 
            payoff = settle_hand(final_player_hand, dealer_hand, blackjack_payout = self.blackjack_payout)
            payoffs.append(payoff)

        # 
        n = len(payoffs)
        mean = sum(payoffs) / n if n else 0.0
        wins = sum(1 for p in payoffs if p > 0)
        losses = sum(1 for p in payoffs if p < 0)
        pushes = n - wins - losses
        var = sum((p - mean) ** 2 for p in payoffs) / n if n else 0.0

        return {
            'action': action,
            'n': n,
            'ev': mean,
            'win_rate': wins / n,
            'loss_rate': losses / n,
            'push_rate': pushes / n,
            'stddev': math.sqrt(var)
        }

    """
    ====================================================================================================================
    
    ====================================================================================================================
    """
    def evaluate_all(self, player_cards: List[Rank], dealer_cards: List[Rank]) -> Dict:

        actions = ['STAND']

        if len(player_cards) < 5:
            actions.append('HIT')

        if len(player_cards) == 2:
            actions.append('DOUBLE')

        results = {}
        for action in actions:
            results[action] = self.simulate_action(player_cards[:], dealer_cards[:], action)

        # 
        best = max(results.items(), key = lambda kv: kv[1]['ev'])
        return {
            'player_hand': [card_str(r) for r in player_cards[:]],
            'dealer_hand': [card_str(r) for r in dealer_cards[:]],
            'results': results,
            'best_action': best[0],
            'best_ev': best[1]['ev']
        }
    

"""
========================================================================================================================
Main Function
========================================================================================================================
"""
if __name__ == "__main__":

    base_shoe = Shoe(num_decks = 6, rng = random.Random(12345))
    simulator = Simulator(base_shoe, num_sim = 10000, blackjack_payout = 1.5, rng_seed = 42)

    # Example states
    examples = [
        ([1, 6], [6]),
    ]

    for player, dealer in examples:

        print("=== State:", [card_str(x) for x in player], "vs", [card_str(x) for x in dealer])

        res = simulator.evaluate_all(player, dealer)
        for a, stats in res['results'].items():
            print(f"  {a}: ev={stats['ev']:.4f}, win={stats['win_rate']:.3f}, loss={stats['loss_rate']:.3f}, push={stats['push_rate']:.3f}")
        print("  Best:", res['best_action'], "EV=", res['best_ev'])
        print()