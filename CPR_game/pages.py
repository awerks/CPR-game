from otree.api import Page, WaitPage
from .models import Constants


class IntroductionPage(Page):
    def is_displayed(self):
        # Show this page only on the first round
        return self.round_number == 1


class QuestionnairePage(Page):
    def is_displayed(self):
        return self.round_number == 1


class TestRoundEndPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class RolePage(Page):
    def is_displayed(self):
        return self.round_number == 2

    def vars_for_template(self):
        game_type = (
            self.player.participant.vars["game_order"][0]
            if self.round_number < Constants.num_rounds // 2
            else self.player.participant.vars["game_order"][1]
        )

        if game_type == "equal":
            endowment = 50
        else:
            if self.player.id_in_group <= 2:  # the first two players get a lower endowment
                endowment = min(Constants.unequal_endowments)
            else:
                endowment = max(Constants.unequal_endowments)
        return {
            "is_homogenous": self.player.participant.vars["game_order"][0] == "equal",
            "player_endownment": endowment,
            "other_players_endownment": 70 if endowment == 30 else 30,
        }


class TestRoundIntroPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class EmissionsDecisionPage(Page):
    form_model = "player"
    form_fields = ["emissions"]

    def get_timeout_seconds(self):
        return Constants.equal_endowment

    def is_displayed(self):
        return self.round_number <= Constants.num_rounds

    def vars_for_template(self):
        # if we are in the first half of the rounds, "game_number" should be 1, otherwise it should be 2
        game_number = 1 if self.round_number - 1 <= Constants.num_rounds // 2 else 2

        round_number = (self.round_number if game_number == 1 else self.round_number - Constants.num_rounds // 2) - 1

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

        total_group_profit_all_rounds = sum(
            p.payoff for player in self.group.get_players() for p in player.in_all_rounds()
        )
        total_group_emissions_all_rounds = sum(player_emissions_in_all_rounds[:-1] if self.round_number > 1 else [0])

        half_round = Constants.num_rounds // 2
        game_number = 1 if self.round_number - 1 <= half_round else 2

        first_round_to_display = max(
            (2 if game_number == 1 else half_round + 2),
            self.subsession.round_number - Constants.num_recent_rounds_to_display + 1,
        )

        if self.subsession.round_number == 1:  # test round
            first_round_to_display = 1

        table_data = []

        for round_number in range(first_round_to_display, self.subsession.round_number + 1):
            round_data = []
            total_group_emission = 0
            total_group_profit = 0
            next_round_profit_rate = self.player.group.in_round(round_number).profit_rate
            for player in players_in_all_rounds:
                endowment = player[round_number - 1].endowment
                emission = player[round_number - 1].emissions
                profit = player[round_number - 1].payoff
                round_data.append([endowment, emission, profit])
                total_group_emission += emission
                total_group_profit += profit
            table_data.append(
                (
                    round_number - 1 if game_number == 1 else round_number - 1 - half_round,
                    total_group_emission,
                    total_group_profit,
                    next_round_profit_rate,
                    round_data,
                )
            )

        return {
            "not_test_round": self.round_number > 1,
            "player_id": self.player.id_in_group,
            "table_data": table_data,
            "group_total_emission": self.player.group.total_emission,
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "player_profit": self.player.payoff,
            "next_round_profit_rate2": self.player.group.profit_rate,
        }

    def is_displayed(self):
        return (
            self.player.participant.vars["feedback_type"] == "immediate"
            or self.player.round_number - 1 in Constants.feedback_rounds
            if self.player.round_number <= Constants.num_rounds // 2
            else self.player.round_number - Constants.num_rounds // 2 in Constants.feedback_rounds
        )


class FirstGameSummaryPage(Page):
    def is_displayed(self):
        return self.round_number - 1 == Constants.num_rounds // 2

    def vars_for_template(self):
        players_in_group = self.player.group.get_players()
        players_in_all_rounds = [player.in_rounds(2, self.round_number) for player in players_in_group]

        total_group_emissions_all_rounds = sum(
            [player.emissions for round in players_in_all_rounds for player in round]
        )

        total_group_profit_all_rounds = sum([player.payoff for round in players_in_all_rounds for player in round])
        total_personal_profit = sum([player.payoff for player in self.player.in_rounds(2, self.round_number)])
        return {
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "total_personal_profit": total_personal_profit,
        }


class NextGamePage(Page):
    def is_displayed(self):
        return self.round_number - 1 == Constants.num_rounds // 2

    def vars_for_template(self):
        game_type = (
            self.player.participant.vars["game_order"][0]
            if self.round_number < Constants.num_rounds // 2
            else self.player.participant.vars["game_order"][1]
        )

        if game_type == "equal":
            endowment = 50
        else:
            if self.player.id_in_group <= 2:  # the first two players get a lower endowment
                endowment = min(Constants.unequal_endowments)
            else:
                endowment = max(Constants.unequal_endowments)
        return {
            "is_homogenous": self.player.participant.vars["game_order"][1] == "equal",
            "player_endownment": endowment,
            "other_players_endownment": 70 if endowment == 30 else 30,
        }


class NextGameWaitPage(WaitPage):
    pass


class EndPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        players_in_group = self.player.group.get_players()
        players_in_all_rounds = [player.in_rounds(2, self.round_number) for player in players_in_group]

        total_group_emissions_all_rounds = sum(
            [player.emissions for round in players_in_all_rounds for player in round]
        )

        total_group_profit_all_rounds = sum([player.payoff for round in players_in_all_rounds for player in round])
        total_personal_profit = sum([player.payoff for player in self.player.in_rounds(2, self.round_number)])
        return {
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "total_personal_profit": total_personal_profit,
        }


page_sequence = [
    IntroductionPage,
    QuestionnairePage,
    TestRoundIntroPage,
    RolePage,
    EmissionsDecisionPage,
    ResultsWaitPage,
    FeedbackPage,
    TestRoundEndPage,
    FirstGameSummaryPage,
    NextGamePage,
    NextGameWaitPage,
    EndPage,
]
