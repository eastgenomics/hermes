#!/bin/python3

""" Hermes
Slack bot to send messages
Needs Python3.6

Usage:
python hermes.py msg "message" slack_token.txt egg-alerts
"""

import argparse
import logging.config
import os
import time
import sys

from slack import WebClient
from slack.errors import SlackApiError


def setup_logging():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'normal': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'hermes_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'normal',
                'filename': 'hermes.log',
                'mode': 'a',
                'maxBytes': 10000000,
                'backupCount': 5,
            },
        },
        'loggers': {
            'hermes': {
                'level': 'DEBUG',
                'handlers': ['hermes_handler']
            },
        }
    })

    return logging.getLogger("hermes")


def get_slack_token(token_file, logger, verbose):
    try:
        assert os.path.exists(token_file)
    except AssertionError as e:
        logger.error("Getting slack token - Token file doesn't exist")

        if verbose:
            print("Getting slack token - Token file doesn't exist")

        raise e
    else:
        logger.info(
            "Getting slack token - Token file found, retrieving token..."
        )

        if verbose:
            print(
                "Getting slack token - Token file found, retrieving token..."
            )

        with open(token_file) as f:
            token = f.readline().strip()

        try:
            assert token.startswith("xoxb-")
        except AssertionError as e:
            logger.error(
                "Getting slack token - Token doesn't match what's expected"
            )

            if verbose:
                print(
                    "Getting slack token - Token doesn't match what's expected"
                )

            raise e
        else:
            logger.info("Getting slack token - Token retrieved successfully")
            return token


def connect_to_slack(token, logger, verbose):
    try:
        client = WebClient(token=token)
    except Exception as e:
        logger.error(f"Connect to slack - Unsuccessful: {e}")

        if verbose:
            print(f"Connect to slack - Unsuccessful: {e}")

        raise e
    else:
        logger.info("Connect to slack - Successful")

        if verbose:
            print("Connect to slack - Successful")

        return client


def send_message(client, message, channel, logger, verbose):
    i = 1

    while i <= 5:
        try:
            response = client.chat_postMessage(
                channel=f'#{channel}',
                text=message)
        except Exception as e:
            logger.error(
                f"Sending message to {channel} - Unsuccessful: {e}"
            )
            logger.error((
                f"Sending message to {channel} - "
                f"Retrying...{i} out of 5"
            ))

            if verbose:
                print(f"Sending message to {channel} - Unsuccessful: {e}")
                print((
                    f"Sending message to {channel} - "
                    f"Retrying...{i} out of 5"
                ))

            i += 1
            time.sleep(30.0)
        else:
            logger.info(f"Sending message to {channel} - Message sent!")

            if verbose:
                print(f"Sending message to {channel} - Message sent!")

            return True

    logger.error(
        (
            f"Sending message to {channel} - "
            "Unsucessful: couldn't send message after 5 tries"
        )
    )

    if verbose:
        print((
            f"Sending message to {channel} - "
            "Unsucessful: couldn't send message after 5 tries"
        ))

    sys.exit(-1)


def main(param):
    logger = setup_logging()
    token = get_slack_token(param["token_file"], logger, param["verbose"])
    client = connect_to_slack(token, logger, param["verbose"])

    if param["cmd"] == "msg":
        send_message(
            client, param["message"], param["channel"],
            logger, param["verbose"]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    parser.add_argument("token_file", help="File containing the slack token")
    parser.add_argument("channel", help="Channel to send to")
    parser.add_argument(
        "-v", "--verbose", default=False,
        action="store_true", help="Verbose for dx apps"
    )

    msg = subparser.add_parser("msg")
    msg.add_argument("message", help="Message to send in Slack")

    args = vars(parser.parse_args())

    main(args)
