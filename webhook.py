import os
import stripe
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Retrieve Webhook Secret from Environment Variables
endpoint_secret = os.getenv("WEBHOOK_SECRET")

# Set Stripe API Key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    if not endpoint_secret:
        return jsonify({"error": "Webhook secret not set in environment"}), 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400

    # Process Events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_invoice_success(invoice)

    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_invoice_failure(invoice)

    return jsonify({"status": "success"}), 200

def handle_checkout_session(session):
    """Handles successful checkout sessions."""
    customer_email = session.get("customer_email", "No email provided")
    print(f"✅ Payment success for {customer_email}")

def handle_invoice_success(invoice):
    """Handles successful invoice payments."""
    invoice_id = invoice["id"]
    print(f"✅ Invoice {invoice_id} was paid successfully.")

def handle_invoice_failure(invoice):
    """Handles failed invoice payments."""
    invoice_id = invoice["id"]
    print(f"❌ Invoice {invoice_id} failed. Payment required.")

if __name__ == '__main__':
    app.run(port=4242, debug=True)
