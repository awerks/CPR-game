from otree.api import *
from otree.api import Currency as c


class Constants(BaseConstants):
    name_in_url = "CPR_game"
    players_per_group = 4
    num_rounds = 8  # 2 games of 20 rounds each

    # feedback_rounds = [4, 9, 13, 17, 20]
    feedback_rounds = [1, 2, 3, 4, 5]

    equal_endowment = 50
    unequal_endowments = [30, 70]  # used for the unequal game

    initial_profit_rate = 1.4
    regeneration_rate = 100
    min_co2_level = 1000


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            for group in self.get_groups():
                for player in group.get_players():
                    if group.id_in_subsession % 2 == 0:
                        player.participant.vars["game_order"] = ["equal", "unequal"]
                        player.participant.vars["feedback_type"] = "immediate"
                    else:
                        player.participant.vars["game_order"] = ["unequal", "equal"]
                        player.participant.vars["feedback_type"] = "delayed"

        for p in self.get_players():
            game_type = (
                p.participant.vars["game_order"][0]
                if self.round_number <= Constants.num_rounds // 2
                else p.participant.vars["game_order"][1]
            )

            if game_type == "equal":
                p.endowment = Constants.equal_endowment
            else:
                if p.id_in_group <= 2:  # the first two players get a lower endowment
                    p.endowment = min(Constants.unequal_endowments)
                else:
                    p.endowment = max(Constants.unequal_endowments)


class Group(BaseGroup):
    total_emission = models.FloatField(initial=0)
    co2_level = models.FloatField()
    profit_rate = models.FloatField()

    def get_previous_value(self, attribute, initial_value):
        return getattr(self.in_round(self.round_number - 1), attribute) if self.round_number > 1 else initial_value

    def set_payoffs(self):
        players = self.get_players()
        self.total_emission = sum([p.emissions for p in players])

        previous_co2_level = self.get_previous_value("co2_level", Constants.min_co2_level)
        previous_profit_rate = self.get_previous_value("profit_rate", Constants.initial_profit_rate)

        for p in players:
            p.payoff = c(p.endowment - p.emissions + p.emissions * previous_profit_rate)

        self.co2_level = max(
            Constants.min_co2_level,
            previous_co2_level + self.total_emission - Constants.regeneration_rate,
        )
        self.profit_rate = round(previous_profit_rate * (Constants.min_co2_level / self.co2_level), 2)


class Player(BasePlayer):
    emissions = models.FloatField(
        label="How many units of CO2 do you want to emit?",
    )
    endowment = models.IntegerField()

    def emissions_max(self):
        return self.endowment
