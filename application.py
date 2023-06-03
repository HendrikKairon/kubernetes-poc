from flask import Flask, request
from flask_restful import Resource, Api
from uuid import uuid4
import kube_manager
from kubernetes import client

app = Flask(__name__)
api = Api(app)


class BotCreator(Resource):
    def post(self):
        payload = request.get_json()

        # Use a default symbol if not provided
        symbol = payload.get("symbol", "BTC/USDT")

        job_name = "bot-job-" + str(uuid4())  # Unique job name

        # We created a name for the kubernetes job, we could for example add a botname for easier filtering.
        # If we would send a botName in the JSON body we could use it to create the name and store it in the associated DB based off of that name.
        # This is beyond the scope of this poc but a possibility
        job = kube_manager.create_job_object(job_name, symbol)
        status = kube_manager.create_job(client.BatchV1Api(), job)
        return {"message": f"Starting bot: {job_name}", "status": status}, 200


class BotManager(Resource):
    def get(self, job_name):
        # You can implement a logic here to get status of your bots.
        # For simplicity, this method returns a message.
        # We could write a get_logs function in the kube_manager or so but that's beyond the scope of a start/stop poc
        # logs = kube_manager.get_logs_for_job(job_name)
        logs = "Logs as temp"
        return {"status": "Running", "logs": logs}

    def delete(self, job_name):
        # Stop the bot
        kube_manager.delete_job(job_name)
        return {"message": f"Stopped bot: {job_name}"}, 200


# '/bots/' is our route for creating bots and takes the value in the JSON body such as {'symbol':'SHITCOIN/USDT'}
# This returns a value such as
# "message": "Starting bot: bot-job-a14bf5c2-d162-4310-8eb6-13f75d6f0785"
# This bot job ID could then be stored in our DB for example to manage the botstate
api.add_resource(BotCreator, "/bots/")
# '/bots/job_name' is our route for managing bots
api.add_resource(BotManager, "/bots/<string:job_name>")

if __name__ == "__main__":
    app.run(debug=True)
