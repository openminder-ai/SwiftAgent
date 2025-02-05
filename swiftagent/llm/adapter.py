from litellm import (
    acompletion,
)

import openai

client = openai.AsyncOpenAI()


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
        # return await client.chat.completions.create(*args, **kwargs)
