from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing Anthropic API connection...")

try:
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "Say 'API working!' in one sentence"
        }]
    )
    
    print("✅ SUCCESS!")
    print(f"Response: {message.content[0].text}")
    
except Exception as e:
    print("❌ ERROR:")
    print(f"   {str(e)}")