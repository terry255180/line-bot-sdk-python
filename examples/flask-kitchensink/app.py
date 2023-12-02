# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import datetime
import errno
import os
import sys
import logging
import tempfile
from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.models import (
    UnknownEvent
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    UserSource,
    RoomSource,
    GroupSource,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    BeaconEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    MulticastRequest,
    BroadcastRequest,
    TextMessage,
    ApiException,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
)

from linebot.v3.insight import (
    ApiClient as InsightClient,
    Insight
)


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.INFO)


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

configuration = Configuration(
    access_token=channel_access_token
)


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except ApiException as e:
        app.logger.warn("Got exception from LINE Messaging API: %s\n" % e.body)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
#def handle_follow(event):
#    app.logger.info("Got Follow event:" + event.source.user_id)
#    with ApiClient(configuration) as api_client:
#        line_bot_api = MessagingApi(api_client)
#        line_bot_api.reply_message(
#            ReplyMessageRequest(
#                reply_token=event.reply_token,
#                messages=[
#                    TextMessage(text='❤️歡迎各位孕媽咪、寶媽咪❤️\n加入禾佳藥局中繼站審核群\n《本群組沒有任何活動通知》\n《請審核加入臉書表單群》\n請要審核加入群組媽咪\n"直接私訊小幫手媽咪"審核資料\n1️⃣媽媽手冊審核資格：\n媽媽手冊+預產期內頁+媽媽本人健保卡（請遮/馬身分證字號）\n《限有效孕期內\n🆘生產完請用寶寶手冊審核🆘\n2️⃣寶寶手冊審核資格：\n寶寶手冊+媽媽健保卡\n（寶寶手冊需要填寫家長姓名）\n找下列其中的一位媽媽審核\n@Shu-Lin Wang\n@溫寧\n@Fanny lee\n@周蕎蕎\n@010\n@王靜靜 WJY鴻利童裝\n@Jacqueline\n私訊完畢後請在本群組tag你私訊的小幫手（09:00-22:00）\n小幫手也需要休息，有自己的時間，請勿22:00後私訊\n請務必這邊tag小幫手喔，不然您們的私訊我怕被洗到深海裡QQ\n《審核完畢就可以退出中繼站嘍》\n《審核完畢就可以退出中繼站嘍》\n《本群組沒有任何活動通知》\n《請審核後加入臉書表單群》\n⬇️免費快閃媽媽手冊禮⬇️\n⬇️免費快閃寶寶手冊禮⬇️\n⬇️都在粉專發文快閃限定⬇️\n《各位媽咪記得關注禾佳粉專》\n《按讚+訂閱+追蹤我的最愛》\nhttps://www.facebook.com/%E7%A6%BE%E4%BD%B3%E8%97%A5%E5%B1%80-%E6%96%B0%E8%8E%8A%E6%B0%91%E5%AE%89%E8%A5%BF%E8%B7%AF154%E8%99%9F-298842283885133/'),
#                    ImageMessage(original_content_url = "https://i.imgur.com/Rqe5hTF.jpg",preview_image_url = "https://i.imgur.com/Rqe5hTF.jpg"),
#                    ImageMessage(original_content_url = "https://i.imgur.com/UUaHK5E.jpg",preview_image_url = "https://i.imgur.com/UUaHK5E.jpg"),
#                    ImageMessage(original_content_url = "https://i.imgur.com/k0khHtd.jpg",preview_image_url = "https://i.imgur.com/k0khHtd.jpg"),
#                    ImageMessage(original_content_url = "https://i.imgur.com/wYA4auN.jpg",preview_image_url = "https://i.imgur.com/wYA4auN.jpg")
#                ]
#            )
#        )

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text='❤️歡迎各位孕媽咪、寶媽咪❤️\n加入禾佳藥局中繼站審核群\n《本群組沒有任何活動通知》\n《請審核加入臉書表單群》\n請要審核加入群組媽咪\n"直接私訊小幫手媽咪"審核資料\n1️⃣媽媽手冊審核資格：\n媽媽手冊+預產期內頁+媽媽本人健保卡（請遮/馬身分證字號）\n《限有效孕期內\n🆘生產完請用寶寶手冊審核🆘\n2️⃣寶寶手冊審核資格：\n寶寶手冊+媽媽健保卡\n（寶寶手冊需要填寫家長姓名）\n找下列其中的一位媽媽審核\n@Shu-Lin Wang\n@溫寧\n@Fanny lee\n@周蕎蕎\n@010\n@王靜靜 WJY鴻利童裝\n@Jacqueline\n私訊完畢後請在本群組tag你私訊的小幫手（09:00-22:00）\n小幫手也需要休息，有自己的時間，請勿22:00後私訊\n請務必這邊tag小幫手喔，不然您們的私訊我怕被洗到深海裡QQ\n《審核完畢就可以退出中繼站嘍》\n《審核完畢就可以退出中繼站嘍》\n《本群組沒有任何活動通知》\n《請審核後加入臉書表單群》\n⬇️免費快閃媽媽手冊禮⬇️\n⬇️免費快閃寶寶手冊禮⬇️\n⬇️都在粉專發文快閃限定⬇️\n《各位媽咪記得關注禾佳粉專》\n《按讚+訂閱+追蹤我的最愛》\nhttps://www.facebook.com/%E7%A6%BE%E4%BD%B3%E8%97%A5%E5%B1%80-%E6%96%B0%E8%8E%8A%E6%B0%91%E5%AE%89%E8%A5%BF%E8%B7%AF154%E8%99%9F-298842283885133/'),
                    ImageMessage(original_content_url = "https://i.imgur.com/Rqe5hTF.jpg",preview_image_url = "https://i.imgur.com/Rqe5hTF.jpg"),
                    ImageMessage(original_content_url = "https://i.imgur.com/UUaHK5E.jpg",preview_image_url = "https://i.imgur.com/UUaHK5E.jpg"),
                    ImageMessage(original_content_url = "https://i.imgur.com/k0khHtd.jpg",preview_image_url = "https://i.imgur.com/k0khHtd.jpg"),
                    ImageMessage(original_content_url = "https://i.imgur.com/wYA4auN.jpg",preview_image_url = "https://i.imgur.com/wYA4auN.jpg")
                ]
            )
        )


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)
