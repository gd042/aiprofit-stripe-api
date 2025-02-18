import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "AIProfit Stripe API is Live!"

# Stripe API Keys
stripe.api_key = "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"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'AIProfitHQ Subscription',
                    },
                    'unit_amount': 2000,  # $20 per month
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://www.aiprofithq.com/success',
            cancel_url='https://www.aiprofithq.com/cancel',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = "your_endpoint_secret_here"
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        print("Payment successful!")
    elif event['type'] == 'invoice.payment_failed':
        print("Payment failed!")

    return '', 200

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 if PORT is not set
    app.run(host='0.0.0.0', port=port)

