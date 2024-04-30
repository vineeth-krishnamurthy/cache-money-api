import json
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from openai import OpenAI
from data.client_data import client_data
import base64
import os
import datetime as dt
import time
from datetime import date, timedelta
from dotenv import load_dotenv
import plaid
from plaid.model.payment_amount import PaymentAmount
from plaid.model.payment_amount_currency import PaymentAmountCurrency
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.recipient_bacs_nullable import RecipientBACSNullable
from plaid.model.payment_initiation_address import PaymentInitiationAddress
from plaid.model.payment_initiation_recipient_create_request import PaymentInitiationRecipientCreateRequest
from plaid.model.payment_initiation_payment_create_request import PaymentInitiationPaymentCreateRequest
from plaid.model.payment_initiation_payment_get_request import PaymentInitiationPaymentGetRequest
from plaid.model.link_token_create_request_payment_initiation import LinkTokenCreateRequestPaymentInitiation
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.asset_report_create_request import AssetReportCreateRequest
from plaid.model.asset_report_create_request_options import AssetReportCreateRequestOptions
from plaid.model.asset_report_user import AssetReportUser
from plaid.model.asset_report_get_request import AssetReportGetRequest
from plaid.model.asset_report_pdf_get_request import AssetReportPDFGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.identity_get_request import IdentityGetRequest
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transfer_authorization_create_request import TransferAuthorizationCreateRequest
from plaid.model.transfer_create_request import TransferCreateRequest
from plaid.model.transfer_get_request import TransferGetRequest
from plaid.model.transfer_network import TransferNetwork
from plaid.model.transfer_type import TransferType
from plaid.model.transfer_authorization_user_in_request import TransferAuthorizationUserInRequest
from plaid.model.ach_class import ACHClass
from plaid.model.transfer_create_idempotency_key import TransferCreateIdempotencyKey
from plaid.model.transfer_user_address_in_request import TransferUserAddressInRequest
from plaid.model.signal_evaluate_request import SignalEvaluateRequest
from plaid.model.statements_list_request import StatementsListRequest
from plaid.model.link_token_create_request_statements import LinkTokenCreateRequestStatements
from plaid.model.statements_download_request import StatementsDownloadRequest
from plaid.api import plaid_api

load_dotenv()

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')
host = plaid.Environment.Sandbox

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

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

access_token = None
payment_id = None
transfer_id = None
item_id = None

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

client = OpenAI()

class GenerateBudget(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint - calls the openAI api, with a budget response
        responses:
            200:
                description: A successful GET request
        """
        user_message = request.args.get('text')
        user1 = client_data[0]
        transactions_input = str(user1)

        ai_prompt = "If the user input is related to finances, creating a budget, or saving money your answer should be a budget" \
                    "that follows this format for every transaction category in transactions input - {budget:{category: dollar amount}} that addresses the user's needs"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "system", "content": ai_prompt},
                {"role": "system", "content": transactions_input},
                {"role": "user", "content": user_message},
            ]
        )

        output = response.choices[0].message.content

        return jsonify(output)

class GrabData(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint, and grabs all the data in our mock database
        responses:
            200:
                description: A successful GET request
        """
        return jsonify(client_data)


class CreateLinkToken(Resource):
    def post(self):
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
            response = plaid_client.link_token_create(request)
            return response.to_dict(), 200
        except plaid.ApiException as e:
            return json.loads(e.body), 400

class GetTransactions(Resource):
    def get(self):
        """
        This method responds to the GET request for this endpoint and returns the transactions.
        ---
        tags:
        - Transactions
        parameters:
            - name: access_token
              in: query
              type: string
              required: true
              description: The access token for the user
            - name: start_date
              in: query
              type: string
              required: true
              description: The start date for the transactions in 'YYYY-MM-DD' format
            - name: end_date
              in: query
              type: string
              required: true
              description: The end date for the transactions in 'YYYY-MM-DD' format
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            transactions:
                                type: array
                                description: The list of transactions
        """
        access_token = request.args.get('access_token')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Get transactions for a date range
        response = plaid_client.Transactions.get(access_token, start_date, end_date)

        # Manipulate the count and offset parameters to paginate transactions and retrieve all available data
        while len(response['transactions']) < response['total_transactions']:
            response['transactions'].extend(plaid_client.Transactions.get(access_token, start_date, end_date, offset=len(response['transactions']))['transactions'])

        return jsonify(response['transactions'])


api.add_resource(GenerateBudget, "/generatebudget")
api.add_resource(GrabData, "/grabdata")
api.add_resource(GetTransactions, "/transactions/get")
api.add_resource(CreateLinkToken, '/api/create_link_token')

if __name__ == "__main__":
    app.run(debug=True)