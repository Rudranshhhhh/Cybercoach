from services.llm_client import llm_client
import traceback

print("Testing LLM Client...")
print(f"Configured: {llm_client.is_configured()}")
print(f"API Key length: {len(llm_client.api_key) if llm_client.api_key else 0}")
print(f"Base URL: {llm_client.base_url}")
print(f"Model: {llm_client.model_name}")

# Test chat completion with error handling
print("\n" + "="*50)
print("Testing chat completion...")

try:
    if llm_client.client:
        response = llm_client.client.chat.completions.create(
            model=llm_client.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello"}
            ],
            temperature=0.8
        )
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("ERROR: Client is None")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
