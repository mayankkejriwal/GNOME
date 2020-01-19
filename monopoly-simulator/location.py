from bank import Bank

class Location(object):

    def __init__(self, loc_class, name, start_position, end_position, color):
        """
         Super-class that all locations on the board will be sub-classed to, and that has the common attributes.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        """
        self.loc_class = loc_class
        self.name = name
        self.start_position = start_position
        self.end_position = end_position
        self.color = color

    def update_asset_owner(self, player, current_gameboard):
        """
        If the asset is non-purchaseable, we will raise an exception. A more elegant way (we'll make this change
        in a close future edition) is to have a PurchaseableLocation class sitting between the purchaseable sub-classes
        like real estate and Location, and to add update_asset_owner as a method of PurchaseableLocation.
        :param player: Player instance. The player who now owns this asset (self)
        :param current_gameboard: A dict. The global gameboard data structure
        :return: None
        """
        print 'attempting to update asset ', self.name, ' to reflect new owner: ', player.player_name
        if self.loc_class == 'real_estate' or self.loc_class == 'railroad' or self.loc_class == 'utility':
            self.owned_by = player
            player.add_asset(self, current_gameboard)
            print 'Asset ownership update succeeded.'
        else:
            print 'Asset ',self.name,' is non-purchaseable!'
            raise Exception


class DoNothingLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color):
        """
        This is a location (such as free parking) where nothing happens. It has loc_class 'do_nothing' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        """
        super(DoNothingLocation, self).__init__(loc_class, name, start_position, end_position, color)


class ActionLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, perform_action):
        """
        This is a location that is associated with a non tax-paying action such as
        picking a card from community chest or chance. It has loc_class 'action' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        :param perform_action: A function from card_utility_actions. This is the action that will be performed when
        the player lands on this location.
        """
        super(ActionLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.perform_action = perform_action


class RealEstateLocation(Location):

    def __init__(self, loc_class, name, start_position, end_position, color, rent_1_house, rent_hotel,
                 price, rent_3_houses, rent, mortgage, price_per_house, rent_4_houses, rent_2_houses, owned_by,
                 num_houses, num_hotels):

        """
        This is a real estate location. It has loc_class 'real_estate' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        :param rent_1_house: An integer. The rent that must be paid if there is one house on the property.
        :param rent_hotel: An integer. The rent that must be paid if there is a hotel on the property (currently, at most 1 hotel is allowed/property).
        :param price: An integer. The purchase price of the property if the bank is the owner.
        :param rent_3_houses: An integer. The rent that must be paid if there are three houses on the property.
        :param rent: An integer. The rent that must be paid if the property is unimproved (no houses or hotels)
        :param mortgage: An integer. The amount that you can mortgage the property for.
        :param price_per_house: An integer. The cost of setting up a house on the property.
        :param rent_4_houses: An integer. The rent that must be paid if there are four houses on the property.
        :param rent_2_houses: An integer. The rent that must be paid if there are two houses on the property.
        :param owned_by: An instance of Player or Bank. Specifies who owns the property
        :param num_houses: An integer. Number of houses currently set up on the property.
        :param num_hotels: An integer. Number of hotels currently set up on the property.
        """
        super(RealEstateLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.rent_1_house = rent_1_house
        self.rent_2_houses = rent_2_houses
        self.rent_3_houses = rent_3_houses
        self.rent_4_houses = rent_4_houses
        self.rent_hotel = rent_hotel
        self.rent = rent
        self.price = price
        self.price_per_house = price_per_house
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.num_houses = num_houses
        self.num_hotels = num_hotels
        self.is_mortgaged = False

        obj = dict()
        obj[1] = self.rent_1_house
        obj[2] = self.rent_2_houses
        obj[3] = self.rent_3_houses
        obj[4] = self.rent_4_houses
        self._house_rent_dict = obj


    def calculate_rent(self):
        """
        When calculating the rent, note that a real estate can either have a hotel OR houses OR be
        unimproved-monopolized OR be unimproved-non-monopolized. Rent is calculated based on which of these
        situations applies.
        :return: An integer. The rent due.
        """
        # a property can
        if self.num_hotels == 1:
            return self.rent_hotel
        elif self.num_houses > 0: # later we can replace these with reflections
            return self._house_rent_dict[self.num_houses] # if for some reason you have more than 4 houses, you'll get a key error
        elif self.color in self.owned_by.full_color_sets_possessed:
            return self.rent*2 # charge twice the rent on unimproved monopolized properties.
        else:
            return self.rent # unimproved-non-monopolized rent


class TaxLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, amount_due):
        """
        This is a tax (luxury or income) location. It has loc_class 'tax' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        :param amount_due: An integer. The amount of tax that is due when the player is at this location.
        """
        super(TaxLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.amount_due = amount_due


class RailroadLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, price, mortgage, owned_by):
        """
        This is a railroad location. It has loc_class 'railroad' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        :param price: An integer. The purchase price of the property if the bank is the owner.
        :param mortgage: An integer. The amount that you can mortgage the property for.
        :param owned_by: An instance of Player or Bank. Specifies who owns the property
        """
        super(RailroadLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.price = price
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.is_mortgaged = False

        obj = dict()
        obj[1] = 25
        obj[2] = 50
        obj[3] = 100
        obj[4] = 200
        self._railroad_dues = obj

    def calculate_railroad_dues(self):
        """
        Compute dues if a player lands on railroad owned by another player.
        :return: An integer. Specifies railroad dues
        """
        if self.owned_by.num_railroads_possessed > 4 or self.owned_by.num_railroads_possessed < 0:
            print 'Error! num railroads possessed by ', self.owned_by.player_name, ' is ', \
                str(self.owned_by.num_railroads_possessed)

            raise Exception

        return self._railroad_dues[self.owned_by.num_railroads_possessed]


class UtilityLocation(Location):
    def __init__(self, loc_class, name, start_position, end_position, color, price, mortgage, owned_by):
        """
        This is a utility location. It has loc_class 'utility' in the game
        schema. The attributes are the same as in the schema.
        :param loc_class: A string. The location class/type as specified in the schema.
        :param name: A string. The name of the location
        :param start_position: An integer. Specifies (inclusively) the index on the location_sequence of the current
        gameboard where this location begins.
        :param end_position: An integer. Specifies (non-inclusively) the index on the location_sequence of the current
        gameboard where this location ends. In the default board, it is always start_position+1
        :param color: A string or None. If string, it specifies the color of the location.
        :param price: An integer. The purchase price of the property if the bank is the owner.
        :param mortgage: An integer. The amount that you can mortgage the property for.
        :param owned_by: An instance of Player or Bank. Specifies who owns the property
        """
        super(UtilityLocation, self).__init__(loc_class, name, start_position, end_position, color)
        self.price = price
        self.mortgage = mortgage
        self.owned_by = owned_by
        self.is_mortgaged = False

        obj = dict()
        obj[1] = 4
        obj[2] = 10
        self._die_multiples = obj

    def calculate_utility_dues(self, die_total):
        """
        Compute dues if a player lands on utility owned by another player.
        :param die_total: An integer. The dice total (if there's more than 1 dice as there is in the default game)
        :return: An integer. Specifies utility dues.
        """
        if self.owned_by.num_utilities_possessed > 2 or self.owned_by.num_utilities_possessed < 0:
                print 'Error! num utilities possessed by ',self.owned_by.player_name,' is ', \
                    str(self.owned_by.num_utilities_possessed)

                raise Exception

        return die_total*self._die_multiples[self.owned_by.num_utilities_possessed]




