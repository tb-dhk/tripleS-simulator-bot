# tripleS-simulator-bot

## installation 
add to your server [here](https://discord.com/api/oauth2/authorize?client_id=1041703388057960479&permissions=2048&scope=bot%20applications.commands)

## how to use
use /run with the following parameters:
- prefix: the letter that comes before the serial number (e.g. 'S' for tripleS)
- lineup: list of members, space-separated
- random: whether the reveal of the members is random or in the specified order.
- grav: a list of gravity strings (strings that specify the number of members, then each unit separated by colons, e.g. '8:aaa:kre'). these gravity strings should be separated by spaces.
- haus: a valid haus.json file, with a seoul HAUS in case of gravity. the default haus.json file can be found [here](https://github.com/shuu-wasseo/tripleS-simulator-bot/blob/main/haus.json)
