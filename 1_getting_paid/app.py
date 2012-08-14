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
    tr_data = braintree.Transaction.tr_data_for_sale(
            {"transaction": {"type": "sale",
                             "amount": "10",
                             "options": {"submit_for_settlement": True}}},
            "http://localhost:5000/braintree")
    braintree_url = braintree.TransparentRedirect.url()
    return render_template("form.html", tr_data=tr_data,
                           braintree_url=braintree_url)

@app.route("/braintree")
def result():
    query_string = urlparse.urlparse(request.url).query
    result = braintree.TransparentRedirect.confirm(query_string)
    if result.is_success:
        message = "Transaction Successful: %s. Amount: %s" % (
                        result.transaction.status, result.transaction.amount)
    else:
        message = "Errors: %s" % " ".join(error.message for error in
                                                   result.errors.deep_errors)
    return render_template("response.html", message=message)

# Run the app
if __name__ == "__main__":
    app.run()
