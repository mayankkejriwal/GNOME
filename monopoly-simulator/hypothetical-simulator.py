import initialize_game_elements
import background_agent_v1, json
import simple_decision_agent_1
import pprint
import copy
import diagnostics
from card_utility_actions import move_player_after_die_roll


def initialize_hypothetical_universe(current_gameboard, player_decision_agents):
    hypothetical_gameboard = copy.deepcopy(current_gameboard)
    player_name_obj = dict()
    for p in hypothetical_gameboard['players']:
        player_name_obj[p.player_name] = p
        # pprint.pprint(p.__dict__)
    for k,v in player_name_obj.items(): # k,v is player name, player object
        v.change_decision_agent(**player_decision_agents[k])
    # for p in hypothetical_gameboard['players']:
    #     pprint.pprint(p.__dict__) # we've run the check and verified the function pointer changes
    hypothetical_gameboard['seed'] = None # these should not be used, as it would be like looking into the future.
    hypothetical_gameboard['choice_function'] = None # you can set these with your own, or you could ignore these fields (our recommended option)
    return hypothetical_gameboard


def simulate_hypothetical_game(hypothetical_gameboard, die_roll_substitute):
    """
    If you want to simulate the game from a different 'starting' point than when you spawned the hypothetical universe,
    then you should make those changes (e.g., you could change the current_player, but you should do so safely i.e.
    make sure there aren't 'two' current players!) before calling simulate.
    :param hypothetical_gameboard:
    :param die_roll_substitute: This is a function that takes the list of Dice objects in the hypothetical gameboard as
    its argument. See expected function signature (and example) at the end of this file
    :return:
    """
    #TODO: all of these need to be modified to reflect hypothetical gameboard
    num_die_rolls = 0
    current_player_index = 0
    num_active_players = 4
    winner = None

    while num_active_players > 1:
        current_player = hypothetical_gameboard['players'][current_player_index]
        while current_player.status == 'lost':
            current_player_index += 1
            current_player_index = current_player_index % len(hypothetical_gameboard['players'])
            current_player = hypothetical_gameboard['players'][current_player_index]
        current_player.status = 'current_move'

        # pre-roll for current player + out-of-turn moves for everybody else,
        # till we get num_active_players skip turns in a row.

        skip_turn = 0
        if current_player.make_pre_roll_moves(hypothetical_gameboard) == 2: # 2 is the special skip-turn code
            skip_turn += 1
        out_of_turn_player_index = current_player_index + 1
        out_of_turn_count = 0
        while skip_turn != num_active_players and out_of_turn_count<=200:
            out_of_turn_count += 1
            # print 'checkpoint 1'
            out_of_turn_player = hypothetical_gameboard['players'][out_of_turn_player_index%len(hypothetical_gameboard['players'])]
            if out_of_turn_player.status == 'lost':
                out_of_turn_player_index += 1
                continue
            oot_code = out_of_turn_player.make_out_of_turn_moves(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(out_of_turn_player.make_out_of_turn_moves)
            params = dict()
            params['self']=out_of_turn_player
            params['current_gameboard']=hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(oot_code)

            if  oot_code == 2:
                skip_turn += 1
            else:
                skip_turn = 0
            out_of_turn_player_index += 1

        # now we roll the dice and get into the post_roll phase,
        # but only if we're not in jail.


        r = die_roll_substitute(hypothetical_gameboard['dies'])
        # add to game history
        hypothetical_gameboard['history']['function'].append(die_roll_substitute)
        params = dict()
        params['die_objects'] = hypothetical_gameboard['dies']
        hypothetical_gameboard['history']['param'].append(params)
        hypothetical_gameboard['history']['return'].append(r)

        num_die_rolls += 1
        hypothetical_gameboard['current_die_total'] = sum(r)
        print 'dies have come up ',str(r)
        if not current_player.currently_in_jail:
            check_for_go = True
            move_player_after_die_roll(current_player, sum(r), hypothetical_gameboard, check_for_go)
            # add to game history
            hypothetical_gameboard['history']['function'].append(move_player_after_die_roll)
            params = dict()
            params['player'] = current_player
            params['rel_move'] = sum(r)
            params['current_gameboard'] = hypothetical_gameboard
            params['check_for_go'] = check_for_go
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

            current_player.process_move_consequences(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.process_move_consequences)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

            # post-roll for current player. No out-of-turn moves allowed at this point.
            current_player.make_post_roll_moves(hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.make_post_roll_moves)
            params = dict()
            params['self'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(None)

        else:
            current_player.currently_in_jail = False # the player is only allowed to skip one turn (i.e. this one)

        if current_player.current_cash < 0:
            code = current_player.handle_negative_cash_balance(current_player, hypothetical_gameboard)
            # add to game history
            hypothetical_gameboard['history']['function'].append(current_player.handle_negative_cash_balance)
            params = dict()
            params['player'] = current_player
            params['current_gameboard'] = hypothetical_gameboard
            hypothetical_gameboard['history']['param'].append(params)
            hypothetical_gameboard['history']['return'].append(code)
            if code == -1 or current_player.current_cash < 0:
                current_player.begin_bankruptcy_proceedings(hypothetical_gameboard)
                # add to game history
                hypothetical_gameboard['history']['function'].append(current_player.begin_bankruptcy_proceedings)
                params = dict()
                params['self'] = current_player
                params['current_gameboard'] = hypothetical_gameboard
                hypothetical_gameboard['history']['param'].append(params)
                hypothetical_gameboard['history']['return'].append(None)

                num_active_players -= 1
                diagnostics.print_asset_owners(hypothetical_gameboard)
                diagnostics.print_player_cash_balances(hypothetical_gameboard)

                if num_active_players == 1:
                    for p in hypothetical_gameboard['players']:
                        if p.status != 'lost':
                            winner = p
                            p.status = 'won'
        else:
            current_player.status = 'waiting_for_move'

        current_player_index = (current_player_index+1)%len(hypothetical_gameboard['players'])


def test_gameboard(game_schema_file): # we use this file for trying out various things.

    player_decision_agents = dict()
    player_decision_agents['player_1'] = background_agent_v1.decision_agent_methods
    player_decision_agents['player_2'] = background_agent_v1.decision_agent_methods
    player_decision_agents['player_3'] = background_agent_v1.decision_agent_methods
    player_decision_agents['player_4'] = background_agent_v1.decision_agent_methods

    game_schema = json.load(open(game_schema_file, 'r'))
    game_elements_orig = initialize_game_elements.initialize_board(game_schema, player_decision_agents)
    # pprint.pprint(game_elements_orig,indent=4)

    player_decision_agents2 = dict()
    player_decision_agents2['player_1'] = simple_decision_agent_1.decision_agent_methods
    player_decision_agents2['player_2'] = simple_decision_agent_1.decision_agent_methods
    player_decision_agents2['player_3'] = simple_decision_agent_1.decision_agent_methods
    player_decision_agents2['player_4'] = background_agent_v1.decision_agent_methods

    initialize_hypothetical_universe(game_elements_orig,player_decision_agents2)

    # game_elements_copy = copy.deepcopy(game_elements_orig)
    # print 'printing copy'
    # pprint.pprint(game_elements_copy, indent=4)


def die_roll_substitute(die_objects):
    pass

test_gameboard('/Users/mayankkejriwal/git-projects/GNOME/monopoly_game_schema_v1-2.json') # use this to set up a gameboard and test various things
