import paypalrestsdk

class PaypalServiceAccessor(object):
    """
    A wrapper over paypalrestsdk to create and execute payments on paypal

    Here are the steps involved in a transaction:
        1. first create payment with amount and a return_url
        2. after creating payment, redirect user to an auth_url returned by paypal
        3. after user authenticates, paypal will redirect back to return_url
        4. return_url will call execute_payment to finish the transaction

    see: https://devtools-paypal.com/guide/pay_paypal/python?interactive=OFF&env=sandbox
    """

    # Client Modes
    CLIENT_SANDBOX_MODE = "sandbox"
    CLIENT_LIVE_MODE = "live"

    # Paypal Response Query String keys
    RESPONSE_QS_SUCCESS = "success"
    RESPONSE_QS_PAYMENT_ID = "paymentId"
    RESPONSE_QS_PAYER_ID = "PayerID"


    def __init__(self, client_id, client_secret, mode):
        paypalrestsdk.configure({
            'mode': mode,                                  # live or sandbox
            'client_id': client_id,
            'client_secret': client_secret
        })
        self.paypal_client = paypalrestsdk

    def create_payment(self, amount, return_url, cancel_url, description=""):
        """ Creates a payment in paypal and returns the auth url """
        amount = "%0.2f" % amount
        payment = self.paypal_client.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
            "transactions": [{
                "amount": { "total": amount, "currency": "USD" },
                "description": description 
            }]
        })
        payment.create()
        payment_info = payment.to_dict()
        if not payment.success():
            raise ValueError("Payment creation failed: %s" % payment_info)
        for link in payment_info['links']:
            if link['rel'] == 'approval_url':
                return link['href']
        raise ValueError("Paypal response did not contain redirect url : %s" % payment_info)

    def is_payment_successful(self, payment_id):
        payment = self.paypal_client.Payment.find(payment_id)
        return payment.success()

    def execute_payment(self, payment_id, payer_id):
        payment = self.paypal_client.Payment.find(payment_id)
        return payment.execute({"payer_id": payer_id})
