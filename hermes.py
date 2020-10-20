#!/bin/python3

""" Hermes
Slack bot to send messages
Needs Python3.6

Usage:
python hermes.py msg "Message to send to egg-alerts"
"""

import argparse
import logging.config
import os
import time

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


def get_slack_token(logger):
    try:
        assert os.path.exists("slack_token.txt")
    except AssertionError as e:
        logger.error("Getting slack token - Token file doesn't exist")
        raise
    else:
        logger.info(
            "Getting slack token - Token file found, retrieving token..."
        )

        with open("slack_token.txt") as f:
            token = f.readline().strip()

        try:
            assert token.startswith("xoxb-")
        except AssertionError as e:
            logger.error(
                "Getting slack token - Token doesn't match what's expected"
            )
            raise
        else:
            logger.info("Getting slack token - Token retrieved successfully")
            return token


def connect_to_slack(token, logger):
    try:
        client = WebClient(token=token)
    except Exception as e:
        logger.error(f"Connect to slack - Unsuccessful: {e}")
        raise e
    else:
        logger.info(f"Connect to slack - Successful")
        return client


def send_message(client, message, logger):
    i = 0

    while i <= 5:
        try:
            response = client.chat_postMessage(
                channel='#egg-alerts',
                text=message)
        except Exception as e:
            logger.error(
                f"Sending message - Unsuccessful: {e}"
            )
            logger.error(f"Sending message - Retrying...{i} out of 5")
            i += 1
            time.sleep(60.0)
        else:
            logger.info("Sending message - Message sent!")
            return True

    logger.error(
        "Sending message - Unsucessful: couldn't send message after 5 tries"
    )


def main(param):
    logger = setup_logging()
    token = get_slack_token(logger)
    client = connect_to_slack(token, logger)

    if param["cmd"] == "msg":
        send_message(client, param["message"], logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    msg = subparser.add_parser("msg")
    msg.add_argument("message")

    args = vars(parser.parse_args())

    main(args)
