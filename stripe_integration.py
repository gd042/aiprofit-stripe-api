import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Stripe secret key from environment (Render)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Webhook secret from environment (Render)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


# -----------------------------
# 1. Customer & Subscription Routes
# -----------------------------
@app.route("/create-customer", methods=["POST"])
def create_customer():
    """
    Creates a Stripe Customer.
    JSON input: { "email": "...", "name": "..." }
    Returns the new Customer object.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    name = data.get("name")

    if not email or not name:
        return jsonify({"error": "Missing email or name"}), 400

    try:
        customer = stripe.Customer.create(email=email, name=name)
        return jsonify(customer)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/create-subscription", methods=["POST"])
def create_subscription():
    """
    Creates a Stripe Checkout session for subscription or direct subscription.
    JSON input: { "customer_id": "cus_...", "price_id": "price_..." }
    Must return { "sessionId": "..." } if using redirectToCheckout in the frontend.
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    customer_id = data.get("customer_id")
    price_id = data.get("price_id")

    if not customer_id or not price_id:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Using Stripe Checkout to collect payment details:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url="https://YOUR_DOMAIN.com/success",
            cancel_url="https://YOUR_DOMAIN.com/cancel",
        )
        return jsonify({"sessionId": session.id})

        # OR, if you already have a default payment method & want direct sub:
        # subscription = stripe.Subscription.create(
        #     customer=customer_id,
        #     items=[{"price": price_id}],
        #     expand=["latest_invoice.payment_intent"]
        # )
        # return jsonify(subscription)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# 2. Webhook Route
# -----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Stripe Webhook listener for events like:
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    if not WEBHOOK_SECRET:
        return jsonify({"error": "No WEBHOOK_SECRET in environment"}), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except Exception as e:
        return f"Webhook Error: {str(e)}", 400

    # Handle specific events
    if event["type"] == "checkout.session.completed":
        print("✅ checkout.session.completed - finalize user subscription logic here.")
    elif event["type"] == "invoice.payment_succeeded":
        print("✅ invoice.payment_succeeded - subscription payment successful.")
    elif event["type"] == "invoice.payment_failed":
        print("❌ invoice.payment_failed - notify user or try again.")
    else:
        print(f"Unhandled event type: {event['type']}")

    return "", 200


if __name__ == "__main__":
    # Local dev testing: python stripe_integration.py
    # On Render, set Start Command to: gunicorn stripe_integration:app
    app.run(port=5000, debug=True)
