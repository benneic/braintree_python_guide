import braintree

from flask import Flask, request, render_template
app = Flask(__name__)

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="use_your_merchant_id",
                                  public_key="use_your_public_key",
                                  private_key="use_your_private_key")

@app.route("/")
def form():
    return render_template("braintree.html")

@app.route('/create_customer', methods=["POST"])
def create_customer():
    result = braintree.Customer.create({
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "credit_card": {
            "billing_address": {
                "postal_code": request.form["postal_code"]
            },
            "number": request.form["number"],
            "expiration_month": request.form["month"],
            "expiration_year": request.form["year"],
            "cvv": request.form["cvv"]
        }
    })
    if result.is_success:
        return """<h1>Customer created with name: {0}</h1>'
                '<a href="/subscriptions?id={1}">Click here to sign this Customer up for a recurring payment</a>'
                """.format(result.customer.first_name + " " + result.customer.last_name, result.customer.id)
    else:
        return "<h1>Error: {0}</h1>".format(result.message)

@app.route('/subscriptions')
def subscriptions():
    try:
        customer_id = request.args['id']
        customer = braintree.Customer.find(customer_id)
        payment_method_token = customer.credit_cards[0].token

        result = braintree.Subscription.create({
            "payment_method_token": payment_method_token,
            "plan_id": "test_plan_1"
        })
        if result.is_success:
            return "<h1>Subscription Status {0}</h1>".format(result.subscription.status)
        else:
            return "<h1>Error: {0}</h1>".format(result.message)
    except braintree.exceptions.NotFoundError:
        return "<h1>No customer found for id: {0}".format(request.args['id'])

if __name__ == '__main__':
    app.run(debug=True)
