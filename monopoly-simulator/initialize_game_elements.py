import location
from dice import Dice
from bank import Bank
from card_utility_actions import * # functions from this module will be used in reflections in initialize_board, and excluding this import will lead to run-time errors
import sys
from player import Player
import card


def initialize_board(game_schema, player_decision_agents):

    game_elements = dict()

    # Step 0: initialize bank
    game_elements['bank'] = Bank()

    # Step 1: set locations
    location_objects = dict()
    railroad_positions = list()
    utility_positions = list()
    for l in game_schema['locations']['location_states']:

        if l['loc_class'] == 'action':
            action_args = l.copy()
            action_args['perform_action'] = getattr(sys.modules[__name__], l['perform_action'])
            location_objects[l['name']]=location.ActionLocation(**action_args)

        elif l['loc_class'] == 'do_nothing':
            location_objects[l['name']]=location.DoNothingLocation(**l)

        elif l['loc_class'] == 'real_estate':
            real_estate_args = l.copy()
            real_estate_args['owned_by'] = 'bank'
            real_estate_args['num_houses'] = 0
            real_estate_args['num_hotels'] = 0
            location_objects[l['name']] = location.RealEstateLocation(**real_estate_args)

        elif l['loc_class'] == 'tax':
            location_objects[l['name']] = location.TaxLocation(**l)

        elif l['loc_class'] == 'railroad':
            railroad_args = l.copy()
            railroad_args['owned_by'] = 'bank'
            location_objects[l['name']] = location.RailroadLocation(**railroad_args)

        elif l['loc_class'] == 'utility':
            utility_args = l.copy()
            utility_args['owned_by'] = 'bank'
            location_objects[l['name']] = location.UtilityLocation(**utility_args)

        else:
            print 'encountered unexpected location class: ',l['loc_class']
            raise Exception

    location_sequence = list()
    for i in range(0, len(game_schema['location_sequence'])):
        location_sequence.append(location_objects[game_schema['location_sequence'][i]])
        if location_objects[game_schema['location_sequence'][i]].loc_class == 'railroad':
            railroad_positions.append(i)
        elif location_objects[game_schema['location_sequence'][i]].loc_class == 'utility':
            utility_positions.append(i)
        elif location_objects[game_schema['location_sequence'][i]].name == 'In Jail/Just Visiting':
            game_elements['jail_position'] = i

    game_elements['railroad_positions'] = railroad_positions
    game_elements['utility_positions'] = utility_positions


    if len(location_sequence) != game_schema['locations']['location_count']:
        print 'location count: ',str(game_schema['locations']['location_count']),', length of location sequence: ',
        str(len(location_sequence)), ' are unequal.'
        raise Exception

    if location_sequence[game_schema['go_position']].name != 'Go':
        print 'go positions are not aligned'
        raise Exception
    else:
        game_elements['go_position'] = game_schema['go_position']
        game_elements['go_increment'] = game_schema['go_increment']

    game_elements['location_objects'] = location_objects
    game_elements['location_sequence'] = location_sequence

    color_assets = dict() # we will not put anything in here that does not have a color.
    for o in location_sequence:
        if o.color and o.color in game_schema['players']['player_states']['full_color_sets_possessed'][0]:
            if o.color not in color_assets:
                color_assets[o.color] = set()
            color_assets[o.color].add(o)

    game_elements['color_assets'] = color_assets

    # Step 2: set dice
    if len(game_schema['die']['die_state']) != game_schema['die']['die_count']:
        print 'dice count and length of dice states vector are inconsistent'
        raise Exception
    die_count = game_schema['die']['die_count']
    die_objects = list()
    for i in range(0, die_count):
        die_objects.append(Dice(game_schema['die']['die_state'][i]))

    game_elements['dies'] = die_objects
    game_elements['current_die_total'] = 0

    # Step 3: set cards
    community_chest_cards = set()
    chance_cards = set()

    community_chest_card_objects = dict()
    chance_card_objects = dict()
    card_obj = None
    for specific_card in game_schema['cards']['community_chest']['card_states']:

        if specific_card['card_type'] == 'movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['destination'] = location_objects[specific_card['destination']]
                card_obj = card.MovementCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.ContingentMovementCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_bank' or specific_card['card_type'] == 'negative_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.CashFromBankCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['contingency'] = getattr(sys.modules[__name__], specific_card['contingency'])
                card_obj = card.ContingentCashFromBankCard(**card_args)
                community_chest_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_players' or card['card_type'] == 'negative_cash_from_players':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.CashFromPlayersCard(**card_args)
                community_chest_cards.add(card_obj)

        community_chest_card_objects[card_obj.name] = card_obj

    if len(community_chest_cards) != game_schema['cards']['community_chest']['card_count']:
        print 'community chest card count and number of items in community chest card set are inconsistent'

    card_obj = None
    for specific_card in game_schema['cards']['chance']['card_states']:

        if specific_card['card_type'] == 'movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['destination'] = location_objects[specific_card['destination']]
                card_obj = card.MovementCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'movement_payment':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.MovementPaymentCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_movement':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.ContingentMovementCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'movement_relative':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.MovementRelativeCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_bank' or specific_card['card_type'] == 'negative_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.CashFromBankCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'contingent_cash_from_bank':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_args['contingency'] = getattr(sys.modules[__name__], specific_card['contingency'])
                card_obj = card.ContingentCashFromBankCard(**card_args)
                chance_cards.add(card_obj)

        elif specific_card['card_type'] == 'positive_cash_from_players' or specific_card['card_type'] == 'negative_cash_from_players':
            for i in range(0, specific_card['num']):
                card_args = specific_card.copy()
                del card_args['num']
                card_args['action'] = getattr(sys.modules[__name__], specific_card['action'])
                card_obj = card.CashFromPlayersCard(**card_args)
                chance_cards.add(card_obj)

        chance_card_objects[card_obj.name] = card_obj

    if len(chance_cards) != game_schema['cards']['chance']['card_count']:
        print 'chance card count and number of items in chance card set are inconsistent'

    game_elements['chance_cards'] = chance_cards
    game_elements['community_chest_cards'] = community_chest_cards
    game_elements['chance_card_objects'] = chance_card_objects
    game_elements['community_chest_card_objects'] = community_chest_card_objects

    # Step 4: set players
    players = list()
    player_dict = game_schema['players']['player_states']

    player_args = player_dict.copy()
    player_args['status'] = 'waiting_for_move'
    player_args['current_position'] = game_schema['go_position']
    player_args['has_get_out_of_jail_chance_card'] = False
    player_args['has_get_out_of_jail_community_chest_card'] = False
    player_args['current_cash'] = player_dict['starting_cash']
    player_args['num_railroads_possessed'] = 0
    player_args['num_utilities_possessed'] = 0
    player_args['full_color_sets_possessed'] = set()
    player_args['assets'] = set()
    player_args['currently_in_jail'] = False
    del player_args['starting_cash']
    for player in player_dict['player_name']:
        player_args['player_name'] = player
        for k,v in player_decision_agents[player].items():
            player_args[k] = v
        players.append(Player(**player_args))

    game_elements['players'] = players

    return game_elements