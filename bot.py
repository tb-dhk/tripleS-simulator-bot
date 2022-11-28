# bot.py

# load discord
import os
import discord
from discord import app_commands
from typing import Optional
from dotenv import load_dotenv
from io import BytesIO
from random import randint, choice
import math
import json
import asyncio
import requests
from prettytable import PrettyTable
from collections import Counter

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
MY_GUILD = discord.Object(id=896690066620035112)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

bot = MyClient(intents=intents)

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
unitss = []

# the command
@bot.tree.command(name="help", description="help")
async def help(interaction):
	await interaction.respond("""
__**parameters for `/run`:**__
    
**prefix**
the letter that comes before the serial number (e.g. 'S' for tripleS)

**lineup**
list of members, space-separated

**random**
whether the reveal of the members is random or in the specified order.

**grav**
a list of gravity strings (strings that specify the number of members, then each unit separated by colons, e.g. '8:aaa:kre'). these gravity strings should be separated by spaces.

**haus** a valid haus.json file, with a seoul HAUS in case of gravity. the default haus.json file can be found here (https://github.com/shuu-wasseo/tripleS-simulator-bot/blob/main/haus.json)
    """)

@bot.tree.command(name="run", description="run the simulator")
async def run(interaction, prefix: str, lineup: str, grav: str, haus: Optional[discord.Attachment], random_members: Optional[bool] = False, unit: Optional[str] = "", random_grav: Optional[bool] = True):
    global unitss

    story = ""
   
    # members + events
    members = lineup.split(" ")
    gravs = [g.split(".") for g in grav.split(" ")]
    unitss = [u.split(".") for u in unit.split(" ")]
    
    # HAUS classes + methods
    
    if haus != None:
        try:
            ohaus = requests.get(haus).json() 
        except:
            await interaction.response.send_message("invalid HAUS.")
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
        print(text)
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
                story = p(story, "oops! it appears we are out of beds :(")
                return house, True
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
        return haus, False
    
    def perms(ls): # credits to geeksforgeeks i could not bother to do this on my own
        if len(ls) == 0:
            return []
     
        if len(ls) == 1:
            return [ls]
     
        l = []
     
        for i in range(len(ls)):
           m = ls[i]
     
           remlst = ls[:i] + ls[i+1:]
     
           # generating all permutations where m is first
           # element
           for p in perms(remlst):
               l.append([m] + p)
        return l

    async def gravity(membs, units):
        global story
        global unitss
        global view
        
        msg = []
        votes = []
        emoji = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🫶", "❤️", "😊", "✨", "🥹", "🎄", "🔥", "😂", "👍", "🫡", "🎁", "🎡", "🧀"]
            
        story = p(story, "\ngrand gravity time!")
        if not random_grav:
            await interaction.response.send_message("grand gravity time!")
        tab = PrettyTable(["unit", "description"])
        for x in units:
            found = False
            for y in unitss:
                if y[0] == x:
                    tab.add_row(y)
                    found = True
                    break
            if not found:
                tab.add_row([x, "null"])
        story = p(story, tab)
        if not random_grav:
            try:
                await interaction.followup.send(f"```{tab}```")
            except:
                await interaction.response.send_message(f"```{tab}```")
        tab = PrettyTable(units)
        ms = membs.copy()
        lrs = ""
        for x in range(math.ceil(len(membs)/len(units))):
            pair = []
            for y in range(len(units)):
                try:
                    picked = choice(membs)
                except:
                    pass
                else:
                    pair.append(picked)
                    membs.remove(picked)
            if not random_grav:
                stri = f"\n```{tab}```"
                subt = PrettyTable(units)
                lrs = ""

                for n in range(len(perms(pair))):
                    subt.add_row([pm(m) for m in perms(pair)[n]])
                stri += (f"\nround {x+1}: ({math.factorial(len(units))*2.5} seconds)\n")
                lines = len(str(subt).split("\n"))
                for row in range(lines):
                    r = str(subt).split("\n")[row]
                    if (row >= 0 and row <= 2) or row == lines-1:
                        stri += ("       " + f"`{r}`\n")
                    else:
                        stri += (emoji[row-3] + f" `{r}`\n")
                msg = await interaction.followup.send(stri + "\npick the number of your desired permutation (react with :x: to stop voting): ")
                for x in range(math.factorial(len(units))):
                    try:
                        await msg.add_reaction(emoji[x])
                    except:
                        pass

                await asyncio.sleep(math.factorial(len(units))*2.5)

                await msg.edit(content = f"round over!\n{lrs}")

                cache_msg = discord.utils.get(bot.cached_messages, id=msg.id)
                votes = [e.emoji for e in cache_msg.reactions]
 
                print(votes)

                for e in Counter(votes):
                    print(e, emoji.index(e), Counter(votes)[e])
                    lrs += f"{e}: {Counter(votes)[e]-1}\n"
                    
                pick = emoji.index(Counter(votes).most_common()[0][0])
                while 1:
                    try:
                        pair = perms(pair)[int(pick)]
                    except:
                        pass
                    else:
                        break
            tab.add_row([pm(m) for m in pair])
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

    async def event(haus, omembers, number, hs, events, gravities, mmoves, tab, wave):
        global story
        brk = False
        
        if number == cbeds(uhaus, hs[:-1]) + 1 and len(hs) > 1:
            events = [["mmove"]] + events

        if len(events) == 0:
            haus, brk = move(haus, [omembers[-1]], hs)
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
                    haus, brk= move(haus, omembers, hs, hs[-1])
                    phaus(haus)
                    story = p(story, "\n")
                case "gravity":
                    gravities += 1
                    haus, brk = move(haus, [omembers[-1]], hs)
                    if not moved:
                        tab.add_row([pm(omembers[-1]), omembers[-1].color, pb(omembers[-1].beds[-1])])
                        wave += 1
                        story = p(story, f"new wave of {prefix}!")
                        story = p(story, f"wave {str(wave)}:")
                        story = p(story, tab)
                        tab = PrettyTable(["member", "color", "bed"])
                    phaus(haus)
                    await gravity(omembers.copy(), e[1])
                    haus, brk = move(haus, omembers, "seoul")
                    phaus(haus, True)
                    story = p(story, "\n")
        
        if full(ohaus, "seoul") and len(events) > 0:
            story = p(story, f"the seoul HAUS is full.\n")

        return haus, gravities, mmoves, tab, wave, brk

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
    print()

    omembers = []
    gravities = 0
    mmoves = 1
    wave = 0
    tab = PrettyTable(["member", "color", "bed"])

    for x in range(len(members)):
        events = []

        # add member to database
        if random_members:
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

        lis = await event(uhaus, om, x+1, hs, events, gravities, mmoves, tab, wave)
        uhaus = lis[0]
        gravities = lis[1]
        mmoves = lis[2]
        tab = lis[3]
        wave = lis[4]
        if lis[5]:
            break

        
    story = p(story, "to be continued...")
    phaus(uhaus, False, True)
    phaus(uhaus, True, True)

    # summary table
    summary(omembers)

    as_bytes = map(str.encode, story)
    content = b"".join(as_bytes)
    try:
        await interaction.response.send_message("your simulation:", file=discord.File(BytesIO(content), "simulated.txt"))
    except:
        await interaction.followup.send("your simulation:", file=discord.File(BytesIO(content), "simulated.txt"))

bot.run(TOKEN)