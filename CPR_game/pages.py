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
            self.session.config["game_order"][0]
            if self.round_number < Constants.num_rounds // 2
            else self.session.config["game_order"][1]
        )

        if game_type == "equal":
            endowment = 50
        else:
            if self.player.id_in_group <= 2:  # the first two players get a lower endowment
                endowment = min(Constants.unequal_endowments)
            else:
                endowment = max(Constants.unequal_endowments)
        return {
            "is_homogenous": self.session.config["game_order"][0] == "equal",
            "player_endownment": endowment,
            "other_players_endownment": 70 if endowment == 30 else 30,
        }

    def before_next_page(self):
        self.subsession.group_randomly()


class TestRoundIntroPage(Page):
    def is_displayed(self):
        return self.round_number == 1


class EmissionsDecisionPage(Page):
    form_model = "player"
    form_fields = ["emissions"]

    # def get_timeout_seconds(self):
    #     return Constants.equal_endowment

    def is_displayed(self):
        return self.round_number <= Constants.num_rounds

    def vars_for_template(self):
        # if we are in the first half of the rounds, "game_number" should be 1, otherwise it should be 2
        game_number = 1 if self.round_number - 1 <= Constants.num_rounds // 2 else 2

        round_number = (self.round_number if game_number == 1 else self.round_number - Constants.num_rounds // 2) - 1

        endowment = self.player.endowment if self.round_number > 1 else Constants.equal_endowment
        feedback_type = self.session.config["feedback_type"] if self.round_number > 1 else "immediate"
        game_order = self.session.config["game_order"] if self.round_number > 1 else ["equal", "unequal"]
        return {
            "game_number": game_number,
            "round_number": round_number,
            "endowment": endowment,
            "game_order": game_order,
            "feedback_type": feedback_type,
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
            co2_level = Constants.min_co2_level

            for player in players_in_all_rounds:
                endowment = player[round_number - 1].endowment
                emission = player[round_number - 1].emissions
                profit = player[round_number - 1].payoff
                round_data.append([endowment, emission, profit])
                total_group_emission += emission
                total_group_profit += profit

            co2_level += total_group_emission - Constants.regeneration_rate
            co2_level = max(Constants.min_co2_level, co2_level)
            next_round_profit_rate = round(Constants.initial_profit_rate * (Constants.min_co2_level / co2_level), 2)
            table_data.append(
                (
                    round_number - 1 if game_number == 1 else round_number - 1 - half_round,
                    total_group_emission,
                    total_group_profit,
                    next_round_profit_rate,
                    co2_level,
                    round_data,
                )
            )
        # print(self.player.group.get_previous_value("co2_level", Constants.min_co2_level))
        # print((self.player.group.total_emission))
        return {
            "not_test_round": self.round_number > 1,
            "player_id": self.player.id_in_group,
            "table_data": table_data,
            "co2_level": co2_level,
            "group_total_emission": self.player.group.total_emission,
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "player_profit": self.player.payoff,
            "next_round_profit_rate2": self.player.group.profit_rate,
        }

    def is_displayed(self):
        return (
            self.session.config["feedback_type"] == "immediate"
            or self.player.round_number - 1 in Constants.feedback_rounds
            if self.player.round_number - 1 <= Constants.num_rounds // 2
            else self.player.round_number - 1 - Constants.num_rounds // 2 in Constants.feedback_rounds
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
            self.session.config["game_order"][0]
            if self.round_number < Constants.num_rounds // 2
            else self.session.config["game_order"][1]
        )

        if game_type == "equal":
            endowment = 50
        else:
            if self.player.id_in_group <= 2:  # the first two players get a lower endowment
                endowment = min(Constants.unequal_endowments)
            else:
                endowment = max(Constants.unequal_endowments)
        return {
            "is_homogenous": self.session.config["game_order"][1] == "equal",
            "player_endownment": endowment,
            "other_players_endownment": 70 if endowment == 30 else 30,
        }


class NextGameWaitPage(WaitPage):
    def before_next_page(self):
        self.group_randomly()


class EndGamePage(Page):
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
        payoff = float(total_personal_profit) / Constants.points_per_euro
        return {
            "total_group_emissions_all_rounds": total_group_emissions_all_rounds,
            "total_group_profit_all_rounds": total_group_profit_all_rounds,
            "total_personal_profit": total_personal_profit,
            "payoff": payoff,
        }


class DemographicsPage(Page):
    form_model = "player"
    form_fields = [
        "age",
        "gender",
        "country_of_origin",
        "field_of_study",
        "level_of_education",
        "political_views_scale",
    ]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class ExperimentQuestionsPage(Page):
    form_model = "player"
    form_fields = [
        "known_people_pre_experiment",
        "past_experiment_participation",
        "scenario_complexity",
        "tasks_understanding",
        "imagined_situation_difficulty",
        "issues_during_experiment",
    ]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class ClimateChangePage(Page):
    form_model = "player"
    form_fields = [
        "climate_change_belief",
        "thoughts_on_climate_change",
        "cause_of_climate_change",
        "personal_responsibility_to_reduce_climate_change",
        "worry_about_climate_change",
        "impact_of_climate_change",
        "likelihood_of_reducing_climate_change_by_limiting_emissions",
        "likelihood_people_will_limit_emissions",
        "likelihood_governments_will_take_action",
        "personal_impact_on_climate_change_by_limiting_emissions",
        "support_for_climate_policies_fossil_fuels",
        "support_for_climate_policies_renewable_energy",
        "support_for_climate_policies_energy_efficient_appliances",
    ]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class SocialPreferences(Page):
    form_model = "player"
    form_fields = ["income_differences_acceptable", "government_reduce_income_differences"]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class PropensityToCooperate(Page):
    form_model = "player"
    form_fields = [
        "propensity_to_cooperate_1",
        "propensity_to_cooperate_2",
        "propensity_to_cooperate_3",
    ]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class SurveyEndPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        total_personal_profit = sum([player.payoff for player in self.player.in_rounds(2, self.round_number)])
        payoff = float(total_personal_profit) / Constants.points_per_euro
        return {
            "payoff": payoff,
            "total_personal_profit": total_personal_profit,
        }


page_sequence = [
    # IntroductionPage,
    # QuestionnairePage,
    TestRoundIntroPage,
    RolePage,
    EmissionsDecisionPage,
    ResultsWaitPage,
    FeedbackPage,
    TestRoundEndPage,
    FirstGameSummaryPage,
    NextGamePage,
    NextGameWaitPage,
    EndGamePage,
    ClimateChangePage,
    SocialPreferences,
    PropensityToCooperate,
    ExperimentQuestionsPage,
    DemographicsPage,
    SurveyEndPage,
]
