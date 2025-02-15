from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

print("hi")

import time

time.sleep(3)

models = ["gpt-4o"]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.75
    )
    print(response.choices[0].message.content)

print("bye")
