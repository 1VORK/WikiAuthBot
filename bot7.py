import discord, logging, requests, pickle, datetime
from dateutil import parser
from discord_slash import SlashCommand, SlashContext
from discord.utils import get
from discord_slash.utils.manage_commands import create_option, create_choice
from tinydb import TinyDB, Query
from mwoauth import ConsumerToken, Handshaker

logging.basicConfig(level=logging.INFO)

client = discord.AutoShardedClient(intents=discord.Intents(members=True, messages=True, guilds=True), chunk_guilds_at_startup=False)
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

@slash.slash(name='invite', description="Invite bot to your own server")
async def invite(ctx: SlashContext):
    t = get_lang(ctx)
    await ctx.reply(f'{t["invt"]}: <{invlink}>')

@slash.slash(name='help', description='Show command usage')
async def help(ctx: SlashContext):
    embed=discord.Embed(title=f"WikiAuthBot - Help", description=f"**[Support Server](https://discord.gg/rcdBUwy)**\n\n</auth:1025443470388764714> - authenticate to you account\n</whois:1025464845694406686> - check your own or another person's account\n</set_language:1025462693886439464> - set the server language\n</set_channel_authenticate:1025462240062734440> - set a channel to post auth messages to\n</set_channel_welcome:1025462240062734439> - set a channel to prompt new joiners to athenticate\n</set_role:1025504106787389562> - set a role to be assigned to authenticated users\n</set_block:1025456381811249192> - disallow blocked users from authenticating\n</set_type:1025462240062734438> - choose between Wikimedia & Miraheze authentication\n</invite:1025437585687973888> - invite the bot to your server", color=0xCCCCCC)
    await ctx.reply(embed=embed)    
    
@slash.slash(name='auth',description='Authenticate to a Wikimedia or Miraheze account')
async def auth(ctx: SlashContext):
    gdb = TinyDB('Wiki/gsettings.json')
    Ft = Query()
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
            kamsg = await ctx.reply(f"I will send you the links in a direct message in a second.", hidden=True)
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
                tm = await ctx.author.dm_channel.send(embed=embed)
                await kamsg.edit(f"I have sent you the [links in a direct message](https://discord.com/channels/@me/{ctx.author.dm_channel.id}/{tm.id}).", hidden=True)
            except:
                await kamsg.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name)}", hidden=True)
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
            tm = await ctx.author.dm_channel.send(embed=embed)
            await ctx.reply(f"I have sent you the [links in a direct message](https://discord.com/channels/@me/{ctx.author.dm_channel.id}/{tm.id}).", hidden=True)
        except:
            await ctx.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name).replace('.auth','/auth')}")
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
            tm = await ctx.author.dm_channel.send(embed=embed)
            await ctx.reply(f"I have sent you the [links in a direct message](https://discord.com/channels/@me/{ctx.author.dm_channel.id}/{tm.id}).", hidden=True)
        except:
            await ctx.reply(f"{t['pmoff']} <@{ctx.author.id}> {t['pmoff2'].replace('GUILDNAME', ctx.guild.name).replace('.auth','/auth')}")

@slash.slash(name='whois',description='Check account details for an authenticated member',
    options=[
        create_option(
            name="user",
            description="User to check, leave blank for yourself",
            option_type=6,
            required=False
        )
    ])
async def whois(ctx: SlashContext, user=None):
    endm = ''
    gdb = TinyDB('Wiki/gsettings.json')
    t=get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        endm = 'Commands via DM default to Wikimedia, use in a Miraheze server to search Miraheze'
        mira = 0
    else:
        if gdb.search(Ft.id==ctx.guild.id)[0]['mira']==0:
            mira = 0
        else:
            mira = 1
    if user == None:
        user = ctx.author
    if mira:
        apiurl = "https://meta.miraheze.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json"
        GAIurl = "https://meta.miraheze.org/w/index.php?title=Special%3ACentralAuth/"
        tdb = TinyDB('Wiki/mauth.json')
        col = 0xfcba03
    else:
        apiurl = "https://en.wikipedia.org/w/api.php?action=query&meta=globaluserinfo&guiuser={usr['wnam']}&guiprop=groups%7Cmerged%7Cunattached&format=json"
        GAIurl = "https://{t['lang'].lower()}.wikipedia.org/w/index.php?title=Special%3ACentralAuth/"
        tdb = TinyDB('Wiki/auth.json')
        col = 0xCCCCCC        
    try:
        usr = tdb.search(Ft.id==user.id)[0]
    except:
        try:
            await ctx.reply(t["notauthd"].replace('That user',f'{user.name}#{user.discriminator}'))
        except:
            await ctx.reply(t["notauthd"])
        return
    kamsg = await ctx.reply("<a:typing:1017425614938062929> WikiAuthBot is thinking...") 
    dat = requests.get(apiurl.replace("{usr['wnam']}",usr['wnam']))
    dat.raise_for_status()
    dat = dat.json()['query']['globaluserinfo']
    try:
        if dat['groups'] != []:
            ggps = f"{t['gGroups:']} {', '.join(dat['groups'])}"
        else:
            ggps = ''
    except:
        await kamsg.edit(content="Sorry, this user's authentication appears to be outdated, they will need to re-auth to fix this.")
        return
    wiki=[]
    edits=0
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
        embed.set_footer(text=f"{t['max8']}\n{endm}")
    elif endm != '':
        embed.set_footer(text=endm)
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
    await kamsg.edit(content=None,embed=embed)
    try:
        settings = gdb.search(Ft.id==ctx.guild.id)[0]
        lang = settings['lang']
        if settings['ablock'] == 1 and indefd == 1:
            role = role=get(ctx.guild.roles, id=gdb.search(Ft.id==ctx.guild.id)[0]['arole'])
            mem = ctx.guild.get_member(usr['id'])
            if role in mem.roles:
                if lang.lower() != 'ru':
                    await mem.remove_roles(role)
                    await ctx.reply(f"<:declined:359850777453264906> {mem.mention} you have been unauthenticated as this server does not permit indef blocked users to have the authenticated role.")
                else:
                    await mem.remove_roles(role)
                    await ctx.reply( f"<:declined:359850777453264906> Роль ✓ удалена у бессрочно заблокированного участника {mem.name} (User:{usr['wnam']}).") #Removed role from <@{mem.id}> (User:{usr['wnam']}) due to currently being blocked.")

    except Exception as e:
        print(e)        

@slash.slash(name='set_block',description="Prevent blocked users being able to authenticate",
    options=[
        create_option(
            name="value",
            description="If enabled, blocked users can't authenticate. Leave blank to check value",
            option_type=5,
            required=False
        )
    ])
async def set_block(ctx: SlashContext, value=None):
    gdb = TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return
    if not value:
        en = gdb.search(Ft.id==ctx.guild.id)[0]
        await ctx.reply(f"This server has set_block set to: **{en}**.")
    else:
        if ctx.author.guild_permissions.manage_guild == False:
            await ctx.reply(f"{t['needmanser']}", hidden=True)
        else:
            en = gdb.search(Ft.id==ctx.guild.id)[0]['ablock']
            if en == 1 and value == True:
                await ctx.reply("Set_block is already enabled.")
            elif en == 0 and value == False:
                await ctx.reply("Set_block is already disabled.")
            else:
                val = 0
                if value == True:
                    val = 1
                gdb.upsert({'ablock':val, 'id':ctx.guild.id},Ft.id==ctx.guild.id)
                await ctx.reply(f"Successfully changed set_block to **{value}**")

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
async def set_type(ctx: SlashContext, type=None):
    gdb = TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return
    if not type:
        en = gdb.search(Ft.id==ctx.guild.id)[0]['mira']
        if en == 0:
            ty = '<:Wikipedia:542102882741125122>'
        else:
            ty = '<:mirahezelogo:446641749142798339>'
        await ctx.reply(f"This server is set to {ty}")
    else:
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.reply(f"{t['needmanser']}", hidden=True)
        else:
            en = gdb.search(Ft.id==ctx.guild.id)[0]['mira']
            if en == 1 and type == 'M':
                await ctx.reply(f"This server is already set to <:mirahezelogo:446641749142798339>")
            elif en == 0 and type == 'W':
                await ctx.reply(f"This server is already set to <:Wikipedia:542102882741125122>")
            else:
                ty = 0
                valr = "<:Wikipedia:542102882741125122> Wikipedia"
                if type == 'M':
                    ty = 1
                    valr = "<:mirahezelogo:446641749142798339> Miraheze"
                gdb.upsert({'mira':ty, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                await ctx.reply(t['YNMS'].replace("VAL", valr))

@slash.slash(name="set_language", description="Set the language for the server to use",
    options=[
        create_option(
            name="language",
            description="Language to set, leave blank to see set value and options",
            option_type=3,
            required=False
        )
    ])
async def set_language(ctx: SlashContext, language=None):
    gdb = TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return
    rdb = TinyDB('Wiki/responses.json')
    langs = []
    for e in rdb.all():
        langs.append(e['lang'])        
    if not language:    
        en = gdb.search(Ft.id==ctx.guild.id)[0]['lang']
        await ctx.reply(f"This server has it's language set to {en}\nAvailable languages: {', '.join(langs)}")
    else:
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.reply(t['needmanser'])
        else:
            if language.upper() not in langs:
                await ctx.reply(t['errlang'] + ': ' + ', '.join(langs))
            else:
                gdb.upsert({'lang':language.upper(), 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                t = get_lang(ctx)
                await ctx.reply(f"{ctx.guild.name} {t['langset']} {language.upper()}.")      

@slash.slash(name='set_channel_welcome', description="Set channel to post welcome messages prompting a user to authenticate",
    options=[
        create_option(
            name="channel",
            description="Channel for welcome messages to be posted to. Leave blank to check value",
            option_type=7,
            required=False
        ),
        create_option(
            name='additional_options',
            description="Remove welcome channel or set it to DMs. Leave blank if setting a channel/checking value",
            option_type=3,
            required=False,
            choices=[
                create_choice(name="Remove welcome channel",value='remove'),
                create_choice(name="Send welcome via DM if able",value='dm')
            ]
        )
    ])
async def set_channel_welcome(ctx: SlashContext, channel=None, additional_options=None):
    gdb = TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return
    if not channel and not additional_options:
        en = gdb.search(Ft.id==ctx.guild.id)[0]['wmsgs']
        if en == 555:
            enm = 'DMs'
        elif en == 'N':
            enm = 'None'
        else:
            enm = f'<#{en}>'
        await ctx.reply(f"This server has it's welcome channel set to {enm}.")
    else:
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.reply(t['needmanser'])
        else:
            if not additional_options:
                en = gdb.search(Ft.id==ctx.guild.id)[0]['wmsgs']
                if channel.id == en:
                    await ctx.reply(f"That channel is already set up as the welcome channel.")
                else:
                    try:
                        await channel.send(content='Test message', delete_after=1)
                    except:
                        await ctx.reply(t['cantsend'].replace('CHANNAME',channel.name))
                    else:
                        gdb.upsert({'wmsgs':channel.id, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                        await ctx.reply(t['ssetwchan'].replace('CHANNAME', f'<#{channel.id}>').split('.')[0])
            else:
                if additional_options == 'remove':
                    gdb.upsert({'wmsgs':"N", 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                    await ctx.reply(t['sremwchan'])
                else:
                    gdb.upsert({'wmsgs':555,'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                    await ctx.reply('Set to send welcome messages via DMs if possible.')

@slash.slash(name='set_channel_authenticate', description="Set channel to log successful authentications to",
    options=[
        create_option(
            name="channel",
            description="Channel for authentication messages to be posted to. Leave blank to check value",
            option_type=7,
            required=False
        ),
        create_option(
            name="remove",
            description="Select True to remove authentication messages posting to set channel, otherwise leave blank",
            option_type=5,
            required=False
        )
    ])
async def set_channel_authenticate(ctx: SlashContext, channel=None, remove=None):
    gdb=TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return    
    en = gdb.search(Ft.id==ctx.guild.id)[0]['achan']
    if not channel and not remove:        
        if en == 0:
            enm = 'None'
        else:
            enm = f'<#{en}>'
        await ctx.reply(f"The authentication channel is set to {enm}")
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.reply(t['needmanser'])
    else:
        if remove:
            if not en:
                await ctx.reply("There isn't a set authentication channel to remove")
            else:
                gdb.upsert({'achan':0, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                await ctx.reply(t['sremachan'])
        else:
            if channel.id == en:
                await ctx.reply('That channel is already set up to get authentication messages.')
            else:
                try:
                    await channel.send(content='Test message', delete_after=1)
                except:
                    await ctx.reply(t['cantsend'].replace('CHANNAME',channel.name))
                else:
                    gdb.upsert({'achan':channel.id, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                    await ctx.reply(t['ssetachan'].replace('CHANNAME',f'<#{channel.id}>').split('.')[0])


@slash.slash(name="set_role",description="Set the role authenticated users should be assigned",
    options=[
        create_option(
            name='role',
            description='Role to be assigned, leave blank to check value, will check & assign to all members once set',
            option_type=8,
            required=False
        ),
        create_option(
            name='remove',
            description="Select True to remove assigning more users to the authentication role, else leave blank",
            option_type=5,
            required=False
        )
    ])
async def set_role(ctx: SlashContext, role=None, remove=None):
    gdb = TinyDB('Wiki/gsettings.json')
    t = get_lang(ctx)
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.reply("Changing of server settings is only available within servers.")
        return
    en = gdb.search(Ft.id==ctx.guild.id)[0]['arole']
    if not role:
        if not en:
            await ctx.reply('This guild does not have an authentication role setup currently.')
        else:
            ro = get(ctx.guild.roles, id=en)
            if not ro:
                ron = 'a seemingly deleted role'
            else:
                ron = ro.name
            await ctx.reply(f"This guild currently has the authentication role set to {ron}")
    else:
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.reply(t['needmanser'])
        else:
            if remove:
                if en == 0:
                    await ctx.reply('There already is no authentication role set.')
                else:
                    gdb.upsert({'arole':0, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                    await ctx.reply('I will no longer assign the role to new authentications.\nFeel free to manually delete or unassign the role as you see fit.')
            else:
                if role.id == en:
                    kamsg = await ctx.reply(f'That role is the one currently set to.\n{t["checku"]}...')
                    db = TinyDB('Wiki/auth.json')
                    count = 0
                    async for m in ctx.guild.fetch_members(limit=99999):
                        if db.search(Ft.id==m.id) != []:
                            try:
                                if role not in m.roles:
                                    await m.add_roles(role)
                                count+=1
                            except:
                                await kamsg.edit(content=f'That role is the one currently set to.\n{t["cantass"]} {role.name} {t["cantass2"]}')
                                return
                    await kamsg.edit(content=f"That role is the one currently set to.\n{t['havass'].replace('ROLENAME',role.name).replace('COUNT',str(count)).replace('LENMESSAGEGUILDMEMBERS',str(ctx.guild.member_count))}")                
                else:
                    gdb.upsert({'arole':role.id, 'id':ctx.guild.id}, Ft.id==ctx.guild.id)
                    db = TinyDB('Wiki/auth.json')
                    count = 0
                    async for m in ctx.guild.fetch_members(limit=99999):
                        if db.search(Ft.id==m.id) != []:
                            try:
                                if role not in m.roles:
                                    await m.add_roles(role)
                                count+=1
                            except:
                                await ctx.reply(f'{t["cantass"]} {role.name} {t["cantass2"]}')
                                return
                    await ctx.reply(f"{t['havass'].replace('ROLENAME',role.name).replace('COUNT',str(count)).replace('LENMESSAGEGUILDMEMBERS',str(ctx.guild.member_count))}")

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
