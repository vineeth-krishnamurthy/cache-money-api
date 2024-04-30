import json
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from openai import OpenAI
from data.client_data import client_data

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

        ai_prompt = "If the user input is related to finances, creating a budget, or saving money, your answer should be a budget that follows this format for every transaction category in the transactions input - {budget:{category: dollar amount}} that addresses the user's needs. The total of the budget should reflect any reduction specified by the user in their input."

        # ai_prompt_2 = "There will always be a savings category. If a savings category does not exist, make sure to create one. Never decrease the dollar amount or percentage allocated to the savings category."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "system", "content": ai_prompt},
                # {"role": "system", "content": ai_prompt_2},
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

api.add_resource(GenerateBudget, "/generatebudget")
api.add_resource(GrabData, "/grabdata")

if __name__ == "__main__":
    app.run(debug=True)