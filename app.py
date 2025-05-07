import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# OpenAI API key from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

# Twilio Client setup
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(twilio_account_sid, twilio_auth_token)

@app.route("/incoming/", methods=["POST"])
def incoming():
    # Get the incoming message and sender's number
    user_message = request.form.get("Body")
    user_number = request.form.get("From")

    # Log incoming message (optional)
    print(f"Received message from {user_number}: {user_message}")

    # OpenAI Chat Completion (response generation)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful Red Cross Kenya assistant."},
            {"role": "user", "content": user_message}
        ]
    )

    # Extract response from OpenAI
    reply = response["choices"][0]["message"]["content"]

    # Create a Twilio response
    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    
    # Send the reply back to the user on WhatsApp
    return str(twilio_response)

if __name__ == "__main__":
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)
