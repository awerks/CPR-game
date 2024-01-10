from otree.api import Page, WaitPage
from .models import Constants


class IntroductionPage(Page):
    def is_displayed(self):
        # Show this page only on the first round
        return self.round_number == 1


class EmissionsDecisionPage(Page):
    form_model = "player"
    form_fields = ["emissions"]

    def is_displayed(self):
        return self.round_number <= Constants.num_rounds

    def vars_for_template(self):
        # if we are in the first half of the rounds, "game_number" should be 1, otherwise it should be 2
        game_number = 1 if self.round_number <= Constants.num_rounds // 2 else 2

        round_number = self.round_number if game_number == 1 else self.round_number - Constants.num_rounds // 2

        return {
            "game_number": game_number,
            "round_number": round_number,
            "endowment": self.player.endowment,
            "game_order": str(self.player.participant.vars["game_order"]),
            "feedback_type": self.player.participant.vars["feedback_type"],
        }


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class FeedbackPage(Page):
    def vars_for_template(self):
        players_in_group = self.player.group.get_players()

        players_in_all_rounds = [player.in_all_rounds() for player in players_in_group]

        player_emissions_in_all_rounds = [player.emissions for round in players_in_all_rounds for player in round]

        player_profits_in_all_rounds = [player.payoff for round in players_in_all_rounds for player in round]

        total_rounds = self.subsession.round_number
        players_per_group = Constants.players_per_group

        # Organize data by round
        game_1 = []
        game_2 = []
        for round_index in range(total_rounds):
            round_data = []
            for player_index in range(players_per_group):
                emissions_index = round_index + player_index * total_rounds
                profits_index = round_index + player_index * total_rounds
                round_data.append(
                    (
                        player_emissions_in_all_rounds[emissions_index],
                        player_profits_in_all_rounds[profits_index],
                    )
                )
            game_1.append(round_data)

        # Total group emissions for all previous rounds
        total_group_emissions_all_rounds = sum(player_emissions_in_all_rounds[:-1] if self.round_number > 1 else [0])

        # Total profit for the group (previous + current round)
        total_group_profit_all_rounds = sum(
            p.payoff for player in self.group.get_players() for p in player.in_all_rounds()
        )

        if total_rounds > Constants.num_rounds // 2:
            game_2 = game_1[Constants.num_rounds // 2 :]

        game_1 = game_1[: Constants.num_rounds // 2]

        return {
            "game_1": game_1,
            "game_2": game_2,
            "group_total_emission": self.player.group.total_emission,
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "player_profit": self.player.payoff,
            "next_round_profit_rate": self.player.group.profit_rate,
        }

    def is_displayed(self):
        return (
            self.player.participant.vars["feedback_type"] == "immediate"
            or self.player.round_number in Constants.feedback_rounds
            if self.player.round_number <= Constants.num_rounds // 2
            else self.player.round_number - Constants.num_rounds // 2 in Constants.feedback_rounds
        )
        print("something")


class NextGameWaitPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds // 2


class EndPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    IntroductionPage,
    EmissionsDecisionPage,
    ResultsWaitPage,
    FeedbackPage,
    NextGameWaitPage,
    EndPage,
]
