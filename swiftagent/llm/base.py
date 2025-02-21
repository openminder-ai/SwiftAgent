from litellm import acompletion
from dotenv import load_dotenv

load_dotenv()


class LLM:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    async def inference(self):
        return await acompletion(model=self.name, *self.args, **self.kwargs)
