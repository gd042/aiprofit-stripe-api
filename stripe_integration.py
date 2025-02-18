import os
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@app.route("/create-customer", methods=["POST"])
def create_customer():
    data = request.json
    if not data or "email" not in data or "name" not in data:
        return jsonify({"error": "Missing email or name"}), 400
    try:
        customer = stripe.Customer.create(
            email=data["email"],
            name=data["name"]
        )
        return jsonify(customer)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/create-subscription", methods=["POST"])
def create_subscription():
    data = request.json
    if not data or "customer_id" not in data or "price_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        session = stripe.checkout.Session.create(
            customer=data["customer_id"],
            payment_method_types=["card"],
            line_items=[{"price": data["price_id"], "quantity": 1}],
            mode="subscription",
            success_url="https://your-website.com/success",
            cancel_url="https://your-website.com/cancel"
        )
        return jsonify({"sessionId": session.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/webhook", methods=["POST"])
def webhook():
    if not WEBHOOK_SECRET:
        return jsonify({"error": "No WEBHOOK_SECRET"}), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except Exception as e:
        return f"Webhook Error: {str(e)}", 400

    if event["type"] == "checkout.session.completed":
        print("✅ checkout.session.completed - user subscribed!")
    elif event["type"] == "invoice.payment_succeeded":
        print("✅ invoice.payment_succeeded - subscription payment success!")
    elif event["type"] == "invoice.payment_failed":
        print("❌ invoice.payment_failed - needs updated payment method.")
    else:
        print(f"Unhandled event type: {event['type']}")

    return "", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
