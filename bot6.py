import discord, discord.utils, asyncio, requests, bs4, datetime, os, time, aiohttp, re, sys
from discord.ext import commands
from discord.utils import get
from discord.utils import find
from dateutil import parser
from tinydb import TinyDB, Query
from fuzzywuzzy import process, fuzz
import pickle, codecs
from bs4 import BeautifulSoup as bsw
from time import gmtime, strftime

#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(filename=f'''WAB.log''', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)

intents = discord.Intents(messages=True, guilds=True, members=True)
intents.typing = True
intents.presences = False #True


db = TinyDB('Wiki/authd.json')
Ft = Query()
gdb = TinyDB('Wiki/gsettings.json')
rdb = TinyDB('Wiki/responses.json')
tdb = TinyDB('Wiki/auth.json')
client=discord.AutoShardedClient(intents=intents)
#import RPi.GPIO as IO

#from requests import get


from mwoauth import ConsumerToken, Handshaker
from six.moves import input # For compatibility between python 2 and 3


# Consruct a "consumer" from the key/secret provided by MediaWiki

import config

token = open('tokens/wiki','r').read()
contok = open('tokens/ontok','r').read()
consec = open('tokens/onsec','r').read() 
m2ntok = open('tokens/m2ntok','r').read()
m2nsec = open('tokens/m2nsec','r').read()
tggtok=open('tokens/topgg2', 'r').read()
headers = {"Authorization" : tggtok}
ggurl = 'https://discordbots.org/api/bots/625962497165230080/stats'
dbggtok=open('tokens/dbgg','r').read()
geaders = {"Authorization" : dbggtok}
dbggurl = 'https://discord.bots.gg/api/v1/bots/625962497165230080/stats'

@client.event
async def on_connect():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'startup process...'))
    client.loop.create_task(oread())

@client.event
async def on_ready():
    print()
    print('_'*34)
    print(f'{client.user} is online')
    print('_'*34)
    print()

async def oread():
#    print('Entered ORead')

    await client.wait_until_ready()
 #   print('IsReady')

    smems = 0
    for g in client.guilds:
        smems = smems + len(g.members)
    msg = await client.get_channel(683550524611624998).fetch_message(683554590238441499)
    await msg.edit(content=f'''Servers: {len(client.guilds):,} Members: {smems:,}''')
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'''/auth in {len(client.guilds)} servers'''))
            
@client.event
async def on_member_join(member):
    db = TinyDB('Wiki/authd.json')
    Ft = Query()
    gdb = TinyDB('Wiki/gsettings.json')
    rdb = TinyDB('Wiki/responses.json')
    tdb = TinyDB('Wiki/auth.json')
    botlists = [110373943822540800, 264445053596991498]
    if member.guild.id in botlists or member.bot == True:
        return
    try:
        ismira = gdb.search(Ft.id==member.guild.id)[0]['mira']
    except:
        gdb.upsert({'mira':0, 'id':member.guild.id},Ft.id==member.guild.id)
    if 1==1:
        try:
            settings = gdb.search(Ft.id==member.guild.id)[0]
            lang = settings['lang']
        except:
            lang = "EN"
        t = rdb.search(Ft.lang==lang)[0]
        gdb = TinyDB('Wiki/gsettings.json')
        rdb = TinyDB('Wiki/responses.json')
        try:
            if member.guild.id == 434994995410239488:
                tdbs = [TinyDB('WWauth.json'), TinyDB('Wiki/mauth.json'), TinyDB('Wiki/fauth.json')]
            elif gdb.search(Ft.id==member.guild.id)[0]['mira'] == 0:
                tdbs = [TinyDB('Wiki/auth.json')]
            elif gdb.search(Ft.id==member.guild.id)[0]['mira'] == 1:
                tdbs = [TinyDB('Wiki/mauth.json')]
            else:
                tdbs = [TinyDB('Wiki/fauth.json')]
        except:
            gdb.upsert({'mira':0, 'id':member.guild.id},Ft.id==member.guild.id)
            tdb = TinyDB('Wiki/auth.json')
        for tdb in tdbs:
            if tdb.search(Ft.id==member.id) != []:
                mem = tdb.search(Ft.id==member.id)[0]
                if gdb.search(Ft.id==member.guild.id)[0]['arole'] != 0:
                    try:
                        await member.add_roles(get(member.guild.roles, id=gdb.search(Ft.id==member.guild.id)[0]['arole']))
                    except:
                        print(f"Error adding role on join for {member.name}({member.id}) in {member.guild.name}({member.guild.id}) with roleID {gdb.search(Ft.id==member.guild.id)[0]['arole']} at {datetime.datetime.now()}")
                found = 0
                fmsg = 0
                if lang == 'RU':
                    gen = requests.get(f"https://ru.wikipedia.org/w/api.php?action=query&list=users&ususers={mem['wnam']}&usprop=gender&format=json")
                    gen.raise_for_status()
                    gen = gen.json()
                    if gen['query']['users'][0]['gender'] == 'female':
                        tauthas = t['authas'].replace('авторизован', 'авторизована').replace('Участник', 'Участница')
                    else:
                        tauthas = t['authas']
                else:
                    tauthas = t['authas']                
                try:
                    async for msg in client.get_channel(gdb.search(Ft.id==member.guild.id)[0]['achan']).history(limit=999):
                        if str(member.id) in msg.content:
                            fmsg = msg
                            found = 1
                except:
                    print(f'Get channel history failed for {member.guild}')
                if found == 0:
                    try:
                        await client.get_channel(gdb.search(Ft.id==member.guild.id)[0]['achan']).send(f"{t['predID']}<@{member.id}> {tauthas}{mem['wnam']} {t['postID']}")
                    except:
                       print(f"Couldn't post welcome message for {member.guild}")
                else:
                    try:
                        await fmsg.edit(content=f"{t['predID']}<@{member.id}> {tauthas}{mem['wnam']} {t['postID']}")
                    except:
                        pass
            if gdb.search(Ft.id==member.guild.id)[0]['wmsgs'] != 'N':
                if ismira == 1:
                    t2auth = t['2auth'].replace('Wikipedia','Miraheze').replace('Wikimedia','Miraheze')
                elif ismira == 2:
                    t2auth = t['2auth'].replace('Wikipedia','Fandom').replace('Wikimedia','Miraheze')
                else:
                    t2auth = t['2auth']
                if gdb.search(Ft.id==member.guild.id)[0]['wmsgs'] == 555:
                    try:
                        await member.create_dm()
                        if tdb.search(Ft.id==member.id) == []:
                            msg = await member.dm_channel.send(f"{t['Welcome']} {member.mention}{t2auth}")
                            await msg.add_reaction(emoji = '👋')
                        else:
                            msg = await member.dm_channel.send(f"{t['Welcome']} {member.mention}! {t['alrauth']}{tdb.search(Ft.id==member.id)[0]['wnam']}{t['alrauth2']}")
                            await msg.add_reaction(emoji = '👋')
                    except:
                        print(f'Cant welcome {member.display_name} in {member.guild.name}')
                else:
                    chanz = client.get_channel(gdb.search(Ft.id==member.guild.id)[0]['wmsgs'])
                    if member.guild.id != 697848129185120256:
                        if tdb.search(Ft.id==member.id) == []:
                            msg = await chanz.send(f"{t['Welcome']} {member.mention}{t2auth}")
                            await msg.add_reaction(emoji = '👋')
                        else:
                            msg = await chanz.send(f"{t['Welcome']} {member.mention}! {t['alrauth']}{tdb.search(Ft.id==member.id)[0]['wnam']}{t['alrauth2']}")
                            await msg.add_reaction(emoji = '👋')
                    else:
                        if tdb.search(Ft.id==member.id) == []:
                            msg = await chanz.send(f"{t['Welcome']} {member.mention}{t2auth}")
                            await msg.add_reaction(emoji = '👋')
                        else:
                            msg = await chanz.send(f"{t['Welcome']} {member.mention}! {t['alrauth']}{tdb.search(Ft.id==member.id)[0]['wnam']}{t['alrauth2']}")
                            await msg.add_reaction(emoji = '👋')                        
    smems = 0
    for g in client.guilds:
        try:
            smems = smems + g.member_count
        except:
            pass
        #print(f'{g.name} has {g.member_count:,} members')

    msg = await client.get_channel(683550524611624998).fetch_message(683554590238441499)
    await msg.edit(content=f'''Servers: {len(client.guilds):,} Members: {smems:,}''')        

@client.event
async def on_guild_join(guild):
    gdb = TinyDB('Wiki/gsettings.json')
    Ft = Query()
    if gdb.search(Ft.id==guild.id) == []:
        gdb.upsert({'id':guild.id, 'nam':guild.name, 'achan':0, 'arole':0, 'lang':'EN', 'wmsgs':'N', 'ablock':0, 'mira':0}, Ft.id==guild.id)
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'''.auth in {len(client.guilds)} servers'''))
    payload = {'server_count'  : len(client.guilds)}
    payloag = {'guildCount' : len(client.guilds)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(ggurl, data=payload, headers=headers)
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(dbggurl, data=payloag, headers=geaders)
    print(f'Updated TopGG & DBGG server number to {len(client.guilds)}')  

    smems = 0
    for g in client.guilds:
        smems = smems + g.member_count
    msg = await client.get_channel(683550524611624998).fetch_message(683554590238441499)
    await msg.edit(content=f'''Servers: {len(client.guilds):,} Members: {smems:,}''')
    embed=discord.Embed(title=f'Joined {guild.name} - {guild.owner}', color=8690468, description=f'''{guild.region}\n{guild.member_count}''')
    mro = '⛔'
    sme = '⛔'
    are = '⛔'
    ere = '⛔'
    c = await guild.fetch_member(625962497165230080)
    if c.guild_permissions.manage_roles == True:
        mro = '✅'
    if c.guild_permissions.send_messages == True:
        sme = '✅'
    if c.guild_permissions.add_reactions == True:
        are = '✅'
    if c.guild_permissions.external_emojis == True:
        ere = '✅'
    embed.add_field(name='Perms', value=f'{mro} Manage Roles\n{sme} Send Messages\n{are} Add Reactions\n{ere} External Reactions')
    embed.set_thumbnail(url=guild.icon_url)
    await client.get_channel(702683724407373855).send(embed=embed)

@client.event
async def on_guild_remove(guild):
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'''.auth in {len(client.guilds)} servers'''))
    payload = {'server_count'  : len(client.guilds)}
    payloag = {'guildCount' : len(client.guilds)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(ggurl, data=payload, headers=headers)
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(dbggurl, data=payloag, headers=geaders)
    print(f'Updated TopGG & DBGG server number to {len(client.guilds)}')      
    smems = 0
    for g in client.guilds:
        smems = smems + g.member_count
    msg = await client.get_channel(683550524611624998).fetch_message(683554590238441499)
    await msg.edit(content=f'''Servers: {len(client.guilds):,} Members: {smems:,}''')
    embed=discord.Embed(title=f'Left {guild.name} - {guild.owner}', color=13447987, description=f'''{guild.region}\n{guild.member_count}''')
    embed.set_thumbnail(url=guild.icon_url)
    await client.get_channel(702683724407373855).send(embed=embed)

@client.event
async def on_message(message):
    try:
        if message.guild.id == 394606131433177099:
            return
    except:
        pass
    try:
        if message.guild.id != 434994995410239488 and message.content[:1] != '.' and message.content.replace('<','').replace('>','').replace('@','').replace('!','') != '625962497165230080':
            return
    except:
        pass       
    
    try:                                                ##### Auth'd members in auth list
        if message.guild.id == 221049808784326656:
            trashval = 1
    except:
        pass
    else:
        try:
            if message.content.split()[0] == '.nauth':
                srv = client.get_guild(221049808784326656)
                arole = get(srv.roles, id=642751332263919618)
                try:
                    role = srv.get_role(int(message.content.split()[1]))
                    nauth = []
                    for member in role.members:
                        if arole not in member.roles:
                            nauth.append(f"{member.name}#{member.discriminator} - {member.id}")
                    if len(nauth) != 0:
                        nauth1 = f"```{role.name} role members that aren't authd.\n\n" + "\n".join(nauth) + "```"
                    else:
                        nauth1 = f"All members in the {role.name} role are authenticated."
                    await message.reply(nauth1)
                except Exception as e:
                    await message.reply(f"Command failed:\n{e}")
        except:
            pass
                
    
        
    
    logchan = client.get_channel(626426940403744779)  
    db = TinyDB('Wiki/authd.json')
    Ft = Query()
    gdb = TinyDB('Wiki/gsettings.json')
    rdb = TinyDB('Wiki/responses.json')
    tdb = TinyDB('Wiki/auth.json')
    settingcmds = ".miraheze .setblock .setrole .setwchan .setachan .setlang".split(' ')

    if not isinstance(message.channel, discord.DMChannel):   #IGNORE MIRAHEZE SERVERS

        try:
            ismira = gdb.search(Ft.id==message.guild.id)[0]['mira'] #message.guild.id == 697848129185120256 or message.guild.id == 407504499280707585:

        except:
            gdb.upsert({'mira':0, 'id':message.guild.id},Ft.id==message.guild.id)
            ismira = 0
        try:
            settings = gdb.search(Ft.id==message.guild.id)[0]
            lang=settings['lang']
        except:
            lang = "EN"
    else:
        if message.content.split(' ')[0] in settingcmds:
            await rply(message, 'Sorry, settings can only be set within servers.')
            return
        msers = []
        for g in client.guilds:                                                                                                        
            try:                                                                                                                       
                if g.get_member(message.author.id) is not None:                                                                        
                    msers.append(g)                                                                                                    
            except:                                                                                                                    
                pass                                                                                                                   
        mpc = 0                                                                                                                        
        for g in msers:                                                                                                                
            if len(g.members) > mpc:                                                                                                   
                mpc = len(g.members)                                                                                                   
                mpg = g                                                                                                                
        try:                                                                                                                           
            lang=gdb.search(Ft.id==mpg.id)[0]['lang']                                                                                  
        except:                                                                                                                        
            lang = "EN"                                                                                                                
    
    t = rdb.search(Ft.lang==lang)[0]
    if isinstance(message.channel, discord.DMChannel):
        ismira=0

    if message.content == '.auth': # and ismira == 0: #NOT MM

        mutmira = 0
        skip = 0
        if isinstance(message.channel, discord.DMChannel):
            ismira = 0
            for g in client.guilds:
                if g.get_member(message.author.id) is not None:
                    if gdb.search(Ft.id==g.id)[0]['mira'] == 1:
                        mutmira = 1
        else:
            if message.guild.id == 434994995410239488:
                skip = 1
        if skip == 0:
            limint = '' #Please note that roles being added and messages posted are temporarily not working. But authenticating will still add you into the database. The role and ping will all be added in bulk at a later time.'

            if mutmira == 1:
                afoot = f'In order to authenticate to a Miraheze or Fandom account, please use the .auth command within the server.\n{limint}'
            else:
                afoot = limint
            if ismira == 0:
                try:
                    await message.add_reaction('<a:typing:712290091002757190>')
                except:
                    print('Cant add typing react')
                if requests.get('https://wikiauthbot.toolforge.org/test/').text == 'Hello World!':
                    consumer_token = ConsumerToken(contok, consec)
                    sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

                    handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
                    sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

                    redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/wauth/{hex(message.author.id)}/') 
                else:
                    await client.get_channel(695443373292781599).send(f'WikiAuthBot (wiki auth): Failed to get test result from toolforge. Reverting to pythonanywhere.')
                    consumer_token = ConsumerToken(open('tokens/contok','r').read(), open('tokens/consec','r').read())
                    handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
                    redirect, request_token = handshaker.initiate(callback=f'https://1vork.pythonanywhere.com/wauth/{hex(message.author.id)}/')                     
                db = TinyDB('Wiki/authd.json')
                Ft = Query()
                rt = pickle.dumps(request_token, 0).decode()
                db.upsert({'id':message.author.id, 'request_token':rt, 'wikilang': f"https://{t['lang'].lower()}.wikipedia.org/w/index.php"}, Ft.id==message.author.id)
                await message.author.create_dm()
                try:
                    embed=discord.Embed(title='WikiAuthBot', description=f"{t['pmauth']} {redirect}",color=0xCCCCCC)
                    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/546848856650809344.png')
                    embed.set_footer(text=afoot)
                    await message.author.dm_channel.send(embed=embed)
                except:
                    await rply(message, f"{t['pmoff']} <@{message.author.id}> {t['pmoff2'].replace('GUILDNAME', message.guild.name)}")
                else:
                    try:
                        await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                        await message.add_reaction('📧')
                    except:
                        print('Cant add email react')
        if isinstance(message.channel, discord.DMChannel):
            return
           
    if message.content == '.auth' and ismira == 1 and message.guild.id != 434994995410239488: #message.author.id == 140902977618706432:#message.content == '.auth' and message.guild.id == 407504499280707585: #MM

        m2ntok = open('tokens/m2ntok','r').read()
        m2nsec = open('tokens/m2nsec','r').read()
        try:
            await message.add_reaction('<a:typing:712290091002757190>')
        except:
            print('Cant add typing react')
        if requests.get('https://wikiauthbot.toolforge.org/test/').text == 'Hello World!':
            consumer_token = ConsumerToken(m2ntok, m2nsec)
            handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/mauth/{hex(message.author.id)}/')
        else:
            await client.get_channel(695443373292781599).send(f'WikiAuthBot (mira auth): Failed to get test result from toolforge. Reverting to pythonanywhere.')
            consumer_token = ConsumerToken(open('tokens/montok','r').read(), open('tokens/monsec','r').read())
            handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://1vork.pythonanywhere.com/mauth/{hex(message.author.id)}/')
        db = TinyDB('Wiki/authd.json')
        Ft = Query()
        rt = pickle.dumps(request_token, 0).decode()
        db.upsert({'id':message.author.id, 'mrequest_token':rt, 'mikilang': f"https://meta.miraheze.org/w/index.php"}, Ft.id==message.author.id)
        await message.author.create_dm()
        try:
            embed=discord.Embed(title='WikiAuthBot', description=f"{t['pmauth'].replace('Wikimedia', 'Miraheze')} {redirect}", color=0xfcba03)
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/446641749142798339.png')
            await message.author.dm_channel.send(embed=embed)
        except:
            await rply(message, f"You have private messages disabled <@{message.author.id}>, please enable them by hitting the arrow next to **{message.guild.name}**, selecting **Privacy Settings**, change it's value, then type **.auth** again.")
        else:
            try:
                await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                await message.add_reaction('📧')
            except:
                print('Cant add email react')          

    if message.content.split(' ')[0] == '.auth' and ismira == 2:
        msg = message.content.split(' ')
        if len(msg) != 2:
            await rply(message, f"Hi there, to authenticate to your Fandom account, ensure you have editted a Fandom account to include your Discord username per below, then type **.auth** again followed by your profile link i.e. `.auth https://community.fandom.com/wiki/User:IVORK`\nhttps://i.imgur.com/sEokWt8.png")
            return
        url = msg[1]
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://

            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...

            r'localhost|' #localhost...

            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip

            r'(?::\d+)?' # optional port

            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if (re.match(regex, url) is not None) == False:
            await rply(message, f"Sorry {message.author.mention}, that does not appear to be a well-formed profile URL, try something like `.auth https://community.fandom.com/wiki/User:IVORK`")
            return
        try:
            try:
                await message.add_reaction('<a:typing:712290091002757190>')
            except:
                pass
            wnam = url.split(':')[-1]
            if '/' in wnam:
                print(wnam)
                wnam = wnam.split('/')[0]
            if '?' in wnam:
                print(wnam)
                wnam = wnam.split('?')[0]
            com = url.split('.com')[0].split('/')[-1] + '.com'
            dat = requests.get(url)
            soup = bsw(dat.text, 'html.parser')
            md = soup.findAll("div", {"class": "wds-dropdown__content"})
            li = []
            for e in md:
                li.append(str(e.text))
            for e in li:
                if 'Username:' in e:
                    to = (e.replace('\t','').replace('\n',''))[10:].split('#')
            if to[0].lower() != message.author.name.lower() or to[1] != message.author.discriminator:
                print(f"{to[0]}:{message.author.name} & {to[1]}:{message.author.discriminator}")
                raise Exception
            else:
                raise IndexError
            gdb = TinyDB('Wiki/gsettings.json')
            fdb = TinyDB('Wiki/fauth.json')
            Ft = Query()
            ibe = requests.get(f'https://www.wikia.com/api/v1/Wikis/ByString?string={com}&limit=1&batch=1&includeDomain=true').json()['items'][0]['id']
            try:
                pcom = fdb.search(Ft.id==message.author.id)[0]['com']
                exi = 0
                for e in pcom.split('+'):
                    if str(ibe) == str(e):
                        exi = 1
                if exi == 0:
                    fcom = pcom + f'+{ibe}'
            except:
                fcom = str(ibe)
            fdb.upsert({'id':message.author.id, 'wnam':wnam, 'com':fcom},Ft.id==message.author.id)            
            try:
                await message.add_reaction('✅')
            except:
                pass
        except IndexError:
            try:
                await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                await message.add_reaction(' ^{^t')
                await rply(message, f"""Sorry {message.author.mention}, I found an account `{to[0]}#{to[1]}` instead of your account `{message.author.name}#{message.author.discriminator}`. Please edit this value to reflect your current account.""")
            except:
                pass
        except Exception as e:
            print(e)
            try:
                await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                await message.add_reaction('⛔')
                await rply(message, f"Sorry {message.author.mention}, I could not find your Discord username `{message.author.name}#{message.author.discriminator}` through that link you provided. Please ensure you have editted your profile to add it.")
            except:
                pass
            return
        for g in client.guilds:
            try:
                ismira = gdb.search(Ft.id==g.id)[0]['mira']
            except:
                gdb.upsert({'mira':0, 'id':g.id},Ft.id==g.id)
                ismira == 0
            if ismira == 2:
                try:
                    settings = gdb.search(Ft.id==g.id)[0]
                    lang = settings['lang']
                except:
                    lang = "EN"                      
                if g.get_member(message.author.id) is not None:
                    #blocked = 0

                    if 1==1: #blocked == 0:

                        if settings['arole'] != 0:
                            try:
                                await message.author.add_roles(get(g.roles, id=settings['arole']))
                            except:
                                print(f"Couldn't add role to {message.author.name} in {g}")
                        if settings['achan'] != 0:
                            found = 0
                            fmsgs = []
                            async for msg in client.get_channel(settings['achan']).history(limit=999):
                                if str(message.author.id) in msg.content and msg.author == client.user and 'authenticated as User' in msg.content:
                                    fmsgs.append(msg)
                                    found = 1
                            if found == 0:
                                await client.get_channel(settings['achan']).send(f"{message.author.mention} authenticated as User:{wnam}")
                            else:
                                for fmsg in fmsgs:
                                    try:
                                        await fmsg.edit(content=f"{message.author.mention} authenticated as User:{wnam}")
                                    except:
                                        print(f"Couldn't update message for {message.author.name}")                    
        await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)

    if message.content == '.auth' and message.guild.id == 434994995410239488:
        m2ntok = open('tokens/m2ntok','r').read()
        m2nsec = open('tokens/m2nsec','r').read()
        try:
            await message.add_reaction('<a:typing:712290091002757190>')
        except:
            print('Cant add typing react')
        consumer_token = ConsumerToken(m2ntok, m2nsec)
        sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

        handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
        redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/mauth/{hex(message.author.id)}/')
        sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

        db = TinyDB('Wiki/authd.json')
        Ft = Query()
        rt = pickle.dumps(request_token, 0).decode()
        db.upsert({'id':message.author.id, 'mrequest_token':rt, 'mikilang': f"https://meta.miraheze.org/w/index.php"}, Ft.id==message.author.id)    
        ######################################################

        consumer_token = ConsumerToken(contok, consec)
        sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

        handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
        wedirect, wequest_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/wauth/{hex(message.author.id)}/')
        sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

        db = TinyDB('Wiki/authd.json')
        Ft = Query()
        rt = pickle.dumps(wequest_token, 0).decode()
        db.upsert({'id':message.author.id, 'request_token':rt, 'wikilang': f"https://{t['lang'].lower()}.wikipedia.org/w/index.php"}, Ft.id==message.author.id)  
        await message.author.create_dm()
        try:
            embed=discord.Embed(title='WikiAuthBot', description=f"**Click the relevant link below to authenticate:**\n<:mirahezelogo:446641749142798339> [Miraheze]({redirect})\n<:wikilogo:546848856650809344> [Wikimedia]({wedirect})")
            embed.set_footer(text='For any issues, please ping IVORK#0001 on this server')          
            await message.author.dm_channel.send(embed=embed)
        except:
            await rply(message, f"{t['pmoff']} <@{message.author.id}> {t['pmoff2'].replace('GUILDNAME', message.guild.name)}")
        else:
            try:
                await message.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                await message.add_reaction('📧')
            except:
                print('Cant add email react') 

    if message.content.split(' ')[0] == '.setblock':
        if ismira == 2:
            await rply(message, 'Sorry, this command is not setup for Fandom servers yet.')
            return
        if ismira == 1:
            await rply(message, "Sorry, this command is not supported on Miraheze servers currently.")
            return
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return
        val = message.content.split(' ')
        valrets = ['yes', 'no', 'y', 'n']
        if len(val) < 2:
            await rply(message, t["YN2B"])
            return
        if val[1].lower() not in valrets:
            await rply(message, t["YN2B"])
            return
        val = val[1].lower()
        if val == 'yes' or val == 'y':
            gdb.upsert({'ablock':1, 'id':message.guild.id},Ft.id==message.guild.id)
        else:
            gdb.upsert({'ablock':0, 'id':message.guild.id},Ft.id==message.guild.id)
        await rply(message, t['YNBS'].replace("VAL", val.upper()))

    if message.content.split(' ')[0] == '.settype':
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return
        val = message.content.split(' ')
        valrets = ['w', 'm', 'f']
        if len(val) < 2:
            await rply(message, t['YN2M'])
            return
        if val[1].lower() not in valrets:
            await rply(message, t['YN2M'])
            return
        val = val[1].lower()
        if val == 'w':
            gdb.upsert({'mira':0, 'id':message.guild.id},Ft.id==message.guild.id)
            valr = '<:Wikipedia:542102882741125122> Wikimedia'
        elif val == 'm':
            gdb.upsert({'mira':1, 'id':message.guild.id},Ft.id==message.guild.id)
            valr = '<:mirahezelogo:446641749142798339> Miraheze'
        elif val == 'f':
            await rply(message, "Sorry, Fandom is no longer supported.")
            return
            gdb.upsert({'mira':2, 'id':message.guild.id},Ft.id==message.guild.id)
            valr = '<:Fandom:760427808069255170> Fandom' 
        await rply(message, t['YNMS'].replace("VAL", valr))

    if message.content.split(' ')[0] == '.whois':
        if ismira == 2:
            await rply(message, 'Sorry, this command is not setup for Fandom servers yet.')
            return
        if ismira == 1:
            apiurl = "https://meta.miraheze.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json"
            GAIurl = "https://meta.miraheze.org/w/index.php?title=Special%3ACentralAuth/"
            tdb = TinyDB('Wiki/mauth.json')
            col = 0xfcba03
        else:
            apiurl = "https://en.wikipedia.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json"
            GAIurl = "https://{t['lang'].lower()}.wikipedia.org/w/index.php?title=Special%3ACentralAuth/"
            tdb = TinyDB('Wiki/auth.json')
            col = 0xCCCCCC
        msg = message.content.split(' ')
        if len(msg) == 1:
            try:
                usr = tdb.search(Ft.id==message.author.id)[0]
            except:
                await rply(message, t["notauthd"].replace('That user',message.author.mention))
                return
        else:
            try:
                usr = tdb.search(Ft.id==int("".join(filter(str.isdigit, msg[1]))))[0]
            except Exception as e:
                mems = []
                for m in message.guild.members:
                    mems.append(m.display_name)
                f = 0
                for n in mems:
                    if message.content[7:].lower() in n.lower():
                        f = 1   
                        mat = (n, 100)
                if f == 0:        
                    mat = process.extractOne(message.content[7:],mems, scorer=fuzz.ratio)
                    print(f'{mat} from {message.content[7:]} in {message.guild.name}')
                    if mat[1] < 60:
                        await rply(message, t["Cantfindusedisplayorid"].replace('unam', message.content[7:])) #f"I couldn't find a user by the name of *{message.content[7:]}*. Make sure you are using their display name, or use their UserID.")

                        return
                for m in message.guild.members:
                    if mat[0] == m.display_name:
                        to = m
                        break
                try:
                    usr = tdb.search(Ft.id==to.id)[0]
                except:
                    await rply(message, t["notauthd"].replace('That user',to.display_name))
                    return
        async with message.channel.typing():
            #usra = await message.guild.fetch_member(int(msg[1]))

            dat = requests.get(apiurl.replace("{usr['wnam']}",usr['wnam']))
            dat.raise_for_status()
            dat = dat.json()['query']['globaluserinfo']
            try:
                if dat['groups'] != []:
                    ggps = f"{t['gGroups:']} {', '.join(dat['groups'])}"
                else:
                    ggps = ''
            except:
                await rply(message, '''Sorry, this user's authentication appears to be outdated, they will need to re-auth to fix this.''')
                return
            #embed=discord.Embed(title=f"{usr['wnam']}", description=f"Registered: {dat['registration'].split('T')[0]}\nHome: {dat['home']}\n{ggps}", url=f"https://en.wikipedia.org/w/index.php?title=Special%3ACentralAuth/{usr['wnam'].replace(' ', '+')}")

            #wiks = das['query']['globaluserinfo'].sort(key=lambda k: k['merged'].get('editcount', 0), reverse = True)

            wiki=[]
            edits = 0
            for s in dat['merged']:
                if s['editcount'] > 0:
                    edits = edits + s['editcount']
                    try:
                        if s['groups'] == 'groups':
                            raise IndexError
                        gps = f"{t['Groups:']} {', '.join(s['groups'])}"
                        inl = False
                    except Exception as e:
                        gps = ''
                        inl = True
                    wiki.append({'wik':s['wiki'], 'ec':s['editcount'], 'gps':gps, 'inl':inl})
            wiki = sorted(wiki, key = lambda i: i['ec'], reverse=True)
            blkd = ''
            indefd = 0
            for w in dat['merged']:
                if 'blocked' in str(w):
                    try:
                        if w['blocked']['reason'] == '':
                            reas = '<!---No reason provided--->'
                        else:
                            reas = w['blocked']['reason']
                        if blkd == '':
                            blkd = f"**{w['wiki']}** ({w['blocked']['expiry']})\n  *{reas}*"
                        else:
                            blkd = f"{blkd}\n**{w['wiki']}** ({w['blocked']['expiry']})\n  *{reas}*"
                        if w['blocked']['expiry'].lower() == 'infinity':
                            indefd = 1
                    except:
                        print(f"Got blocked but not err for {usr['wnam']}")
            if blkd != '':
                blkd = f"\n<:declined:359850777453264906> **BLOCKED**\n{blkd}"
            embed=discord.Embed(title=f"{usr['wnam']}", description=f"Discord: <@{usr['id']}>\n{t['Registered:']} {dat['registration'].split('T')[0]}\n{t['Home:']} {dat['home']}\n{t['Total_edits:']} {edits:,}\n{ggps}{blkd}\n"[:2040], url=f"{GAIurl}{usr['wnam'].replace(' ', '+')}".replace("{t['lang'].lower()}",t['lang'].lower()),color=col)
            i = 1
            for s in wiki:
                if i < 11:
                    embed.add_field(name=s['wik'], value=f"{t['Edits:']} {s['ec']:,}\n{s['gps']}", inline=s['inl']) 
                    i += 1
            then = parser.parse(dat['registration'])
            for x in dat['merged']:
                if parser.parse(x['timestamp']) < then:
                    then = parser.parse(x['timestamp'])
            if i > 7:
                embed.set_footer(text=t['max8'])          
            if (datetime.datetime.now(datetime.timezone.utc)-then).days > 6570 and edits > 150000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/1/12/Editor_-_lapis_matter_iv.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 5840 and edits > 132000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/9/91/Editor_-_lapis_matter_iii.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 5110 and edits > 11400:
                med = 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Editor_-_lapis_matter_ii.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 4380 and edits > 96000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/8/85/Editor_-_lapis_philosophorum_superstar.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 3650 and edits > 78000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/0/00/Editor_-_orichalcum_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 2920 and edits > 60000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Editor_-_bufonite_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 2555 and edits > 51000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Editor_-_platinum_star_II.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 2190 and edits > 42000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/8/86/Editor_-_platinum_star_I.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 1825 and edits > 33000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/4/4a/Editor_-_rhodium_star_III.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 1642 and edits > 28500:
                med = 'https://upload.wikimedia.org/wikipedia/commons/1/1f/Editor_-_rhodium_star_II.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 1460 and edits > 24000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Editor_-_rhodium_star_I.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 1277 and edits > 20000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Editor_-_gold_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 1095 and edits > 16000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/0/06/Editor_-_silver_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 912 and edits > 12000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Editor_-_bronze_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 730 and edits > 8000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/5/53/Editor_-_iron_star.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 547 and edits > 6000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Editor_-_gold_ribbon_-_3_pips.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 365 and edits > 4000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/c/c2/Editor_-_silver_ribbon_-_2_pips.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 182 and edits > 2000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/6/67/Editor_-_bronze_ribbon_-_1_pip.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 91 and edits > 1000:
                med = 'https://upload.wikimedia.org/wikipedia/commons/f/f3/Editor_-_blue_ribbon_-_0_pips.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 30 and edits > 200:
                med = 'https://upload.wikimedia.org/wikipedia/commons/e/e7/Editor_-_white_ribbon_-_0_pips.jpg'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 23 and edits > 150:
                med = 'https://upload.wikimedia.org/wikipedia/commons/7/74/Registered_editor_badge_with_tildes.jpg'    
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 15 and edits > 100:                    
                med = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Registered_Editor_lv2.svg/222px-Registered_Editor_lv2.svg.png'
            elif (datetime.datetime.now(datetime.timezone.utc)-then).days > 8 and edits > 50:
                med = 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Registered_Editor_lv3.svg/222px-Registered_Editor_lv3.svg.png'
            else:
                med = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Registered_Editor_lv4.svg/222px-Registered_Editor_lv4.svg.png'
            embed.set_thumbnail(url=med)
        try:
            if message.guild.id == 221049808784326656:
                rchan = client.get_channel(737668131190865920).send
                if message.channel.send != rchan:
                    text = f'<@{message.author.id}>'
                else:
                    text = None
                    rchan = message.reply
            else:
                raise Exception
        except:
            rchan = message.reply
            text = None
        await rchan(content=text,embed=embed)
        try:
            if settings['ablock'] == 1 and indefd == 1:
                role = role=get(message.guild.roles, id=gdb.search(Ft.id==message.guild.id)[0]['arole'])
                mem = message.guild.get_member(usr['id'])
                if role in mem.roles:
                    if lang.lower() != 'ru':
                        await mem.remove_roles(role)
                        await rply(message, f"<:declined:359850777453264906> {mem.mention} you have been unauthenticated as this server does not permit indef blocked users to have the authenticated role.")
                    else:
                        await mem.remove_roles(role)
                        await rply(message, f"<:declined:359850777453264906> Роль ✓ удалена у бессрочно заблокированного участника {mem.name} (User:{usr['wnam']}).") #Removed role from <@{mem.id}> (User:{usr['wnam']}) due to currently being blocked.")

        except Exception as e:
            print(e)

    #if message.content == '.dauth':

    #    try:

    #        u = tdb.search(Ft.id==message.author.id)[0]['wnam']

    #        tdb.remove(Ft.id==message.author.id)

    #    except:

    #        await rply(message, "You don't appear to be in the database, you may have already been removed. Type **.auth** to authenticate again.")

    #    else:

    #        #tdb.remove(Ft.id==message.author.id)

    #        await rply(message, f"Your link to `User:{u}` has been successfully removed from the database.")



    if message.channel.id == 626426940403744779 and message.author.display_name == 'WikiOAuthBot':
        try:
            consumer_token = ConsumerToken(contok, consec)
            db = None
            gdb = None
            rdb = None
            tdb = None
            db = TinyDB('Wiki/authd.json')
            gdb = TinyDB('Wiki/gsettings.json')
            rdb = TinyDB('Wiki/responses.json')
            tdb = TinyDB('Wiki/auth.json')
            Ft = Query()        
            resp = message.content.split()
            diID = int(resp[2])
            sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

            handshaker = Handshaker(db.search(Ft.id == diID)[0]['wikilang'], consumer_token)
            sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

            oV = resp[4]
            oT = resp[6]
            request_token = pickle.loads(db.search(Ft.id == diID)[0]['request_token'].encode())
            response_qs=f'oauth_verifier={oV}&oauth_token={oT}'
            access_token = handshaker.complete(request_token, response_qs)
        except requests.exceptions.ConnectionError:
            eusr = await client.get_user(diID)
            await eusr.create_dm()
            await eusr.dm_channel.send("Sorry, I'm having connection issues to the WMF API, please try authenticating later. For continued issues, join the support server and let IVORK#0001 know via http://ivork.com")
            await client.get_channel(695443373292781599).send(f'wikioauth: Connection error for {eusr.name} ({eusr.id})')
            print(f'WMF API con error for user {eusr.name} ({eusr.id})')
            return
        except:
            await client.get_channel(695443373292781599).send('WikiAuthBot (wiki auth): Handled auth webhook from pythonanywhere')
            consumer_token = ConsumerToken(open('tokens/contok','r').read(), open('tokens/consec','r').read())
            db = None
            gdb = None
            rdb = None
            tdb = None
            db = TinyDB('Wiki/authd.json')
            gdb = TinyDB('Wiki/gsettings.json')
            rdb = TinyDB('Wiki/responses.json')
            tdb = TinyDB('Wiki/auth.json')
            Ft = Query()        
            resp = message.content.split()
            diID = int(resp[2])
            sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

            handshaker = Handshaker(db.search(Ft.id == diID)[0]['wikilang'], consumer_token)
            sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

            oV = resp[4]
            oT = resp[6]
            request_token = pickle.loads(db.search(Ft.id == diID)[0]['request_token'].encode())
            response_qs=f'oauth_verifier={oV}&oauth_token={oT}'        
            access_token = handshaker.complete(request_token, response_qs)
        identity = handshaker.identify(access_token)
        tdb.upsert({'id':diID, 'wnam':identity['username']}, Ft.id==diID)
        await message.add_reaction(emoji='✅')
        sne = 0
        uchkd = 0
        for g in client.guilds:
            try:
                mi = gdb.search(Ft.id==g.id)[0]['mira'] 
            except:
                gdb.upsert({'mira':0, 'id':g.id}, Ft.id==g.id)
                mi = 0
            if mi == 0:
                try:
                    settings = gdb.search(Ft.id==g.id)[0]
                    lang = settings['lang']
                except:
                    lang = "EN"
                t = rdb.search(Ft.lang==lang)[0]
                if g.get_member(diID) is not None:
                    blocked = 0
                    try:
                        if settings['ablock'] == 1:
                            if uchkd == 0:
                                dat = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json")
                                dat.raise_for_status()
                                dat = dat.json()           
                                if 'blocked' in str(dat).lower():
                                    ublocked = 1
                                uchkd = 1
                            if ublocked == 1:
                                try:
                                    await g.get_member(diID).create_dm()
                                    await g.get_member(diID).send(t['BlockAuth'].replace('GUILDNAME', g.name).replace('UNAM', identity['username']))                                                             
                                    blocked = 1
                                except:
                                    print(f"Couldn't message {identity['usernam']} about failed auth due to being blocked in {g.name}")                                                                         
                    except:
                        gdb.upsert({'ablock':0},Ft.id==g.id)
                    if blocked == 0:
                        try:
                            role=get(g.roles, id=gdb.search(Ft.id==g.id)[0]['arole'])
                        except:
                            print(f'Usual error with guild {g.name}')
                        mem = g.get_member(diID)
                        try:
                            await mem.add_roles(role)
                        except:
                            print(f"Couldn't add role({gdb.search(Ft.id==g.id)[0]['arole']}) to {mem.name}({mem.id}) in guild {g.name}({g.id})")
                        if sne == 0:
                            await g.get_member(diID).create_dm()
                            await g.get_member(diID).send(f"<:wikilogo:546848856650809344><:yesvote:359850124186353664> {identity['username']}")
                            sne = 1
                        #except Exception as e:

                        #    print(f'{g.name} {diID} 289 line error:\n{e}')

                        found = 0
                        fmsgs = []
                        if lang == 'RU':
                            gen = requests.get(f"https://ru.wikipedia.org/w/api.php?action=query&list=users&ususers={identity['username']}&usprop=gender&format=json")
                            gen.raise_for_status()
                            gen = gen.json()
                            if gen['query']['users'][0]['gender'] == 'female':
                                tauthas = t['authas'].replace('авторизован', 'авторизована').replace('Участник', 'Участница')
                            else:
                                tauthas = t['authas']
                        else:
                            tauthas = t['authas']
                        try:
                            async for msg in client.get_channel(gdb.search(Ft.id==g.id)[0]['achan']).history(limit=999):
                                if str(diID) in msg.content and msg.author == client.user:
                                    fmsgs.append(msg)
                                    found = 1
                            if found == 0:
                                await client.get_channel(gdb.search(Ft.id==g.id)[0]['achan']).send(f"{t['predID']}<@{diID}> {tauthas}{identity['username']} {t['postID']}")
                            else:
                                for fmsg in fmsgs:
                                    try:
                                        await fmsg.edit(content=f"{t['predID']}<@{diID}> {tauthas}{identity['username']} {t['postID']}")
                                    except:
                                        print(f"Couldn't update message for {identity['username']}")
                        except:
                            print(f"Couldn't update message for {identity['username']} in {g.name}({g.id})")
        await message.delete()

    if message.channel.id == 626426940403744779 and message.author.display_name == 'MikiOAuthBot':
        m2ntok = open('tokens/m2ntok','r').read()
        m2nsec = open('tokens/m2nsec','r').read()
        try:
            consumer_token = ConsumerToken(m2ntok, m2nsec)
            db = None
            gdb = None
            rdb = None
            tdb = None
            db = TinyDB('Wiki/authd.json')
            mdb = TinyDB('Wiki/mauth.json')
            gdb = TinyDB('Wiki/gsettings.json')
            Ft = Query()        
            resp = message.content.split()
            diID = int(resp[2])
            sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

            handshaker = Handshaker(db.search(Ft.id == diID)[0]['mikilang'], consumer_token)
            sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

            oV = resp[4]
            oT = resp[6]
            request_token = pickle.loads(db.search(Ft.id == diID)[0]['mrequest_token'].encode())
            response_qs=f'oauth_verifier={oV}&oauth_token={oT}'
            access_token = handshaker.complete(request_token, response_qs)
        except:
            await client.get_channel(695443373292781599).send('WikiAuthBot (mira auth): Handled auth webhook from pythonanywhere')
            consumer_token = ConsumerToken(open('tokens/montok','r').read(), open('tokens/monsec','r').read())
            db = None
            gdb = None
            rdb = None
            tdb = None
            db = TinyDB('Wiki/authd.json')
            mdb = TinyDB('Wiki/mauth.json')
            gdb = TinyDB('Wiki/gsettings.json')
            Ft = Query()        
            resp = message.content.split()
            diID = int(resp[2])
            sys.stdout = open(os.devnull, 'w') #TURN OFF CONSOLE PRINT

            handshaker = Handshaker(db.search(Ft.id == diID)[0]['mikilang'], consumer_token)
            sys.stdout = sys.__stdout__        #TURN ON  CONSOLE PRINT

            oV = resp[4]
            oT = resp[6]
            request_token = pickle.loads(db.search(Ft.id == diID)[0]['mrequest_token'].encode())
            response_qs=f'oauth_verifier={oV}&oauth_token={oT}'
            access_token = handshaker.complete(request_token, response_qs)
        identity = handshaker.identify(access_token)
        mdb.upsert({'id':diID, 'wnam':identity['username']}, Ft.id==diID)
        await message.add_reaction(emoji='✅')
        sne = 0
        uchkd = 0
        for g in client.guilds:
            try:
                ismira = gdb.search(Ft.id==g.id)[0]['mira']
            except:
                gdb.upsert({'mira':0, 'id':g.id},Ft.id==g.id)
                ismira == 0
            if ismira == 1:
                try:
                    settings = gdb.search(Ft.id==g.id)[0]
                    lang = settings['lang']
                except:
                    lang = "EN"
                rdb = TinyDB('Wiki/responses.json')
                t = rdb.search(Ft.lang==lang)[0]
                if g.get_member(diID) is not None:
                    blocked = 0
                        #try:

                        #    if settings['ablock'] == 1:

                        #        if uchkd == 0:

                        #            dat = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json")

                        #            dat.raise_for_status()

                        #            dat = dat.json()

                        #            if 'blocked' in str(dat).lower():

                        #                ublocked = 1

                        #            uchkd = 1

                        #        if ublocked == 1:

                        #            try:

                        #                await g.get_member(diID).create_dm()

                        #                await g.get_member(diID).send(t['BlockAuth'].replace('GUILDNAME', g.name).replace('UNAM', identity['username']))

                        #                blocked = 1

                        #            except:

                        #                print(f"Couldn't message {identity['usernam']} about failed auth due to being blocked in {g.name}")

                        #except:

                        #    gdb.upsert({'ablock':0},Ft.id==g.id)

                    if blocked == 0:
                        #try:

                        gdb = TinyDB('Wiki/gsettings.json')
                        mem = g.get_member(diID)
                        try:
                            await mem.add_roles(get(g.roles, id=gdb.search(Ft.id==g.id)[0]['arole']))
                        except:
                             print(f"Couldn't add role({gdb.search(Ft.id==g.id)[0]['arole']}) to {mem.name}({mem.id}) in guild {g.name}")
                        if sne == 0:
                            await g.get_member(diID).create_dm()
                            await g.get_member(diID).send(f"<:mirahezelogo:446641749142798339><:yesvote:359850124186353664> {identity['username']}")
                            sne = 1
                        #except Exception as e:

                        #    print(f'{g.name} {diID} 289 line error:\n{e}')

                        #else:

                        found = 0
                        fmsgs = []
                        try:
                            async for msg in client.get_channel(gdb.search(Ft.id==g.id)[0]['achan']).history(limit=999):
                                if str(diID) in msg.content and msg.author == client.user:
                                    fmsgs.append(msg)
                                    found = 1                                
                        except:
                            pass
                        else:
                            if found == 0:
                                await client.get_channel(gdb.search(Ft.id==g.id)[0]['achan']).send(f"{t['predID']}<@{diID}> {t['authas']}{identity['username']} {t['postID']}")
                            else:
                                for fmsg in fmsgs:
                                    try:
                                        await fmsg.edit(content=f"{t['predID']}<@{diID}> {t['authas']}{identity['username']} {t['postID']}")
                                    except:
                                        print(f"Couldn't update message for {identity['username']}")
        await message.delete()

    if message.content.split(' ')[0] == '.setlang':
        if ismira == 2:
            await rply(message, 'Sorry, this command is not setup for Fandom servers yet.')
            return
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return        
        langs = []
        for e in rdb.all():
            langs.append(e['lang'])
        if len(message.content.split(' ')) == 1:
            langs = []
            for e in rdb.all():
                langs.append(e['lang'])
            await rply(message, f"{t['sellang']}: {(', ').join(langs)}")
        elif message.content.split(' ')[1].upper() in langs:
            gdb.upsert({'lang':message.content.split(' ')[1].upper()}, Ft.id==message.guild.id)
            t = rdb.search(Ft.lang==message.content.split(' ')[1].upper())[0]
            await rply(message, f"{message.guild.name} {t['langset']} {message.content.split(' ')[1].upper()}.")
        else:
            await rply(message, f"{t['errlang']}: {(', ').join(langs)}")

    if message.content.split(' ')[0] == '.setrole':
        if gdb.search(Ft.id==message.guild.id)[0]['mira']==0:
            tdb = TinyDB('Wiki/auth.json')
        else:
            tdb = TinyDB('Wiki/mauth.json')
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return
        if len(message.content.split(' ')) == 1:
            await rply(message, f"{t['etagid']}")
            return
        if message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('&','').isnumeric():
            role = get(message.guild.roles, id=int(message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('&','')))
        else:
            role = None
        if role is not None:
            gdb.upsert({'arole':role.id}, Ft.id==message.guild.id)
            await rply(message, f"{t['aroleset']} {role.name}.\n{t['checku']}...")
            count = 0
            for m in message.guild.members:
                if tdb.search(Ft.id==m.id) != []:
                    try:
                       await m.add_roles(role)
                       count += 1
                    except:
                        await rply(message, f"""{t["cantass"]} {role.name} {t["cantass2"]}""")
                        return
            await rply(message, f"{t['havass'].replace('ROLENAME',role.name).replace('COUNT',str(count)).replace('LENMESSAGEGUILDMEMBERS',str(len(message.guild.members)))}")
        else:
            await rply(message, f"{t['nfindrole'].replace('MESCONTSPLI1', message.content.split(' ')[1])}")
        tdb = TinyDB('Wiki/auth.json')

    if message.content.split(' ')[0] == '.setachan':
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return
        if len(message.content.split(' ')) == 1:
            await rply(message, f"{t['etagid']}")
        elif message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('#','').isnumeric():
            chan = client.get_channel(int(message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('#','')))
            if chan is not None:
                try:
                    await chan.send(content='Test message',delete_after=1)
                except:
                    await rply(message, f'{t["cantsend"].replace("CHANNAME",chan.name)}')
                else:
                    gdb.upsert({'achan':chan.id}, Ft.id==message.guild.id)
                    await rply(message, f'{t["ssetachan"].replace("CHANNAME",chan.name)}')
            else:
                await rply(message, f"{t['cfchan'].replace('SPLITTOID',message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('&',''))}")
        elif message.content.split(' ')[1].lower() == 'none':
            gdb.upsert({'achan':0}, Ft.id==message.guild.id)
            await rply(message, f'{t["sremachan"]}')
        else:
            await rply(message, f"{t['etagid']}")

    if message.content.split(' ')[0] == '.setwchan':
        if ismira == 2:
            await rply(message, 'Sorry, this command is not setup for Fandom servers yet.')
            return
        if message.author.guild_permissions.manage_guild == False and message.author.id != 140902977618706432:
            await rply(message, f"<@{message.author.id}> {t['needmanser']}")
            return
        if len(message.content.split(' ')) == 1:
            await rply(message, f'{t["hsetwchan"]}')
        elif message.content.split(' ')[1].lower() == 'dm':
            gdb.upsert({'wmsgs':555}, Ft.id==message.guild.id)
            await rply(message, f'{t["ssetwchan"].replace("CHANNAME","DM")}')  
        elif message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('#','').isnumeric():
            chan = client.get_channel(int(message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('#','')))
            if chan is not None:
                try:
                    await chan.send(content='Test message',delete_after=1)
                except:
                    await rply(message, f'{t["cantsend"].replace("CHANNAME",chan.name)}')
                else:
                    gdb.upsert({'wmsgs':chan.id}, Ft.id==message.guild.id)
                    await rply(message, f'{t["ssetwchan"].replace("CHANNAME",chan.name)}')  
            else:
                await rply(message, f"{t['cfchan'].replace('SPLITTOID',message.content.split(' ')[1].replace('<','').replace('>','').replace('@','').replace('&',''))}")                            
        elif message.content.split(' ')[1].lower() == 'none':
            gdb.upsert({'wmsgs':'N'},Ft.id==message.guild.id)    
            await rply(message, f"{t['sremwchan']}")

    if message.content == '.help' or message.content.replace('<','').replace('>','').replace('@','').replace('!','') == '625962497165230080':
        gdb = TinyDB('Wiki/gsettings.json')
        try:
            if message.guild.id == 454409434676854786:
                return
        except:
            pass
        langs = []
        for e in rdb.all():
            langs.append(e['lang']) 
        langs.sort()
        if isinstance(message.channel, discord.DMChannel):
            AVAILLANG = f'{", ".join(langs)}'
            CURACHAN = CURWCHAN = CURROLE = CURSBLOCK = CURSMIRA = ''
            hauth = t['hauth']
        else:
            g = gdb.search(Ft.id==message.guild.id)[0]
            AVAILLANG = f'{", ".join(langs)} **({g["lang"]})**'
            if g['achan'] != 0:
                CURACHAN = f"**(<#{g['achan']}>)**"
            else: 
                CURACHAN = '**(N/A)**'
            if len(str(g['wmsgs'])) > 4:
                CURWCHAN = f"**(<#{g['wmsgs']}>)**"
            elif g['wmsgs'] == 555:
                CURWCHAN = '**(DM)**'
            else:
                CURWCHAN = '**(N/A)**'
            if g['arole'] != 0:
                CURROLE = f"**(<@&{g['arole']}>)**"
            else:
                CURROLE = "**(N/A)**"
            try:
                if g['ablock'] == 1:
                    CURSBLOCK = '**(Y)**'
                else:
                    CURSBLOCK = '**(N)**'
            except:
                gdb.upsert({'ablock':0}, Ft.id==message.guild.id)
                CURSBLOCK = '**(N)**'
            try:
                if g['mira'] == 1:
                    CURSMIRA = '**(<:mirahezelogo:446641749142798339>)**'
                elif g['mira'] == 0:
                    CURSMIRA = '**(<:Wikipedia:542102882741125122>)**'
                else:
                    CURSMIRA = '**(<:Fandom:760427808069255170>)**'
            except:
                gdb.upsert({'mira':0, 'id':message.guild.id}, Ft.id==message.guild.id)
                CURSMIRA = '**(?)**'
            if ismira == 1:
                hauth = t['hauth'].replace('Wikimedia','Miraheze')
            elif ismira == 2:
                hauth = t['hauth'].replace('Wikimedia','Fandom')
            else:
                hauth = t['hauth']
        embed=discord.Embed(title=f"WikiAuthBot - Help", description=f"**[Support Server](https://discord.gg/rcdBUwy)**\n\n{hauth.replace('*.','*/')}\n{t['hwho'].replace('*.','*/')}\n**.setlang *Language***{t['helpcommands'].split('**.setlang *Language***')[1].replace('AVAILLANG',AVAILLANG).replace('CURACHAN',CURACHAN).replace('CURROLE',CURROLE).replace('CURWCHAN',CURWCHAN).replace('CURSBLOCK', CURSBLOCK).replace('CURSMIRA', CURSMIRA).replace('*.','*/')}", color=0xCCCCCC)
        try:
            if message.guild.id == 221049808784326656:
                rchan = client.get_channel(737668131190865920).send
                if message.channel.send != rchan:
                    text = f'<@{message.author.id}>'
                else:
                    text = None
                    rchan = message.reply
            else:
                raise Exception
        except:
            rchan = message.reply
            text = None
        try:
            await rchan(content=text,embed=embed)
        except Exception as e:
            try:
                print(f"Failed on help send in {message.guild.name}({message.guild.id}), channel {message.channel.name}({message.channel.id}) from {message.author.name}#{message.author.discriminator}({message.author.id})")
            except:
                print(f"Failed on help send (failed on guild/chan too) from {message.author.name}#{message.author.discriminator}({message.author.id})")

    if message.content == '.translations':
        file=discord.File(f'Wiki/responses.json', filename='WikiAuthBot Translations.json')
        await rply(message, file=file)

    if message.content == ".status":                                                                    #STATUS

        msg = await client.get_channel(683550524611624998).fetch_message(683557246688690183)
        dmsg = msg.content.split('||')
        damsg = f'{dmsg[0]}*REDACTED*{dmsg[2]}'
        try:
            if message.guild.id == 221049808784326656:
                rchan = client.get_channel(737668131190865920).send
                if message.channel.send != rchan:
                    text = f'<@{message.author.id}>'
                else:
                    text = ''
                    rchan=message.reply
            else:
                raise Exception
        except:
            rchan = message.reply
            text = ''
        await rchan(f'{text}\n{damsg}')
    
    if message.content =='.invite':
        invlink = 'https://discord.com/api/oauth2/authorize?client_id=625962497165230080&permissions=2416298048&scope=applications.commands%20bot'
        await message.author.create_dm()
        try:
            await message.author.dm_channel.send(f'{t["invt"]}: <{invlink}>')
            await message.add_reaction(emoji='📧')
        except:
            await rply(message, f'{t["invt"]}: <{invlink}>')

async def rply(message, content=None, embed=None, file=None):
    globerr = client.get_channel(695443373292781599)
    try:
        await message.reply(content=content, embed=embed, file=file)
    except:
        try:
            await message.channel.send(content=content, embed=embed, file=file)
        except discord.errors.Forbidden:
            issz = []
            if embed != None:
                issz.append('***Embed Links***')
            if file != None:
                issz.append('***Attach Files***')
            try:
                if issz == []:
                    raise discord.errors.Forbidden
                await message.channel.send(f'Please allow me {"and".join(issz)} permissions for this channel for me to be able to respond.')
            except discord.errors.Forbidden:
                try:
                    await message.author.create_dm()
                    await message.author.dm_channel.send(content=f'I could not reply in that channel so am responding here instead:\n{content}', embed=embed, file=file)
                except Exception as e:
                    await globerr.send(f'rply failed even after DM due to {e} with message:\n{content}', embed=embed, file=file)
    embed=discord.Embed(title='UPDATE: .chat commands are being deprecated',description="Due to upcoming changes with discord limiting access to *message intents* (my ability to view messages directly). I will only be usable via ***/slash*** commands after some time soon, but not all commands are working just yet. Use **/help** for more detail or join the support server via http://ivork.com.\n\n~[The dev](https://discord.com/users/140902977618706432); <t:1664578350:R>", url='https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-FAQ#:~:text=MESSAGE%20CONTENT%20IS%20BECOMING%20A,in%20100%20or%20more%20servers.', color=0xff0000)
    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/665395417101631498.gif?size=48")
    await message.channel.send(embed=embed)
    
client.run(token)                 
