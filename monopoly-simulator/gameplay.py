import initialize_game_elements
from action_choices import roll_die
import numpy as np
from card_utility_actions import move_player_after_die_roll
from simple_decision_agent import decision_agent_methods # this is where you should import your own decision agent methods dict
import json

def simulate_game_instance(game_elements, np_seed=2):

    np.random.seed(np_seed)
    np.random.shuffle(game_elements['players'])
    game_elements['seed'] = np_seed
    game_elements['choice_function'] = np.random.choice
    print 'players will play in the following order: ','->'.join([p.player_name for p in game_elements['players']])
    print 'Beginning play. Rolling first die...'
    current_player_index = 0
    num_active_players = 4

    while num_active_players > 1:
        current_player = game_elements['players'][current_player_index]
        while current_player.status == 'lost':
            current_player_index += 1
            current_player = game_elements['players'][current_player_index]
        current_player.status = 'current_move'

        # pre-roll for current player + out-of-turn moves for everybody else,
        # till we get num_active_players skip turns in a row.

        skip_turn = 0
        if current_player.make_pre_roll_moves(game_elements) == 2: # 2 is the special skip-turn code
            skip_turn += 1
        out_of_turn_player_index = current_player_index + 1
        while skip_turn != num_active_players:
            print 'checkpoint 1'
            out_of_turn_player = game_elements['players'][out_of_turn_player_index%len(game_elements['players'])]
            if out_of_turn_player.status == 'lost':
                out_of_turn_player_index += 1
                continue
            if out_of_turn_player.make_out_of_turn_moves(game_elements) == 2:
                skip_turn += 1
            else:
                skip_turn = 0
            out_of_turn_player_index += 1

        # now we roll the dice and get into the post_roll phase,
        # but only if we're not in jail.

        r = roll_die(game_elements['dies'], np.random.choice)
        game_elements['current_die_total'] = sum(r)
        # print sum(r)
        if not current_player.currently_in_jail:
            move_player_after_die_roll(current_player, sum(r), game_elements, check_for_go=True)
            current_player.process_move_consequences(game_elements)
            print 'checkpoint 2'
            # post-roll for current player. No out-of-turn moves allowed at this point.
            current_player.make_post_roll_moves(game_elements)

        else:
            current_player.currently_in_jail = False # the player is only allowed to skip one turn (i.e. this one)

        print 'checkpoint 3'

        # check for bankruptcy

        if current_player.current_cash < 0:
            code = current_player.handle_negative_cash_balance(current_player, game_elements)
            if code == -1 or current_player.current_cash < 0:
                current_player.begin_bankruptcy_proceedings()
                num_active_players -= 1
        else:
            current_player.status = 'waiting_for_move'

        current_player_index += 1
        current_player_index = current_player_index%len(game_elements['players'])

        cash_balance = list()
        for p in game_elements['players']:
            cash_balance.append(str(p.current_cash))
        print ' '.join(cash_balance)

        if int(cash_balance[0]) > 20000:
            print cash_balance[0]
            break


def set_up_board(game_schema_file_path, player_decision_agents):
    game_schema = json.load(open(game_schema_file_path, 'r'))
    return initialize_game_elements.initialize_board(game_schema, player_decision_agents)


player_decision_agents = dict()
for p in ['player_1','player_2','player_3','player_4']:
    player_decision_agents[p] = decision_agent_methods
game_elements = set_up_board('/Users/mayankkejriwal/git-projects/GNOME/monopoly_game_schema_v1-2.json',
                             player_decision_agents)
simulate_game_instance(game_elements)