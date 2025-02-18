import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your Stripe secret key from environment variables (Render, etc.)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Optional: If you have a separate environment variable for the webhook secret
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


# -----------------------------
# 1) Subscription & Customer Routes
# -----------------------------

@app.route("/create-customer", methods=["POST"])
def create_customer():
    """
    Creates a Stripe Customer.
    JSON Input: { "email": "...", "name": "..." }
    Returns the new Customer object.
    """
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
    """
    Creates a subscription for the given customer & price.
    JSON Input: { "customer_id": "cus_...", "price_id": "price_..." }
    Returns either a Subscription or a Checkout Session ID, depending on your approach.
    """
    data = request.json
    if not data or "customer_id" not in data or "price_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    customer_id = data["customer_id"]
    price_id = data["price_id"]

    try:
        # Direct Subscription Approach (requires the customer to have a default payment method attached):
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            expand=["latest_invoice.payment_intent"]
        )
        return jsonify(subscription)

        # OR, if you want to use Stripe Checkout for new card details:
        # session = stripe.checkout.Session.create(
        #     customer=customer_id,
        #     payment_method_types=["card"],
        #     line_items=[{"price": price_id, "quantity": 1}],
        #     mode="subscription",
        #     success_url="https://yourdomain.com/success",
        #     cancel_url="https://yourdomain.com/cancel",
        # )
        # return jsonify({"sessionId": session.id})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# 2) Webhook Route
# -----------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Stripe Webhook listener. Verifies signature & handles events like:
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    if not WEBHOOK_SECRET:
        return jsonify({"error": "No WEBHOOK_SECRET set in environment"}), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except Exception as e:
        return f"Webhook Error: {str(e)}", 400

    # Handle specific event types
    if event["type"] == "checkout.session.completed":
        print("✅ checkout.session.completed event received")
        # e.g., finalize user account creation or mark them active
    elif event["type"] == "invoice.payment_succeeded":
        print("✅ invoice.payment_succeeded event received")
        # e.g., confirm subscription payment
    elif event["type"] == "invoice.payment_failed":
        print("❌ invoice.payment_failed event received")
        # e.g., notify user of failed payment
    else:
        print(f"Unhandled event type: {event['type']}")

    return "", 200


# -----------------------------
# 3) Run Locally (For Dev)
# -----------------------------

if __name__ == "__main__":
    # For local testing: python stripe_integration.py
    # On Render, gunicorn will handle this (Start Command: gunicorn stripe_integration:app)
    app.run(port=5000, debug=True)
