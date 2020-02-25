from dice import Dice
from novelty_functions import *
import copy
import sys

"""
The novelty methods in here should be called after an initial game board has been set up, but before simulate has
been called within gameplay. It is unsafe to introduce novelty in the middle of a 'game'. The novelties should
only operate at the tournament level and be introduced prior to game instance simulation.

This generator should be used for the Month 6 SAIL-ON evals.

The consistency_check function should be called after all novelties have been generated. If the function finds problems
it will print them out and then raise an Exception. Otherwise, you're good to start using the updated gameboard
to start playing the game.
"""

class Novelty(object):
    def __init__(self):
        pass


class ClassNovelty(Novelty):
    def __init__(self):
        super(ClassNovelty, self).__init__()

class RepresentationNovelty(Novelty):
    def __init__(self):
        super(RepresentationNovelty, self).__init__()


class SpatialRepresentationNovelty(RepresentationNovelty):
    def __init__(self):
        super(SpatialRepresentationNovelty, self).__init__()

    def location_sequence_novelty(self, current_gameboard, new_location_sequence):
        pass

class NumberClassNovelty(ClassNovelty):
    def __init__(self):
        super( NumberClassNovelty, self).__init__()

    def die_novelty(self, current_gameboard, die_count, die_state_vector):
        """
        Introduce sub-level novelty (class/number) for dice.
        :param current_gameboard: The current gameboard dict. Note that this dict will be modified.
        :param die_count: number of dice
        :param die_state_vector: A list of lists, where each inner list represents the die state for each dice
        :return: None
        """
        if len(die_state_vector) != die_count:
            print 'die states are unequal to die count. Raising exception...'
            raise Exception

        current_gameboard['dies'] = list() # wipe out what was there before.
        for i in range(0, die_count):
            current_gameboard['dies'].append(Dice(die_state_vector[i]))

    def card_novelty(self, current_gameboard, community_chest_cards_num, chance_cards_num):
        """

        :param current_gameboard: current_gameboard['chance_cards'] and current_gameboard['community_chest_cards'] will
        both be modified. However, current_gameboard['chance_card_objects'] and current_gameboard['community_chest_card_objects']
        will stay as it is.
        :param community_chest_cards_num: a dict where the key is the card's name, and the value is the num. You must pass in the
        complete description (of the cards and nums), not just
        cards for which you're changing the num value, since we will re-initialize and populate current_gameboard['community_chest_cards']
        and current_gameboard['chance_cards'] from scratch.
        :param chance_cards_num: a dict where the key is the card's name, and the value is the num
        :return: None
        """
        current_gameboard['community_chest_cards'] = list()
        for card_name, num in community_chest_cards_num.items():
            card = current_gameboard['community_chest_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['community_chest_cards'].append(copy.deepcopy(card))

        current_gameboard['chance_cards'] = list()
        for card_name, num in chance_cards_num.items():
            card = current_gameboard['chance_card_objects'][card_name]
            for i in range(0, num):
                current_gameboard['chance_cards'].append(copy.deepcopy(card))


class TypeClassNovelty(ClassNovelty):
    def __init__(self):
        super(TypeClassNovelty, self).__init__()

    def die_novelty(self, current_gameboard, die_state_distribution_vector, die_type_vector):
        """
        Introduce sub-level novelty (class/type) for dice.
        :param current_gameboard: The current gameboard dict. Note that this dict will be modified.
        :param die_state_distribution_vector: list of die_state_distributions
        :param die_type_vector: list of die_types
        :return: None
        """
        if len(die_state_distribution_vector) != len(die_type_vector):
            print 'die state distributions are unequal to die types. Raising exception...'
            raise Exception
        if len(die_state_distribution_vector) != len(current_gameboard['dies']):
            print 'die state distributions and die types are unequal to number of dies in board. Raising exception...'
            raise Exception

        for i in range(0, len(die_state_distribution_vector)):
            current_gameboard['dies'][i].die_state_distribution = die_state_distribution_vector[i]
            current_gameboard['dies'][i].die_type = die_type_vector[i]

    def card_novelty(self, current_gameboard, community_chest_cards_contingency, chance_cards_contingency):
        """

        :param current_gameboard: current_gameboard['chance_cards'] and current_gameboard['community_chest_cards'] will
        both be modified. However, current_gameboard['chance_card_objects'] and current_gameboard['community_chest_card_objects']
        will stay as it is.
        :param community_chest_cards_contingency: a dict where the key is the card's name, and the value is a contingency function
        from novelty_functions. If there is no change in a card's contingency function, do not include it in this dict.
        :param chance_cards_contingency: a dict where the key is the card's name, and the value is a contingency function
        from novelty_functions. If there is no change in a card's contingency function, do not include it in this dict.
        :return: None
        """
        for card in current_gameboard['chance_cards']:
            if card.name in chance_cards_contingency and hasattr(card, 'contingency'):
                card.contingency = getattr(sys.modules[__name__], chance_cards_contingency[card.name])

        for card in current_gameboard['community_chest_cards']:
            if card.name in community_chest_cards_contingency and hasattr(card, 'contingency'):
                card.contingency = getattr(sys.modules[__name__], community_chest_cards_contingency[card.name])

