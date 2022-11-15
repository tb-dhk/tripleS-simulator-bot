# tripleS-simulator-bot

## installation 
add to your server [here](https://discord.com/api/oauth2/authorize?client_id=1041703388057960479&permissions=2048&scope=bot%20applications.commands).

## how to use
use /run with the following parameters:
- prefix: the letter that comes before the serial number (e.g. 'S' for tripleS)
- lineup: list of members, space-separated
- random: whether the reveal of the members is random or in the specified order.
- grav: a list of gravity strings (strings that specify the number of members, then each unit separated by colons, e.g. '8:aaa:kre'). these gravity strings should be separated by spaces.
- haus: a valid haus.json file, with a seoul HAUS in case of gravity. the default haus.json file can be found [here](https://github.com/shuu-wasseo/tripleS-simulator-bot/blob/main/haus.json)

# further explanation
the following sections have been adapted from the [CLI README.md](https://github.com/shuu-wasseo/tripleS-simulator/blob/main/README.md).

## haus.json
this optional json file represents the structure of the HAUS. with the default values, the normal HAUS and seoul HAUS can house 12 people each.
### normal HAUS
other than the seoul HAUS, each haus contains multiple rooms in the form of a dictionary, each containing a "upper bunk", "lower bunk" and optionally, a "single" bed. the default structure of the haus (based on the original tripleS) has been provided.

### seoul HAUS
the names of these rooms are typically based on the number of beds in the room, while rooms with the same number of beds are differentiated by a suffix, separated from the original nunumber of beds with a "-". the beds in the rooms here are strictly bunk beds at the moment.

for example, the default seoul HAUS contains 5 rooms, "2-1", "2-2", "2-3", "2-4" and "4". the "2"s and "4" in these names indicates the number of beds there will be while "-1", "-2", etc. are simply used to differentiate the rooms.

## events
in the tripleS simulator, there are multiple types of events. as of now, we only feature two major events, mass moving and (grand) gravity.

### mass moving
after the occupied HAUS become full, each member will either "choose" to stay in their original HAUS or move to the next HAUS. 

for example, based on the default HAUS:
- when the 6th member arrives, a mass moving event is initiated as HAUS 1 can only house 5 people.
- the 6th member is automatically put into HAUS 2.
- the other 5 members either choose to move to HAUS 2 or stay in HAUS 1.

### gravity
after your group reaches a certain number of members, a gravity (or grand gravity) will be initiated. gravity cannot be customised or controlled in any way, and every unit is assigned members at random. however, the number of members in every unit is as equal as possible.

## notes
we have been made aware that if new members join during dimension, the members will move into the seoul HAUS with the other members first. however, we do not intend to put this in place at the moment.
