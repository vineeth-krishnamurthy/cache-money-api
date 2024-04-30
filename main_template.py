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
        This method responds to the GET request for this endpoint and returns the data in uppercase.
        ---
        tags:
        - Text Processing
        parameters:
            - name: text
              in: query
              type: string
              required: true
              description: The text to be converted to uppercase
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            text:
                                type: string
                                description: The text in uppercase
        """
        text = request.args.get('text')
        user1 = client_data[0]
        transactions_input = str(user1)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": transactions_input},
                {"role": "user", "content": "Given these monthly transactions, create a budget for me for next month"}
            ]
        )

        output = response.choices[0].message.content

        print(output)

        return jsonify(output)

api.add_resource(GenerateBudget, "/generatebudget")

if __name__ == "__main__":
    app.run(debug=True)