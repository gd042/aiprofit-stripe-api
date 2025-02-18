import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

stripe.api_key = os.getenv("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")

@app.route('/')
def home():
    return "AIProfit Stripe API is Live!"

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv("WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400

    if event['type'] == 'checkout.session.completed':
        print("✅ Payment successful!")
        return jsonify({"success": True}), 200

    return jsonify({"status": "Webhook received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
