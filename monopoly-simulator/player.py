from action_choices import *


class Player(object):
    def __init__(self, current_position, status, has_get_out_of_jail_community_chest_card, has_get_out_of_jail_chance_card,
                 current_cash, num_railroads_possessed, player_name, assets,full_color_sets_possessed, currently_in_jail,
                 num_utilities_possessed,
                 handle_negative_cash_balance, make_pre_roll_move, # on this line and below, all variables are assigned to a method
                 make_out_of_turn_move,
                 make_post_roll_move, make_buy_property_decision, make_bid
                 ):
        self.current_position = current_position # this is an integer. Use 'location_sequence' in the game schema to map position into an actual location
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
        self.make_pre_roll_move = make_pre_roll_move
        self.make_out_of_turn_move = make_out_of_turn_move
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

        self._option_to_buy = False # this option will turn true when  the player lands on a property that could be bought.
        # We always set it to false again at the end of the post_roll phase.

    def begin_bankruptcy_proceedings(self):
        self.current_position = None
        self.status = 'lost'
        self.has_get_out_of_jail_chance_card = False # if this is true, we need to place the card back in the pack
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
                self._option_to_buy = True
                return
            elif current_location.is_mortgaged is True:
                return
            else:
                self.calculate_and_pay_rent_dues(current_gameboard, True)
                return
        elif current_location.loc_class == 'tax':
                self.current_cash -= current_location.amount_due
                return
        elif current_location.loc_class == 'railroad':
            if current_location.owned_by == 'bank':
                self._option_to_buy = True
                return
            elif current_location.is_mortgaged is True:
                return
            else:
                dues = current_location.calculate_railroad_dues()
                recipient = current_location.owned_by
                recipient.receive_cash(dues)
                self.current_cash -= dues
                return
        elif current_location.loc_class == 'utility':
            if current_location.owned_by == 'bank':
                self._option_to_buy = True
                return
            elif current_location.is_mortgaged is True:
                return
            else:
                dues = current_location.calculate_utility_dues(current_gameboard['current_die_total'])
                recipient = current_location.owned_by
                recipient.receive_cash(dues)
                self.current_cash -= dues
                return
        elif current_location.loc_class == 'action':
                current_location.perform_action(self, current_gameboard)
                return
        else:
            print 'unidentified location type'
            raise Exception


    def _own_or_auction(self, current_gameboard, asset):
        dec = self.make_buy_property_decision(self, current_gameboard, asset)
        if dec:
            asset.update_asset_owner(self, current_gameboard)
            return
        else:
            index_current_player = current_gameboard['players'].index(self) # in players, find the index of the current player
            starting_player_index = (index_current_player+1)%len(current_gameboard['players']) # the next player's index. this player will start the auction
            return current_gameboard['bank'].auction(starting_player_index, current_gameboard, asset)


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
            print self.player_name
            print amount
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


    def compute_allowable_pre_roll_actions(self, current_gameboard):
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.is_property_offer_outstanding is True:
            allowable_actions.add(accept_sell_property_offer)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            allowable_actions.add(make_sell_property_offer)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if len(self.mortgaged_assets) > 0:
            allowable_actions.add(free_mortgage)

        if self.has_get_out_of_jail_chance_card or self.has_get_out_of_jail_community_chest_card:
            allowable_actions.add(use_get_out_of_jail_card)

        if self.currently_in_jail:
            allowable_actions.add(pay_jail_fine)

        if len(self.full_color_sets_possessed) > 0:
            allowable_actions.add(improve_property) # there is a chance this is not dynamically allowable because you've improved a property to its maximum.
            # However, you have to make this check in your decision agent.

        return allowable_actions


    def compute_allowable_out_of_turn_actions(self, current_gameboard):
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.is_property_offer_outstanding is True:
            allowable_actions.add(accept_sell_property_offer)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            allowable_actions.add(make_sell_property_offer)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if len(self.mortgaged_assets) > 0:
            allowable_actions.add(free_mortgage)



        if len(self.full_color_sets_possessed) > 0:
            allowable_actions.add(
                improve_property)  # there is a chance this is not dynamically allowable because you've improved a property to its maximum.
            # However, you have to make this check in your decision agent.

        return allowable_actions

    def compute_allowable_post_roll_actions(self, current_gameboard):
        allowable_actions = set()
        allowable_actions.add(concluded_actions)

        if self.num_total_hotels > 0 or self.num_total_houses > 0:
            allowable_actions.add(sell_house_hotel)

        if len(self.assets) > 0:
            allowable_actions.add(sell_property)
            if len(self.mortgaged_assets) < len(self.assets):
                allowable_actions.add(mortgage_property)

        if self._option_to_buy is True:
            allowable_actions.add(buy_property)

        return allowable_actions


    def make_pre_roll_moves(self, current_gameboard):
        allowable_actions = self.compute_allowable_pre_roll_actions(current_gameboard)
        allowable_actions.remove(concluded_actions)
        allowable_actions.add(skip_turn)
        code = 0
        action_to_execute, parameters = self.make_pre_roll_move(self, current_gameboard, allowable_actions, code)

        if action_to_execute == skip_turn:
            return self._execute_action(action_to_execute, parameters)


        allowable_actions.add(concluded_actions)
        allowable_actions.remove(skip_turn) # from this time on, skip turn is not allowed.

        while True:  # currently, we set no limits on this; the assumption is that eventually the player will 'pass the baton'
            if action_to_execute == concluded_actions: # short of raising an exception, this is the only way to exit this function
                return self._execute_action(action_to_execute, parameters)
            else:
                action_to_execute, parameters = self.make_pre_roll_move(self, current_gameboard, self.compute_allowable_pre_roll_actions(current_gameboard), code)
                code = self._execute_action(action_to_execute, parameters)


    def make_out_of_turn_moves(self, current_gameboard):
        allowable_actions = self.compute_allowable_out_of_turn_actions(current_gameboard)
        allowable_actions.remove(concluded_actions)
        allowable_actions.add(skip_turn)
        code = 0
        action_to_execute, parameters = self.make_out_of_turn_move(self, current_gameboard, allowable_actions, code)

        if action_to_execute == skip_turn:
            return self._execute_action(action_to_execute, parameters)

        allowable_actions.add(concluded_actions)
        allowable_actions.remove(skip_turn)  # from this time on, skip turn is not allowed.

        while True:  # currently, we set no limits on this; the assumption is that eventually the player will 'pass the baton'
            if action_to_execute == concluded_actions:  # short of raising an exception, this is the only way to exit this function
                return self._execute_action(action_to_execute, parameters)
            else:
                action_to_execute, parameters = self.make_out_of_turn_move(self, current_gameboard,
                                                                        self.compute_allowable_out_of_turn_actions(
                                                                            current_gameboard), code)
                code = self._execute_action(action_to_execute, parameters)


    def make_post_roll_moves(self, current_gameboard):
        allowable_actions = self.compute_allowable_post_roll_actions(current_gameboard)
        code = 0
        action_to_execute, parameters = self.make_post_roll_move(self, current_gameboard, allowable_actions, code)

        if action_to_execute == concluded_actions:
            self._force_buy_outcome(current_gameboard)
            return self._execute_action(action_to_execute, parameters) # now we can conclude actions


        while True:
            if action_to_execute == concluded_actions: # this is the only way to exit this function
                self._force_buy_outcome(current_gameboard)
                return self._execute_action(action_to_execute, parameters)  # now we can conclude actions

            else:
                action_to_execute, parameters = self.make_post_roll_move(self, current_gameboard,
                                                                        self.compute_allowable_post_roll_actions(
                                                                            current_gameboard), code)
                # print action_to_execute
                code = self._execute_action(action_to_execute, parameters)
                if action_to_execute == buy_property: # at this point you do not have the option to buy since you've had the option.
                    self.reset_option_to_buy()


    def _force_buy_outcome(self, current_gameboard): # if you land on a property owned by the bank, and don't buy it, this function will do the needful
        if self._option_to_buy is True:
            self._own_or_auction(current_gameboard, current_gameboard['location_sequence'][self.current_position])

        self.reset_option_to_buy()
        return

    def reset_option_to_buy(self):
        self._option_to_buy = False

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





