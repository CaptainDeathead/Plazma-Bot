# this is a discord bot called "Plazma"
import discord
import random
import chess
import engine
import utils
import asyncio
import flask
from threading import Thread

intents = discord.Intents.all()

client = discord.Client(intents=intents)

app = flask.Flask('app')

@app.route('/')
def home():
    return flask.render_template('index.html')

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@app.route('/trigger_function', methods=['POST'])
def trigger_function():
    data = request.get_json()
    id = data['id']
    print(id)
    keys = db.keys()
    for i in keys:
        print(i)
    return 'success'

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    username = str(message.author).split("#")[0]
    try:
        channel = str(message.channel.name)
    except AttributeError:
        channel = str(message.channel)
    user_message = str(message.content)
  
    print(f'Message {user_message} by {username} on {channel}')
  
    user_message = user_message.lower()

    if message.author == client.user:
        return

    if user_message == "hello":
        await message.channel.send("Henlo!")

    elif user_message == "ping":
        await message.channel.send("pong")

    elif user_message == "pong":
        await message.channel.send("ping")

    elif user_message == "e":
        await message.channel.send("e")

    elif user_message == "help":
        pass

    elif "c++" in user_message:
        user_message = user_message.replace("c++ ", "")
        user_message = user_message.replace("```", "")
        with open("code.cpp", "w") as file:
            file.write(user_message)
        await message.channel.send("Compiling...")
        await client.change_presence(activity=discord.Game(name="Compiling..."), status=discord.Status.dnd)
        response = utils.compile_cpp()
        response = f"`Plazma C++ Code Compilation:`\n```{response}```"
        try:
            await message.channel.send(response)
        except discord.errors.HTTPException:
            with open("output.txt", "w") as file:
                file.write(response)
            await message.channel.send(file=discord.File("output.txt"))
        await client.change_presence(activity=discord.Game(name="Plazma"), status=discord.Status.online)

    elif "python" in user_message:
        user_message = user_message.replace("python ", "")
        with open("code.py", "w") as file:
            file.write(user_message)
        await message.channel.send("Compiling...")
        try:
            await client.change_presence(activity=discord.Game(name="Compiling..."), status=discord.Status.dnd)
            response = utils.compile_python()
        except Exception as e:
            response = str(e)
        response = f"`Plazma Python Code Compilation:`\n```{response}```"
        try:
            await message.channel.send(response)
        except discord.errors.HTTPException:
            with open("output.txt", "w") as file:
                file.write(response)
            await message.channel.send(file=discord.File("output.txt"))
        await client.change_presence(activity=discord.Game(name="Plazma"), status=discord.Status.online)

    elif "tts" in user_message:
        user = message.author
        voice_channel = user.voice.channel
        channel = None
        if voice_channel != None and "file" not in user_message:
            user_message = user_message.replace("tts ", "")
            utils.speak(user_message)
            channel = voice_channel.name

            await message.channel.send(f"Playing *{user_message}* in {channel}")

            vc = await voice_channel.connect()

            source = discord.FFmpegOpusAudio("voice.mp3")

            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

            vc.stop()
            await vc.disconnect()
        elif voice_channel != None and "file" in user_message:
            user_message = user_message.replace("tts", "")
            user_message = user_message.replace("file", "")
            user_message = user_message.replace(" ", "")
            file = open(user_message)
            contents = ""
            for line in file:
                contents += line
            try:
                utils.speak(contents)
            except RecursionError:
                utils.speak("File too long.")
            channel = voice_channel.name

            await message.channel.send(f"Playing {user_message} in {channel}")

            vc = await voice_channel.connect()

            source = discord.FFmpegOpusAudio("voice.mp3")

            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

            vc.stop()
            await vc.disconnect()
        else:
            await message.channel.send(f"{username} is not in a voice channel.")

    # check if the message includes "number_guess" and a mention
    elif "number_guess" in user_message and message.mentions:
        number = random.randint(1, 10)
        await message.channel.send(f"Guess a number between 1 and 10, {username}!")
        guess = await client.wait_for('message', check=lambda message: message.author == message.author)
        if int(guess.content) == number:
            await message.channel.send(f"Correct, {username}!")
        else:
            await message.channel.send(f"Wrong, {username}! The number was {number}.")
        await message.channel.send(f"Thanks for playing, {username}!")
        # ping the mentioned user to guess the number
        await message.channel.send(f"{message.mentions[0].mention} guess a number between 1 and 10!")
        number = random.randint(1, 10)
        # wait for the mentioned user to guess the number
        guess1 = await client.wait_for('message', check=lambda message: message.author == message.mentions)
        if int(guess1.content) == number:
            await message.channel.send(f"Correct, {message.mentions[0].mention}!")
        else:
            await message.channel.send(f"Wrong, {message.mentions[0].mention}! The number was {number}.")
        await message.channel.send(f"Thanks for playing, {message.mentions[0].mention}!")

    elif "chess" in user_message:
        channel = message.channel
        if message.mentions:
            board = chess.Board()
            black = message.mentions[0]
            white = message.author
            await message.channel.send(f"{black.mention} is black and {white.mention} is white.")
            await message.channel.send(f"{white.mention} starts.")
            # draw the letters
            readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
            await message.channel.send(f"```{readable_board}```")
            while not board.is_game_over():
                if board.turn == chess.WHITE:
                    await message.channel.send(f"{white.mention} select a piece to move. (exit to cancel move)")
                    piece = await client.wait_for('message', check=lambda message: message.author == white and message.channel == channel)
                    if piece.content == "exit":
                        await message.channel.send("Move cancelled.")
                        break
                    else:
                        await message.channel.send(f"{white.mention} select a square to move to. (exit to cancel move)")
                        square = await client.wait_for('message', check=lambda message: message.author == white and message.channel == channel)
                        if square.content == "exit":
                            await message.channel.send("Move cancelled.")
                            continue
                        else:
                            try:
                                board.push_san(f"{piece.content}{square.content}")
                            except ValueError:
                                await message.channel.send("That is not a valid move.")
                            # draw the letters
                            readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
                            await message.channel.send(f"```{readable_board}```")
                else:
                    await message.channel.send(f"{black.mention} select a piece to move. (exit to cancel move)")
                    piece = await client.wait_for('message', check=lambda message: message.author == black and message.channel == channel)
                    if piece.content == "exit":
                        await message.channel.send("Move cancelled.")
                        break
                    else:
                        await message.channel.send(f"{black.mention} select a square to move to. (exit to cancel move)")
                        square = await client.wait_for('message', check=lambda message: message.author == black and message.channel == channel)
                        if square.content == "exit":
                            await message.channel.send("Move cancelled.")
                            continue
                        else:
                            try:
                                board.push_san(f"{piece.content}{square.content}")
                            except ValueError:
                                await message.channel.send("That is not a valid move.")
                            # draw the letters
                            readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
                            await message.channel.send(f"```{readable_board}```")

        else:
            depth = 3
            board = chess.Board()
            moves_played = 0
            white = "Plazma Chess Engine"
            black = message.author
            await message.channel.send(f"{message.author.mention} is black.")
            await message.channel.send(f"Plazma Chess Engine is white.")
            await message.channel.send(f"{message.author.mention} starts.")
            await message.channel.send(f"Please enter a depth for the engine to search to (2 - 5 is recommended). (exit to cancel game)")
            depth = await client.wait_for('message', check=lambda message: message.author == black and message.channel == channel)
            # draw the letters
            readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
            await message.channel.send(f"```{readable_board}```")
            while not board.is_game_over():
                if board.turn == chess.WHITE:
                    await message.channel.send(f"Plazma Chess Engine is thinking...")
                    engine_move, moves_played = engine.process(board, "black", moves_played, int(depth.content))
                    print(engine_move)
                    board.push(engine_move)
                    # draw the letters
                    readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
                    await message.channel.send(f"```{readable_board}```")
                else:
                    await message.channel.send(f"{message.author.mention} select a piece to move. (exit to cancel move)")
                    piece = await client.wait_for('message', check=lambda message: message.author == black and message.channel == channel)
                    if piece.content == "exit":
                        await message.channel.send("Move cancelled.")
                        break
                    else:
                        await message.channel.send(f"{message.author.mention} select a square to move to. (exit to cancel move)")
                        square = await client.wait_for('message', check=lambda message: message.author == black and message.channel == channel)
                        if square.content == "exit":
                            await message.channel.send("Move cancelled.")
                            continue
                        else:
                            try:
                                board.push_san(f"{piece.content}{square.content}")
                            except ValueError:
                                await message.channel.send("That is not a valid move.")
                            # draw the letters
                            readable_board = "  a  b  c  d  e  f  g  h\n8 " + board.unicode()[0:16] + "7 " + board.unicode()[16:32] + "6 " + board.unicode()[32:48] + "5 " + board.unicode()[48:64] + "4 " + board.unicode()[64:80] + "3 " + board.unicode()[80:96] + "2 " + board.unicode()[96:112] + "1 " + board.unicode()[112:128]
                            await message.channel.send(f"```{readable_board}```")

            if board.is_checkmate():
                await message.channel.send(f"Checkmate! {board.turn} wins!")
            elif board.is_stalemate():
                await message.channel.send("Stalemate!")
            elif board.is_insufficient_material():
                await message.channel.send("Draw!")
            elif board.is_seventyfive_moves():
                await message.channel.send("Draw!")
            elif board.is_fivefold_repetition():
                await message.channel.send("Draw!")
            else:
                await message.channel.send("Draw!")

    elif "menu" in user_message:
        view = Menu()
        await message.reply('Click a button to get started!', view=view)

class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Children', style=discord.ButtonStyle.blurple)
    async def children(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Children", description="Children are people under the age of 18.", color=discord.Color.random())
        embed.add_field(name="Children", value="Children are people under the age of 18.", inline=False)
        embed.add_field(name="Not Children", value="Not Children are people over the age of 18.", inline=False)
        embed.set_footer(text="Plazma")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label='Not Children', style=discord.ButtonStyle.blurple)
    async def not_children(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Not Children", description="Not Children are people over the age of 18.", color=discord.Color.random())
        embed.add_field(name="Children", value="Children are people under the age of 18.", inline=False)
        embed.add_field(name="Not Children", value="Not Children are people over the age of 18.", inline=False)
        embed.set_footer(text="Plazma")
        await interaction.response.send_message(embed=embed, ephemeral=True)

keep_alive()
client.run('MTAwMjE4NjEwMDE3OTIyNjYyNA.Gq7onl.ZlqnGHfAU8nH7A-oD7O_BjcRDojSF_Xf6x_yaE')