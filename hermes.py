#!/bin/python3

""" Hermes
Slack bot to send messages
Needs Python > 3.6

Usage:
python hermes.py msg "message" slack_channel [-v]
"""

import argparse
import logging.config
import time
import sys

from slack import WebClient
from slack.errors import SlackApiError

try:
    from slack_token import hermes_token
except ImportError as e:
    print(f"Can't import \"slack_token\": {e}")
    raise e


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


def connect_to_slack(token, logger, verbose):
    """ Return Slack WebClient

    Args:
        token (str): Slack token
        logger (Logger): Logger
        verbose (bool): Verbose

    Raises:
        e: Raised when couldn't connect to Slack

    Returns:
        WebClient: Slack WebClient
    """

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
    """ Sends messages to Slack

    Args:
        client (WebClient): Slack WebClient
        message (str): Message to send
        channel (str): Channel to send message to
        logger (Logger): Logger
        verbose (bool): Verbose
    """

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
    client = connect_to_slack(hermes_token, logger, param["verbose"])

    if param["cmd"] == "msg":
        send_message(
            client, param["message"], param["channel"],
            logger, param["verbose"]
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    parser.add_argument(
        "channel", choices=["egg-logs", "egg-alerts"],
        help="Channel to send to"
    )
    parser.add_argument(
        "-v", "--verbose", default=False,
        action="store_true", help="Verbose for dx apps"
    )

    msg = subparser.add_parser("msg")
    msg.add_argument("message", help="Message to send in Slack")

    args = vars(parser.parse_args())

    main(args)
