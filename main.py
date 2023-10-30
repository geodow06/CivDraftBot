# Work with Python 3.9
import random

import discord
import numpy as np
from discord.ext import commands

from constants import DISCORD_TOKEN

client = discord.Client()
bot = commands.Bot(command_prefix='!')

list_of_civilisations = ["Spain", "Babylon", "England", "America", "Arabia", "Aztec", "Austria", "Brazil", "Morocco",
                         "Greece", "Maya",
                         "Assyria", "Portugal", "Byzantine", "Carthage", "Celts", "China", "Danes", "Dutch", "Egypt",
                         "Ethiopia",
                         "India", "France", "Germany", "Huns", "Inca", "Japan", "Korea", "Mongols", "ottomans",
                         "Persia", "Poland",
                         "Roman", "Russian", "Shoshone", "Siam", "Songhai", "Sweden", "Zulu", "polynesia", "Indonesia",
                         "Iroquois"]

bot.players = ["Jack", "George", "Noob Chris", "Good Chris", "Tim", "Lewis", "Other weaker George"]
bot.number_of_players = len(bot.players)
bot.civilisations = list_of_civilisations


# Misc

@bot.command()
async def reset(ctx):
    reset_players()
    bot.civilisations = list_of_civilisations
    await ctx.send("Reset")


# PLAYERS

def reset_players():
    bot.players = ["Jack", "George", "Chris"]
    bot.number_of_players = len(bot.players)


@bot.command()
async def players(ctx):
    await ctx.send("```{}```".format(bot.players))


@bot.command()
async def users(ctx):
    channel_id = int(ctx.guild.voice_channels[0].id)
    current_players = []
    for member in ctx.guild.get_channel(channel_id).members:
        if member.status == discord.Status.online:
            current_players.append(member.name)
    bot.players = current_players
    await ctx.send("New players {}".format(bot.players))


def get_player_number(msg):
    if msg.content.isdigit():
        player_to_veto = int(msg.content)
        veto_player_number = player_to_veto - 1
    elif bot.players.__contains__(msg.content):
        veto_player_number = bot.players.index(msg.content)
    else:
        print("fucked")
    return veto_player_number


@bot.command()
async def remove(ctx, *arguments):
    removed = []
    not_removed = []
    for argument in arguments:
        if bot.players.__contains__(argument):
            bot.players.remove(argument)
            bot.number_of_players = len(bot.players)
            removed.append(argument)
        else:
            not_removed.append(argument)
            continue
    if len(removed) > 0:
        await ctx.send("{} removed from list of players".format(', '.join(removed)))
    if len(not_removed) > 0:
        await ctx.send("{} cannot be removed from list of players as they do not exist".format(', '.join(not_removed)))


@bot.command()
async def add(ctx, *arguments):
    for argument in arguments:
        bot.players.append(argument)
        bot.number_of_players = len(bot.players)

    await ctx.send("{} added to the list of players".format(', '.join(arguments)))


# Civilisations

def reset_civilisations():
    civilisation_pool = []
    for civ in bot.civilisations:
        civilisation_pool.append(civ)
    return civilisation_pool


@bot.command()
async def pool(ctx):
    await ctx.send("```{}```".format(bot.civilisations))


@bot.command()
async def remove_civ(ctx, *arguments):
    removed = []
    not_removed = []
    for argument in arguments:
        if bot.civilisations.__contains__(argument):
            bot.civilisations.remove(argument)
            removed.append(argument)
        else:
            not_removed.append(argument)
            continue
    if len(removed) > 0:
        await ctx.send("{} removed from pool of civilisations".format(', '.join(removed)))
    if len(not_removed) > 0:
        await ctx.send(
            "{} cannot be removed from pool of civilisations as they do not exist".format(', '.join(not_removed)))


@bot.command()
async def add_civ(ctx, *arguments):
    for argument in arguments:
        bot.civilisations.append(argument)

    await ctx.send("{} added to the list of civilisations".format(', '.join(arguments)))


# VETOES

def use_veto(player_number, vetoes):
    if vetoes[player_number]:
        np.put(vetoes, player_number, False)
        print("%s uses their veto\n" % bot.players[player_number])
        return vetoes
    else:
        print("\n%s does not have a veto idiots" % bot.players[player_number])
        return vetoes


def validate_veto(player_number, vetoes):
    if vetoes[player_number]:
        return True
    else:
        return False


def reset_vetoes(number_of_players):
    vetoes = np.full([number_of_players], True, dtype=bool)
    return vetoes


def veto_logic(vetoes, veto_player_number):
    validated = validate_veto(veto_player_number, vetoes)
    if validated:
        use_veto(veto_player_number, vetoes)
        return True
    else:
        print("\n%s has already used their veto! the picks stay the same\n" % bot.players[veto_player_number])
        return False


# DRAFT

def generate_picks(number_of_players, number_of_picks, civilisations, picks, vetoes):
    if number_of_picks * number_of_players < len(civilisations):
        for x in range(number_of_players):
            for y in range(number_of_picks):
                pick = random.randint(0, len(civilisations) - 1)
                position = [int(number_of_picks * x + y)]
                value = [civilisations[pick]]
                np.put(picks, position, value)
                civilisations.remove(civilisations[pick])
        return picks, vetoes

    else:
        print("Number of picks too high for number of players")
        exit(0)


def check(m):
    return m.content.isdigit() or bot.players.__contains__(m.content)


def george_spain_bink(picks, number_of_picks):
    george_number = bot.players.index("George")
    for i in range(0, number_of_picks):
        test = picks[george_number][i]
        if test == "Spain":
            return True
        else:
            continue


@bot.command()
async def draft(ctx, *args):
    if args:
        number_of_picks = int(args[0])
    else:
        number_of_picks = 3
    vetoes = reset_vetoes(bot.number_of_players)
    civilisation_pool = reset_civilisations()
    picks = np.full((bot.number_of_players, number_of_picks), "Not filled")
    await ctx.send('Drafting for {} players {} picks each'.format(bot.number_of_players, number_of_picks))
    current_picks = generate_picks(bot.number_of_players, number_of_picks, civilisation_pool, picks, vetoes)
    await ctx.send("---- Round 1 ----")
    for i in range(bot.number_of_players):
        player = bot.players[i]
        await ctx.send("```{} {} Veto : {}```".format(player, picks[i], vetoes[i]))
    draft_round = 1
    while True in vetoes:
        draft_round += 1
        if george_spain_bink(picks, number_of_picks):
            await ctx.send("Ofcourse George the bot binks Spain again")
        await ctx.send("Who wants to veto?")
        msg = await bot.wait_for('message', check=check)
        veto_player_number = get_player_number(msg)
        player = bot.players[veto_player_number]
        if veto_logic(vetoes, veto_player_number):
            await ctx.send("{} is using their veto".format(player))
            civilisation_pool = reset_civilisations()
            current_picks, vetoes = generate_picks(bot.number_of_players, number_of_picks, civilisation_pool, picks,
                                                   vetoes)
            await ctx.send("---- Round {} ----".format(draft_round))
            for i in range(bot.number_of_players):
                player = bot.players[i]
                await ctx.send("```{} {} Veto : {}```".format(player, picks[i], vetoes[i]))

        else:
            await ctx.send("{} has already used their veto, same picks".format(player))
            for i in range(bot.number_of_players):
                player = bot.players[i]
                await ctx.send("```{} {} Veto : {}```".format(player, picks[i], vetoes[i]))

    await ctx.send("\nNo more vetoes suck it up")


bot.run(DISCORD_TOKEN)
