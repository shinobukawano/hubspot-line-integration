# -*- coding: utf-8 -*-
import os
import sys
import requests
import json

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerMessage,
)


app = Flask(__name__)

channel_secret = "{your_channel_secret}"
channel_access_token = "{channel_access_token}"
hubspot_api_key = "{hubspot_api_key}"

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    url = 'https://api.hubapi.com/contacts/v1/contact/batch/?hapikey=' + hubspot_api_key

    obj = [
        {
            "email": "test-user@email.com",
            "properties": [
                {
                    "property": "line_reply_message",
                    "value": event.message.text
                }
            ]
        }    
    ]

    requests.post(url, json=obj)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='HubSpotにデータを送信しました')
    )

    return 'OK'


@app.route("/")
def root():
    return 'Hello, World! :)'


@app.route("/push-message", methods = ['POST'])
def push_message():
    properties = request.json.get('properties')
    user_id = properties.get('line_user_id')
    message = properties.get('line_text_message')

    if (user_id and message):
        # Text
        line_bot_api.push_message(user_id.get('value'), TextSendMessage(
            text = message.get('value')
        ))
        # Sticker
        line_bot_api.push_message(user_id.get('value'), StickerMessage(
            package_id='1', 
            sticker_id='2'
        ))

    return 'OK'


if __name__ == "__main__":
    app.run()


