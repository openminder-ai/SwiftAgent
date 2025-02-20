from litellm import (
    acompletion,
)

# from openai import AsyncOpenAI

from dotenv import load_dotenv

load_dotenv()


class LLMAdapter:

    @staticmethod
    async def inference(
        *args,
        **kwargs,
    ):
        return await acompletion(
            *args,
            **kwargs,
        )
        # async with AsyncOpenAI() as client:
        #     return await client.chat.completions.create(*args, **kwargs)
