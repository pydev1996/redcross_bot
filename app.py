import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Twilio client setup (not used for sending manually in this code)
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(twilio_account_sid, twilio_auth_token)

# Store user states in memory (use Redis or DB in production)
user_state = {}

@app.route("/incoming", methods=["POST"])
def incoming():
    user_message = request.form.get("Body").strip()
    user_number = request.form.get("From")
    print(f"Received message from {user_number}: {user_message}")

    response = MessagingResponse()
    state = user_state.get(user_number, "menu")

    # Handle main menu
    if state == "menu":
        if user_message == "1":
            response.message("🚨 Emergency help: Call 1199 for Red Cross Kenya assistance.\nReply 0 to return.")
            user_state[user_number] = "emergency"
        elif user_message == "2":
            response.message("💡 Health Tips:\n- Wash hands\n- Eat well\n- Stay hydrated\nReply 0 to return.")
            user_state[user_number] = "health"
        elif user_message == "3":
            response.message("🙋‍♂️ Volunteer Info:\nVisit: redcross.or.ke/volunteer\nReply 0 to return.")
            user_state[user_number] = "volunteer"
        elif user_message == "4":
            response.message("🔍 Ask me anything using AI.\nType your question:")
            user_state[user_number] = "ai_chat"
        else:
            response.message(
                "🇰🇪 Welcome to Red Cross Kenya.\nChoose an option:\n"
                "1. Emergency Assistance\n"
                "2. Health Tips\n"
                "3. Volunteer Info\n"
                "4. Chat with Assistant"
            )
    # AI Chat mode
    elif state == "ai_chat":
        if user_message == "0":
            user_state[user_number] = "menu"
            response.message("Back to main menu:\n1. Emergency\n2. Health Tips\n3. Volunteer\n4. Chat with Assistant")
        else:
            ai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful Red Cross Kenya assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = ai_response["choices"][0]["message"]["content"]
            response.message(reply + "\n\nReply 0 to return to menu.")

    # Any other state: return to menu
    else:
        response.message("Reply 0 to return to the main menu.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
