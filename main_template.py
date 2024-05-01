import json
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from openai import OpenAI
from data.client_data import client_data
import plaid
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.link_token_create_request_statements import LinkTokenCreateRequestStatements
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from dotenv import load_dotenv
from datetime import date, timedelta
import os
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
import time
from datetime import date, timedelta


load_dotenv()

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')


def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)
api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_id is only relevant for the UK Payment Initiation product.
# We store the payment_id in memory - in production, store it in a secure
# persistent data store.
payment_id = None
# The transfer_id is only relevant for Transfer ACH product.
# We store the transfer_id in memory - in production, store it in a secure
# persistent data store.
transfer_id = None

item_id = None

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

client = OpenAI()

class CurrentSpending(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint, and grabs all the data in our mock database
        responses:
            200:
                description: A successful GET request
        """
        userID = request.args.get('userID')
        client_info = client_data[userID]

        client_transactions = client_info['transactions']

        # Groups all transactions by category. Initializes the budget
        total_spend = 0
        spending_by_category = {}
        for transaction in client_transactions:
            total_spend += transaction['amount']
            category = transaction['category']
            if category in spending_by_category:
                spending_by_category[category]['dollar_amount'] = spending_by_category[category]['dollar_amount'] + transaction['amount']
                spending_by_category[category]['amount_trans'] = spending_by_category[category]['amount_trans'] + 1
            else:
                spending_by_category[category] = {'dollar_amount': transaction['amount'], 'amount_trans': 1}
                # see if budget exists for category. if not, intitialize to 0
                if category in client_info['budget']['by_category']:
                    spending_by_category[category]['budget'] = client_info['budget']['by_category'][category]
                else:
                    spending_by_category[category]['budget'] = 0

        totals = {"total_spend": total_spend, "total_budget": client_info['budget']['total']}

        output_data = {'transactions': client_transactions, 'categories': spending_by_category, 'total': totals}
        json_data = json.dumps(output_data)

        return json_data

class GenerateBudget(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint - calls the openAI api, with a budget response
        responses:
            200:
                description: A successful GET request
        """
        userID = request.args.get('userID')
        client_transactions = client_data[userID]['transactions']
        transactions_input = str(client_transactions)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": transactions_input},
                {"role": "user", "content": "Create a budget following this format - {budget: {category: dollar amount}} for each transaction category, making sure that the budget for each category is less than the amount actually spent on that category"},
            ]
        )

        output = response.choices[0].message.content

        return jsonify(output)

class GenerateChatBotResponse(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint - calls the openAI api, with a budget response
        responses:
            200:
                description: A successful GET request
        """
        user_id = request.args.get('userID')
        user_message = request.args.get('text')

        client_transactions = client_data[user_id]['transactions']

        ai_prompt = "If the user input is related to general finance, creating a budget, or saving money, answer their question with their transactions in mind. Else, the output should be 'Sorry, I can only answer finance related questions :('"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={ "type": "json_object" },
            messages=[
                {'role': 'system', 'content': ai_prompt},
                {'role': 'system', 'content': str(client_transactions)},
                {'role': 'user', 'content': user_message}
            ]
        )

        return response

api.add_resource(CurrentSpending, "/current_spending")
api.add_resource(GenerateBudget, "/generate_budget")
api.add_resource(GenerateChatBotResponse, "/generate_chat_response")

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )
        if PLAID_REDIRECT_URI!=None:
            request['redirect_uri']=PLAID_REDIRECT_URI
        if Products('statements') in products:
            statements=LinkTokenCreateRequestStatements(
                end_date=date.today(),
                start_date=date.today()-timedelta(days=30)
            )
            request['statements']=statements
    # create link token
        response = plaid_client.link_token_create(request)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)

if __name__ == "__main__":
    app.run(debug=True)