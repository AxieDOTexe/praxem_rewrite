import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

from tools import _json, item_handling

load_dotenv('.env')
dbclient = MongoClient(os.getenv('DBSTRING1'))
db = dbclient[os.getenv('DBSTRING2')]


class Inventory(commands.Cog):
    def __init__(self, pr_client):
        self.bot = pr_client

    @commands.Cog.listener()
    async def on_ready(self):
        print('inventory.py -> on_ready()')

    @discord.slash_command(
        name="inventory",
        description="View your inventory",
        guild_only=True
    )
    async def inventory(self, ctx):
        target = ctx.author.id

        check = db["Inventory"].count_documents({"_id": target})
        if check == 0:
            em = discord.Embed(color=0xadcca6,
                               description=f"**{ctx.author.name}#{ctx.author.discriminator}** I couldn't find any profile linked to your account. Create one with `/profile`")
            await ctx.respond(embed=em)
            return

        # inventory = db["Inventory"].find_one({"_id": target})
        inventory_document = db["Inventory"].find({"_id": target})
        inventory_empty_list = item_handling.inventory_list()

        inventory_list = []

        '''GENERATE LIST'''
        for value in inventory_document:
            for item in inventory_empty_list:
                item_name = item.replace("_", " ")
                item_value = value[item]
                inventory_list.append(f"{item_name}: {item_value}")

        inventory_list = item_handling.decorate_inventory_list(inventory_list)

        '''DEFINE ITEMS'''
        main_weapon = inventory_list[0]
        secondary_weapon = inventory_list[1]
        balance = inventory_list[4]

        '''ITEM PAGES AND CHECK IF AMOUNT=0'''
        items = inventory_list[5:]
        items = item_handling.decorate_inventory_items(items)

        page_1 = ""

        if len(items) == 0:
            page_1 += "You don't have any items."
        else:
            for item in items:
                page_1 += "{}\n\n".format(item)

        '''CREATE EMBED'''
        em = discord.Embed(color=0xadcca6, title=f"{ctx.author.name}'s Inventory",
                           description=f"{main_weapon}\n"
                                       f"{secondary_weapon}\n\n"
                                       f"**Balance: {balance}** 💸")

        em.add_field(name="ITEMS", value=page_1)
        em.set_thumbnail(url=_json.get_art()["bot_icon_longbow"])
        em.set_footer(text="do /item [item] to see detailed information.")

        await ctx.respond(embed=em)

    @discord.slash_command(
        name="item",
        description="View detailed information about an item",
        guild_only=True
    )
    async def item(self, ctx, *, item: discord.Option(choices=item_handling.inventory_list()[5:])):
        inventory = db["Inventory"].find({"_id": ctx.author.id})
        for i in inventory:
            item_amount = i[item]

        description = ""
        cost = 0
        thumbnail = ""
        emote = None

        items = db["Items"].find({"_id": item})
        for info in items:
            description = info["description"]
            cost = info["cost"]
            thumbnail = info["image_url"]
            emote = self.bot.get_emoji(info["emote_id"])

        ''' CREATE EMBED'''
        em = discord.Embed(color=0xadcca6, title=f"{emote} {item}", description=f"**Item cost: {cost}**")
        em.add_field(name="Description", value=description)
        em.set_thumbnail(url=thumbnail)

        if item_amount > 1:
            em.set_footer(text=f"You have this item {item_amount} times.")
        elif item_amount == 1:
            em.set_footer(text=f"You have this item {item_amount} times.")
        else:
            em.set_footer(text=f"You don't have this item.")

        await ctx.respond(embed=em)


def setup(client):
    client.add_cog(Inventory(client))
