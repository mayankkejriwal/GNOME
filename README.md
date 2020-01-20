

MONOPOLY SIMULATOR:

Full code for the simulator is in monopoly-simulator/ and is written using OOP methodology.

The entry point for the simulator is gameplay.py and can be run on the command line:

$ python gameplay.py > game-log.txt

The simulator currently relies on Python 2.7.x. Because inheritance has a different syntax between 2.7 and 3, we will
need to release a different version if you really like 3. This can be accomplished relatively easily, but for now, we recommend
setting up a 2.7 interpreter and running the code therein.

You could also choose to print the log on the command line. We've found the log to be very useful in providing a human
readable version of game events. When debugging a decision agent, these logs are your friend. If you succeed in running
the game off the shelf, you should get a log that looks somewhat (though probably not exactly) like game-1-log.txt

To run the simulator, you need a decision agent and the game schema. We have provided the schema already in the outer folder,
although you will have to specify the path to the schema once you clone this repo on your own system. In gameplay, we
also have to specify the numpy seed (currently a default is set) and if we want, we can modify elements of the game schema
for testing purposes. For simple agents that do not try to monopolize, we recommend modifying go_increment to avoid
runaway cash increases from the bank to the players.

We have provided an example 'dummy' decision agent to guide you on how to build out your own decision agent. We plan
to release at least one sophisticated decision agent sometime in January, and the baseline agent used in evaluations
will also be a rule-based, sophisticated decision maker who weighs the state of the board carefully before deciding
what to do.

The code has been fairly well documented, and we've done a lot of testing on it. That does not mean it's completely clear
or that mistakes might not appear. On our part, we are continuously running tests but if you see something that's unclear
or that seems like an error we'd appreciate feedback!

GAME SCHEMA:

The current version of the schema, generated using monopoly-game-schema.py is monopoly_game_schema_v1-2.json. We provide
_v1-1.json for comparison only. It should not be used in the game. Here's a succinct version of some of the more
important changes in going from v1-1 to v1-2:


Updates from v1-1 to v1-2:

--In location_states, we have changed 'class' to 'loc_class'. The reason is (and we should have realized it earlier)
that class is a reserved word in Python.

--we have added a new field called go_increment. This is the amount you get when you pass go each time.

--has_get_out_of_jail card has been replaced with its community chest and chance equivalents.
The reason is that a player can have two of these at the same time (one from each of the card categories), and we need
to be able to track this (e.g., if the player uses the chance card, it should go back to the chance pile.
Unlike the other cards, which get used and replaced immediately in the pile, this one is something the player can hold
on to for a while, which complicates matters)

--another change in location is that we now keep track of who owns the location WITHIN the location itself, and also
how many houses/hotels are on that location. We decided to make this change to avoid too many function
calls/indirections when calculating rent. This means that under 'assets' in player_states, we have removed hotels and
houses; now, we only track which properties the player owns, along with an derivatory data structure that tracks
whether the players possesses full color sets. In turn, this means the 'assets' has been considerably simplified,
since we only need to keep track of the names of the properties the player owns. More details are provided in the
player.py file.

--chance cards were previously missing from the schema due to a glitch in the JSON generation (these have now been added)

--in chance/community chest, we have added a new card class called 'contingent_cash_from_bank' that was previously in
the class positive/negative_cash_from_bank. The reason is that the positive/negative class always involves a
fixed amount, while contingent cash requires a function calculation (e.g., calculating street repair cost),
which makes the structure of the class different.

--name of 'go_to_nearest_railroad_pay_double_1' card is now just 'go_to_nearest_railroad_pay_double'. Note that the
'name' of a card does not have to be unique since there could be multiple identical cards (such as in this case)

--we've added skip_turn and concluded_actions to out_of_turn action choices. skip_turn in this context just means that we
won't take action on out_of_turn (at least right now). concluded_actions means that we're done with whatever actions we
wanted to take. concluded_actions must follow at least one action, otherwise skip_turn should be invoked. Only when
all out_of_turn players have skipped the turn and the current player rolls the die will the die be rolled, and the
post die roll phase begin. The exception is the post-die roll phase where concluded_actions can be called as the very
first action.

--we have simplified player_states since it contained redundant information. Now it refers to a single dictionary.

--there is a small chance my current cash might become negative even if it's not my turn (if another player collects
from me due to a card draw, and I have low cash). Because the chances are so small of this happening, we do not force
that player to take action just yet but once it's his turn, he'll have to deal with the negative cash before he can
conclude his turn (or declare bankruptcy)

--the 'player' objects now have some additional fields that will be useful for keeping track of the game state.

--I've added 'mortgage_property', 'improve_property' to the list of functions that are allowed in out_of_turn moves.
'bid_on_property' has been removed. The reason is that currently, the only way you can bid on a property is at auction,
which is conducted by the bank as a special process when a player refuses to buy a property on which he/she has
landed. So you can't really 'choose' to bid in an out_of_turn move; instead, you can bid only in a player's
post-roll phase.


REMINDERS:

--it is possible to sell a mortgaged property