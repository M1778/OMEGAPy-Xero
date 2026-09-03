from .xero import blockize, Compiler, BlockChain
from markdown_it import MarkdownIt


class BaseAPI:
    model = ""
    max_tokens = 8000

    def __init__(self, apikey):
        self.client = None
        self.messages = []
        self.compiler = Compiler(BlockChain("_STARTER_BLOCKCHAIN"))

    def get_formatted_messages(self):
        self.convert_message_roles()
        fmessages = []
        copymessages = self.messages.copy()
        for msg in copymessages:
            newmsg = msg.copy()
            if newmsg['role'] == 'assistant':
                content = ""
                for chunk in self.compiler.update_blockchain(blockize(newmsg['content'])).execute():
                    content += chunk
                MI = MarkdownIt('commonmark', {'html': True, 'breaks': True})
                newmsg['content'] = MI.render(content)
            fmessages.append(newmsg)
        self.convert_message_roles()
        return fmessages

    def chat_pure_message(self, role, content):
        comp = self.client.chat.completions.create(
            messages=[{"role": role, "content": content}],
            max_tokens=self.max_tokens,
            model=self.model)
        return comp

    def user_message(self, content):
        self.messages.append({"role": "user", "content": content})
        comp = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            max_tokens=self.max_tokens)
        self.messages.append({"role": comp.choices[0].message.role, "content": comp.choices[0].message.content})
        return comp

    def system_message(self, content, execute=True):
        self.messages.append({"role": "system", "content": content})
        self.messages.append({"role": "assistant", "content": "$SEND_MESSAGE Start\nHello👋 I am Genos, your virtual assistant. I can do simple tasks on your system if you want...\nI am made using an ULTRAX model of OMEGAPy-XERO Project.\nLet's chat for a bit...\n$END_BLOCK Start"})

    def convert_message_roles(self):
        return True


class ChatGPT_API(BaseAPI):
    model = "gpt-3.5-turbo"
    max_tokens = 8000

    def __init__(self, apikey):
        super().__init__(apikey)
        from openai import OpenAI
        self.client = OpenAI(api_key=apikey)

    def demo_speech(self, text):
        out = self.client.audio.speech.create(text, "tts-1", "fable")
        return out


class Groq_API(BaseAPI):
    model = "llama3-8b-8192"
    max_tokens = 8000

    def __init__(self, apikey):
        super().__init__(apikey)
        from groq import Groq
        self.client = Groq(api_key=apikey)


class TogetherAI(BaseAPI):
    model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    max_tokens = 8000

    def __init__(self, apikey):
        super().__init__(apikey)
        from together import Together
        self.client = Together(api_key=apikey)

    def user_message(self, content):
        self.messages.append({"role": "user", "content": content})
        comp = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            max_tokens=self.max_tokens)
        self.messages.append({"role": comp.choices[0].message.role, "content": comp.choices[0].message.content})
        self.convert_message_roles()
        return comp

    def convert_message_roles(self):
        from together.types import chat_completions
        for i in range(len(self.messages)):
            if self.messages[i]['role'] == chat_completions.MessageRole.ASSISTANT and str(self.messages[i]['role']) != self.messages[i]['role']:
                self.messages[i]['role'] = 'assistant'
        return True


select_api = {
    "chatgpt": ChatGPT_API,
    "groq": Groq_API,
    "together": TogetherAI
}
