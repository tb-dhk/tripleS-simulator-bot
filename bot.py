# bot.py

# load discord
import os
import discord
from discord.ext import commands
from discord.commands import option
from dotenv import load_dotenv
import hashlib
import mysql.connector
import random
import json
import datetime as dt
import calendar
import math
import dateutil.relativedelta
import statistics

intents = discord.Intents.default()
intents.messages = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = discord.Bot()

# load mysql
mydb = mysql.connector.connect(
    host = os.getenv("host"),
    user = os.getenv("user"),
    password = os.getenv("password"),
    port = os.getenv("port"),
)
cursor = mydb.cursor(buffered=True)
maindb = os.getenv("database")
cursor.execute(f"use {maindb};")
cursor.execute("select * from accounts;")
result = cursor.fetchall()

@bot.event
async def on_ready():
    print(f'{bot.user} is online.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "habitmap" in message.content:
        await message.channel.send("hewwo! :3")

# tiny commands

def checklog(userid):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    for row in result:
        if row[6] == str(userid):
            return True
    return False

def gensalt(uid, pwd):
        alpha = "qweryuiopasdfghjklzxcvbnm"
        count = 0
        for x in uid:
            try:
                count += alpha.index(x) + 1
            except:
                count += ord(x) 
        for x in pwd:
            try:
                count += alpha.index(x) + 1
            except:
                count += ord(x)
        return hashlib.sha3_512(hex(count)[::-1].encode()).hexdigest()

def newyear(json, habit, year):
    nmth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    lmth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    json[habit] = {
        str(year) : []
    }

    for x in range(12):
        json[habit][str(year)].append([])
        if int(year) % 4 == 0:
            for x in range(lmth[x]):
                json[habit][str(year)][-1].append(0)
        else:
            for x in range(nmth[x]):
                json[habit][str(year)][-1].append(0)

    return json

def lis(id):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(id):
        for row in result:
            if row[6] == str(id):
                if row[3] == "":
                    return {}
                else:
                    return json.loads(row[3])

def cday(day):
    try:
        day = dt.date.fromisoformat(day)
    except:
        match day:
            case "tdy":
                return dt.date.today()
            case "yst":
                return dt.date.today() - dt.timedelta(days=1)
            case "sun" | "mon" | "tue" | "wed" | "thu" | "fri" | "sat":
                ds = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
                wd = dt.date.today().weekday()

                if dt.date.today().weekday() < 5:
                    sat = dt.date.today() + dt.timedelta(days=5-wd)
                elif dt.date.today().weekday() == 6:
                    sat = dt.date.today() + dt.timedelta(days=6)
                else:
                    sat = dt.date.today()

                return sat - dt.timedelta(days=6-ds.index(day))
            case _:
                if isinstance(day, dt.date):
                    return day
                else:
                    return ("invalid day. the 'day' argument must either be 'tdy', 'yst', the first three letters of a day of the week or a date in ISO format (YYYY-MM-DD).")
    else:
        return day

# account commands (dm only)
@bot.slash_command(name = "signup", description = "sign up for habitmap")
@commands.dm_only()
async def signup(interaction, username: str, password: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if not checklog(interaction.user.id):
        found = False
        for x in result:
            if username == x[0]:
                await interaction.response.send_message("this username is already taken. please choose another username.", ephemeral=True)
                found = True
        
        if not found:
            await interaction.response.send_message("creating account...", ephemeral=True)
            salt = gensalt(username, password)
            hpwd = hashlib.sha3_512((password + salt).encode()).hexdigest()
            id = hashlib.sha3_512(str(random.random()).encode()).hexdigest()
            cursor.execute(f"""
            insert into
                `accounts` (`username`, `salt`, `password`, `data`, `config`, `id`, `discord`)
            values
                ('{username}', '{salt}', '{hpwd}', '{r"{}"}', '{r"{}"}', '{id}', '{interaction.user.id}');
            """)
            mydb.commit()
            await interaction.followup.send("account creation complete!", ephemeral=True)
    else:
        await interaction.response.send_message("you are currently logged in as another user. please log out with `/logout` to sign up for a new account.", ephemeral=True)
            
@bot.slash_command(name = "login", description = "log in to habitmap")
@commands.dm_only()
async def login(interaction, username: str, password: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall() 

    if checklog(interaction.user.id):
        await interaction.response.send_message("you have already logged in. if you would like to log out, try `/logout` instead.", ephemeral=True)
    else:
        await interaction.response.send_message(f"logging in as {username}...", ephemeral=True)
        
        found = False
        for row in result:
            if row[0] == username:
                found = True
                if hashlib.sha3_512((password + row[1]).encode()).hexdigest() == row[2]:
                    await interaction.followup.send("login successful!", ephemeral=True)
                    if row[6] == "":
                        cursor.execute(f"update accounts set discord = '{interaction.user.id}' where username = '{username}'")
                        mydb.commit()
                else:
                    await interaction.followup.send("invalid credentials. please try again.", ephemeral=True)
                break

        if not found:
            await interaction.followup.send("invalid username. if you would like to make a new account, try `/signup` instead.", ephemeral=True)
   
@bot.slash_command(name = "logout", description = "log out from habitmap")
@commands.dm_only()
async def logout(interaction):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        await interaction.response.send_message(f"logging out...", ephemeral=True)
        for row in result:
            if row[6] == str(interaction.user.id):
                cursor.execute(f"update accounts set discord = '' where id = '{row[5]}'")
                mydb.commit()
        await interaction.followup.send("logout successful!", ephemeral=True)
    else:
        await interaction.response.send_message("you have already logged out. if you would like to log in, try `/login` instead.", ephemeral=True)

@bot.slash_command(name = "checka", description = "check habitmap account status")
@commands.dm_only()
async def viewa(interaction):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()
    
    if checklog(interaction.user.id):
        found = False
        for row in result:
            if row[6] == str(interaction.user.id):
                found = True
                await interaction.response.send_message(f"you are logged in as {row[0]}.", ephemeral=True)
                break
        if not found:
            await interaction.response.send_message("error.")
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login`.")

@bot.slash_command(name = "edita", description = "change habitmap account details")
@commands.dm_only()
async def edita(interaction, credential: str, old: str, new: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    fuser = False
    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                fuser = True
                account = row
                acct = {"username": row[0], "password": row[2]}
                break

        if fuser:
            if credential == "username":
                if old == acct["username"]:
                    await interaction.response.send_message("username verified.", ephemeral=True)
                    acct["username"] = new
                    cursor.execute(f"""
                        UPDATE
                            accounts
                        SET
                            username = '{new}'
                        WHERE
                            id = '{account[5]}';
                    """)
                    mydb.commit()
                    await interaction.followup.send(f"your username is now {new}.", ephemeral=True)
                else:
                    await interaction.response.send_message("invalid username.", ephemeral=True)
            elif credential == "password":
                if hashlib.sha3_512((old + account[1]).encode()).hexdigest() == account[2]:
                    await interaction.response.send_message("password verified.", ephemeral=True)
                    cursor.execute(f"""
                        UPDATE
                            accounts
                        SET
                            salt = '{gensalt(account[0], new)}',
                            password = '{hashlib.sha3_512((new + gensalt(account[0], new)).encode()).hexdigest()}'
                        WHERE
                            username = '{acct["username"]}';
                    """)
                    mydb.commit()
                    await interaction.followup.send(f"your password has been changed.", ephemeral=True)
                else:
                    await interaction.response.send_message("invalid password.", ephemeral=True)
            else:
                await interaction.response.send_message("invalid credential.", ephemeral=True)
    else:
        await interaction.response.send_message("please login first.", ephemeral=True)

@bot.slash_command(name = "dela", description = "delete habitmap account")
@commands.dm_only()
async def removea(interaction, password: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        found = False
        for row in result:
            if row[6] == str(interaction.user.id):
                found = True
                if hashlib.sha3_512((password + row[1]).encode()).hexdigest() == row[2]:
                    cursor.execute(f"delete from accounts where discord = '{interaction.user.id}'")
                    mydb.commit()
                    await interaction.response.send_message("account successfully deleted.")
                    break
                else:
                    await interaction.response.send_message("invalid credentials. please try again.", ephemeral=True)
                break
       
        if not found:
                await interaction.response.send_message("invalid username. if you would like to make a new account, try `/signup` first.", ephemeral=True)
    
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

# habit commands
@bot.slash_command(name = "listh", description = "list all habits")
async def listh(interaction):

    data = lis(interaction.user.id)
    
    if len(data) == 0:
        msg = "you have no habits. please consider getting a life or using `/edith` to add some new habits."
    else:
        msg = "you have the following habits:\n"
        for x in data:
            msg += f"- {x}\n"
    
    try:
        await interaction.response.send_message(msg)
    except:
        await interaction.followup.send(msg)

def edhb(ctx: discord.AutocompleteContext):
    return [act for act in ["add", "remove"] if act.startswith(ctx.value.lower())]

@bot.slash_command(name = "edith", description = "add a habit")
@option("action", description="action", autocomplete=edhb)
async def edith(interaction, action: str, habit: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break
        
        if action == "add":
            if habit in data:
                await interaction.response.send_message(f"habit '{habit}' already exists.", ephemeral=True)
            else:
                tyr = dt.date.today().year
                data = newyear(data, habit, tyr)
                data[habit]["stepno"] = 4
                await interaction.response.send_message(f"habit '{habit}' added.")
        elif action == "remove":
            if habit not in data:
                await interaction.response.send_message(f"habit '{habit}' does not exist.", ephemeral=True)
            else:
                del data[habit]
                await interaction.response.send_message(f"habit '{habit}' removed.")
        
        cursor.execute(f"update accounts set data = '{json.dumps(data)}' where discord = '{interaction.user.id}'")
        await listh(interaction)
        mydb.commit() 
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

@bot.slash_command(name = "trackh", description = "add a habit")
@option("habit", description="habit", required = False, default = "")
async def trackh(interaction, date: str, num: str, habit: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()
    step_to4 = [ [0, 4], [0, 2, 4], [0, 1, 3, 4] ]

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break
        
        if habit == "":
            msg = ""
            lis = []
            
            for habit in data:
                lis.append(habit)

            nums = [int(x) for x in num.split()]
            for x in range(len(lis)):
                habit = lis[x]
                try:
                    number = nums[x]
                except:
                    msg = "not enough numbers. please try again."
                    break

                stepno = data[habit]["stepno"]
                if number <= stepno and number >= 0:
                    day = cday(date)
                    if day != "invalid day. the 'day' argument must either be 'tdy', 'yst', the first three letters of a day of the week or a date in ISO format (YYYY-MM-DD).":
                        dat = (day.year, day.month, day.day)
                        
                        if str(dat[0]) not in data[habit]:
                            newyear(data, habit, dat[0])
                       
                        if stepno != 4:
                            no = step_to4[stepno-1][number]
                            data[habit][str(dat[0])][dat[1]-1][dat[2]-1] = no
                            msg += f"value of habit {habit} on {dat[0]}-{dat[1]}-{dat[2]} changed to {number} of {stepno} ({no} in 4-step).\n"
                        else:
                            data[habit][str(dat[0])][dat[1]-1][dat[2]-1] = number
                            msg += f"value of habit {habit} on {dat[0]}-{dat[1]}-{dat[2]} changed to {number} of {stepno}.\n"
                    else:
                        msg += ("invalid day.")
                        break
                else:
                    msg += ("invalid stepno.")
                    break
            await interaction.response.send_message(msg)
        else:
            number = int(num)
            if habit in data:
                try:
                    stepno = data[habit]["stepno"]
                except:
                    data[habit]["stepno"] = 4
                    stepno = 4
                if number <= stepno and number >= 0:
                    day = cday(date)
                    if day != "invalid day. the 'day' argument must either be 'tdy', 'yst', the first three letters of a day of the week or a date in ISO format (YYYY-MM-DD).":
                        dat = (day.year, day.month, day.day)
                        
                        if str(dat[0]) not in data[habit]:
                            newyear(data, habit, dat[0])
                       
                        if stepno != 4:
                            no = step_to4[stepno-1][number]
                            data[habit][str(dat[0])][dat[1]-1][dat[2]-1] = no
                            await interaction.response.send_message(f"value of habit {habit} on {dat[0]}-{dat[1]}-{dat[2]} changed to {number} of {stepno} ({no} in 4-step).")
                        else:
                            data[habit][str(dat[0])][dat[1]-1][dat[2]-1] = number
                            await interaction.response.send_message(f"value of habit {habit} on {dat[0]}-{dat[1]}-{dat[2]} changed to {number} of {stepno}.")
                    else:
                        await interaction.response.send_message("invalid day.")
                else:
                    await interaction.response.send_message("invalid stepno.")
            else:
                await interaction.response.send_message("invalid habit.")
        cursor.execute(f"update accounts set data = '{json.dumps(data)}' where discord = '{interaction.user.id}'")
        mydb.commit()
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

@bot.slash_command(name = "moveh", description = "move one habit after another habit.")
@option("after", description="habit to move after. if left blank, the moved habit is moved to the top.", required = False, default = "")
async def moveh(interaction, habit: str, after: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break
        
        if habit not in data or (after != "" and after not in data):
            await interaction.response.send_message("habit not found.")
        else:
            lis = []

            for hab in data:
                lis.append(hab)

            lis.remove(habit)
            if after != "":
                ind = lis.index(after)
            else:
                ind = -1
            lis.insert(ind + 1, habit)

            data = {habit : data[habit] for habit in lis}

            cursor.execute(f"update accounts set data = '{json.dumps(data)}' where discord = '{interaction.user.id}'")
            mydb.commit()
            if after == "":
                await interaction.response.send_message(f"{habit} moved to top.")
            else:
                await interaction.response.send_message(f"{habit} moved after {after}.")
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

@bot.slash_command(name = "steph", description = "change stepno of habit.")
async def steph(interaction, habit: str, number: int):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break

        if number < 1 or number > 4:
            await interaction.response.send_message("invalid number.")
        elif habit not in data:
            await interaction.response.send_message("invalid habit.")
        else:
            data[habit]["stepno"] = number
            await interaction.response.send_message(f"stepno for {habit} changed to {number}.")

        cursor.execute(f"update accounts set data = '{json.dumps(data)}' where discord = '{interaction.user.id}'")
        mydb.commit()
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

# map commands
@bot.slash_command(name = "durm", description = "show a daymap / durmap.")
async def daymap(interaction, start: str, finish: str, bydur: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break
    
        match len(str(start)):
            case 10:
                begin = dt.date.fromisoformat(start)
            case 7:
                begin = dt.date.fromisoformat(start + "-01")
            case 4:
                begin = dt.date.fromisoformat(start + "-01-01")

        match len(str(finish)):
            case 10:
                end = dt.date.fromisoformat(finish)
            case 7:
                end = dt.date.fromisoformat(finish + "-" + str(calendar.monthrange(int(finish[0:4]), int(finish[5:7]))[1]))
            case 4:
                end = dt.date.fromisoformat(finish + "-12-31")

        try:
            st = cday(begin)
        except:
            st = cday(start)
        
        try:
            end = cday(end)
        except:
            end = cday(finish)

        max = 0
        lis = ["yy", "mm", "dd"]
        
        for habit in data:
            if len(habit) > max:
                max = len(habit)
            lis.append(habit)

        if max < 7:
            max = 7
        lis.append("overall")
        lis.append("")
        
        if len(lis) <= 4:
            print("you have no habits. please add a habit and try again.")
            exit()

        strings = {}

        star = st
        ps = st
            # start += dt.timedelta(days=1) 
        colno = 0

        if star > end:
            print("start is later than end. please try again.")
        while star <= end:
            match bydur:
                case "day":
                    ns = star + dateutil.relativedelta.relativedelta(days=+1)
                case "week":
                    if star.weekday() != 6:
                        ns = star
                        while ns.weekday() != 6:
                            ns += dateutil.relativedelta.relativedelta(days=+1)
                    else:
                        ns = star + dateutil.relativedelta.relativedelta(days=+7)
                case "month":
                    if star.day != 1:
                        ns = star
                        while ns.day != 1:
                            ns += dateutil.relativedelta.relativedelta(days=+1)
                    else:
                        ns = star + dateutil.relativedelta.relativedelta(months=+1)
                case "year":
                    if star.day != 1 and star.month != 1:
                        ns = star
                        while ns.day != 1 and ns.month != 1:
                            ns += dateutil.relativedelta.relativedelta(days=+1)
                    else:
                        ns = star + dateutil.relativedelta.relativedelta(years=+1)
                case _:
                    print("invalid bydur.")
                    exit()

            date = (star.year, star.month, star.day)
            nums = []
            for habit in lis:
                try:
                    string = strings[habit]
                except:
                    string = habit
                    while len(string) < max:
                        string = " " + string
                    string = "" + string + " "

                if habit == "overall":
                    ended = False
                    try:
                        num = math.floor(statistics.mean(nums))
                    except:
                        await interaction.response.send_message("you have no habits. please consider getting a life or using `/edith` to add some new habits.")
                        ended = True
                    else:
                        match num:
                            case 0:
                                string += "  "
                            case 1:
                                string += "░░"
                            case 2:
                                string += "▒▒"
                            case 3:
                                string += "▓▓"
                            case 4:
                                string += "██"
                elif habit == "":
                    if not ended:
                        num = int(round(statistics.mean(nums)/4, 2)*100)
                        if num < 10:
                            num = "0" + str(num)
                        elif num == 100:
                            num = "!!"
                        string += str(num)
                elif habit in ["yy", "mm", "dd"]:
                    match habit:
                        case "yy":
                            if ps.year != star.year or star == st or star == end:
                                if star.year < 10:
                                    string += "0" + str(star.year)
                                else:
                                    string += str(star.year)[-2:]
                            else:
                                string += "  "
                        case "mm":
                            if ps.month != star.month or star == st or star == end:
                                if star.month < 10:
                                    string += "0" + str(star.month)
                                else:
                                    string += str(star.month)
                            else:
                                string += "  "
                        case "dd":
                            if star.day == 1:
                                string += "01"
                            elif star.day == 5:
                                string += "05"
                            elif star.day == 30 and calendar.monthrange(star.year, star.month)[1] in [30, 31] and star != st and star != end:
                                string += "  "
                            elif star.day % 5 == 0 or star == st or star == end or star.day - ps.day != 1:
                                if star.day < 10:
                                    string += "0" + str(star.day)
                                else:
                                    string += str(star.day)
                            else:
                                string += "  "
                else:
                    snums = []
                    sta = star
                    while sta < ns:
                        try:
                            num = data[habit][str(sta.year)][sta.month-1][sta.day-1]
                        except:
                            newyear(data, habit, date[0])
                            num = 0
                        nums.append(num)
                        snums.append(num)
                        sta += dateutil.relativedelta.relativedelta(days=+1)
                    
                    num = math.floor(statistics.mean(snums))
                    match num:
                        case 0:
                            string += "  "
                        case 1:
                            string += "░░"
                        case 2:
                            string += "▒▒"
                        case 3:
                            string += "▓▓"
                        case 4:
                            string += "██" 
                strings[habit] = string
            ps = star
            star = ns
            colno += 1

        msg = ""
        for x in strings:
            msg += (strings[x] + "\n")
        if not ended:
            await interaction.response.send_message(f"```{msg}```")
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

@bot.slash_command(name = "yearm", description = "show a yearly calendar heatmap.")
async def yearm(interaction, year: int, habit: str):
    cursor = mydb.cursor(buffered=True)
    maindb = os.getenv("database")
    cursor.execute(f"use {maindb};")
    cursor.execute("select * from accounts;")
    result = cursor.fetchall()

    if checklog(interaction.user.id):
        for row in result:
            if row[6] == str(interaction.user.id):
                data = json.loads(row[3])
                break

        stat = data[habit][str(year)]
        yearindow = [[], [], [], [], [], [], []]
        strings = []
        months = [0]
        weekcount = 0
        def twkd(date):
            if date.weekday() == 6:
                return 0
            else:
                return date.weekday() + 1
        for x in range(twkd(dt.date(dt.date.today().year,1,1))):
            yearindow[x].append(0)
        for x in range(12):
            for y in range(len(stat[x])):
                yearindow[twkd(dt.date(dt.date.today().year,x+1,y+1))].append(int(stat[x][y]))
                if twkd(dt.date(dt.date.today().year,x+1,y+1)) == 6:
                    weekcount += 1
            months.append(weekcount)

        months = months[:-1]
        monstr = "    "
        colno = 0
        for x in range(len(months)):
            while len(monstr) < months[x] * 2 + 6:
                monstr = monstr + ("  ")
            if x+1 < 10:
                monstr = monstr + "0" + str(x+1)
            else:
                monstr = monstr + str(x+1)
            colno += 1
        strings.append(monstr)

        colno = 0
        for x in range(len(yearindow)):
            days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
            string = " " + days[x] + "  "
            for y in yearindow[x]:
                try:
                    int(y) 
                except:
                    string += "  "
                else:
                    match y:
                        case 0:
                            string += "  "
                        case 1:
                            string += "░░"
                        case 2:
                            string += "▒▒"
                        case 3:
                            string += "▓▓"
                        case 4:
                            string += "██"
            strings.append(string)
            colno += 1

        msg = ""
        for x in strings:
            msg += x + "\n"
        await interaction.response.send_message(f"```{msg}```")
    else:
        await interaction.response.send_message("you are not logged in. if you would like to log in, try `/login` first.", ephemeral=True)

bot.run(TOKEN)
