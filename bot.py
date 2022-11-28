# bot.py

# load discord
import os
import discord
from discord.commands import option
from dotenv import load_dotenv
from io import BytesIO
from random import randint, choice
import math
import json
import requests
from prettytable import PrettyTable

intents = discord.Intents.default()
intents.messages = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = discord.Bot()

# load mysql
@bot.event
async def on_ready():
    print(f'{bot.user} is online.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "tripleS" in message.content:
        await message.channel.send(":eyes:")

story = ""

# the command
@bot.slash_command(name = "help", description = "help")
async def help(ctx):
	await ctx.respond("""
__**parameters for `/run`:**__
    
**prefix**
the letter that comes before the serial number (e.g. 'S' for tripleS)

**lineup**
list of members, space-separated

**random**
whether the reveal of the members is random or in the specified order.

**grav**
a list of gravity strings (strings that specify the number of members, then each unit separated by periods, e.g. '8.aaa.kre'). these gravity strings should be separated by spaces.

**haus** a valid haus.json file, with a seoul HAUS in case of gravity. the default haus.json file can be found here (https://github.com/shuu-wasseo/tripleS-simulator-bot/blob/main/haus.json)
    """)

@bot.slash_command(name = "run", description = "run the simulator")
@option("haus", required = False, default = None)
async def signup(ctx, prefix: str, lineup: str, random: bool, grav: str, haus: discord.Attachment):
    global story
    
    await ctx.defer()
    
    story = ""
   
    # members + events
    members = lineup.split(" ")
    gravs = [g.split(".") for g in grav.split(" ")]
    
    # verification
    badgrav = False
    for x in gravs:
        if len(x) < 3:
            badgrav = True
            await ctx.respond("invalid gravity string.")
            break

    # HAUS classes + methods
    if haus != None:
        try:
            ohaus = requests.get(haus).json() 
        except:
            await ctx.respond("invalid HAUS.")
            return
    else:
        ohaus = json.load(open("haus.json"))

    uhaus = ohaus.copy()
        
    class b:
        def __init__(self, haus, room, bed, seoul):
            self.haus = haus
            self.room = room
            self.bed = bed
            self.seoul = seoul
            
    def edhaus(haus, memb, bed):
        dic = haus
        dic[bed.haus][bed.room][bed.bed] = memb
        return dic 

    def pb(bed):
        if bed == "":
            return ""
        else:
            return f"{bed.haus}, {bed.room} room, {bed.bed} bed"

    # member classes + methods
    class memb:
        def __init__(self, serial, name, gravity, beds, seoul, color):
            self.serial = serial
            self.name = name
            self.beds = beds
            self.gravity = gravity
            self.seoul = seoul
            self.color = color

    def pm(memb):
        return f"{prefix}{memb.serial} {memb.name}"
           
    def p(story, text):
        story = story + str(text) + "\n"
        return story 

    def move(house, membs, hs, move_event=""):
        global story
        length = len(membs)
        if len(membs) > 1:
            tab = PrettyTable(["member", "room"])
            story = p(story, "\nmoving time!")
        
        beds = []
        for h in house:
            if h in hs:
                for room in house[h]:
                    for bed in house[h][room]:
                        if move_event != "":
                            beds.append(b(h, room, bed, hs=="seoul"))
                        elif house[h][room][bed] == "":
                            beds.append(b(h, room, bed, hs=="seoul"))
                        
        for m in membs:
            found = False
            if hs == "seoul":
                for room in house["seoul"]:
                    for bed in house["seoul"][room]:
                        if house["seoul"][room][bed] == m:
                            found = True
            if found:
                continue
            try:
                if move_event != "" and m.serial == length:
                    bed = choice([bed for bed in beds if bed.haus == move_event])
                else:
                    bed = choice(beds)
            except:
                story = p(story, "oh dear! it appears we have run out of beds. time to wait for HAUS 3!")
                return house 
            else:
                if (move_event != "" and bed.haus == move_event) or move_event == "":
                    if move_event != "":
                        for h in house:
                            if house != "seoul":
                                for room in house[h]:
                                    for be in house[h][room]:
                                        if house[h][room][be] == m:
                                            house[h][room][be] = ""
                    haus = edhaus(house, m, bed)
                    beds.remove(bed)
                    if len(membs) > 1:
                        tab.add_row([pm(m), pb(bed)])
                    if hs == "seoul":
                        m.seoul = bed
                    else:
                        m.beds.append(bed)
                else:
                    haus = house
                    if hs == "seoul":
                        m.seoul = bed
                    else:
                        m.beds.append(m.beds[-1])

        if len(membs) > 1:
            story = p(story, tab)
        try:
            return haus
        except:
            return hs
        
    def gravity(membs, units):
        global story
        tab = PrettyTable(units)
        ms = membs.copy()
        story = p(story, "\ngrand gravity time!")
        for x in range(math.ceil(len(membs)/len(units))):
            pair = []
            for y in range(len(units)):
                try:
                    picked = choice(membs)
                except:
                    picked = ""
                else:
                    membs.remove(picked)
                finally:
                    pair.append(picked)
            row = []
            for m in pair:
                try:
                    row.append(pm(m))
                except:
                    row.append("")
            tab.add_row(row)
            for y in range(len(units)):
                try:
                    pair[y].gravity.append(units[y])
                except:
                    pass
        story = p(story, tab)
        return ms

    def phaus(haus, seoul=False, final=False):
        global story

        if seoul:
            str = f"\nHAUS update: (seoul)"
        else:
            str = f"\nHAUS update:"
        if final:
            story = p(story, str.replace("HAUS update", "final HAUS"))
        else:
            story = p(story, str)
        tab = PrettyTable(["room", "members"])
        for h in haus:
            if (h=="seoul") == seoul:
                for room in haus[h]:
                    row = [f"{h}, {room} room", ""]
                    for bed in haus[h][room]:
                        try:
                            row[-1] += pm(haus[h][room][bed]) + ", "
                        except:
                            pass
                    row[-1] = row[-1][:-2]
                    tab.add_row(row)
        story = p(story, tab)

    def full(uhaus, hs):
        full = True
        for haus in uhaus:
            if haus in hs:
                for room in uhaus[haus]:
                    for bed in uhaus[haus][room]:
                        if uhaus[haus][room][bed] == "":
                            full = False

        return full

    def cbeds(uhaus, hs):
        count = 0
        for haus in uhaus:
            if haus in hs:
                for room in uhaus[haus]:
                    for bed in uhaus[haus][room]:
                        count += 1
        
        return count

    def event(haus, omembers, number, hs, events, gravities, mmoves, tab, wave):
        global story

        if number == cbeds(uhaus, hs[:-1]) + 1 and len(hs) > 1:
            events = [["mmove"]] + events

        if len(events) == 0:
            haus = move(haus, [omembers[-1]], hs)
            try:
                bed = pb(omembers[-1].beds[-1])
            except:
                bed = ""
            tab.add_row([pm(omembers[-1]), omembers[-1].color, bed])
        
        moved = False
                
        for e in events: 
            match e[0]:
                case "mmove":
                    mmoves += 1
                    tab.add_row([pm(omembers[-1]), omembers[-1].color, "TBC"])
                    wave += 1
                    story = p(story, f"new wave of {prefix}!")
                    story = p(story, f"wave {str(wave)}:")
                    story = p(story, tab)
                    tab = PrettyTable(["member", "color", "bed"])
                    moved = True
                    haus = move(haus, omembers, hs, hs[-1])
                    phaus(haus)
                    story = p(story, "\n")
                case "gravity":
                    gravities += 1
                    haus = move(haus, [omembers[-1]], hs)
                    if not moved:
                        tab.add_row([pm(omembers[-1]), omembers[-1].color, pb(omembers[-1].beds[-1])])
                        wave += 1
                        story = p(story, f"new wave of {prefix}!")
                        story = p(story, f"wave {str(wave)}:")
                        story = p(story, tab)
                        tab = PrettyTable(["member", "color", "bed"])
                    phaus(haus)
                    omembers = gravity(omembers, e[1])
                    haus = move(haus, omembers, "seoul")
                    phaus(haus, True)
                    story = p(story, "\n")
        
        if full(ohaus, "seoul") and len(events) > 0:
            story = p(story, f"the seoul HAUS is full.\n")

        return haus, gravities, mmoves, tab, wave, 

    def summary(omembers):
        global story

        story = p(story, "")
        maxg = 0
        maxm = 0
        
        for memb in omembers:
            if len(memb.gravity) > maxg:
                maxg = len(memb.gravity)
            if len(memb.beds) > maxm:
                maxm = len(memb.beds)

        for memb in omembers:
            while len(memb.gravity) < maxg:
                memb.gravity = [""] + memb.gravity
            while len(memb.beds) < maxm:
                memb.beds = [""] + memb.beds

        gs = []
        bs = []

        for x in range(maxg):
            gs.append(f"unit {x+1}")
        for x in range(maxm):
            bs += [f"haus {x+1}", f"room {x+1}", f"bed {x+1}"]

        tab = PrettyTable(["name", "serial", "color"] + gs + bs + ["seoul room", "seoul bed"])
        
        for m in omembers:
            beds = []
            for bed in m.beds:
                if bed != "":
                    beds += [bed.haus, bed.room, bed.bed]
                else:
                    beds += ["", "", ""]
            try:
                seoul = [m.seoul.room, m.seoul.bed]
            except:
                seoul = ["", ""]
            row = [m.name, prefix + str(m.serial), m.color] + m.gravity + beds + seoul
            tab.add_row(row)
            
        story = p(story, tab)

    # main code
    if not badgrav:
        omembers = []
        gravities = 0
        mmoves = 1
        wave = 0
        tab = PrettyTable(["member", "color", "bed"])

        for x in range(len(members)):
            events = []

            # add member to database
            if random:
                nmemb = choice(members)
            else:
                nmemb = members[0]
            new = memb(x+1, nmemb, [], [], "", "")
            omembers.append(new)
            members.remove(nmemb)

            # reveal new member
            def genhex():
                n = hex(randint(0,255))[2:]
                if len(n) == 1:
                    return "0" + n
                return n
            hexc = "#" + genhex() + genhex() + genhex()
            omembers[-1].color = hexc
                    
            # moving
            hauses = list(dict.keys(ohaus))
            hauses.remove("seoul")
            for y in range(len(hauses)):
                if x+1 <= cbeds(uhaus, hauses[:y+1]):
                    hs = hauses[:y+1]
                    break

            for gravi in gravs:
                if x+1 == int(gravi[0]):
                    events.append(["gravity", gravi[1:]])
            
            om = omembers.copy()

            lis = event(uhaus, om, x+1, hs, events, gravities, mmoves, tab, wave)
            uhaus = lis[0]
            gravities = lis[1]
            mmoves = lis[2]
            tab = lis[3]
            wave = lis[4]

            
        story = p(story, "to be continued...")
        phaus(uhaus, False, True)
        phaus(uhaus, True, True)

        # summary table
        summary(omembers)

        as_bytes = map(str.encode, story)
        content = b"".join(as_bytes)
        await ctx.respond("your simulation:", file=discord.File(BytesIO(content), "simulated.txt"))

bot.run(TOKEN)
