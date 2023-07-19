from gtts import gTTS
import subprocess


def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = 'voice.mp3'
    tts.save(filename)


def compile_cpp():
    code = open("code.cpp", "r").read()
    code = code.replace("```", "")
    message = subprocess.run(["g++", "code.cpp", "-o", "code"],
                             capture_output=True)
    if message.returncode == 0:
        message = subprocess.run(["./code"], capture_output=True)
        message = message.stdout.decode('utf-8')
    else:
        message = message.stderr.decode('utf-8')
    return message


def compile_python():
    new_code = ""
    code = open("code.py", "r").read()
    for letter in code:
        if letter == "`":
            new_code += ""
        else:
            new_code += letter
    open("code.py", "w").write(new_code)
    message = subprocess.run(["python", "code.py"], capture_output=True)
    if message.returncode == 0:
        message = message.stdout.decode('utf-8')
    else:
        message = message.stderr.decode('utf-8')
    return message
