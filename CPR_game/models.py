from otree.api import *
from otree.api import Currency as c


class Constants(BaseConstants):
    name_in_url = "CPR_game"
    players_per_group = 4

    num_rounds = 8 + 1  # add 1 for the test round

    # include zero if you want feedback on the practice round

    # feedback_rounds = [0, 4, 9, 13, 17, 20] # actual feedback rounds

    feedback_rounds = [0, 1, 2, 3, 4, 5]  # for testing purposes

    num_recent_rounds_to_display = 4
    equal_endowment = 50
    unequal_endowments = [30, 70]

    initial_profit_rate = 1.4
    regeneration_rate = 100
    min_co2_level = 1000

    points_per_euro = 500

    extremely_unlikely_choices = [
        "Extremely unlikely",
        "Very unlikely",
        "Unlikely",
        "Neutral",
        "Likely",
        "Very likely",
        "Extremely likely",
        "Refusal",
        "Don’t know",
    ]

    strongly_agree_choices = [
        "Strongly in favor",
        "Somewhat in favor",
        "Neither in favor nor against",
        "Somewhat against",
        "Strongly against",
        "Refusal",
        "Don’t know",
    ]


class Subsession(BaseSubsession):
    def creating_session(self):
        # if self.round_number == Constants.num_rounds // 2 + 2 or self.round_number == 2:
        #     # shuffle players before the next game and after practice round
        #     self.group_randomly()
        for p in self.get_players():
            game_type = (
                self.session.config["game_order"][0]
                if self.round_number - 1 <= Constants.num_rounds // 2
                else self.session.config["game_order"][1]
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
        return (
            getattr(self.in_round(self.round_number - 1), attribute)
            if self.round_number > 1 and self.round_number - 1 <= Constants.num_rounds // 2
            else initial_value
        )

    def set_payoffs(self):
        players = self.get_players()

        self.total_emission = sum([p.emissions for p in players])

        previous_co2_level = self.get_previous_value("co2_level", Constants.min_co2_level)
        previous_profit_rate = self.get_previous_value("profit_rate", Constants.initial_profit_rate)

        for p in players:
            p.endowment = p.endowment if self.round_number > 1 else Constants.equal_endowment  # for the test round
            p.payoff = c(p.endowment - p.emissions + p.emissions * previous_profit_rate)

        self.co2_level = max(
            Constants.min_co2_level,
            previous_co2_level + self.total_emission - Constants.regeneration_rate,
        )
        self.profit_rate = round(previous_profit_rate * (Constants.min_co2_level / self.co2_level), 2)


class Player(BasePlayer):
    emissions = models.IntegerField(
        label="How many units of CO2 do you want to emit?",
        min=0,
    )
    endowment = models.IntegerField()

    def emissions_max(self):
        return self.endowment

    # Survey questions
    age = models.IntegerField(label="What is your age?")
    gender = models.StringField(
        choices=["Female", "Male", "Diverse"], widget=widgets.RadioSelect, label="What is your gender?"
    )
    country_of_origin = models.StringField(label="Which country are you from?")
    field_of_study = models.StringField(label="What is your field of study?")
    level_of_education = models.StringField(
        choices=["Completed High School", "Bachelor’s Degree", "Master’s Degree", "Professional or Doctorate", "Other"],
        widget=widgets.RadioSelect,
        label="What is your level of education?",
    )
    political_views_scale = models.IntegerField(
        choices=range(1, 11),
        widget=widgets.RadioSelectHorizontal,
        label="We have a scale that runs from left to right. Thinking of your own political views, where would you place these on the scale?",
    )
    known_people_pre_experiment = models.IntegerField(
        label="How many people who are present in the laboratory today did you know prior to the experiment?"
    )
    past_experiment_participation = models.IntegerField(
        label="How often did you participate in similar experiments in the past? (times)",
    )

    # Experiment comprehension and feedback questions.
    scenario_complexity = models.IntegerField(
        label="The experiment's scenario was too complex or difficult to comprehend",
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5],
    )
    tasks_understanding = models.IntegerField(
        label="I understood my tasks during the experiment",
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5],
    )
    imagined_situation_difficulty = models.IntegerField(
        label="It was challenging to try to imagine myself in the described situation",
        widget=widgets.RadioSelectHorizontal,
        choices=[1, 2, 3, 4, 5],
    )
    # Open-ended question for experiment issues
    issues_during_experiment = models.StringField(
        label="If you had some issues during the experiment please elaborate on those",
        initial="No issues",
    )

    # Climate change questions
    climate_change_belief = models.StringField(
        label="Do you think the world’s climate is changing?",
        widget=widgets.RadioSelect,
        choices=[
            "Definitely changing",
            "Probably changing",
            "Probably not changing",
            "Definitely not changing",
            "Refusal",
            "Don’t know",
        ],
    )
    thoughts_on_climate_change = models.StringField(
        label="How much have you thought about climate change before today?",
        widget=widgets.RadioSelect,
        choices=["Not at all", "Very little", "Some", "A lot", "A great deal", "Refusal", "Don’t know"],
    )

    cause_of_climate_change = models.StringField(
        label="Do you think that climate change is caused by natural processes, human activity, or both?",
        widget=widgets.RadioSelect,
        choices=[
            "Entirely by natural processes",
            "Mainly by natural processes",
            "About equally by natural processes and human activity",
            "Mainly by human activity",
            "Entirely by human activity",
            "I don’t think climate change is happening",
            "Refusal",
            "Don’t know",
        ],
    )

    personal_responsibility_to_reduce_climate_change = models.StringField(
        label="To what extent do you feel a personal responsibility to try to reduce climate change?",
        widget=widgets.RadioSelect,
        choices=["Not at all", "A great deal", "Refusal", "Don’t know"],
    )

    worry_about_climate_change = models.StringField(
        label="How worried are you about climate change?",
        widget=widgets.RadioSelect,
        choices=[
            "Not at all worried",
            "Not very worried",
            "Somewhat worried",
            "Very worried",
            "Extremely worried",
            "Refusal",
            "Don’t know",
        ],
    )

    impact_of_climate_change = models.StringField(
        label="How good or bad do you think the impact of climate change will be on people across the world?",
        widget=widgets.RadioSelect,
        choices=[
            "Extremely bad",
            "Very bad",
            "Bad",
            "Neutral",
            "Good",
            "Very good",
            "Extremely good",
            "Refusal",
            "Don’t know",
        ],
    )

    likelihood_of_reducing_climate_change_by_limiting_emissions = models.StringField(
        label="Now imagine that large numbers of individuals limited their CO2 emissions. How likely do you think it is that this would reduce climate change?",
        widget=widgets.RadioSelect,
        choices=Constants.extremely_unlikely_choices,
    )

    likelihood_people_will_limit_emissions = models.StringField(
        label="How likely do you think it is that large numbers of individuals will actually limit their CO2 emissions to try to reduce climate change?",
        widget=widgets.RadioSelect,
        choices=Constants.extremely_unlikely_choices,
    )

    likelihood_governments_will_take_action = models.StringField(
        label="How likely do you think it is that governments in enough countries will take action that reduces CO2 emissions?",
        widget=widgets.RadioSelect,
        choices=Constants.extremely_unlikely_choices,
    )

    personal_impact_on_climate_change_by_limiting_emissions = models.StringField(
        label="How likely do you think it is that limiting your own CO2 emissions would help reduce climate change?",
        widget=widgets.RadioSelect,
        choices=Constants.extremely_unlikely_choices,
    )

    support_for_climate_policies_fossil_fuels = models.StringField(
        label="To what extent do you support or oppose the following policy: Increasing taxes on fossil fuels, such as oil, gas, and coal.",
        widget=widgets.RadioSelect,
        choices=Constants.strongly_agree_choices,
    )

    support_for_climate_policies_renewable_energy = models.StringField(
        label="To what extent do you support or oppose the following policy: Using public money to subsidize renewable energy such as wind and solar power.",
        widget=widgets.RadioSelect,
        choices=Constants.strongly_agree_choices,
    )

    support_for_climate_policies_energy_efficient_appliances = models.StringField(
        label="To what extent do you support or oppose the following policy: A law banning the sale of the least energy-efficient household appliances.",
        widget=widgets.RadioSelect,
        choices=Constants.strongly_agree_choices,
    )

    # Social preferences questionnaire

    income_differences_acceptable = models.StringField(
        label="Large differences in people’s incomes are acceptable to properly reward differences in talents and efforts.",
        widget=widgets.RadioSelect,
        choices=Constants.strongly_agree_choices,
    )

    government_reduce_income_differences = models.StringField(
        label="The government should take measures to reduce differences in income levels.",
        widget=widgets.RadioSelect,
        choices=Constants.strongly_agree_choices,
    )

    # Propensity to cooperate questionnaire
    propensity_to_cooperate_1 = models.IntegerField(
        label="I function better alone than when I collaborate with others.",
        widget=widgets.RadioSelectHorizontal,
        choices=range(1, 8),
    )

    propensity_to_cooperate_2 = models.IntegerField(
        label="I prefer when I have clear duties than when I collaborate with other people.",
        widget=widgets.RadioSelectHorizontal,
        choices=range(1, 8),
    )

    propensity_to_cooperate_3 = models.IntegerField(
        label="When someone approaches me on the street, my first reaction is caution.",
        widget=widgets.RadioSelectHorizontal,
        choices=range(1, 8),
    )
