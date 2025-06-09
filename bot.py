import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
import os
import numpy as np

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def a8resources(ctx):
    await ctx.send("# A8 Resources \n**Tunes list**: https://docs.google.com/spreadsheets/d/1EsOl2d_TDYf4TSGh2DzxoR09_nN_Ln-Zq_QPppfVtj0/edit?usp=drivesdk \n**A8 MP Tuner**: https://docs.google.com/spreadsheets/d/1KN7rxutZVxDsyDnBv3m4MPEI2yhRXB_8cBaoGxfEULk/edit?usp=sharing \n**Nitro/Accel Testing**: https://docs.google.com/spreadsheets/d/1qkNwkJ7uHJ0GH4B09vLPXmYIF_nmow-x5bCed118NLM/edit?usp=drivesdk")
    
import numpy as np
arr = np.array([12.2, 15.4, 18, 15.4, 30, 30, 30, 30, 45.4, 33.8])/260.2
def tune(tire, suspension, drivetrain, exhaust, start_rank, end_rank, fake_rank=False, start_speed_override=np.nan, start_nitro_override=np.nan, end_nitro_override=np.nan):
    if tire > 10 or suspension > 10 or drivetrain > 10 or exhaust > 10 or tire < 0 or suspension < 0 or drivetrain < 0 or exhaust < 0:
        print('invalid levels!')
        return None
    if start_rank > 2000 or start_rank < 0 or end_rank > 2000 or end_rank < 0:
        print('invalid ranks!')
        return None
    if not(fake_rank):
        start_speed = 0.26651*start_rank-13.32246 if np.isnan(start_speed_override) else start_speed_override
    else:
        start_speed = 0.26651*(start_rank-100)-13.32246 if np.isnan(start_speed_override) else start_speed_override
    start_nitro = 10 if np.isnan(start_nitro_override) else start_nitro_override
    start_raw_speed = start_speed - start_nitro
    end_nitro = 0
    if end_rank <= 993:
        end_nitro = 26.5 if np.isnan(end_nitro_override) else end_nitro_override
    else:
        end_nitro = np.round((end_rank-1052)/90) * 2.4 + 27.7 if np.isnan(end_nitro_override) else end_nitro_override
    end_speed = 0.266727*end_rank-3.055354
    end_raw_speed = end_speed - end_nitro
    slope = (end_speed - start_speed)/(end_rank - start_rank)
    tire_speed = np.sum(arr[:tire])*(end_raw_speed - start_raw_speed)/2
    dt_speed = np.sum(arr[:drivetrain])*(end_raw_speed - start_raw_speed)/2
    suspension_speed = np.sum(arr[:suspension])*(end_nitro - start_nitro)/2
    exhaust_speed = np.sum(arr[:exhaust])*(end_nitro - start_nitro)/2
    
    speed_increase = tire_speed + dt_speed + suspension_speed + exhaust_speed
    tuned_speed = start_speed + speed_increase 
    tuned_rank = (tuned_speed - start_speed)/(slope)+start_rank
    return tuned_speed, tuned_rank
    
    
@bot.command()
async def tuner(ctx, *args):
    if len(args) < 6:
        await ctx.send(
            "❌ Missing required arguments!\n\n"
            "**Usage:** `!tuner <tire> <suspension> <drivetrain> <exhaust> <start_rank> <end_rank> [--fake] [override_start_speed=...] [override_start_nitro=...] [override_end_nitro=...]`\n"
            "**NOTE:** The overrides do **NOT** have to be used - fake rank and overrides are optional parameters in case a car has lower or higher than normal nitro at stock or pro. For example, the Koenigsegg One:1, which has a nitro of only ~30 km/h at pro (override_end_nitro=30), or the Renault DeZir, which has a starting nitro of ~15 km/h (override_start_nitro=15). You do not need to override start speed in case of fake rank; --fake does that for you.\n\n"
            "**Example:** `!tuner 3 4 5 2 1213 1501 --fake override_start_speed=290 override_start_nitro=12`"
        )
        return

    try:
        tire = int(args[0])
        suspension = int(args[1])
        drivetrain = int(args[2])
        exhaust = int(args[3])
        start_rank = float(args[4])
        end_rank = float(args[5])
    except ValueError:
        await ctx.send("❌ Invalid argument types. Make sure the first 6 are numbers.")
        return

    optional_args = args[6:]
    args_dict = {}
    for arg in optional_args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            args_dict[key.lower()] = value.lower()
        elif arg.lower() == "--fake":
            args_dict["fake_rank"] = True

    try:
        start_speed_override = float(args_dict.get("override_start_speed", "nan"))
        start_nitro_override = float(args_dict.get("override_start_nitro", "nan"))
        end_nitro_override = float(args_dict.get("override_end_nitro", "nan"))
    except ValueError:
        await ctx.send("❌ Optional overrides (`start_speed`, `start_nitro`, `end_nitro`) must be valid numbers.")
        return

    fake_rank = args_dict.get("fake_rank", False)

    if any(not (0 <= val <= 10) for val in [tire, suspension, drivetrain, exhaust]):
        await ctx.send("❌ Part levels must each be between 0 and 10.")
        return
    if any(not (0 <= r <= 2000) for r in [start_rank, end_rank]):
        await ctx.send("❌ Ranks must each be between 0 and 2000.")
        return

    result = tune(
        tire, suspension, drivetrain, exhaust,
        start_rank, end_rank,
        fake_rank=fake_rank,
        start_speed_override=start_speed_override,
        start_nitro_override=start_nitro_override,
        end_nitro_override=end_nitro_override
    )

    if result is None:
        await ctx.send("❌ Something went wrong during tuning.")
    else:
        tuned_speed, tuned_rank = result
        await ctx.send(
            f"**Tuned speed:** `{tuned_speed:.2f}`\n"
            f"**Tuned rank:** `{tuned_rank:.2f}`"
        )


@bot.command()
async def sus(ctx):
    await ctx.message.add_reaction("🈷️")
    
@bot.command()
async def vroomshield(ctx):
    with open("vroomshield.png", "rb") as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
        
@bot.command()
async def potatoman(ctx):
    with open("SPOILER_potatoman.png", "rb") as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

@bot.command()
async def youtube(ctx):
    await ctx.send('https://www.youtube.com/@DBTsVrooms')

@bot.command()
async def pixo(ctx):
    await ctx.send('I am totally a bot.')

@bot.command()
async def vroomer(ctx):
    await ctx.send("To be part of the Vroomers, there's a few requirements: \n * Be a chill member (no drama, no hyper agressive KDer) \n * Don't be a cheater (no MP cheating shenanigans) \n \nAnd voilá! You're part of the Vroomy fam, though that doesn't give you the Flag Bearer role here. For that, you do need to add the `VROOMS` to your IGN, preferrably without spaces, so that the full name shows in races, like: `'VROOMS'-John`, because if you add an space, in the leaderboard it shows as `'Vrooms' J.`")
        

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_lower = message.content.lower()
    
    emoji = discord.utils.get(message.guild.emojis, name="lambo")
    
    ch = random.randint(1, 1000) == 1
    
    if "sus" in content_lower or "🈷️" in message.content or ch:
        try:
            await message.add_reaction("🈷️")
            if random.randint(1, 10) < 2 and "🈷️" in message.content:
                if random.randint(1, 10) < 5:
                    await message.channel.send("Ngl that's kinda 🈷️")
                else:
                    await message.channel.send("🈷️")
            if ch and random.randint(1, 10) < 2:
                await message.channel.send(f"{message.author.mention} is a 🈷️")
        except discord.HTTPException:
            print("Failed to add reaction (possibly missing permissions)")
            
    if "lambo" in content_lower:
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            print("Failed to add reaction (possibly missing permissions)")
    
    if "electric" in content_lower:
        try:
            if random.randint(1, 30) < 10:
                await message.channel.send("EEEEEEEEEEEEEE")
        except discord.HTTPException:
            print("Failed to add reaction (possibly missing permissions)")


    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    bad_words = ["gamdite", "porn", "bitch", "nigga", "fuck"]
    username = member.name.lower()

    if any(word in username for word in bad_words):
        role = discord.utils.get(member.guild.roles, name="VrooModerators")
        mod_channel = discord.utils.get(member.guild.text_channels, name="moderators")

        if role and mod_channel:
            await mod_channel.send(
                f"{role.mention} 🚨 Suspicious user joined: {member.mention} (username: `{member.name}`, id: `{member.name}` )"
            )


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot.run(token)