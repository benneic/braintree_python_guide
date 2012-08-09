import urlparse

from flask import Flask, request, render_template
app = Flask(__name__)

import braintree

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="your_merchant_id",
                                  public_key="your_public_key",
                                  private_key="your_private_key")

@app.route("/")
def form():
    tr_data = braintree.Customer.tr_data_for_create({},
                                             "http://localhost:5000/braintree")
    braintree_url = braintree.TransparentRedirect.url()
    return render_template("form.html", tr_data=tr_data,
                           braintree_url=braintree_url)

@app.route("/braintree")
def result():
    query_string = urlparse.urlparse(request.url).query
    result = braintree.TransparentRedirect.confirm(query_string)
    customer_id = None
    if result.is_success:
        message = "Customer Created with ID: %s" % result.customer.email
        customer_id = result.customer.id
    else:
        message = "Errors: %s" % " ".join(error.message for error in
                                                    result.errors.deep_errors)
    return render_template("response.html", message=message,
                           customer_id=customer_id)

@app.route("/subscriptions")
def subscriptions():
    customer_id = request.args["id"]
    customer = braintree.Customer.find(customer_id)
    payment_method_token = customer.credit_cards[0].token
    result = braintree.Subscription.create(
            {"payment_method_token": payment_method_token,
             "plan_id": "test_plan_1"})
    # Start error handling
    if result.is_success:
        message = "Subscription status: %s" % result.subscription.status
    else:
        message = "Message: %s" % result.message
    return render_template("subscriptions.html", message=message)


# Run the app
if __name__ == "__main__":
    app.run()
