#!/bin/python3

import argparse
from slack import WebClient
from slack.errors import SlackApiError


def get_slack_token():
    with open("slack_token.txt") as f:
        token = f.readline().strip()

    return token


def connect_to_slack(token):
    client = WebClient(token=token)
    return client


def send_message(client, message):
    try:
        response = client.chat_postMessage(
            channel='#egg-alerts',
            text=message)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


def main(param):
    token = get_slack_token()
    client = connect_to_slack(token)

    if param["cmd"] == "msg":
        send_message(client, param["message"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    msg = subparser.add_parser("msg")
    msg.add_argument("message")

    args = vars(parser.parse_args())

    main(args)
