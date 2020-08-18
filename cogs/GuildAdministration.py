import os

from discord.ext import commands
import discord
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
load_dotenv()

cluster = MongoClient(os.getenv('DB_LINK'))
db = cluster["myuDB"]
collection = db["guilds"]

class GuildAdministration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.group(name='guild', invoke_without_command=True)
    async def guild_cmd(self, ctx):
        await ctx.channel.send("``guild`` is a base command. Try ''.myu guild help'' for available guild commands.")

    @guild_cmd.command(name='initialize', aliases=['create', 'start', 'begin'])
    @commands.has_permissions(administrator=True)
    async def start_guild(self, ctx):
        '''Embed indexes:
        0: Guild name
        1: Member promotion duration (min:0)
        2: Veteran promotion duration (min:1)
        3: 
        '''
        if collection.count_documents({"_id": ctx.guild.id}, limit=1) != 0:
            await ctx.channel.send("There is already an initialized guild with this Discord server.")
            return 

        embed = discord.Embed(
            title="Guild Creation",
            colour = discord.Colour(0xfccfff),
        )
        guild_name = ''
        member_days = ''
        vet_days = ''

        def check_m(msg):
            return msg.channel == ctx.channel and msg.author == ctx.author

            
        while True:
            await ctx.channel.send("What is the name of your guild?")
            guild_name = await self.bot.wait_for('message', check=check_m)
            embed.add_field(name='\nGuild Name', value=guild_name.content, inline=False)

            flag = False
            await ctx.channel.send("How many days until Initiates are promoted to Member? (0 or more)")
            while flag is False:
                member_days = await self.bot.wait_for('message', check=check_m)
                flag = await self.check_int(ctx, member_days.content)
            embed.add_field(name="\nMember promotion (days)", value=member_days.content, inline=False)
            
            flag = False
            await ctx.channel.send("How many days until Members are promoted to Veteran? (0 or more)")
            while flag is False:
                vet_days = await self.bot.wait_for('message', check=check_m)
                flag = await self.check_int(ctx, vet_days.content)
            embed.add_field(name="\nVeteran promotion (days)", value=vet_days.content, inline=False)

            await ctx.channel.send("**Please review your guild's details below.**\
            \n\nIf the information is correct, react with :white_check_mark:\
            \nIf you would like to redo the creation process, react with :arrows_counterclockwise:\
            \nIf you would like to cancel, react with :x:\n")
            guild_post = await ctx.channel.send(embed=embed)
            check_emoji = '\U00002705'
            ccw_emoji = '\U0001F504'
            x_emoji = '\U0000274C'
            await guild_post.add_reaction(check_emoji)
            await guild_post.add_reaction(ccw_emoji)
            await guild_post.add_reaction(x_emoji)

            def check_r(rxn, user):
                return ctx.author == user and rxn.message.id == guild_post.id

            reaction, user = await self.bot.wait_for('reaction_add', check=check_r)

            if reaction.emoji == check_emoji:
                post1 = {"_id": ctx.guild.id,
                         "guild_name": guild_name.content,
                         "member_promotion": int(member_days.content),
                         "vet_promotion": int(vet_days.content)}
                collection.insert_one(post1)
                await ctx.channel.send('Confirmed!')
                break
            elif reaction.emoji == ccw_emoji:
                embed.clear_fields()
                await guild_post.delete()
                await ctx.channel.send('Redoing guild creation process.')
                continue
            elif reaction.emoji == x_emoji:
                await ctx.channel.send('Guild initialization cancelled.')
                return

    @guild_cmd.command(name='help')
    @commands.has_permissions(administrator=True)
    async def guild_help(self, ctx,):
        embed = discord.Embed(
            title="Guild Commands",
            colour = discord.Colour(0xfccfff),
            description="Usage: ''.myu guild [command]''"
        )
        embed.add_field(name='initialize', 
            value="Register/initalize your guild and define member and veteran promotion durations.",
            inline=False)
        embed.add_field(name='update',
            value="Make changes/updates to your guild's information.",
            inline=False)
        
        await ctx.channel.send(embed=embed)


    @guild_cmd.command(name='update')
    @commands.has_permissions(administrator=True)
    async def guild_update(self, ctx,):
        guild_embed = await self.get_guild_info(ctx)
        await ctx.channel.send("If you would like to change the guild name, react with :one:\
        \nIf you would like to change the time until member promotion, react with :two:\
        \nIf you would like to change the time until veteran promotion, react with :three:\
        \nIf you would like to cancel this operation, react with :x: or any other emoji.\n")
        guild_post = await ctx.channel.send(embed=guild_embed)
        one_emoji = '1\U000020E3'
        two_emoji = '2\U000020E3'
        three_emoji = '3\U000020E3'
        x_emoji = '\U0000274C'
        await guild_post.add_reaction(one_emoji)
        await guild_post.add_reaction(two_emoji)
        await guild_post.add_reaction(three_emoji)
        await guild_post.add_reaction(x_emoji)

        def check_r(rxn, user):
            return ctx.author == user and rxn.message.id == guild_post.id

        reaction, user = await self.bot.wait_for('reaction_add', check=check_r)
        
        def check_m(msg):
            return msg.channel == ctx.channel and msg.author == ctx.author

        if reaction.emoji == one_emoji:
            await ctx.channel.send("Enter the new name for your guild.")
            guild_name = await self.bot.wait_for('message', check=check_m)

            collection.update_one({"_id": ctx.guild.id},
                {"$set": {
                    "guild_name": guild_name.content
                }}, upsert=False)

        elif reaction.emoji == two_emoji:
            flag = False
            member_days = ''
            await ctx.channel.send("How many days until Initiates are promoted to Member? (0 or more)")
            while flag is False:
                member_days = await self.bot.wait_for('message', check=check_m)
                flag = await self.check_int(ctx, member_days.content)

            collection.update_one({"_id": ctx.guild.id},
                {"$set": {
                    "member_promotion": int(member_days.content)
                }}, upsert=False)

        elif reaction.emoji == three_emoji:
            flag = False
            vet_days = ''
            await ctx.channel.send("How many days until Members are promoted to Veteran? (0 or more)")
            while flag is False:
                vet_days = await self.bot.wait_for('message', check=check_m)
                flag = await self.check_int(ctx, vet_days.content)

            collection.update_one({"_id": ctx.guild.id},
                {"$set": {
                    "vet_promotion": int(vet_days.content)
                }}, upsert=False)
        else:
            await ctx.channel.send("Guild update has been cancelled.")
            return
        
        guild_embed = await self.get_guild_info(ctx)
        await ctx.channel.send("Guild information has been updated to the following details below!")
        await ctx.channel.send(embed=guild_embed)
            

    async def get_guild_info(self, ctx):
        '''Embed indexes:
        0: Guild name
        1: Member promotion duration (min:0)
        2: Veteran promotion duration (min:0)
        '''
        embed = discord.Embed(
            title="Guild Information",
            colour = discord.Colour(0xfccfff)
        )
        guild_info = collection.find_one({"_id": ctx.guild.id})
        embed.add_field(name='\nGuild Name', value=guild_info["guild_name"], inline=False)
        embed.add_field(name="\nMember promotion (days)", value=guild_info["member_promotion"], inline=False)
        embed.add_field(name="\nVeteran promotion (days)", value=guild_info["vet_promotion"], inline=False)
        return embed

    @guild_cmd.command(name='delete')
    @commands.has_permissions(administrator=True)
    async def delete_guild(self, ctx):
        def check_m(msg):
            return msg.channel == ctx.channel and msg.author == ctx.author

        await ctx.channel.send("Are you sure you would like to delete the guild? This action will remove all registered members in our database as well.\
                                \n\nEnter 'Yes' to confirm this action. Enter anything else to cancel this action.")
        choice = await self.bot.wait_for('message', check=check_m)
        if choice.content == 'Yes':
            collection.delete_one({"_id": ctx.guild.id})
            #TODO: add member purging when guild is deleted.
            await ctx.channel.send("The guild and respective member data has been deleted.")
        else:
            await ctx.channel.send("Guild deletion has been cancelled.")
    

    async def check_int(self, ctx, msg_content):
        try:
            val = int(msg_content)
            if  val < 0:
                await ctx.channel.send("Sorry, input must be a non-negative integer. Please try again.")
                return False
            return True
        except ValueError:
            await ctx.channel.send("Sorry, input must be a non-negative integer. Please try again.")
            return False

def setup(bot):
    bot.add_cog(GuildAdministration(bot))