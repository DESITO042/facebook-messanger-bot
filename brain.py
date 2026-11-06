from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# PUT YOUR GROQ KEY HERE
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
You are DESITO AI Bot for Amos Store in Enugu, Nigeria.
You sell: Phones (iPhone, Samsung, Tecno, Infinix), Laptops (HP, Dell, MacBook), Accessories, Data, Airtime.
Prices: iPhone 13 - 450k, iPhone 14 - 620k, iPhone 15 - 850k, Samsung S23 - 550k, A54 - 320k, HP ProBook - 380k, Dell - 420k, MacBook Air - 950k.
Delivery: Enugu town 1,500, free above 100k. Areas: Holy Ghost, New Haven, Independence Layout, Abakpa, Emene, Nsukka.
Payment: Transfer or Pay on Delivery.
Style: Friendly Nigerian shop owner, warm, small Pidgin, short replies (max 3 sentences), always try to close sale.
If customer wants to order, collect name, phone, address.
Never say you are AI. You are DESITO AI Bot assistant for Amos Store.
"""

@app.post("/chat")
def chat(req: ChatRequest):
    # Try Real AI first
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": req.message}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            },
            timeout=10
        )
        data = res.json()
        reply = data["choices"][0]["message"]["content"]
        return {"reply": reply, "source": "AI"}
    except Exception as e:
        print("AI failed, using fallback:", e)
        # Fallback - old rules if internet/API fail
        msg = req.message.lower()
        if "iphone" in msg:
            reply = "iPhone we get! 13 - ₦450,000, 14 - ₦620,000, 15 - ₦850,000. Which one you want?"
        elif "laptop" in msg:
            reply = "Laptop full ground! HP - ₦380k, Dell - ₦420k, MacBook - ₦950k. Which one?"
        else:
            reply = f"I hear you. For Amos Store, we fit help you buy phone, laptop, accessory. Wetin you wan buy?"
        return {"reply": reply, "source": "fallback"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)