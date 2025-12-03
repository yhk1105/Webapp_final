from Utils import *
from Game import *
from Simulator import Simulator
from Hand import Hand
from Shoe import Shoe

class Manager():
    def __init__(self, num_decks: int = 6, num_sim: int = 10000, threshold_ratio: float = 0.5) -> None:
        self.base = Shoe(num_decks=num_decks)
        self.shoe = self.base.clone()
        self.simu = Simulator(self.shoe, num_sim)

        # 仕様書に合わせて threshold を「残り枚数」で管理
        # 例: 4副(208枚)なら 104枚になったら終了
        self.initial_shoe_size = self.base.remaining()
        self.stop_threshold = int(self.initial_shoe_size * threshold_ratio)

        # 記録用変数の追加
        self.rounds_played = 0
        self.actions_taken = []  # 現在のラウンドのアクション履歴
        self.all_mistakes = []  # 整個訓練過程中的所有錯誤記錄
        self.current_round_mistakes = []  # 當前回合的錯誤記錄

    def start_round(self) -> None:
        # 自動シャッフルは削除（セッション終了はmain.pyで判定するため）

        self.player_hand = Hand([])
        self.dealer_hand = Hand([])
        self.actions_taken = []  # 履歴リセット
        self.current_round_mistakes = []  # 當前回合的錯誤記錄重置

        self.finish = False
        self.result = None
        self.final_player_value = None
        self.final_dealer_value = None

    def deal_initial(self):
        self.player_hand.add_card(self.shoe.draw_one())
        self.player_hand.add_card(self.shoe.draw_one())
        self.dealer_hand.add_card(self.shoe.draw_one())

        # ラウンド数をカウントアップ
        self.rounds_played += 1

    def get_recommendation(self) -> dict:
        return self.simu.evaluate_all(player_cards=self.player_hand.cards, dealer_cards=self.dealer_hand.cards)

    def player_hit(self) -> None:
        self.actions_taken.append("hit")  # 履歴に追加
        self.player_hand.add_card(self.shoe.draw_one())
        if self.player_hand.is_bust() or self.player_hand.best_value() >= 21 or len(self.player_hand) >= 5:
            self.finish_round()

    def player_stand(self) -> None:
        self.actions_taken.append("stand")  # 履歴に追加
        self.finish_round()

    def player_double(self) -> None:
        self.actions_taken.append("double")  # 履歴に追加
        self.player_hand.add_card(self.shoe.draw_one())
        self.player_hand.doubled = True
        self.finish_round()

    def finish_round(self) -> None:
        if self.finish:
            return
        self.finish = True
        dealer_play(self.shoe, self.dealer_hand)
        self.result = settle_hand(
            self.player_hand, self.dealer_hand, blackjack_payout=self.simu.blackjack_payout)
        self.final_player_value = self.player_hand.best_value()
        self.final_dealer_value = self.dealer_hand.best_value()

    # --- 新追加: 残りカードの統計（ヒント機能用） ---
    def get_shoe_composition(self) -> dict:
        # Utils.pyのcard_strを使って "A", "2"... "K" のキーに変換
        comp = {}
        for rank, count in self.shoe.counts.items():
            key = card_str(rank)
            comp[key] = comp.get(key, 0) + count
        return comp
