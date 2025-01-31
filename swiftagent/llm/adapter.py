from litellm import (
    acompletion,
)


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
