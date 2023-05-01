from flask import Flask, jsonify, make_response, request
from slack_bolt import BoltRequest
from slack_bolt.adapter.flask import SlackRequestHandler

from chatiq import ChatIQ

chatiq = ChatIQ(rate_limit_retry=True)
chatiq.listen()

app = Flask(__name__)
handler = SlackRequestHandler(chatiq.bolt_app)


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Health check endpoint for the application.

    Returns:
        Response: A response with status code 200.
    """

    return jsonify({"status": "OK"})


@app.route("/slack/install", methods=["GET"])
@app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    """Handles the OAuth redirect for the Slack app installation process.

    Returns:
        Response: A response from the Slack OAuth handler.
    """

    return handler.handle(request)


@app.route("/slack/events", methods=["POST"])
def events():
    """Handles incoming event payloads from Slack.

    Returns:
        Response: The response from the Bolt App's dispatch method.
    """

    body = request.get_data().decode("utf-8")
    headers = {k: v for k, v in request.headers}
    bolt_req = BoltRequest(body=body, headers=headers)
    bolt_resp = chatiq.bolt_app.dispatch(bolt_req)
    return make_response(bolt_resp.body, bolt_resp.status, bolt_resp.headers)
