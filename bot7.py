import discord, logging, requests, pickle
from discord_slash import SlashCommand, SlashContext
from discord import Intents
from tinydb import TinyDB, Query
from mwoauth import ConsumerToken, Handshaker
from discord_slash.utils.manage_commands import create_option, create_choice

logging.basicConfig(level=logging.INFO)

client = discord.AutoShardedClient(intents=Intents(members=True, messages=True, guilds=True), chunk_guilds_at_startup=False)
slash = SlashCommand(client, sync_commands=True)
token = open('tokens/wiki','r').read()
invlink = 'https://discord.com/api/oauth2/authorize?client_id=625962497165230080&permissions=2416298048&scope=applications.commands%20bot'
Ft = Query()
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

@slash.slash(name='invite', description="Invite bot to your own server.")
async def invite(ctx: SlashContext):
    t = get_lang(ctx)
    await ctx.reply(f'{t["invt"]}: <{invlink}>')

@slash.slash(name='auth',description='Authenticate to a Wikimedia or Miraheze account')
async def auth(ctx: SlashContext):
    gdb = TinyDB('Wiki/gsettings.json')
    mutmira = 0
    skip = 0
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        mutmira = 0
        for g in client.guilds:
            if g.get_member(ctx.author.id) is not None:
                if gdb.search(Ft.id==g.id)[0]['mira'] == 1:
                    mutmira = 1
    else:
        if ctx.guild.id == 434994995410239488:  #IF IVORK
            m2ntok = open('tokens/m2ntok','r').read()
            m2nsec = open('tokens/m2nsec','r').read()
            consumer_token = ConsumerToken(m2ntok, m2nsec)
            handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/mauth/{hex(ctx.author.id)}/')
            db = TinyDB('Wiki/authd.json')
            Ft = Query()
            rt = pickle.dumps(request_token, 0).decode()
            db.upsert({'id':ctx.author.id, 'mrequest_token':rt, 'mikilang': f"https://meta.miraheze.org/w/index.php"}, Ft.id==ctx.author.id)    
            consumer_token = ConsumerToken(contok, consec)
            handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
            wedirect, wequest_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/wauth/{hex(ctx.author.id)}/')
            db = TinyDB('Wiki/authd.json')
            Ft = Query()
            rt = pickle.dumps(wequest_token, 0).decode()
            db.upsert({'id':ctx.author.id, 'request_token':rt, 'wikilang': f"https://{t['lang'].lower()}.wikipedia.org/w/index.php"}, Ft.id==ctx.author.id)  
            await ctx.author.create_dm()
            try:
                embed=discord.Embed(title='WikiAuthBot', description=f"**Click the relevant link below to authenticate:**\n<:mirahezelogo:446641749142798339> [Miraheze]({redirect})\n<:wikilogo:546848856650809344> [Wikimedia]({wedirect})")
                embed.set_footer(text='For any issues, please ping IVORK#0001 on this server')          
                await ctx.author.dm_channel.send(embed=embed)
            except:
                await ctx.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name)}")
            else:
                try:
                    await ctx.add_reaction('📧')
                except:
                    print('Cant add email react') 
            return
        try:
            ismira = gdb.search(Ft.id==ctx.guild.id)[0]['mira'] #ctx.guild.id == 697848129185120256 or ctx.guild.id == 407504499280707585:

        except:
            gdb.upsert({'mira':0, 'id':ctx.guild.id},Ft.id==ctx.guild.id)
            ismira = 0            
    if skip == 0:
        if mutmira == 1:
            afoot = f'In order to authenticate to a Miraheze account, please use the /auth command within the server.'
        else:
            afoot = ''
    if ismira == 0:
        if requests.get('https://wikiauthbot.toolforge.org/test/').text == 'Hello World!':
            consumer_token = ConsumerToken(contok, consec)
            handshaker = Handshaker
            kamsg = await ctx.reply("<a:typing:1017425614938062929> WikiAuthBot is thinking...")            
            handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/wauth/{hex(ctx.author.id)}/')
        else:
            await client.get_channel(695443373292781599).send(f'WikiAuthBot (wiki auth): Failed to get test result from toolforge. Reverting to pythonanywhere.')
            consumer_token = ConsumerToken(open('tokens/contok','r').read(), open('tokens/consec','r').read())
            handshaker = Handshaker(f"https://{t['lang'].lower()}.wikipedia.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://1vork.pythonanywhere.com/wauth/{hex(ctx.author.id)}/')       
        db = TinyDB('Wiki/authd.json')
        Ft = Query()
        rt = pickle.dumps(request_token, 0).decode()
        db.upsert({'id':ctx.author.id, 'request_token':rt, 'wikilang': f"https://{t['lang'].lower()}.wikipedia.org/w/index.php"}, Ft.id==ctx.author.id)                     
        await ctx.author.create_dm()
        try:
            embed=discord.Embed(title='WikiAuthBot', description=f"{t['pmauth']} {redirect}",color=0xCCCCCC)
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/546848856650809344.png')
            embed.set_footer(text=afoot)
            await ctx.author.dm_channel.send(embed=embed)
        except:
            await ctx.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name).replace('.auth','/auth')}")
        else:
            try:
                await ctx.add_reaction('📧')
            except:
                print('Cant add email react')
    else:
        m2ntok = open('tokens/m2ntok','r').read()
        m2nsec = open('tokens/m2nsec','r').read()
        if requests.get('https://wikiauthbot.toolforge.org/test/').text == 'Hello World!':
            consumer_token = ConsumerToken(m2ntok, m2nsec)
            handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://wikiauthbot.toolforge.org/mauth/{hex(ctx.author.id)}/')
        else:
            await client.get_channel(695443373292781599).send(f'WikiAuthBot (mira auth): Failed to get test result from toolforge. Reverting to pythonanywhere.')
            consumer_token = ConsumerToken(open('tokens/montok','r').read(), open('tokens/monsec','r').read())
            handshaker = Handshaker(f"https://meta.miraheze.org/w/index.php", consumer_token)
            redirect, request_token = handshaker.initiate(callback=f'https://1vork.pythonanywhere.com/mauth/{hex(ctx.author.id)}/')
        db = TinyDB('Wiki/authd.json')
        Ft = Query()
        rt = pickle.dumps(request_token, 0).decode()
        db.upsert({'id':ctx.author.id, 'mrequest_token':rt, 'mikilang': f"https://meta.miraheze.org/w/index.php"}, Ft.id==ctx.author.id)
        await ctx.author.create_dm()
        try:
            embed=discord.Embed(title='WikiAuthBot', description=f"{t['pmauth'].replace('Wikimedia', 'Miraheze')} {redirect}", color=0xfcba03)
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/446641749142798339.png')
            await ctx.author.dm_channel.send(embed=embed)
        except:
            await ctx.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name).replace('.auth','/auth')}")
        else:
            try:
                await ctx.remove_reaction(emoji='<a:typing:712290091002757190>', member=client.user)
                await ctx.add_reaction('📧')
            except:
                print('Cant add email react')                   

@slash.slash(name='whois',description='Check account details for an authenticated member',
    options=[
        create_option(
            name="user",
            description="User to check, leave blank for yourself",
            option_type=6,
            required=False
        )
    ])
async def whois(ctx: SlashContext, user):
    await ctx.reply(f"You chose {user}\nThis command is still being setup.")

@slash.slash(name='set_block',description="Prevent blocked users being able to authenticate.",
    options=[
        create_option(
            name="value",
            description="If enabled, blocked users can't authenticate.",
            option_type=5,
            required=True
        )
    ])
async def set_block(ctx: SlashContext, value):
    await ctx.reply(f"You chose {value}")
    await ctx.reply("This command is still being setup.")

@slash.slash(name='set_type', description='Set server type between Wikimedia & Miraheze',
    options=[
        create_option(
            name="type",
            description="Server type, leave blank to check value",
            option_type=3,
            required=True,
            choices=[
                create_choice(name="Wikimedia",value="W"),
                create_choice(name="Miraheze",value="M")
            ]
        )
    ])
async def set_type(ctx: SlashContext, type):
    await ctx.reply(f"You chose {type}\nThis command is still being setup.")

@slash.slash(name="set_language", description="Set the language for the server to use",
    options=[
        create_option(
            name="language",
            description="Language to set, leave blank to see options",
            option_type=3,
            required=False
        )
    ])
async def set_language(ctx: SlashContext, language):
    await ctx.reply(f"You chose {language}\nThis command is still being setup.")

@slash.slash(name='set_channel_welcome', description="Set channel to post welcome messages prompting a user to authenticate",
    options=[
        create_option(
            name="channel",
            description="Channel for welcome messages to be posted to. Leave blank to check value",
            option_type=7,
            required=False
        )
    ])
async def set_channel_welcome(ctx: SlashContext, channel):
    await ctx.reply(f"You chose {channel.mention}\nThis command is still being setup.")

@slash.slash(name='set_channel_authenticate', description="Set channel to log successful authentications to",
    options=[
        create_option(
            name="channel",
            description="Channel for authentication messages to be posted to. Leave blank to check value",
            option_type=7,
            required=False
        )
    ])
async def set_channel_authenticate(ctx: SlashContext, channel):
    await ctx.reply(f"You chose {channel.mention}\nThis command is still being setup.")

@slash.slash(name="set_authentication_role",description="Define the role authenticated users should be assigned, will also run a check on all current members",
    options=[
        create_option(
            name='role',
            description='Role to be assigned, leave blank to check value',
            option_type=8,
            required=False
        )
    ])
async def set_authentication_role(ctx: SlashContext, role):
    await ctx.reply(f"You chose {role.mention}\nThis command is still being setup.")

def get_lang(ctx):
    Ft = Query()
    gdb = TinyDB('Wiki/gsettings.json')
    rdb = TinyDB('Wiki/responses.json')    
    if not isinstance(ctx.channel, discord.DMChannel):   #IGNORE MIRAHEZE SERVERS
        try:
            settings = gdb.search(Ft.id==ctx.guild.id)[0]
            lang=settings['lang']
        except:
            lang = "EN"
    else:
        msers = []
        for g in client.guilds:                                                                                                        
            try:                                                                                                                       
                if g.get_member(ctx.author.id) is not None:                                                                        
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
    return t

client.run(token)
