from action_choices import *
import sys


class Player(object):
    def __init__(self, current_position, status, has_get_out_of_jail_community_chest_card, has_get_out_of_jail_chance_card,
                 current_cash, num_railroads_possessed, player_name, assets,full_color_sets_possessed, currently_in_jail,
                 num_utilities_possessed,
                 handle_negative_cash_balance, make_pre_roll_initial_move, make_pre_roll_continuing_move, # on this line and below, all variables are assigned to a method
                 make_out_of_turn_initial_move, make_out_of_turn_continuing_move,
                 make_post_roll_move, make_buy_property_decision, make_bid
                 ):
        self.current_position = current_position
        self.status = status
        self.has_get_out_of_jail_chance_card = has_get_out_of_jail_chance_card
        self.has_get_out_of_jail_community_chest_card = has_get_out_of_jail_community_chest_card
        self.current_cash = current_cash
        self.num_railroads_possessed = num_railroads_possessed
        self.player_name = player_name
        self.assets = assets
        self.full_color_sets_possessed = full_color_sets_possessed
        self.currently_in_jail = currently_in_jail
        self.num_utilities_possessed = num_utilities_possessed

        # method assignments
        self.handle_negative_cash_balance = handle_negative_cash_balance
        self.make_pre_roll_initial_move = make_pre_roll_initial_move
        self.make_pre_roll_continuing_move = make_pre_roll_continuing_move
        self.make_out_of_turn_initial_move = make_out_of_turn_initial_move
        self.make_out_of_turn_continuing_move = make_out_of_turn_continuing_move
        self.make_post_roll_move = make_post_roll_move
        self.make_buy_property_decision = make_buy_property_decision
        self.make_bid = make_bid

        # all of the variables below are assigned a default initial value, and do not need input arguments/game schema inputs
        self.num_total_houses = 0
        self.num_total_hotels = 0
        outstanding_property_offer = dict()
        outstanding_property_offer['from_player'] = None
        outstanding_property_offer['asset'] = None
        outstanding_property_offer['price'] = -1

        self.outstanding_property_offer = outstanding_property_offer
        self.is_property_offer_outstanding = False # only one property offer at a time can be considered

        self.mortgaged_assets = set()
        # self._current_dues = 0
        # self._dues_recipients = list() # we maintain a list, since sometimes (such as when we have to make payments to all other players)
                                       # there may be multiple recipients. The assumption is that if there is more than one element
                                       # in the list, _current_dues will be independently owed to each one of them.

    def begin_bankruptcy_proceedings(self):
        self.current_position = None
        self.status = 'lost'
        self.has_get_out_of_jail_chance_card = False
        self.has_get_out_of_jail_community_chest_card = False
        self.current_cash = 0
        self.discharge_assets_to_bank()
        self.currently_in_jail = False
        # self._current_dues = 0
        # self._dues_recipients = list()


    def discharge_assets_to_bank(self): # discharge assets to bank
        if self.assets:
            for asset in self.assets:
                asset.is_mortgaged = False
                if asset.loc_class == 'real_estate':
                    asset.owned_by = 'bank'
                    asset.num_houses = 0
                    asset.num_hotels = 0
                elif asset.loc_class == 'utility' or asset.loc_class == 'railroad':
                    asset.owned_by = 'bank'
                else:
                    print 'player owns asset that is not real estate, railroad or utility' # unnecessary, since an
                    # exception will be raised if is_mortgaged does not exist. But we like an extra check.
                    raise Exception
            self.num_railroads_possessed = 0 # now we formally discharge assets on the player's side
            self.assets = None
            self.full_color_sets_possessed = None
            self.num_utilities_possessed = 0
            self.mortgaged_assets = None

    # def handle_negative_cash_balance(self):
    #     decision_agent_1.handle_negative_cash_balance(self) # your strategy to handle this deficit
    #     if self.current_cash < 0:
    #         return -1
    #     else:
    #         return 1

    def process_move_consequences(self, current_gameboard):
        current_location = current_gameboard['location_sequence'][self.current_position]
        if current_location.loc_class == 'do_nothing':
            return
        elif current_location.loc_class == 'real_estate':
            if current_location.owned_by == 'bank':
                self.make_buy_property_decision(self, current_gameboard)
            elif current_location.is_mortgaged is True:
                return
            else:
                self.calculate_and_pay_rent_dues(current_gameboard, True)
        elif current_location.loc_class == 'tax':
                self.current_cash -= current_location.amount_due
        elif current_location.loc_class == 'railroad':
            if current_location.owned_by == 'bank':
                self.make_buy_property_decision(self, current_gameboard)
            elif current_location.is_mortgaged is True:
                return
            else:
                dues = current_location.calculate_railroad_dues()
                recipient = current_location.owned_by
                recipient.receive_cash(dues)
                self.current_cash -= dues
        elif current_location.loc_class == 'utility':
            if current_location.owned_by == 'bank':
                self.make_buy_property_decision(self, current_gameboard)
            elif current_location.is_mortgaged is True:
                return
            else:
                dues = current_location.calculate_utility_dues(current_gameboard['current_die_total'])
                recipient = current_location.owned_by
                recipient.receive_cash(dues)
                self.current_cash -= dues
        elif current_location.loc_class == 'action':
                current_location.perform_action(self, current_gameboard)


    def calculate_and_pay_rent_dues(self, current_gameboard, update=True):
        """
        current_gameboard is the current game_elements data structure.
        """
        location_sequence = current_gameboard['location_sequence']
        current_loc = location_sequence[self.current_position]
        rent = current_loc.calculate_rent()
        recipient = current_loc.owned_by
        recipient.receive_cash(rent)
        self.current_cash -= rent

    # def _update_dues_and_recipients(self, amount, recipients):
    #     self._current_dues = amount
    #     self._dues_recipients = recipients.copy() # do a shallow copy

    def receive_cash(self, amount):
        if amount < 0:
            print 'stealing detected. Terminating game.'
            raise Exception
        self.current_cash += amount

    # def pay_dues(self):
    #     if self._dues_recipients:
    #         for recipient in self._dues_recipients:
    #             recipient.receive_cash(self._current_dues)
    #             self.current_cash -= self._current_dues
    #         self._current_dues = 0
    #         self._dues_recipients = list()


    # all of the _allowable_ functions will always return a set of callable actions from action_choices
    # current_gameboard is the current game_elements data structure.
    def compute_allowable_out_of_turn_actions(self, current_gameboard):
        pass # to come

    def compute_allowable_pre_roll_actions(self, current_gameboard):
        pass # to come

    def compute_allowable_post_roll_actions(self, current_gameboard):
        pass # to come

    def make_pre_roll_moves(self, current_gameboard):
        action_to_execute = skip_turn
        parameters = dict()

        self.make_pre_roll_initial_move(self, current_gameboard, self.compute_allowable_pre_roll_actions(current_gameboard))

        action_flag = False  # when it turns true, it means we've attempted some action rather than skipping the turn.

        while True:  # currently, we set no limits on this; the assumption is that eventually the player will 'pass the baton'

            if action_to_execute != skip_turn:
                action_flag = True
                code = self._execute_action(action_to_execute, parameters)

                if action_to_execute == concluded_actions:
                    return 'concluded_actions'

                self.make_pre_roll_continuing_move(self, current_gameboard, self.compute_allowable_pre_roll_actions(current_gameboard))  # you have to decide what to do next if the action is not concluded_actions

            elif action_to_execute == skip_turn:

                if action_flag:
                    print 'You have already taken at least one action and cannot skip turn. To conclude turn, execute concluded_actions'
                    continue
                else:
                    return 'skipped_turn'

    def make_post_roll_moves(self, current_gameboard):
        action_to_execute = concluded_actions
        parameters = dict()

        self.make_post_roll_move(self, current_gameboard, self.compute_allowable_post_roll_actions(current_gameboard))

        while True:
            if action_to_execute == concluded_actions:
                code = self._execute_action(action_to_execute, parameters)
                return 'concluded_actions'
            else:
                self.make_post_roll_move(self, current_gameboard, self.compute_allowable_post_roll_actions(current_gameboard))

    def make_out_of_turn_moves(self, current_gameboard):
        action_to_execute = skip_turn
        parameters = dict()

        self.make_out_of_turn_initial_move(self, current_gameboard, self.compute_allowable_out_of_turn_actions(current_gameboard))

        action_flag = False # when it turns true, it means we've attempted some action rather than skipping the turn.

        while True: # currently, we set no limits on this; the assumption is that eventually the player will 'pass the baton'

            if action_to_execute != skip_turn:
                action_flag = True
                code = self._execute_action(action_to_execute, parameters)

                if action_to_execute == concluded_actions:
                    return 'concluded_actions'

                self.make_out_of_turn_continuing_move(self, current_gameboard, self.compute_allowable_out_of_turn_actions(current_gameboard)) # you have to decide what to do next if the action is not concluded_actions

            elif action_to_execute == skip_turn:

                if action_flag:
                    print 'You have already taken at least one action and cannot skip turn. To conclude turn, execute concluded_actions'
                    continue
                else:
                    return 'skipped_turn'


    def _execute_action(self, action_to_execute, parameters):
        """
        if the action successfully executes, a code of 1 will be returned. If it cannot execute, it will return code -1.
        The most obvious reason this might happens is because you chose an action that is not an allowable action in your
        situation (e.g., you may try to mortgage a property when you have no properties. In other words, you call an action
        that is not in the set returned by the correct compute_allowable_*_actions). It won't break the code. There may
        be cases when an action is allowable in principle but not in practice. For example, you try to buy a property
        when you don't have enough cash. We avoid dynamic checking of this kind when we compute allowable actions.
        :param action_to_execute: the the action to execute. It must be a function inside action_choices
        :param parameters: a dictionary of parameters. These will be unrolled inside the action to execute.
        :return:
        """
        if parameters:
            return action_to_execute(**parameters)
        else:
            return action_to_execute()





