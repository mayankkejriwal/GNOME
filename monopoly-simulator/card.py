class Card(object):
    def __init__(self, action, card_type, name):
        self.action = action
        self.card_type = card_type
        self.name = name


class MovementCard(Card):
    def __init__(self, action, card_type, name, destination):
        super(MovementCard, self).__init__(action, card_type, name)
        self.destination = destination


class MovementPaymentCard(Card):
    def __init__(self, action, card_type, name):
        super(MovementPaymentCard, self).__init__(action, card_type, name)


class ContingentMovementCard(Card):
    def __init__(self, action, card_type, name):
        super(ContingentMovementCard, self).__init__(action, card_type, name)


class MovementRelativeCard(Card):
    def __init__(self, action, card_type, name, new_relative_position):
        super(MovementRelativeCard, self).__init__(action, card_type, name)
        self.new_relative_position = new_relative_position


class CashFromBankCard(Card):
    def __init__(self, action, card_type, name, amount):
        super(CashFromBankCard, self).__init__(action, card_type, name)
        self.amount = amount


class ContingentCashFromBankCard(Card):
    def __init__(self, action, card_type, name, contingency):
        super(ContingentCashFromBankCard, self).__init__(action, card_type, name)
        self.contingency = contingency


class CashFromPlayersCard(Card):
    def __init__(self, action, card_type, name, amount_per_player):
        super(CashFromPlayersCard, self).__init__(action, card_type, name)
        self.amount_per_player = amount_per_player