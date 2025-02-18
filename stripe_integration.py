from flask import Flask, request, jsonify
import stripe
import os

app = Flask(__name__)

# Stripe API Key (Replace with ENV variables)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create a Customer
@app.route("/create-customer", methods=["POST"])
def create_customer():
    data = request.json
    customer = stripe.Customer.create(
        email=data["email"],
        name=data["name"]
    )
    return jsonify(customer)

# Create a Subscription
@app.route("/create-subscription", methods=["POST"])
def create_subscription():
    data = request.json
    customer_id = data["customer_id"]
    price_id = data["price_id"]
    payment_method_id = data["payment_method_id"]

    # Attach the payment method
    stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

    # Set default payment method
    stripe.Customer.modify(
        customer_id,
        invoice_settings={"default_payment_method": payment_method_id}
    )

    # Create the subscription
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        expand=["latest_invoice.payment_intent"]
    )
    return jsonify(subscription)

# Webhook Listener
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        print("🔔 Payment successful! Processing subscription...")

    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
