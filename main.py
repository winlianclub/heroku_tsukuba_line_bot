from __future__ import unicode_literals

import pprint
import os

import datetime
from flask import Flask, request, abort
from linebot.exceptions import (
    InvalidSignatureError
)

from constants import line_bot_api, handler, get_text_template_for_id, \
    get_text_template_for_delegate, CHANNEL_ACCESS_TOKEN, rmm

from sample_handler import (
    text_message_handler_sample, add_group_event_handler,
    add_multimedia_event_handler
)

# noinspection PyUnresolvedReferences
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    # RichMenu, RichMenuBound, RichMenuArea
)

from richmenu import RichMenu, RichMenuManager

app = Flask(__name__)


# before deploying, turn debug device to phone


@app.route("/line/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    pprint.pprint(body, indent=2)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):

    user_text = event.message.text

    my_number_lost_flow(event, user_text)

    my_number_make_flow(event, user_text)

    my_number_others_flow(event, user_text)

    juminhyou_flow(event, user_text)

    kei_car_certificate_flow(event, user_text)

    certificates_flow(event, user_text)

    if user_text in ['計測開始', '計測スタート']:
        now = datetime.datetime.now()
        date_str = datetime.datetime.strftime(now, "YY-MM-DD hh:mm:ss")
        sample_id = 1  # soft code needed
        staff_id = 1234  # soft code needed
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{date_str}\n計測開始。\n対応ID:{sample_id}\n 職員ID:{staff_id}')
        )

    if user_text in ['計測終了']:
        now = datetime.datetime.now()
        date_str = datetime.datetime.strftime(now, "YY-MM-DD hh:mm:ss")
        sample_id = 1  # soft code needed
        staff_id = 1234  # soft code needed

        # 計測終了が押される直前に、同じユーザーに押されていた「計測スタート」の時刻を取りに行く。
        # そして現在時刻との差分を取る。

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'{date_str}\n計測終了。\n対応ID:{sample_id}\n 職員ID:{staff_id}')
        )


def certificates_flow(event, user_text):
    # q1
    if user_text in ['各種証明書']:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='お探しなのはどれでしょう？', title='お選びください。', actions=[
                MessageTemplateAction(label='不在住所証明書・不在籍証明書', text='不在住所証明書・不在籍証明書'),
                MessageTemplateAction(label='住民票の写しの広域交付', text='住民票の写しの広域交付'),
                MessageTemplateAction(label='戸籍謄本/改製原戸/戸籍の附票', text='戸籍謄本・抄本、改製原戸・除籍・戸籍の附票がほしい。'),
            ]),
            CarouselColumn(text='お探しなのはどれでしょう？', title='お選びください。', actions=[
                MessageTemplateAction(label='身分証明書がほしい', text='身分証明書がほしい'),
                MessageTemplateAction(label='独身証明書がほしい', text='独身証明書がほしい'),
                MessageTemplateAction(label='受理証明書がほしい', text='受理証明書がほしい'),
            ]),
            CarouselColumn(text='お探しなのはどれでしょう？', title='お選びください。', actions=[
                MessageTemplateAction(label='戸籍届記載事項証明書', text='戸籍届記載事項証明書'),
                MessageTemplateAction(label='自動車の仮ナンバーがほしい', text='自動車の仮ナンバーがほしい'),
                MessageTemplateAction(label='住所変更証明書がほしい', text='住所変更証明書がほしい'),
            ]),
            CarouselColumn(text='お探しなのはどれでしょう？', title='お選びください。', actions=[
                MessageTemplateAction(label='合併証明', text='合併証明'),
                MessageTemplateAction(label='住民票', text='住民票がほしい'),
                MessageTemplateAction(label='軽自動車用住所証明書', text='軽自動車用住所証明書がほしい'),
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['不在住所証明書・不在籍証明書']:
        reply_text = '誰でも申請できます。窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['住民票の写しの広域交付']:
        reply_text = '２００円。本人または本人と同一世帯の人で、窓口に来た人の本人確認書類が必要です。申請者は記載台に設置されていないので、来庁の際は証明受付窓口までお越しください。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    inkan_flow(event, user_text)
    if user_text in ['戸籍謄本・抄本、改製原戸・除籍・戸籍の附票がほしい。', 'ksk']:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='ほしいのはどなたですか？', title='お選びください。', actions=[
                MessageTemplateAction(label='本人', text='本人が戸籍系書類がほしい。'),
                MessageTemplateAction(label='本人配偶者、直系血族',
                                      text='本人の配偶者、直系の血族（本人の親、祖父母、子、孫）が戸籍系書類をほしい。'),
                MessageTemplateAction(label='任意代理人', text='任意代理人が戸籍系書類をほしい。')
            ]),
            CarouselColumn(text='ほしいのはどなたですか？', title='お選びください', actions=[
                MessageTemplateAction(label='成年後見人', text='成年後見人が戸籍系書類をほしい。'),
                MessageTemplateAction(label='親族',
                                      text='親族（本人が死亡しており、直系の血族もいない場合）が戸籍系書類をほしい。'),
                MessageTemplateAction(label='ダミー', text='このボタンは、ボタンの数を揃えるためのダミーです。')
            ]),
            CarouselColumn(text='ほしいのはど？', title='お選びください', actions=[
                MessageTemplateAction(label='特定事務受給者', text='特定事務時給者が'),
                MessageTemplateAction(label='国/地方公共団体職員', text='国・地方公共団体の機関の職員からの請求'),
                MessageTemplateAction(label='ダミー', text='このボタンは、ボタンの数を揃えるためのダミーです。')
            ])
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人が戸籍系書類がほしい。']:
        reply_text = '本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本人の配偶者、直系の血族（本人の親、祖父母、子、孫）が戸籍系書類をほしい。']:
        reply_text = '直系の血族であることを証明できるもの（例：戸籍謄本・抄本）、本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['任意代理人が戸籍系書類をほしい。']:
        reply_text = '委任状、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['成年後見人が戸籍系書類をほしい。']:
        reply_text = '登記事項証明書、本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['親族（本人が死亡しており、直系の血族もいない場合）が戸籍系書類をほしい。']:
        reply_text = '問い合わせについては、証明交付係につなく。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['特定事務時給者が戸籍系書類をほしい。']:
        reply_text = '問い合わせについては、証明交付係につなく。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['国・地方公共団体の機関の職員からの請求']:
        reply_text = '問い合わせについては、証明交付係につなく。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['身分証明書がほしい']:
        buttons_template = ButtonsTemplate(
            title='身分証明書がほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='本人が身分証明書をほしい'),
                MessageTemplateAction(label='本人以外', text='本人以外が身分証明書をほしい')
            ])
        template_message = TemplateSendMessage(
            alt_text='身分証明書がほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人が身分証明書をほしい']:
        reply_text = '本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本人以外が身分証明書をほしい']:
        reply_text = '本人以外（委任状があっても本籍が不明だったり、申請書記載の本籍が誤っているときは、交付できません）。' \
                     '委任状、窓口に来た人の本人確認書類が必要で'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['独身証明書がほしい']:
        buttons_template = ButtonsTemplate(
            title='独身証明書がほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='本人が独身証明書をほしい'),
                MessageTemplateAction(label='本人以外', text='本人以外が独身証明書をほしい')
            ])
        template_message = TemplateSendMessage(
            alt_text='独身証明書がほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人が独身証明書をほしい']:
        reply_text = '本人確認書類と（あれば）印鑑が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本人以外が独身証明書をほしい']:
        reply_text = '本人にしか交付できません。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['受理証明書がほしい']:
        buttons_template = ButtonsTemplate(
            title='受理証明書がほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='届出人(本人)', text='受理証明書を届出人がほしい'),
                MessageTemplateAction(label='本人以外', text='受理証明を本人以外がほしい')
            ])
        template_message = TemplateSendMessage(
            alt_text='受理証明書がほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['受理証明書を届出人がほしい']:
        reply_text = '本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['受理証明を本人以外がほしい']:
        reply_text = '委任状、窓口に来た人の本人確認書類が必要です。（委任状があっても本籍が不明だったり、申請書記載の本籍が誤っているときは、交付できません）'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['戸籍届記載事項証明書']:
        reply_text = '戸籍届記載事項証明書（戸籍届出をした市役所で交付する）（使用目的が制限されている）' \
                     '（1~2か月以上前に届出した届書は法務局に送付され交付できない可能性があるので、戸籍係へ確認をとる必要がある） ※350円'
        messages = get_text_send_messages(event, reply_text)
        buttons_template = ButtonsTemplate(
            title='戸籍届記載事項証明書をほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='届出人（本人）', text='戸籍届記載事項証明書をほしいのは届出人（本人）'),
                MessageTemplateAction(label='利害関係人', text='戸籍届記載事項証明書をほしいのは利害関係人'),
                MessageTemplateAction(label='死亡給付金の受け取り者', text='戸籍届記載事項証明書をほしいのは死亡給付金の受け取り者（死亡届の記載事項証明）'),
                MessageTemplateAction(label='該当の子の親', text='戸籍届記載事項証明書をほしいのは該当の子の親'),
            ])
        template_message = TemplateSendMessage(
            alt_text='戸籍届記載事項証明書をほしいのはどなたですか？', template=buttons_template
        )
        messages.append(template_message)
        line_bot_api.reply_message(event.reply_token, messages)
    if user_text in ['戸籍届記載事項証明書をほしいのは届出人（本人）']:
        reply_text = '本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['戸籍届記載事項証明書をほしいのは利害関係人']:
        reply_text = 'ケースバイケースであるため、証明交付係につなぐ'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['戸籍届記載事項証明書をほしいのは死亡給付金の受け取り者（死亡届の記載事項証明）']:
        reply_text = '簡易保険の証書等(原本）、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['戸籍届記載事項証明書をほしいのは該当の子の親']:
        reply_text = '※出生届の記載事項証明。届出人でなくても親であれば、委任状をもって取得できる。委任状（届出人でない場合）、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['自動車の仮ナンバーがほしい']:
        reply_text = '''窓口に来た人の本人確認書類、
臨時運行する車の自賠責保険証明書の原本、
臨時運行する車の自動車検査証または抹消登録証明書または完成検査終了証等（車体番号・社名・車体形状が確認できるもの）、窓口に来た人の印鑑(法人の場合は法人の印鑑）、法人に所属していることを示す社員証や代表者からの在職証明書が必要です。'''
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['住所変更証明書がほしい']:
        buttons_template = ButtonsTemplate(
            title='住所変更証明書がほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='住所変更証明書がほしいのは本人'),
                MessageTemplateAction(label='本人以外', text='住所変更証明書がほしいのは本人以外')
            ])
        template_message = TemplateSendMessage(
            alt_text='住所変更証明書がほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['住所変更証明書がほしいのは本人']:
        reply_text = '''（町名地番変更による住所変更を証明するもの） ※無料'''
        messages = get_text_send_messages(event, reply_text)
        reply_text = '窓口に来た人の本人確認書類が必要です。'
        messages.extend(get_text_send_messages(event, reply_text))
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    if user_text in ['住所変更証明書がほしいのは本人以外']:
        reply_text = '窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['合併証明']:
        reply_text = '（旧町村がつくば市に合併されたことを文章により証明するもの） ※無料'
        messages = get_text_send_messages(event, reply_text)
        buttons_template = ButtonsTemplate(
            title='合併証明が必要なかたはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='合併証明が必要なのは本人'),
                MessageTemplateAction(label='本人以外', text='合併証明が必要なのは本人以外')
            ])
        template_message = TemplateSendMessage(
            alt_text='合併証明が必要なかたはどなたですか？', template=buttons_template
        )
        messages.append(template_message)
        line_bot_api.reply_message(event.reply_token, messages)
    if user_text in ['合併証明が必要なのは本人']:
        reply_text = '窓口に来た人の本人確認書類が必要です'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['合併証明が必要なのは本人以外']:
        reply_text = '窓口に来た人の本人確認書類が必要です'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def inkan_flow(event, user_text):
    # q1
    if user_text in ['印鑑登録関連']:
        buttons_template = ButtonsTemplate(
            title='印鑑登録関連の何をお望みですか？', text='お選びください', actions=[
                MessageTemplateAction(label='印鑑登録証明書がほしい', text='印鑑登録証明書'),
                MessageTemplateAction(label='印鑑登録を廃止したい', text='印鑑登録を廃止したい'),
                MessageTemplateAction(label='印鑑登録をしたい', text='印鑑登録をしたい'),
            ])
        template_message = TemplateSendMessage(
            alt_text='印鑑登録関連の何をお望みですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['印鑑登録をしたい']:
        buttons_template = ButtonsTemplate(
            title='印鑑登録をしたいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='印鑑登録をしたいのは本人'),
                MessageTemplateAction(label='本人＋保証人', text='印鑑登録をしたいのは本人＋保証人'),
                MessageTemplateAction(label='本人以外', text='印鑑登録をしたいのは本人以外'),
            ])
        template_message = TemplateSendMessage(
            alt_text='印鑑登録をしたいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['印鑑登録をしたいのは本人']:
        buttons_template = ButtonsTemplate(
            title='写真付き本人確認書類をお持ちですか？', text='お選びください', actions=[
                MessageTemplateAction(label='持っている', text='写真付き本人確認書類を持っている'),
                MessageTemplateAction(label='持っていない', text='写真付き本人確認書類を持っていない')
            ])
        template_message = TemplateSendMessage(
            alt_text='本人確認書類をお持ちですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['写真付き本人確認書類を持っている']:
        reply_text = '即日登録が可能。写真付き本人確認書類と、登録する印鑑が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['写真付き本人確認書類を持っていない']:
        reply_text = '証明交付係に繋ぐ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録をしたいのは本人＋保証人']:
        reply_text = '証明交付係に繋ぐ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録をしたいのは本人以外']:
        reply_text = '証明交付係に繋ぐ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録証明書']:
        buttons_template = ButtonsTemplate(
            title='印鑑登録証明書をほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人がほしい', text='印鑑登録証明書を本人がほしい'),
                MessageTemplateAction(label='本人以外がほしい', text='印鑑登録証明書を本人以外がほしい'),
                MessageTemplateAction(label='印鑑登録証がない場合', text='印鑑登録証がない場合'),
            ])
        template_message = TemplateSendMessage(
            alt_text='印鑑登録証明書をほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['印鑑登録証明書を本人がほしい']:
        reply_text = '本人確認書類が、印鑑登録証が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録証明書を本人以外がほしい']:
        reply_text = '窓口に来た人の本人確認書類、印鑑登録証が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録証がない場合']:
        reply_text = '本人確認書類や実印をもってきても、申請できない。紛失してしまった場合、廃止届＋再登録を案内。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['印鑑登録を廃止したい']:
        buttons_template = ButtonsTemplate(
            title='印鑑登録を廃止したいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='本人が印鑑登録を廃止したい'),
                MessageTemplateAction(label='本人以外', text='本人以外が印鑑登録を廃止したい')
            ])
        template_message = TemplateSendMessage(
            alt_text='印鑑登録を廃止したいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人が印鑑登録を廃止したい']:
        reply_text = '本人確認書類、印鑑登録証（紛失による廃止の場合不要）が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本人以外が印鑑登録を廃止したい']:
        reply_text = '本人確認書類、印鑑登録証（紛失による廃止の場合不要）、委任状が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def kei_car_certificate_flow(event, user_text):
    if user_text in ['軽自動車用住所証明書がほしい', 'kei']:
        buttons_template = ButtonsTemplate(
            title='軽自動車用住所証明書がほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人がほしい', text='軽自動車用住所証明書を本人がほしい'),
                MessageTemplateAction(label='本人以外がほしい', text='軽自動車用住所証明書を本人以外がほしい')
            ])
        template_message = TemplateSendMessage(
            alt_text='軽自動車用住所証明書がほしい', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['軽自動車用住所証明書を本人がほしい']:
        reply_text = '本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['軽自動車用住所証明書を本人以外がほしい']:
        buttons_template = ButtonsTemplate(
            title='軽自動車用住所証明書をほしいのはどなたですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人と同一世帯の人', text='軽自動車用住所証明書を本人と同一世帯の人がほしい'),
                MessageTemplateAction(label='任意代理人', text='軽自動車用住所証明書を任意代理人がほしい'),
                MessageTemplateAction(label='自動車販売関係社社員', text='軽自動車用住所証明書を自動車販売関係会社の社員などがほしい'),
            ])
        template_message = TemplateSendMessage(
            alt_text='軽自動車用住所証明書をほしいのはどなたですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['軽自動車用住所証明書を本人と同一世帯の人がほしい']:
        reply_text = '窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['軽自動車用住所証明書を任意代理人がほしい']:
        reply_text = '委任状、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['軽自動車用住所証明書を自動車販売関係会社の社員などがほしい']:
        reply_text = '軽自動車の売買契約書または注文書の写し、委任状、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def juminhyou_flow(event, user_text):
    if user_text in ['住民票がほしい', 'jumin']:
        buttons_template = ButtonsTemplate(
            title='住民票がほしい方は本人ですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本人', text='本人が住民票をほしい'),
                MessageTemplateAction(label='本人以外', text='本人以外が住民票をほしい')
            ])
        template_message = TemplateSendMessage(
            alt_text='住民票がほしい', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人が住民票をほしい']:
        reply_text = '本人確認書類が必要です。記載事項証明の場合、提出先から提供された書式を使用することが可能です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本人以外が住民票をほしい', 'jh']:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='住民票をほしいのはどなたですか？', title='お選びください', actions=[
                MessageTemplateAction(label='本人と同一世帯の人', text='本人と同一世帯の人'),
                MessageTemplateAction(label='任意代理人', text='任意代理人'),
                MessageTemplateAction(label='法定代理人', text='法定代理人'),
            ]),
            CarouselColumn(text='住民票をほしいのはどなたですか？', title='お選びください', actions=[
                MessageTemplateAction(label='親族',
                                      text='親族（除票の申請で本人がすでに死亡しており、本人が単身世帯だったとき）'),
                MessageTemplateAction(label='債権者', text='債権者'),
                MessageTemplateAction(label='ダミー', text='このボタンはボタンの数を統一するためのダミーです。'),
            ]),
            CarouselColumn(text='住民票をほしいのはどなたですか？', title='お選びください', actions=[
                MessageTemplateAction(label='特定事務責任者', text='特定事務責任者（弁護士・司法書士など）'),
                MessageTemplateAction(label='国/公共地方団体職員', text='国・公共地方団体の機関の職員'),
                MessageTemplateAction(label='ダミー', text='このボタンはボタンの数を統一するためのダミーです。'),
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['本人と同一世帯の人']:
        reply_text = '窓口に来た人の本人確認書類が必要です。記載事項証明の場合、提出先から提供された書式を使用することが可能です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['任意代理人']:
        buttons_template = ButtonsTemplate(
            title='取得したい住民票などは「住基コードやマイナンバー」なし、あり？', text='お選びください', actions=[
                MessageTemplateAction(label='あり', text='「住基コードやマイナンバーなし」'),
                MessageTemplateAction(label='なし', text='「住基コードやマイナンバーあり」')
            ])
        template_message = TemplateSendMessage(
            alt_text='取得したい住民票などは「住基コードやマイナンバーなし」', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['「住基コードやマイナンバーなし」']:
        reply_text = '委任状、窓口に来た人の本人確認書類が必要です。記載事項証明の場合、提出先から提供された書式を使用することが可能です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['「住基コードやマイナンバーあり」']:
        reply_text = '委任状、窓口に来た人の本人確認書類が必要です。ただし、即日交付はできないため、後日申請者本人宛に簡易書留で送付されます。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['法定代理人']:
        buttons_template = ButtonsTemplate(
            title='親権者ですか？成年後見人ですか？', text='お選びください', actions=[
                MessageTemplateAction(label='親権者', text='親権者'),
                MessageTemplateAction(label='成年後見人', text='成年後見人')
            ])
        template_message = TemplateSendMessage(
            alt_text='親権者ですか？成年後見人ですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['親権者']:
        reply_text = '親権者であることの証明（戸籍謄本など。つくば市に本籍がある場合は不要。）窓口に来た人の本人確認書類が必要です。記載事項証明の場合、提出先から提供された書式を使用することが可能です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['成年後見人']:
        reply_text = '登記事項証明書、窓口に来た人の本人確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['親族（除票の申請で本人がすでに死亡しており、本人が単身世帯だったとき）']:
        reply_text = '親族であることの証明（戸籍謄本など。申請者の本籍がつくば市の場合は不要。）窓口に来た人の方んにん確認書類が必要です。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['債権者']:
        reply_text = '交付の可否についての即答厳禁。必要書類や審査などが存在するため、証明交付係に繋ぐ'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['特定事務責任者（弁護士・司法書士など）']:
        reply_text = '職務上請求用紙により身分証持参で申請可能。申請内容については証明交付係に繋ぐ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['国・公共地方団体の機関の職員']:
        reply_text = '公用請求（無料）。証明交付係に繋ぐ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def my_number_others_flow(event, user_text):
    # q1
    if user_text in ['マイナンバー関連', 'number']:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='お選びください', title='マイナンバー関連', actions=[
                MessageTemplateAction(label='個人番号/通知カード紛失', text='マイナンバーカード・通知カードを紛失した'),
                MessageTemplateAction(label='マイナンバーの登録', text='マイナンバーの登録をしたい'),
                MessageTemplateAction(label='"支所"で可能かどうか', text='市役所が遠いから支所でマイナンバー手続きをしたい'),
            ]),
            CarouselColumn(text='お選びください', title='マイナンバー関連', actions=[
                MessageTemplateAction(label='マイナンバーがロック', text='コンビニで証明書を取得しようとしたがロック'),
                MessageTemplateAction(label='個人番号カードの受取予約', text='マイナンバーカードの受け取り予約をしたい'),
                MessageTemplateAction(label='ダミー', text='ダミー'),
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['far', '市役所が遠いから支所でマイナンバー手続きをしたい']:
        buttons_template = ButtonsTemplate(
            title='お客様がおっしゃっている支所とは、「窓口センター」or「出張所」？', text='お選びください', actions=[
                MessageTemplateAction(label='窓口センター', text='窓口センター'),
                MessageTemplateAction(label='出張所', text='出張所'),
            ])
        template_message = TemplateSendMessage(
            alt_text='default alt_text', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['出張所']:
        reply_text = 'マイナンバーの手続きは出張所ではできないことをお伝えして、近くの窓口センターを案内する'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )

    if user_text in ['窓口センター']:
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='希望する手続きはなんですか？', title='お選びください', actions=[
                MessageTemplateAction(label='個人番号入り住民票', text='マイナンバー入りの住民の発行'),
                MessageTemplateAction(label='通知カードの再発行', text='通知カードの再発行'),
                MessageTemplateAction(label='写真付個人番号カード', text='写真付きマイナンバーカードは申込書'),
            ]),
            CarouselColumn(text='希望する手続きはなんですか？', title='お選びください', actions=[
                MessageTemplateAction(label='通知カード返戻カード分の受取', text='通知カード返戻カード分の受け取り'),
                MessageTemplateAction(label='作成済み個人番号カードの受取', text='作成済みマイナンバーカードの受け取り'),
                MessageTemplateAction(label='ダミー', text='ダミー'),
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['マイナンバー入りの住民の発行']:
        reply_text = 'マイナンバーカードを急ぎで知りたいだけの場合、マイナンバー入りの住民票の発行をご案内。本人確認書類を持って、窓口センターへ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['通知カードの再発行']:
        reply_text = '申請者本人が本人確認書類を持って窓口センターへ。家族分など自分自身ではない場合、「通知カードの再発行」を委任事項とした委任状と再発行する人の本人確認書類の原本も必要（５００円）'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['写真付きマイナンバーカードは申込書の作成まで']:
        reply_text = '申請者の作成までは窓口センターで可能。本人確認書類の原本が必要。自分でインターネット申請や郵送申請が必要になる。写真撮影まで無料で実施している窓口申請補助を本庁舎のみ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['通知カード返戻カード分の受け取り']:
        reply_text = '返礼された通知カードの受け取り・確認を行う。氏名・生年月日をきき、該当者を検索。' \
                     '返戻がある場合、どこのセンターでの受け取りを希望を確認する。（職員による直接配送となるので配送可能日を確認し、）いつからお渡し可能化を案内し、' \
                     '本人確認書類を持って本人が該当のセンターに来庁するように伝える。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['作成済みマイナンバーカードの受け取り']:
        reply_text = '交付通知書が届いているか確認する。届いている場合、本人確認書類と交付通知書を持って、市役所に来庁するような案内。届いていない場合、氏名・生年月日を聞き、カード発行状況を確認。' \
                     'カードができていたら、受け取りについて案内を行う。（詳細は個人番号カード係へ繋ぐ。）'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )

    if user_text in ['コンビニで証明書を取得しようとしたがロック']:
        reply_text = '本人確認書類とマイナンバーカードをもって、市役所または窓口センターで暗証番号の初期化をすることでロック解除できることを案内。' \
                     '（代理人の場合、照会になるのでHPを確認するよう案内。詳細は、個人番号カードかかりへ繋ぐ。）'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['マイナンバーカードの受け取り予約をしたい']:
        messages = [TextSendMessage(text='平日の本庁舎希望の場合、予約不要。')]

        buttons_template = ButtonsTemplate(
            title='土日の本庁舎or平日の窓口センター？', text='お選びください', actions=[
                MessageTemplateAction(label='土日の本庁舎', text='土日の本庁舎'),
                MessageTemplateAction(label='平日の窓口センター', text='平日の窓口センター'),
            ])
        template_message = TemplateSendMessage(
            alt_text='default alt_text', template=buttons_template
        )
        messages.append(template_message)

        line_bot_api.reply_message(event.reply_token, messages)
    if user_text in ['土日の本庁舎']:
        reply_text = '今月・来月の予約可能日を案内。予約をする場合は、予約簿を用意し、氏名・生年月日・住所・電話番号を予約簿に書き込む。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['平日の窓口センター']:
        reply_text = '今月の空き状況を説明。予約をする場合は、予約簿を用意し、氏名・生年月日・住所・電話番号を予約簿に書き込む。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def my_number_make_flow(event, user_text):
    if user_text in ['マイナンバーの登録をしたい', 'make']:
        buttons_template = ButtonsTemplate(
            title='１ヶ月以内に必要ですか？', text='お選びください', actions=[
                MessageTemplateAction(label='必要です。', text='必要です。'),
                MessageTemplateAction(label='必要ではないです。', text='必要ではないです。'),
            ])
        template_message = TemplateSendMessage(
            alt_text='１ヶ月以内に必要ですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['必要です。']:
        reply_text = 'マイナンバー入り住民票を案内。本人確認書類を持って、市役所もしくは窓口センターへ。土日も手続き可能。別途カードを作りたい場合、要通知カードor写真入りマイナンバーカード。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['必要ではないです。']:
        buttons_template = ButtonsTemplate(
            title='通知カードと写真入り？', text='お選びください', actions=[
                MessageTemplateAction(label='通知カード', text='通知カードがほしい'),
                MessageTemplateAction(label='個人番号カード', text='マイナンバーカードがほしい'),
            ])
        template_message = TemplateSendMessage(
            alt_text='通知カードor写真入りマイナンバーカード？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['通知カードがほしい']:
        buttons_template = ButtonsTemplate(
            title='通知カードを受け取ったことはございますか？', text='お選びください', actions=[
                MessageTemplateAction(label='受け取ったことがない', text='通知カードを受け取ったことがない'),
                MessageTemplateAction(label='自宅でなくした', text='通知カードを自宅でなくした'),
                MessageTemplateAction(label='自宅外・盗難で紛失', text='通知カードを自宅外または盗難でなくした'),
            ])
        template_message = TemplateSendMessage(
            alt_text='通知カードを受け取ったことはございますか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['通知カードを受け取ったことがない']:
        reply_text = '市役所に問い合わせるよう案内する。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['マイナンバーカードがほしい']:
        buttons_template = ButtonsTemplate(
            title='マイナンバーカードを作るのは初めてですか？', text='お選びください', actions=[
                MessageTemplateAction(label='初めてである', text='初めてである'),
                MessageTemplateAction(label='2回目以降である', text='2回目以降である')
            ])
        template_message = TemplateSendMessage(
            alt_text='マイナンバーカードを作るのは初めてですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['初めてである']:
        buttons_template = ButtonsTemplate(
            title='本庁舎への来庁は可能ですか？（通知カードに付属する申請書が使える場合もあるが、住所移動や修正などでIDが出回っている場合もあることを考えると最新のIDの取得をしていただいたほうが確実。）',
            text='お選びください', actions=[
                MessageTemplateAction(label='本庁舎へ来庁可能', text='本庁舎へ来庁可能'),
                MessageTemplateAction(label='本庁舎へ来庁不可', text='本庁舎へ来庁不可'),
            ])
        template_message = TemplateSendMessage(
            alt_text='本庁舎への来庁は可能ですか？（通知カードに付属する申請書が使える場合もあるが、住所移動や修正などでIDが出回っている場合もあることを考えると最新のIDの取得をしていただいたほうが確実。）',
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['2回目以降である']:
        buttons_template = ButtonsTemplate(
            title='なくしたのはどこですか？', text='お選びください', actions=[
                MessageTemplateAction(label='自宅', text='自宅でマインバーカードを紛失した'),
                MessageTemplateAction(label='自宅外または盗難', text='自宅外または盗難でマイナンバーカードを紛失した'),
            ])
        template_message = TemplateSendMessage(
            alt_text='default alt_text', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['自宅でマインバーカードを紛失した']:
        buttons_template = ButtonsTemplate(
            title='写真付きマイナンバーカード(800円)or 通知カード(500円)？', text='お選びください', actions=[
                MessageTemplateAction(label='マイナンバーカード', text='マイナンバーカードを再発行したい'),
                MessageTemplateAction(label='通知カード', text='通知カードを再発行したい'),
            ])
        template_message = TemplateSendMessage(
            alt_text='default alt_text', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['自宅外または盗難でマイナンバーカードを紛失した']:
        buttons_template = ButtonsTemplate(
            title='マイナンバーの変更を希望しますか？', text='お選びください', actions=[
                MessageTemplateAction(label='変更を希望する', text='マイナンバーの変更を希望する'),
                MessageTemplateAction(label='変更を希望しない', text='マイナンバーの変更を希望しない'),
            ])
        template_message = TemplateSendMessage(
            alt_text='default alt_text', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['通知カードを再発行したい']:
        reply_text = '個人番号カードの廃止のため、本人確認書類を持って、来庁頂く必要があることをご案内。その後※３に準ずる'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['マイナンバーカードを再発行したい']:
        reply_text = 'マイナンバーカードの廃止は、あたらしい個人番号カードの交付の際に行うことを説明、その後※４に準ずる'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    # １枚めスライドのマイナンバー紛失フローと２枚めスライド右下あたりのフローが微妙に違うのはなぜか？
    # ※３と※４はなにか？


def my_number_lost_flow(event, user_text):
    # My number flow lost flow
    if user_text in ['lost', 'マイナンバーカード・通知カードを紛失した']:
        buttons_template = ButtonsTemplate(
            title='なくしたのは通知カード or 個人番号カード？', text='お選びください。', actions=[
                MessageTemplateAction(label='通知カード', text='通知カード'),
                MessageTemplateAction(label='個人番号カード', text='個人番号カードを紛失'),
            ])
        template_message = TemplateSendMessage(
            alt_text='なくしたのは通知カード or 個人番号カード？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    # My number flow answers(1)
    if user_text in ['通知カード']:
        buttons_template = ButtonsTemplate(
            title='なくしたのはどこですか？', text='お選びください', actions=[
                MessageTemplateAction(label='自宅でなくした', text='通知カードを自宅でなくした'),
                MessageTemplateAction(label='自宅外・盗難', text='通知カードを自宅外または盗難でなくした'),
                MessageTemplateAction(label='急ぎで必要', text='通知カードが急ぎで必要'),
            ])
        template_message = TemplateSendMessage(
            alt_text='なくしたのはどこですか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    # My number flow answers(1, 1) and 1,2,2
    if user_text in ['通知カードを自宅でなくした', 'マイナンバーの変更を希望しない']:
        buttons_template = ButtonsTemplate(
            title='どちらで作り直しますか？', text='お選びください', actions=[
                MessageTemplateAction(label='通知カードで', text='通知カードで作り直す'),
                MessageTemplateAction(label='マイナンバーカードで', text='マイナンバーカードで作り直す'),
            ])
        template_message = TemplateSendMessage(
            alt_text='どちらで作り直しますか', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    # My number flow answers(1, 2)
    if user_text in ['通知カードを自宅外または盗難でなくした']:
        buttons_template = ButtonsTemplate(
            title='マイナンバーの変更を希望するか否か', text='お選びください', actions=[
                MessageTemplateAction(label='希望する', text='マイナンバーの変更を希望する'),
                MessageTemplateAction(label='希望しない', text='マイナンバーの変更を希望しない'),
            ])
        template_message = TemplateSendMessage(
            alt_text='どちらで作り直しますか', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    # My number flow answers(1, 3)
    if user_text in ['通知カードが急ぎで必要']:
        reply_text = 'マイナンバー入りの住民票を案内。\n本人確認書類を持って、市役所または窓口へ。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    # My number flow 1,1,1
    if user_text in ['通知カードで作り直す']:
        reply_text = '通知カード再交付のご案内。再交付手数料１通に付き５００円、本人が本人確認書類を持って、市役所または窓口センターに来庁。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    # My number flow 1,1,2
    if user_text in ['マイナンバーカードで作り直す']:
        buttons_template = ButtonsTemplate(
            title='本庁舎へ来庁可能ですか？', text='お選びください', actions=[
                MessageTemplateAction(label='本庁舎へ来庁可能', text='本庁舎へ来庁可能'),
                MessageTemplateAction(label='本庁舎へ来庁不可', text='本庁舎へ来庁不可'),
            ])
        template_message = TemplateSendMessage(
            alt_text='本庁舎へ来庁可能ですか', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    # My number flow 1,2,1
    if user_text in ['マイナンバーの変更を希望する']:
        reply_text = '警察でどういった状況でなくしたのかを説明し、受理番号をもらい本人確認書類を持参し来庁。番号変更の手続きをして新しいマイナンバーで通知カードが送付される。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    # My number flow 1,2,1
    if user_text in ['本庁舎へ来庁可能']:
        reply_text = '申請補助を案内。本人確認書類をもって、平日本庁舎へ。その場で写真を取り申請。１ヶ月程度で自宅にカード受け取りのお知らせが届くので、また受け取りに来てくださいと案内。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['本庁舎へ来庁不可']:
        reply_text = '窓口センターの受付で「個人番号カード申請のための申込書がほしい」とお話して、申請書を作成した後、自分自身で写真を貼って郵送するか、インターネット申請をするように案内。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    # My number flow answers(2)
    if user_text in ['個人番号カードを紛失']:
        buttons_template = ButtonsTemplate(
            title='どこでなくされましたか？', text='お選びください', actions=[
                MessageTemplateAction(label='自宅', text='自宅でマイナンバーカードを紛失'),
                MessageTemplateAction(label='自宅外、または盗難', text='自宅外または盗難でマイナンバーカードを紛失'),
            ])
        template_message = TemplateSendMessage(
            alt_text='どこでなくされましたか', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['自宅でマイナンバーカードを紛失']:
        buttons_template = ButtonsTemplate(
            title='通知カードとマイナンバーカード、どちらを再交付されますか？', text='お選びください', actions=[
                MessageTemplateAction(label='通知カード', text='通知カードを再交付したい'),
                MessageTemplateAction(label='マイナンバーカード', text='マイナンバーカードを再交付したい'),
            ])
        template_message = TemplateSendMessage(
            alt_text='通知カードとマイナンバーカード、どちらを再交付されますか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['通知カードを再交付したい']:
        reply_text = 'カード廃止の手続き後、通知カード再発行の手続きを行う。本人確認書類を持って、本人が来庁するように説明。窓口センターでも可能。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['マイナンバーカードを再交付したい']:
        reply_text = '個人番号カードの申請についてのご案内。電子証明書の一時停止のため、' \
                     'コールセンターの電話番号をお伝えする。カード廃止の手続きは、カード交付の際に実施する旨を説明。本庁舎へ来庁可能であれば、窓口申請補助について案内する。（開発者意見：本庁舎へ来れない場合は？）'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['自宅外または盗難でマイナンバーカードを紛失']:
        buttons_template = ButtonsTemplate(
            title='個人番号の変更を希望されますか？', text='お選びください', actions=[
                MessageTemplateAction(label='変更を希望する', text='マイナンバーカードを自宅外または盗難で紛失したので、番号を変えた上で再交付したい。'),
                MessageTemplateAction(label='変更を希望しない', text='マイナンバーカードを自宅外または盗難で紛失したので、番号をそのままに再交付したい。'),
            ])
        template_message = TemplateSendMessage(
            alt_text='個人番号の変更を希望されますか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    if user_text in ['マイナンバーカードを自宅外または盗難で紛失したので、番号を変えた上で再交付したい。']:
        reply_text = '警察でどういった状況でなくしたのかを説明し、受理番号をもらい本人確認書類を持参し来庁。個人番号カード廃止処理後、番号変更の手続きをして新しいマイナンバーで通知カードが送付される。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['マイナンバーカードを自宅外または盗難で紛失したので、番号をそのままに再交付したい。']:
        buttons_template = ButtonsTemplate(
            title='通知カードとマイナンバーカードのどちらで再交付されますか？', text='お選びください', actions=[
                MessageTemplateAction(label='通知カード', text='自宅外または盗難でマイナンバーカードを紛失したので、番号そのままに通知カードを発行したい'),
                MessageTemplateAction(label='マイナンバーカード', text='自宅外または盗難でマイナンバーカードを紛失したので、番号そのままにマイナンバーカードを再発行したい。'),
            ])
        template_message = TemplateSendMessage(
            alt_text='通知カードとマイナンバーカードのどちらで再交付されますか？', template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    if user_text in ['自宅外または盗難でマイナンバーカードを紛失したので、番号そのままに通知カードを発行したい']:
        reply_text = '個人番号カード廃止の手続き後、通知カード再発行の手続きを行う、本人確認書類を持って、本人が来庁するように説明。窓口センターでも可能。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )
    if user_text in ['自宅外または盗難でマイナンバーカードを紛失したので、番号そのままにマイナンバーカードを再発行したい。']:
        reply_text = '個人番号カードの最新性についてのご案内、' \
                     '電子証明書の一時停止のため、コールセンターの電話番号をお伝えする。カード廃止の手続きはカード交付の際に実施する旨を説明。本庁舎へ来庁可能であれば、窓口補助について案内する。'
        line_bot_api.reply_message(
            event.reply_token,
            get_text_send_messages(event, reply_text)
        )


def get_text_send_messages(event, reply_text):
    messages = [TextSendMessage(text=reply_text)]

    if '本人確認書類' in reply_text:
        messages.append(get_text_template_for_id())

    if '委任状' in reply_text:
        messages.append(get_text_template_for_delegate())

    return messages


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


@handler.add(FollowEvent)
def handle_follow(event):

    user_id = event.source.user_id
    res = rmm.get_applied_menu(user_id)

    if 'richMenuId' not in res.keys():
        print(rmm.get_list())
        rm_id = rmm.get_list()['richmenus'][0]['richMenuId']
        rmm.apply(user_id, rm_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='つくば市役所botを友達登録していただきありがとうございます！。'
                             '\n\n下の『問い合わせ分類』から選択肢をお選びください。')
    )


add_multimedia_event_handler()

add_group_event_handler()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print(port)
    app.run(debug=True, port=port, host='0.0.0.0')
