import asyncio
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI # Using the async client for the event loop

# Load your Azure OpenAI credentials from the .env file
load_dotenv()

class AgentBase:
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        # Using 'role' and 'content' standard for OpenAI message history
        self.state: Dict[str, Any] = {'message_history': []} 
        self.config = config or {}

        # Initialize the Async Azure OpenAI Client
        self.client = AsyncAzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    async def handle_message(self, message: str) -> str:
        # 1. Update history (User message)
        self.state['message_history'].append({'role': 'user', 'content': message})

        # 2. Check for the "Ask:" trigger
        if message.lower().startswith("ask:"):
            # Extract the actual question by slicing off the first 4 characters ("Ask:")
            prompt = message[4:].strip() 
            
            try:
                # Call Azure OpenAI asynchronously
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                ai_answer = response.choices[0].message.content
                reply = f"Echo: {message}\nOpenAI says: {ai_answer}"
            except Exception as e:
                # Basic error handling as requested
                reply = f"Echo: {message}\nError calling Azure OpenAI: {e}"
        else:
            # Default echo response if "Ask:" is not used
            reply = f"Echo: {message}"

        # 3. Update history (Agent reply)
        self.state['message_history'].append({'role': 'assistant', 'content': reply})

        # 4. State Management: Keep only the last 10 messages (5 user/agent pairs)
        if len(self.state['message_history']) > 10:
            self.state['message_history'] = self.state['message_history'][-10:]

        return reply

    # --- The Event Loop ---
async def run_event_loop(agent: AgentBase):
    print(f"Starting {agent.name}. Type 'exit' to quit.")
    print("Tip: Start your message with 'Ask:' to get an AI response.")
    
    # Get the current running async loop
    loop = asyncio.get_running_loop()
    
    while True:
        # Use run_in_executor to make the standard input() function async-friendly
        # This prevents the terminal prompt from freezing the entire background process
        user_input = await loop.run_in_executor(None, input, "\nYou: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting event loop. Goodbye!")
            break
        
        # Process the message
        reply = await agent.handle_message(user_input)
        print(f"\nAgent: {reply}")

if __name__ == "__main__":
    # Instantiate and run
    my_agent = AgentBase(name="MarketResearchAgent")
    asyncio.run(run_event_loop(my_agent))