import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

API_KEY     = os.environ["AZURE_OPENAI_API_KEY"]
ENDPOINT    = os.environ["AZURE_OPENAI_ENDPOINT"]  # e.g., https://<resource>.cognitiveservices.azure.com/
DEPLOYMENT  = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
API_VERSION = os.environ.get("OPENAI_API_VERSION", "2025-01-01-preview")

def normalize_endpoint(ep: str) -> str:
    # Accepts either base host or full REST path; returns base host with trailing slash.
    base = ep.split("?", 1)[0]
    if "/openai/" in base:
        base = base.split("/openai/", 1)[0]
    if not base.endswith("/"):
        base += "/"
    return base

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=normalize_endpoint(ENDPOINT),
)

# 1. Create the dictionary to store our saved responses
response_cache = {}

def chat(prompt: str, stream: bool = False, max_tokens: int = 500, temperature: float = 0.3):
    """
    Calls Chat Completions on your Azure deployment with local caching to save tokens.
    """
    # 2. Check the cache FIRST (We skip caching for streaming to keep it simple)
    if not stream and prompt in response_cache:
        print("\n[⚡ CACHE HIT: Returning saved response instead of calling Azure!]")
        return response_cache[prompt]

    # 3. If not in cache, make the actual API call
    resp = client.chat.completions.create(
        model=DEPLOYMENT, 
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
    )

    if stream:
        print("\n--- streaming start ---")
        for chunk in resp:
            if not getattr(chunk, "choices", None):
                continue
            choice = chunk.choices[0]
            delta = getattr(choice, "delta", None)
            text = getattr(delta, "content", None) if delta else None
            if text:
                print(text, end="", flush=True)
        print("\n--- streaming end ---\n")
        return None
    else:
        # 4. Grab the completed text from Azure
        final_text = resp.choices[0].message.content
        
        # 5. Save it to our dictionary for next time BEFORE returning it
        response_cache[prompt] = final_text
        return final_text



print("Standard completion:")
print(chat("Summarize the main trends in global cloud computing for 2024.", stream=True))



if __name__ == "__main__":
    test_prompt = "What are the top 3 benefits of cloud computing? Keep it very brief."
    
    print("--- FIRST CALL (Should hit Azure) ---")
    print(chat(test_prompt, stream=False))
    
    print("\n--- SECOND CALL (Should hit the local cache) ---")
    print(chat(test_prompt, stream=False))