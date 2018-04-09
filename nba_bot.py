import asyncio
import discord
import requests
import datetime

def padding(size):
    output = ""
    i = 0
    while i < size:
        output = output + " "
        i = i + 1
    return output


def get_nba(message):
    table = ""
    todays_date = ""

    if len(message.content) > 4:
        if message.content[4] == ".":
            todays_date = message.content[5:]
    else:
        today = datetime.date.today()
        todays_date = "%d%02d%02d" % (today.year, today.month, today.day)

    url = "http://data.nba.net/json/cms/noseason/scoreboard/%s/games.json" % (todays_date)
    try:
       data = requests.get(url).json()
    except:
        return "NBA BOT: Bad command"

    for i in data['sports_content']['games']['game']:
        h_pad = padding(3 - len(i['home']['score']))
        v_pad = padding(3 - len(i['visitor']['score']))
        table = table + "```%s %s%s - %s  %s%s --- %s %s```" % (i['home']['team_key'], i['home']['score'], h_pad, i['visitor']['team_key'], i['visitor']['score'],  v_pad, i['period_time']['period_status'], i['period_time']['game_clock'])
    return table;
 
def get_fiats():
    try:
        usd_eur = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=EUR", timeout=10)
        gbp = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=GBP", timeout=10)
        aud = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=AUD", timeout=10)
    except requests.Timeout:
        return None
 
    usd_eur = usd_eur.json()[0]
    gbp = gbp.json()[0]
    aud = aud.json()[0]
    return float(usd_eur["price_usd"]), float(usd_eur["price_eur"]), float(gbp["price_gbp"]), float(aud["price_aud"])
 
 
def get_cryptos():
    try:
        grlc_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/", timeout=10)
        eth_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/ethereum/", timeout=10)
        ltc_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/litecoin/", timeout=10)
        nano_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/nano/", timeout=10)
    except requests.Timeout:
        return None
 
    grlc_btc = grlc_btc.json()[0]
    eth_btc = eth_btc.json()[0]
    ltc_btc = ltc_btc.json()[0]
    nano_btc = nano_btc.json()[0]
 
    grlc_btc = float(grlc_btc["price_btc"])
    grlc_eth = grlc_btc / float(eth_btc["price_btc"])
    grlc_ltc = grlc_btc / float(ltc_btc["price_btc"])
    grlc_nano = grlc_btc / float(nano_btc["price_btc"])
 
    return grlc_btc, grlc_eth, grlc_ltc, grlc_nano
 
 
def fstr(max_size, value):
    # Get the len of the integer part
    i_part = len(str(int(value)))
    f_part = max_size - i_part - 1
 
    formater = "{" + ":.{}f".format(f_part) + "}"
 
    return formater.format(value)
 
 
client = discord.Client()
 
@client.event
async def on_ready():
    print('Logged in as {} <@{}>'.format(client.user.name, client.user.id))
    print('------')
 
@client.event
async def on_message(message):
    if message.content.startswith("*help"):
        table = "```\n" \
                "Usage: \n" \
                "  *help --- brings up this page\n" \
                "  *nba --- shows scoreboard\n" \
                "  *nba.YYYYMMDD --- shows specified day\n" \
                "  *fiat --- shows Garlic fiat value.\n" \
                "  *crypto --- shows Garlic crypto value.\n" \
                "\n" \
                "  Thank you for using the NBA Bot. ₲1 = ₲1\n" \
                "```"
        await client.send_message(message.channel, table)

    if message.content.startswith("*nba"):
        nba_string = get_nba(message);
        await client.send_message(message.channel, nba_string)

    if message.content.startswith("*fiat"):
        # Get the GRLC price in USD, EUR, GBP & AUD
        tmp = await client.send_message(message.channel, "Acquiring fiat rates from CoinMarketCap...")
        fiats = get_fiats()
        if fiats:
            await client.edit_message(tmp, "Acquiring fiat rates from CoinMarketCap... Done!")
            table = "``` ₲ 1 = $ {0} USD, € {1} EUR, £ {2} GBP, $ {3} AUD```".format(fstr(6, fiats[0]), fstr(6, fiats[1]), fstr(6, fiats[2]), fstr(6, fiats[3]))
            await client.send_message(message.channel, table)
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")
 
    if message.content.startswith("*crypto"):
        # Get the GRLC price in BTC, ETH, LTC, NANO
        tmp = await client.send_message(message.channel, "Acquiring crypto rates from CoinMarketCap...")
        cryptos = get_cryptos()
 
        if cryptos:
            await client.edit_message(tmp, "Acquiring crypto rates from CoinMarketCap... Done!")
 
            table = "``` ₲ 1 = ₲ 1, ฿ {0}, Ξ {1}, Ł {2}, η {3}```".format(fstr(11, cryptos[0]), fstr(11, cryptos[1]), fstr(11, cryptos[2]), fstr(11, cryptos[3]))
 
            await client.send_message(message.channel, table)
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")

client.run('BOT TOKEN HERE')