from essentials import apis
from essentials import prompts
from configparser import ConfigParser
import time

config = ConfigParser()
config.read("./config.cfg")

all_models=[]
n = 0
for section in config.values():
    if section == config['DEFAULT']:
        continue
    all_models.append(section)
    print(f"{n} - {section['name']}")
    n+=1

model_n=int(input("Which model do you want to use:"))
model=all_models[model_n]

all_prompts=list(prompts.available.keys())
n = 0
for prompt_ in all_prompts:
    print(f"{n} - {prompt_}")
    n+=1

prompt_n=int(input("Which model settings do you want:"))
prompt = prompts.available[all_prompts[prompt_n]]

print("CONFIGURING...")
def print_slow(content):
    content=content.split(' ')
    for word in content:
        print(word,end=' ')
        time.sleep(0.01)

if model['name'] == "chatgpt":
    ...
elif model['name'] == "groqai":
    api=apis.Groq_API(model['apikey'])
    initial_prompt=prompt.get_random()
    api.system_message(initial_prompt,False)
    while True:
        chat= input("SendMessage: ")
        response=api.user_message(chat)
        print_slow(response.choices[0].message.content)
elif model['name'] == "togetherai":
    api=apis.TogetherAI(model['apikey'])
    initial_prompt=prompt.get_random()
    api.system_message(initial_prompt,False)
    while True:
        chat= input("SendMessage: ")
        #if prompt == prompts.official_assistant_formatting_v1:
        #    api.system_message(initial_prompt,False)
        response=api.user_message(chat)
        print_slow(response.choices[0].message.content)
else:
    raise TypeError("Invalid model selected.")