import gradio as gr
import asyncio

# Import the fully functioning agent from your backend file
from direct_openAI_agent import DirectOpenAIAgent 

# 1. Instantiate the agent once when the server starts
# This ensures it keeps its memory alive for the duration of your web session
my_agent = DirectOpenAIAgent()

# 2. Create the bridge between Gradio and your backend
async def chat_wrapper(message, history):
    # Add a polite intercept for exit commands
    if message.lower() in ['exit', 'quit']:
        yield "Chat session ended. (To shut down the server, press Ctrl+C in your terminal)."
        return # Stops the function here so it doesn't process the exit command
        
    # 'async for' catches each chunk of text as the backend yields it
    # This is the magic that makes the streaming visible in the browser!
    async for partial_reply in my_agent.handle_message(message):
        yield partial_reply

# 3. Build the User Interface
demo = gr.ChatInterface(
    fn=chat_wrapper,
    title="🤖 Direct OpenAI Agent",
    
    # Markdown formatting makes the warning bold and easy to read
    description="**⚠️ IMPORTANT:** You MUST start your message with `Ask:` or `Stream:` (e.g., *Ask: What is Python?*). If you do not use this trigger word, the agent will only echo your text to save API costs.",
    
    # Adding clickable examples teaches the user exactly how to interact
    examples=[
        "Ask: What are the top 3 benefits of cloud computing?", 
        "Stream: Write a short poem about coding.", 
        "Hello! (This will just echo back)"
    ]
)

if __name__ == "__main__":
    print("Launching Web Interface...")
    demo.launch()