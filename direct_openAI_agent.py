import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Import the base class and the event loop from your async_chat_agent.py file
from async_chat_agent import AgentBase, run_event_loop

load_dotenv()

class DirectOpenAIAgent(AgentBase):
    def __init__(self, name="DirectOpenAIAgent"):
        super().__init__(name=name)
        
        self.state['response_cache'] = {}
        self.client = AsyncOpenAI()
        self.model = "gpt-4o-mini"

    # 1. The chat method MUST use 'yield'
    async def chat(self, prompt: str, history: list, stream: bool = False, temperature: float = 0.3):
        if prompt in self.state['response_cache']:
            print("\n[⚡ CACHE HIT: Returning saved response instead of calling OpenAI!]")
            yield self.state['response_cache'][prompt]
            return

        api_payload = [{"role": "system", "content": "You are a helpful and concise AI assistant."}] + history

        resp = await self.client.chat.completions.create(
            model=self.model, 
            messages=api_payload, 
            temperature=temperature,
            stream=stream,
        )

        if stream:
            print("\n--- streaming start ---")
            full_text = "" 
            
            async for chunk in resp:
                if getattr(chunk.choices[0], "delta", None) and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_text += content 
                    # Yield the building string continuously back to handle_message
                    yield full_text 
                    
            print("\n--- streaming end ---\n")
            self.state['response_cache'][prompt] = full_text
            
        else:
            final_text = resp.choices[0].message.content
            self.state['response_cache'][prompt] = final_text
            # Yield the final text block
            yield final_text

    # 2. handle_message MUST ALSO use 'yield'
    async def handle_message(self, message: str):
        self.state['message_history'].append({'role': 'user', 'content': message})
        reply_text = ""

        if message.lower().startswith("ask:"):
            prompt = message[4:].strip()
            try:
                # Catch the yielded text from the chat method
                async for chunk in self.chat(prompt=prompt, history=self.state['message_history'], stream=False):
                    reply_text = chunk
                    yield f"OpenAI says:\n{reply_text}"
            except Exception as e:
                reply_text = f"Error calling OpenAI: {e}"
                yield reply_text
                
        elif message.lower().startswith("stream:"):
            prompt = message[7:].strip()
            try:
                # Continuously yield the building string to the UI
                async for cumulative_text in self.chat(prompt=prompt, history=self.state['message_history'], stream=True):
                    reply_text = cumulative_text
                    yield reply_text
            except Exception as e:
                reply_text = f"Error streaming from OpenAI: {e}"
                yield reply_text
                
        else:
            reply_text = f"Echo: {message}"
            yield reply_text

        # Save AI reply to history
        self.state['message_history'].append({'role': 'assistant', 'content': reply_text})

        # Memory Cleanup
        if len(self.state['message_history']) > 10:
            self.state['message_history'] = self.state['message_history'][-10:]

if __name__ == "__main__":
    my_agent = DirectOpenAIAgent()
    asyncio.run(run_event_loop(my_agent))