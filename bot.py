#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import re
import requests
import urllib
import os
import sys
import traceback
from datetime import datetime

from flask import Flask, request, abort, send_from_directory, jsonify, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

# import database_mock as db
import datastorage as db
import warikan
import vision

app = Flask(__name__)

@app.route('/')
def get_all():
    print('/')
    users = db.get_users()
    print(users)
    groups = db.get_groups()
    print(groups)
    payments = db.get_payments()
    print(payments)

    data_list = {'users': users, 'groups': groups, 'payments':payments}
    print(data_list)

    return jsonify(data_list)

@app.route('/users')
def get_users():
    print('/users')
    users = db.get_users()
    print(users)

    return jsonify(users)

@app.route('/user/<uid>')
def get_user(uid):
    print('/user/%s' % uid)
    #groups_of_user = db.get_groups_of_user(uid)
    #print(groups_of_user)
    user = db.get_user(uid)
    print(user)

    return jsonify(user)

@app.route('/adduser/<uid>')
def add_user(uid):
    print('/add_user/%s' % uid)
    #datastorage.register_user(uid)
    db.add_user(uid, 'test_name', 'test_pict', 'test_status', True)

    users = db.get_users()
    print(users)
    user = db.get_user(uid)
    print(user)

    return jsonify({'users':users, 'uid':user})

@app.route('/deluser/<uid>')
def delete_user(uid):
    print('/del_user/%s' % uid)
    db.delete_user(uid)

    users = db.get_users()
    print(users)
    user = db.get_user(uid)
    print(user)

    return jsonify({'users':users, 'uid':user})

@app.route('/delallusers')
def delete_all_users():
    print('/delalluser')
    db.delete_all_users()

    users = db.get_users()
    print(users)
    user = db.get_user(uid)
    print(user)

    return jsonify({'users':users, 'uid':user})

@app.route('/groups')
def get_groups():
    print('/groups')
    groups = db.get_groups()
    print(groups)

    return jsonify(groups)

@app.route('/group/<gid>')
def get_group(gid):
    print('/group/%s' % gid)
    #users_in_group = db.get_users_in_group(gid)
    #print(users_in_group)
    group_info = db.get_group_info(gid)
    print(group_info)

    return jsonify(group_info)

@app.route('/addgroup/<gid>')
def add_group(gid):
    print('/addgroup/%s' % gid)
    #datastorage.create_group(gid)
    db.add_group(gid, "group")

    groups = db.get_groups()
    print(groups)

    group_info = db.get_group_info(gid)
    print(group_info)

    return jsonify({'groups':groups, 'gid':group_info})

@app.route('/delgroup/<gid>')
def delete_group(gid):
    print('/delgroup/%s' % gid)
    db.delete_group(gid)

    groups = db.get_groups()
    print(groups)

    group_info = db.get_group_info(gid)
    print(group_info)

    return jsonify({'groups':groups, 'gid':group_info})

@app.route('/delallgroups')
def delete_all_groups():
    print('/delallgroups')
    db.delete_all_groups()

    groups = db.get_groups()
    print(groups)

    return jsonify(groups)

@app.route('/add/<uid>/to/<gid>')
def add_user_to_group(uid, gid):
    db.add_user_to_group(gid, uid)

    group_users = db.get_group_users(gid)
    print(group_users)

    return jsonify(group_users)

@app.route('/delete/<uid>/from/<gid>')
def delete_user_from_group(uid, gid):
    db.delete_user_from_group(gid, uid)

    group_users = db.get_group_users(gid)
    print(group_users)

    return jsonify(group_users)

@app.route('/upload/<gid>/<uid>')
def upload_receipt(gid, uid):
    aws.set_receipt(gid, uid, 'checkun.png')
    return 'ok'

@app.route('/download/<gid>/<uid>')
def download_receipt(gid, uid):
    aws.get_receipt(gid, uid, 'checkun.png')
    return 'ok'

@app.route('/status')
def get_all_status():
    print('/status')
    all_status = db.get_all_status()
    print(all_status)

    return jsonify(all_status)

@app.route('/status/<uid>')
def get_status(uid):
    print('/status/%s' % uid)
    status_info = db.get_status_info(uid)
    print(status_info)

    return jsonify(status_info)


# 環境変数が見つかればそっちを読む
# 見つからなければjsonファイルを読む
# なければエラー終了
try:
    # 環境変数読み込み
    line_messaging_api_token = os.environ['LINE_MESSAGING_API_TOKEN']
    line_messaging_api_secret = os.environ['LINE_MESSAGING_API_SECRET']
    line_friend_url = os.environ['LINE_FRIEND_URL']
    line_qr_url = os.environ['LINE_QR_URL']
    line_login_channel_id = os.environ['LINE_LOGIN_CHANNEL_ID']
    line_login_secret = os.environ['LINE_LOGIN_SECRET']
    base_url = os.environ['CHECKUN_BASE_URL']
    print('os.envrion')

except:
    try:
        # load from json
        # f = open('checkun_test.json', 'r')
        # f = open('checkun_dev.json', 'r')
        f = open('checkun_main.json', 'r')
        json_dict = json.load(f)
        f.close

        line_messaging_api_token = json_dict['LINE_MESSAGING_API_TOKEN']
        line_messaging_api_secret = json_dict['LINE_MESSAGING_API_SECRET']
        line_friend_url = json_dict['LINE_FRIEND_URL']
        line_qr_url = json_dict['LINE_QR_URL']
        line_login_channel_id = json_dict['LINE_LOGIN_CHANNEL_ID']
        line_login_secret = json_dict['LINE_LOGIN_SECRET']
        base_url = json_dict['CHECKUN_BASE_URL']
        print('json')

    except:
        traceback.print_exc()
        #print(u'読み込みエラー')
        print('read ok')
        sys.exit(-1)
#print(u'読み込み成功')
print('read ok')

# setup LINE Messaging API
line_bot_api = LineBotApi(line_messaging_api_token)
handler = WebhookHandler(line_messaging_api_secret)

# setup LINE Login API
auth_url = base_url + '/auth'

cmd_prefix = u'▶'

# setup database
# db.init('checkundb.json')
#udb = {}

checkun_url = 'http://checkun.hippy.jp/'
# sys.exit(0)

def line_login_get_access_token(code):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'authorization_code',
        'client_id': line_login_channel_id,
        'client_secret': line_login_secret,
        'code': code,
        'redirect_uri': auth_url
        }

    r = requests.post(
        'https://api.line.me/v2/oauth/accessToken',
        headers = headers,
        params = payload
    )
    #app.logger.info('Auth token: ' + str(r.json()))
    # print payload
    # print r.json()
    # print r.url

    return r.json().get('access_token')

def line_login_get_user_profiles(token):
    headers = {'Authorization': 'Bearer {' + token + '}'}

    r = requests.get(
        'https://api.line.me/v2/profile',
        headers = headers,
    )
    #app.logger.info('Auth prof: ' + str(r.json()))
    # print payload
    # print r.json()
    # print r.url

    return r.json()

def get_commad_number_str(number):
    return(u'{:,d}'.format(number))

@app.route('/images/<title>/<width>', methods=['GET'])
def images(title, width):
    # print(title)
    # print(width)
    # 1040, 700, 460, 300, 240
    return send_from_directory(os.path.join(app.root_path, 'static/imagemap', title),
                               str(width) + '.png', mimetype='image/png')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/auth", methods=['GET'])
def auth_callback():
    # https://access.line.me/dialog/oauth/weblogin?response_type=code&client_id=1498580092&redirect_uri=https%3A%2F%2F068265ed.ngrok.io%2Fauth&state=test123
    code = request.args.get('code')
    state = request.args.get('state')

    #app.logger.info('Auth args: ' + str(request.args))

    # 認証エラー
    if(code is None):
        print 'Auth error: '
        error = request.args.get('error')
        errorCode = request.args.get('errorCode')
        errorMessage = request.args.get('errorMessage')
        print error
        print errorCode
        print errorMessage
        return 'Auth Error'

    print 'Auth callback: ' + state + ', ' + code

    token = line_login_get_access_token(code)
    profile = line_login_get_user_profiles(token)
    uid = profile.get("userId")
    name = profile.get("displayName")

    # add_user_warikan_group(uid, state)
    db.add_user_to_group(state, uid)
    msgs = []
    msgs.append(TextSendMessage(text = u'{}さんが精算グループに入りました'.format(name)))
    line_bot_api.push_message(state, msgs)

    #return 'Auth OK'
    #return '<HTML><HEAD><meta http-equiv="refresh" content="1;URL="></HEAD></HTML>'
    return render_template("index.html", title="Checkun Login", message=u"ログイン成功", friend_url=line_friend_url, qr_url=line_qr_url)

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)

    f = open('log.txt','a')
    f.write(json.dumps(json.loads(body), indent=2, sort_keys=True, separators=(',', ': ')))
    f.write('\n')
    f.close

    body_dict = json.loads(body)

    # handle VERIFY
    if(len(body_dict.get('events')) == 2):
        if(body_dict["events"][0].get('replyToken') == "00000000000000000000000000000000"):
            if(body_dict["events"][1].get('replyToken') == "ffffffffffffffffffffffffffffffff"):
                #app.logger.info("VERIFY code received")
                return 'OK'

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def print_error(e):
    print(e.status_code)
    print(e.error.message)
    print(e.error.details)

@handler.default()
def default(event):
    pass

def get_commad_number_str(number):
    return(u'{:,d}'.format(number))

def get_id(source):
    if source.type == 'user':
        return source.user_id
    elif source.type == 'group':
        return source.group_id
    elif source.type == 'room':
        return source.room_id

def update_profile(uid, follow=True):
    try:
        p = line_bot_api.get_profile(uid)
    except LineBotApiError as e:
        print_error(e)

    db.add_user(uid, p.display_name, p.picture_url, p.status_message, follow)
    # print get_name(_id)
    #print p.display_name

def get_name(uid):
    # return db.get_user(uid)['name']
    return line_bot_api.get_profile(uid).display_name

def send_msgs(msgs, reply_token = None, uid = None, uids = None):
    if not isinstance(msgs, (list, tuple)):
        msgs = [msgs]
    # 各メッセージの不要な改行の削除
    for msg in msgs:
        if msg.type == 'text':
            while msg.text[-1] == '\n':
                msg.text = msg.text[:-1]
    # 空メッセージ削除
    if TextSendMessage('') in msgs:
        msgs.remove(TextSendMessage(''))

    # メッセージがあれば送信
    if len(msgs):
        if len(msgs) > 5:
            try:
                if reply_token:
                    line_bot_api.reply_message(reply_token, msgs[0:5])
                if uid:
                    line_bot_api.push_message(uid, msgs[0:5])
                if uids:
                    line_bot_api.multicast(uids, msgs[0:5])
            except LineBotApiError as e:
                print_error(e)
            print 'len(msgs) > 5'
        else:
            try:
                if reply_token:
                    line_bot_api.reply_message(reply_token, msgs)
                if uid:
                    line_bot_api.push_message(uid, msgs)
                if uids:
                    line_bot_api.multicast(uids, msgs)
            except LineBotApiError as e:
                print_error(e)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

    #print(id)
    udb = {}
    udb[_id] = db.get_status_info(_id)
    #print(udb[_id])
    reply_msgs = []
    #コマンド受信
    if(event.message.text[0] == cmd_prefix):
        print('command received')
        cmd = event.message.text[1:]

        if cmd == u'支払登録':
            user_groups = db.get_user_groups(_id)
            # if len(user_groups) == 0:
            #     reply_msgs.append(TextSendMessage(text = u'まだグループに所属していません'))
            # elif len(user_groups) > 1:
            #     reply_msgs.append(TextSendMessage(text = u'複数のグループに所属しているね'))

            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払登録ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url='https://example.com/image.jpg',
                    title=u'支払登録',
                    text=u'何か支払ったんだね\nリストから選んでね',
                    actions=[
                        PostbackTemplateAction(
                            label=u'金額入力で登録',
                            # text=cmd_prefix + u'支払登録（金額入力）',
                            data=json.dumps({'cmd': 'input_amount_by_number'})
                        ),
                        PostbackTemplateAction(
                            label=u'電卓入力で登録',
                            # text=cmd_prefix + u'支払登録（電卓入力）',
                            data=json.dumps({'cmd': 'input_amount_by_calc'})
                        ),
                        # PostbackTemplateAction(
                        PostbackTemplateAction(
                            label=u'レシートで登録',
                            # text=cmd_prefix + u'支払登録（レシート）',
                            data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd[0:2] == u'電卓':
            if len(cmd[2:]) == 1:
                if cmd[2] == 'E':
                    udb[_id]['status'] = 'input_use'
                    reply_msgs.append(TextSendMessage(text = u'{amount}円だね\n何の金額か教えて(ex.レンタカー代)'.format(amount=get_commad_number_str(udb[_id].get('amount', 0)))))
                elif cmd[2] == 'C':
                    udb[_id]['amount'] = 0
                else:
                    n = int(cmd[2])
                    udb[_id]['amount'] = udb[_id].get('amount', 0) * 10 + n

            elif len(cmd[2:]) == 2:
                udb[_id]['amount'] = udb[_id].get('amount', 0) * 100
            elif len(cmd[2:]) == 3:
                udb[_id]['amount'] = udb[_id].get('amount', 0) * 1000

            if cmd[2] != 'E':
                reply_msgs.append(make_calc_message())
                reply_msgs.append(TextSendMessage(text = u'{amount}円 これで良ければEnterボタンを押してね'.format(amount=get_commad_number_str(udb[_id]['amount']))))

        elif cmd == u'確認':
            # reply_msgs.append(TextSendMessage(text = u'何の確認をするかリストから選んでね'))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'確認ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url='https://example.com/image.jpg',
                    title=u'確認',
                    text=u'何の確認をするかリストから選んでね',
                    actions=[
                        PostbackTemplateAction(
                            label=u'支払メンバー確認',
                            # text=cmd_prefix + u'支払メンバー確認',
                            data=json.dumps({'cmd': 'show_group_members'})
                        ),
                        PostbackTemplateAction(
                            label=u'個別支払合計',
                            # text=cmd_prefix + u'個別支払合計',
                            data=json.dumps({'cmd': 'show_members_amount'})
                        ),
                        PostbackTemplateAction(
                            label=u'支払一覧',
                            # text=cmd_prefix + u'支払一覧',
                            data=json.dumps({'cmd': 'show_payment_list'})
                        ),
                        PostbackTemplateAction(
                            label=u'精算設定確認',
                            # text=cmd_prefix + u'精算設定確認',
                            data=json.dumps({'cmd': 'show_check_config'})
                        ),
                    ]
                )
            ))
        elif cmd == u'支払メンバー確認':
            pass
        elif cmd == u'個別支払合計':
            pass
        elif cmd == u'支払一覧':
            pass
            # uid = event.source.user_id
            # payments = db.get_user_groups_payments(uid)
            # for payment in payments:
            #     pass
            # reply_msgs.append(TemplateSendMessage(
            #     alt_text='支払一覧',
            #     template=ButtonsTemplate(
            #         # thumbnail_image_url=udb[_id].get('image_url', None),
            #         title=u'支払一覧',
            #         text = u'リストの登録金額を選択すると詳細を表示するよ。表示は新しいものから表示しています。',
            #         actions=[
            #             MessageTemplateAction(
            #             # PostbackTemplateAction(
            #                 label=u'『支払金額』(『支払対象人数』)',
            #                 text=cmd_prefix + u'『支払金額』(『支払対象人数』)',
            #                 # data=json.dumps({'cmd': 'input_amount_by_image'})
            #             ),
            #             MessageTemplateAction(
            #             # PostbackTemplateAction(
            #                 label=u'『支払金額』(『支払対象人数』)',
            #                 text=cmd_prefix + u'『支払金額』(『支払対象人数』)',
            #                 # data=json.dumps({'cmd': 'input_amount_by_image'})
            #             ),
            #             MessageTemplateAction(
            #             # PostbackTemplateAction(
            #                 label=u'『支払金額』(『支払対象人数』)',
            #                 text=cmd_prefix + u'『支払金額』(『支払対象人数』)',
            #                 # data=json.dumps({'cmd': 'input_amount_by_image'})
            #             ),
            #             MessageTemplateAction(
            #             # PostbackTemplateAction(
            #                 label=u'『支払金額』(『支払対象人数』)',
            #                 text=cmd_prefix + u'『支払金額』(『支払対象人数』)',
            #                 # data=json.dumps({'cmd': 'input_amount_by_image'})
            #             ),
            #         ]
            #     )
            # ))
        elif cmd == u'『支払金額』(『支払対象人数』)':
            text = u'''『対象ユーザ』さんが『項目名』で『支払金額』円支払
いました。
この支払いに対する支払対象者は『支払対象人数』名で
す。
『対象ユーザ』さん
『対象ユーザ』さん
・
・
・
『対象ユーザ』さん
『対象ユーザ』さん
会計係さん'''
            reply_msgs.append(TextSendMessage(text = text))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払一覧ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'支払一覧',
                    text = u'リストの登録金額を選択すると詳細を表示するよ。表示は新しいものから表示しています。',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'何もしない',
                            text=cmd_prefix + u'何もしない',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'支払対象変更',
                            text=cmd_prefix + u'支払対象変更',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'内容訂正',
                            text=cmd_prefix + u'内容訂正',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'支払削除',
                            text=cmd_prefix + u'支払削除',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'何もしない':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'何もしないボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'支払一覧に戻りますか?',
                    text=u'支払一覧に戻りますか?',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'戻る',
                            text=cmd_prefix + u'支払一覧',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'終了する',
                            text=cmd_prefix + u'終了する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'終了する':
            reply_msgs.append(TextSendMessage(text = u'支払一覧確認を終了しました'))

        elif cmd == u'支払対象変更':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払対象変更ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'支払対象変更?',
                    text = u'行いたい操作をリストから選んでください。',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'1名だけにする',
                            text=cmd_prefix + u'1名だけにする',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'1名減らす',
                            text=cmd_prefix + u'1名減らす',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'1名増やす',
                            text=cmd_prefix + u'1名増やす',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'全員対象にする',
                            text=cmd_prefix + u'全員対象にする',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'1名だけにする':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'1名だけにするボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'特定支払',
                    text = u'支払対象となるユーザーをリストから選んでください。',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'特定支払『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'特定支払『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'特定支払『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'キャンセル',
                            text=cmd_prefix + u'キャンセル',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'特定支払『対象ユーザ』さん':
            # db.set_debt_uid_list(gid, uid_list)
            db.set_debt_uid_list('sample_gid', ['sample_user'])
            reply_msgs.append(TextSendMessage(text = u'支払対象者を『対象ユーザ』さんに設定しました'))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払一覧に戻りますか?',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'支払一覧に戻りますか?',
                    text = u'支払一覧に戻りますか?',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'戻る',
                            text=cmd_prefix + u'支払一覧',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'終了する',
                            text=cmd_prefix + u'終了する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'1名減らす':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払対象除外',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'支払対象除外',
                    text = u'支払対象から除外するユーザーをリストから選んでください。',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'キャンセル',
                            text=cmd_prefix + u'キャンセル',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'1名増やす':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払対象追加',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'支払対象追加',
                    text = u'支払対象に追加するユーザーをリストから選んでください',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'『対象ユーザ』さん',
                            text=cmd_prefix + u'『対象ユーザ』さん',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'キャンセル',
                            text=cmd_prefix + u'キャンセル',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'全員対象にする':
            reply_msgs.append(TextSendMessage(text = u'全てのユーザを支払対象に設定しました'))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払一覧に戻りますか?',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'支払一覧に戻りますか?',
                    text = u'支払一覧に戻りますか?',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'戻る',
                            text=cmd_prefix + u'支払一覧',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'終了する',
                            text=cmd_prefix + u'終了する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))

        elif cmd == u'内容訂正':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払訂正ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url='https://example.com/image.jpg',
                    title=u'支払訂正',
                    text=u'訂正する項目をリストから選んでね',
                    actions=[
                        # PostbackTemplateAction(
                        MessageTemplateAction(
                            label=u'金額',
                            text=cmd_prefix + u'支払訂正金額',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                            label=u'支払項目',
                            text=cmd_prefix + u'支払訂正項目',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        # PostbackTemplateAction(
                        MessageTemplateAction(
                            label=u'写真',
                            text=cmd_prefix + u'支払訂正写真',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'支払削除':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払削除ボタン',
                template=ButtonsTemplate(
                    # thumbnail_image_url='https://example.com/image.jpg',
                    # title=u'支払削除',
                    text=u'この支払を削除してもよいですか？',
                    actions=[
                        # PostbackTemplateAction(
                        MessageTemplateAction(
                            label=u'削除',
                            text=cmd_prefix + u'支払削除実行',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                            label=u'中止',
                            text=cmd_prefix + u'中止',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'支払削除実行':
            # db.delete_payment(payment_id)
            reply_msgs.append(TextSendMessage(text = u'支払を削除しました'))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払一覧に戻りますか?',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'支払一覧に戻りますか?',
                    text = u'支払一覧に戻りますか?',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'戻る',
                            text=cmd_prefix + u'支払一覧',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'終了する',
                            text=cmd_prefix + u'終了する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'中止':
            reply_msgs.append(TextSendMessage(text = u'削除操作を中止しました'))
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'支払一覧に戻りますか?',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'支払一覧に戻りますか?',
                    text = u'支払一覧に戻りますか?',
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'戻る',
                            text=cmd_prefix + u'支払一覧',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'終了する',
                            text=cmd_prefix + u'終了する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
        elif cmd == u'支払訂正金額':
            # db.update_payment(amount, description, image)
            # db.update_payment(amout = 1000)
            reply_msgs.append(TextSendMessage(text = u'省略'))
        elif cmd == u'支払訂正項目':
            # db.update_payment(description = 'テスト')
            reply_msgs.append(TextSendMessage(text = u'省略'))
        elif cmd == u'支払訂正写真':
            # db.update_payment(image = 'https://example.com/image')
            reply_msgs.append(TextSendMessage(text = u'省略'))
        elif cmd == u'精算':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'精算',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'精算',
                    text = u'何の処理をするかリストから選んでね',
                    actions=[
                        PostbackTemplateAction(
                            label=u'精算実行・更新',
                            # text=cmd_prefix + u'精算実行・更新',
                            data=json.dumps({'cmd': 'check_start'})
                        ),
                        PostbackTemplateAction(
                            label=u'精算報告',
                            # text=cmd_prefix + u'精算報告',
                            data=json.dumps({'cmd': 'check_report'})
                        ),
                        PostbackTemplateAction(
                            label=u'精算結果確認',
                            # text=cmd_prefix + u'精算結果確認',
                            data=json.dumps({'cmd': 'check_status'})
                        ),
                    ]
                )
            ))

        elif cmd == u'設定':
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'設定',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            # thumbnail_image_url=base_url + '/static/car.jpg',
                            title=u'精算設定',
                            text=u'どれを操作するかリストから選んでね',
                            actions=[
                                PostbackTemplateAction(
                                    label=u'丸め設定',
                                    # text=cmd_prefix + u'丸め設定',
                                    data=json.dumps({'cmd': 'set_round'})
                                ),
                                PostbackTemplateAction(
                                    label=u'傾斜設定',
                                    # text=cmd_prefix + u'傾斜設定',
                                    data=json.dumps({'cmd': 'set_slope'})
                                ),
                                PostbackTemplateAction(
                                    label=u'精算設定確認',
                                    # text=cmd_prefix + u'精算設定確認',
                                    data=json.dumps({'cmd': 'show_check_config'})
                                ),
                            ]
                        ),
                        CarouselColumn(
                            # thumbnail_image_url=base_url + '/static/car.jpg',
                            title=u'全般',
                            text=u'どれを操作するかリストから選んでね',
                            actions=[
                                PostbackTemplateAction(
                                    label=u'会計係の設定',
                                    # text=cmd_prefix + u'会計係の設定',
                                    data=json.dumps({'cmd': 'set_accountant'})
                                ),
                                PostbackTemplateAction(
                                    label=u'初期化',
                                    # text=cmd_prefix + u'初期化',
                                    data=json.dumps({'cmd': 'initialize'})
                                ),
                                PostbackTemplateAction(
                                    label=u'改善要望・バグ報告',
                                    # text=cmd_prefix + u'改善要望・バグ報告',
                                    data=json.dumps({'cmd': 'report'})
                                ),
                            ]
                        ),

                    ]
                )
            ))

        else:
            reply_msgs.append(TextSendMessage(text = u'知らないコマンドだ'))

    else:
        try:
            print(_id)
            print(udb[_id])
            status = udb[_id]['status']
        except:
            print('except')
            status = 'none'
        print status

        if status == 'input_amount':
            if event.message.text.isdigit():
                amount = int(event.message.text)
                if (amount < 1) | (amount > 999999):
                    reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜999,999円だよ'))

                else:
                    udb[_id]['status'] = 'input_use'
                    udb[_id]['amount'] = amount
                    reply_msgs.append(TextSendMessage(text = u'何の金額か教えて(ex.レンタカー代)'))

            else:
                reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜999,999円だよ'))

        elif status == 'input_use':
            udb[_id]['use'] = event.message.text
            reply_msgs.append(TemplateSendMessage(
                alt_text='登録確認',
                template=ButtonsTemplate(
                    thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'登録確認',
                    text = u'{use}で{amount}円、これで登録してよいですか？'.format(use = udb[_id]['use'], amount = get_commad_number_str(udb[_id]['amount'])),
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'OK',
                            text=u'OK',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'訂正する',
                            text=u'訂正する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
            udb[_id]['status'] = 'ask_photo_addition'

        elif status == 'ask_photo_addition':
            if event.message.text == u'OK':
                reply_msgs.append(TemplateSendMessage(
                    alt_text='写真確認',
                    template=ConfirmTemplate(
                        text = u'この支払に対して一緒に写真も登録しますか？',
                        actions=[
                            MessageTemplateAction(
                            # PostbackTemplateAction(
                                label=u'はい',
                                text=u'はい',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                            MessageTemplateAction(
                            # PostbackTemplateAction(
                                label=u'いいえ',
                                text=u'いいえ',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                        ]
                    )
                ))
                udb[_id]['status'] = 'confirm_photo_addition'

            elif event.message.text == u'訂正する':
                reply_msgs.append(TemplateSendMessage(
                    alt_text=u'支払訂正ボタン',
                    template=ButtonsTemplate(
                        # thumbnail_image_url='https://example.com/image.jpg',
                        title=u'支払訂正',
                        text=u'訂正する項目をリストから選んでね',
                        actions=[
                            # PostbackTemplateAction(
                            MessageTemplateAction(
                                label=u'金額',
                                text=u'金額',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                            MessageTemplateAction(
                                label=u'支払項目',
                                text=u'支払項目',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                            # PostbackTemplateAction(
                            MessageTemplateAction(
                                label=u'写真',
                                text=u'写真',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                        ]
                    )
                ))
                udb[_id]['status'] = 'modify_payment'

            else: #訂正する
                reply_msgs.append(TextSendMessage(text = u'ボタンで選んでね'))

        elif status == 'confirm_photo_addition':
            if event.message.text == u'はい':
                reply_msgs.append(TextSendMessage(text = u'写真を撮るか、写真を選択してね'))
                udb[_id]['status'] = 'add_photo'

            elif event.message.text == u'いいえ':
                reply_msgs.append(TextSendMessage(text = u'登録完了しました！この内容でみんなに報告しますね！'))
                # ここでDB登録＆みんなに報告
                groups = db.get_user_groups(_id)
                for gid in groups:
                    db.add_payment(gid, _id, udb[_id]["amount"], udb[_id].get("use"), udb[_id].get("image"))

                    msgs = []
                    name = get_name(_id)
                    if "use" in udb[_id]:
                        msgs.append(TextSendMessage(text = u'{}さんが{}に{}円支払いました'.format(name, udb[_id].get("use"), get_commad_number_str(udb[_id]["amount"]))))
                    else:
                        msgs.append(TextSendMessage(text = u'{}さんが{}円支払いました'.format(name, get_commad_number_str(udb[_id]["amount"]))))
                    if "image" in udb[_id]:
                        msgs.append(ImageSendMessage(original_content_url = udb[_id]["image"], preview_image_url = udb[_id]["image"]))
                    line_bot_api.push_message(gid, msgs)

                del udb[_id]
                db.delete_status_info(_id)
            else:
                reply_msgs.append(TextSendMessage(text = u'ボタンで選んでね'))

        elif status == 'modify_payment':
            if event.message.text == u'金額':
                reply_msgs.append(TextSendMessage(text = u'金額を入力してね(1~999,999)'))
                udb[_id]['status'] = 'modify_amount'
            if event.message.text == u'支払項目':
                reply_msgs.append(TextSendMessage(text = u'何の金額か教えて(ex.レンタカー代)'))
                udb[_id]['status'] = 'modify_use'
            if event.message.text == u'写真':
                reply_msgs.append(TextSendMessage(text = u'写真を撮るか、写真を選択してね'))
                udb[_id]['status'] = 'modify_photo'

        elif status == 'modify_amount':
            if event.message.text.isdigit():
                amount = int(event.message.text)
                if (amount < 1) | (amount > 999999):
                    reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜999,999円だよ'))

                else:
                    # udb[_id]['status'] = 'input_use'
                    udb[_id]['amount'] = amount
                    reply_msgs.append(TemplateSendMessage(
                        alt_text='登録確認',
                        template=ButtonsTemplate(
                            thumbnail_image_url=udb[_id].get('image_url', None),
                            # title=u'登録確認',
                            text = u'{use}で{amount}円、これで登録してよいですか？'.format(use = udb[_id]['use'], amount = get_commad_number_str(udb[_id]['amount'])),
                            actions=[
                                MessageTemplateAction(
                                # PostbackTemplateAction(
                                    label=u'OK',
                                    text=u'OK',
                                    # data=json.dumps({'cmd': 'input_amount_by_image'})
                                ),
                                MessageTemplateAction(
                                # PostbackTemplateAction(
                                    label=u'訂正する',
                                    text=u'訂正する',
                                    # data=json.dumps({'cmd': 'input_amount_by_image'})
                                ),
                            ]
                        )
                    ))
                    udb[_id]['status'] = 'confirm_modify'

            else:
                reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜999,999円だよ'))


        elif status == 'modify_use':
            udb[_id]['use'] = event.message.text
            reply_msgs.append(TemplateSendMessage(
                alt_text='登録確認',
                template=ButtonsTemplate(
                    thumbnail_image_url=udb[_id].get('image_url', None),
                    # title=u'登録確認',
                    text = u'{use}で{amount}円、これで登録してよいですか？'.format(use = udb[_id]['use'], amount = get_commad_number_str(udb[_id]['amount'])),
                    actions=[
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'OK',
                            text=u'OK',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                        MessageTemplateAction(
                        # PostbackTemplateAction(
                            label=u'訂正する',
                            text=u'訂正する',
                            # data=json.dumps({'cmd': 'input_amount_by_image'})
                        ),
                    ]
                )
            ))
            udb[_id]['status'] = 'confirm_modify'

        elif status == 'confirm_modify':
            if event.message.text == u'OK':
                reply_msgs.append(TextSendMessage(text = u'登録完了しました！この内容でみんなに報告しますね！'))
                # ここでDB登録＆みんなに報告
                groups = db.get_user_groups(_id)
                for gid in groups:
                    #db.add_payment(gid, _id, udb[_id]["amount"], udb[_id].get("use"), udb[_id].get("image_url"))
                    db.add_payment(gid, _id, udb[_id]["amount"], udb[_id].get("use"), udb[_id].get("image"))

                    msgs = []
                    name = get_name(_id)
                    if "use" in udb[_id]:
                        msgs.append(TextSendMessage(text = u'{}さんが{}に{}円支払いました'.format(name, udb[_id].get("use"), get_commad_number_str(udb[_id]["amount"]))))
                    else:
                        msgs.append(TextSendMessage(text = u'{}さんが{}円支払いました'.format(name, get_commad_number_str(udb[_id]["amount"]))))
                    if "image_url" in udb[_id]:
                        msgs.append(ImageSendMessage(original_content_url = udb[_id]["image_url"], preview_image_url = udb[_id]["image_url"]))
                    line_bot_api.push_message(gid, msgs)

                del udb[_id]
                db.delete_status_info(_id)
            elif event.message.text == u'訂正する':
                reply_msgs.append(TemplateSendMessage(
                    alt_text=u'支払訂正ボタン',
                    template=ButtonsTemplate(
                        # thumbnail_image_url='https://example.com/image.jpg',
                        title=u'支払訂正',
                        text=u'訂正する項目をリストから選んでね',
                        actions=[
                            # PostbackTemplateAction(
                            MessageTemplateAction(
                                label=u'金額',
                                text=u'金額',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                            MessageTemplateAction(
                                label=u'支払項目',
                                text=u'支払項目',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                            # PostbackTemplateAction(
                            MessageTemplateAction(
                                label=u'写真',
                                text=u'写真',
                                # data=json.dumps({'cmd': 'input_amount_by_image'})
                            ),
                        ]
                    )
                ))
                udb[_id]['status'] = 'modify_payment'

            else:
                reply_msgs.append(TextSendMessage(text = u'ボタンで選んでね'))

        elif status in ['add_photo', 'modify_photo']:
            reply_msgs.append(TextSendMessage(text = u'写真を撮るか、写真を選択してね'))

        elif status == 'set_rate':
            if event.message.text.isdigit():
                rate = int(event.message.text)
                if (rate < 1) | (rate > 99):
                    reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜99だよ'))

                else:
                    reply_msgs.append(TextSendMessage(text = u'『対象ユーザ』さんの傾斜割合を{rate}に設定しました'.format(rate=get_commad_number_str(rate))))

            else:
                reply_msgs.append(TextSendMessage(text = u'入力できるのは1〜99だよ'))

        if(event.message.text == u'バイバイ'):
            # del_warikan_group(event.source)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=u'またね'))
            if(event.source.type == 'group'):
                line_bot_api.leave_group(event.source.group_id)
                gid = event.source.group_id
            elif(event.source.type == 'room'):
                line_bot_api.leave_room(event.source.room_id)
                gid = event.source.room_id
            db.delete_group(gid)

        if(event.message.text == u'リンク'):
            if(event.source.type == 'group'):
                gid = event.source.group_id
            elif(event.source.type == 'room'):
                gid = event.source.room_id
            reply_msgs.append(TextSendMessage(text = line_friend_url))
            reply_msgs.append(ImageSendMessage(original_content_url = line_qr_url, preview_image_url = line_qr_url))

            link_uri='https://access.line.me/dialog/oauth/weblogin?response_type=code&client_id={}&redirect_uri={}&state={}'.format(line_login_channel_id, urllib.quote(auth_url), gid)
            reply_msgs.append(ImagemapSendMessage(
                base_url=base_url + '/images/LINELogin',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=302, width=1040),
                actions=[
                    URIImagemapAction(
                        link_uri=link_uri,
                        area=ImagemapArea(x=0, y=0, width=1040, height=302)
                    ),
                ]
            ))

    send_msgs(reply_msgs, reply_token = event.reply_token)

def save_content(message_id, filename):
    message_content = line_bot_api.get_message_content(message_id)
    with open(filename, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    _id = get_id(event.source)
    udb = {}
    udb[_id] = db.get_status_info(_id)
    #print(udb[_id])

    if event.source.type == 'user':
        update_profile(_id)

    fname = event.message.id + '_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'
    save_content(event.message.id, 'static/' + fname)

    reply_msgs = []
    try:
        status = udb[_id]['status']
    except:
        print('except')
        status = 'none'
    print status

    if status in ['add_photo', 'modify_photo']:
        udb[_id]['image_url'] = base_url + 'static/' + fname
        udb[_id]['image'] = fname
        receipt_amount = vision.get_receipt_amount('static/' + fname)
        print(receipt_amount)
        udb[_id]['amount'] = int(receipt_amount)

        reply_msgs.append(TemplateSendMessage(
            alt_text='登録確認',
            template=ButtonsTemplate(
                thumbnail_image_url=udb[_id].get('image_url', None),
                # title=u'登録確認',
                #text = u'{use}で{amount}円、これで登録してよいですか？'.format(use = udb[_id]['use'], amount = get_commad_number_str(udb[_id]['amount'])),
                #text = u'{use}で{amount}円、これで登録してよいですか？'.format(use = udb[_id]['use'], amount = receipt_amount),
                text = u'{amount}円、これで登録してよいですか？'.format(amount = receipt_amount),
                actions=[
                    MessageTemplateAction(
                    # PostbackTemplateAction(
                        label=u'OK',
                        text=u'OK',
                        # data=json.dumps({'cmd': 'input_amount_by_image'})
                    ),
                    MessageTemplateAction(
                    # PostbackTemplateAction(
                        label=u'訂正する',
                        text=u'訂正する',
                        # data=json.dumps({'cmd': 'input_amount_by_image'})
                    ),
                ]
            )
        ))
        udb[_id]['status'] = 'confirm_modify'

    db.update_status_info(_id, udb[_id])
    send_msgs(reply_msgs, reply_token = event.reply_token)

@handler.add(MessageEvent, message=VideoMessage)
def handle_video_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

@handler.add(FollowEvent)
def handle_follow_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)

    text = u'''はじめまして、Checkunです。
グループ旅行やイベントの面倒な精算作業は私にお任せ。

まずは、グループトークに私を招待してみてね。

使い方について知りたい場合は、メニューの「ヘルプ」か以下のリンクから調べてみてね。
{}'''.format(checkun_url)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text))

@handler.add(UnfollowEvent)
def handle_unfollow_message(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id, False)


@handler.add(JoinEvent)
def handle_join_message(event):
    if event.source.type == 'group':
        gid = event.source.group_id
    elif event.source.type == 'room':
        gid = event.source.room_id

    msgs=[]

    text = u'はじめまして、Checkunです。このグループの会計係をさせていただきます！\n' \
        u'まずは、このグループメンバー全員の方とお友達になりたいです。\n' \
        u'次のURLかQRコードで友達になってね。\n' \
        u'友達になったら下のログインボタンで精算グループに入ってね。' \
        # u'グループのスタンプを決めて送ってね'
        # u'左のボタンを押して私と友達になって、右のボタンで精算グループに入ってください！'
    msgs.append(TextSendMessage(text = text))

    msgs.append(TextSendMessage(text = line_friend_url))
    msgs.append(ImageSendMessage(original_content_url = line_qr_url, preview_image_url = line_qr_url))

    link_uri='https://access.line.me/dialog/oauth/weblogin?response_type=code&client_id={}&redirect_uri={}&state={}'.format(line_login_channel_id, urllib.quote(auth_url), gid)
    msgs.append(ImagemapSendMessage(
        base_url=base_url + '/images/LINELogin',
        alt_text='this is an imagemap',
        base_size=BaseSize(height=302, width=1040),
        actions=[
            URIImagemapAction(
                link_uri=link_uri,
                area=ImagemapArea(x=0, y=0, width=1040, height=302)
            ),
        ]
    ))

    line_bot_api.reply_message(event.reply_token, msgs)

    db.add_group(gid,event.source.type)
    # add_warikan_group(event.source)

@handler.add(LeaveEvent)
def handle_leave_message(event):
    if event.source.type == 'group':
        gid = event.source.group_id
    elif event.source.type == 'room':
        gid = event.source.room_id
    db.delete_group(gid)

def make_calc_message():
    actions=[]
    calc_buttonid = ['7', '8', '9', '000', 'C', '4', '5', '6', '00', 'E', '1', '2', '3', '0', 'E']
    button_x = 208
    button_y = 188
    for y in range(3):
        for x in range(5):
            actions.append(MessageImagemapAction(text=cmd_prefix + u'電卓' + calc_buttonid[x+y*5], area=ImagemapArea(x=x*button_x, y=y*button_y, width=button_x, height=button_y)))

    calc_message = ImagemapSendMessage(
        base_url=base_url + '/images/Calc170222',
        alt_text='電卓入力ボタン',
        base_size=BaseSize(height=564, width=1040),
        actions=actions
    )
    return calc_message


@handler.add(PostbackEvent)
def handle_postback_event(event):
    _id = get_id(event.source)
    udb = {}
    udb[_id] = db.get_status_info(_id)
    if event.source.type == 'user':
        update_profile(_id)
    data = json.loads(event.postback.data)
    cmd = data.get('cmd')
    value = data.get('value')
    reply_msgs = []

    if False:
        pass
    elif cmd == 'input_amount_by_number':
        udb[_id] = {'status': 'input_amount'}
        reply_msgs.append(TextSendMessage(text = u'金額を入力してね(1~999,999)'))
    elif cmd == 'input_amount_by_calc':
        udb[_id] = {'status': 'input_amount'}
        udb[_id]['amount'] = 0
        reply_msgs.append(make_calc_message())
    elif cmd == 'input_amount_by_image':
        #udb[_id] = {'status': 'input_amount'}
        udb[_id]['status'] = 'add_photo'
        reply_msgs.append(TextSendMessage(text = u'レシートを撮るか、写真を選択してね'))
        #reply_msgs.append(TextSendMessage(text = u'まだ実装していません'))

    elif cmd == 'show_group_members':
        groups = db.get_user_groups(event.source.user_id)
        text = ''
        if len(groups) == 0:
            text = u'グループに所属していません\n'
        else:
            for gid in groups:
                if len(groups) > 1:
                    text += u'グループ：{}\n'.format(db.get_group_info(gid).get("name"))
                users = db.get_group_users(gid)
                text += u'　現在この精算グループには{}人の方が対象になっています\n'.format(len(users))
                for uid in users:
                    text += u'　{}さん\n'.format(get_name(uid))
                text += '\n'

        reply_msgs.append(TextSendMessage(text = text))
    elif cmd == 'show_members_amount':
        text = u'現時点の各個人の支払い合計を報告します。\n'
        groups = db.get_user_groups(event.source.user_id)
        for gid in groups:
            if len(groups) > 1:
                text += u'グループ：{}\n'.format(db.get_group_info(gid).get("name"))

            payments = db.get_groups_payments(gid)
            totals = {}
            for payment in payments:
                uid = payment["payment_uid"]
                amount = payment["amount"]
                totals[uid] = totals.get(uid,0) + amount

            if len(totals) == 0:
                text += u'支払の記録はありません\n'

            else:
                total = 0
                for k, v in totals.items():
                    text += u'{}さんが{}円支払いました\n'.format(get_name(k), get_commad_number_str(v))
                    total += v

                users = db.get_group_users(gid)
                text += u'{}人だと、一人あたり約{}円です'.format(len(users), get_commad_number_str(total/len(users)))
            text += '\n'

        reply_msgs.append(TextSendMessage(text = text))
    elif cmd == 'show_payment_list':
        text = u'現時点の支払い一覧を報告します。\n'
        groups = db.get_user_groups(event.source.user_id)
        for gid in groups:
            if len(groups) > 1:
                text += u'グループ：{}\n'.format(db.get_group_info(gid).get("name"))

            payments = db.get_groups_payments(gid)
            if len(payments) == 0:
                text += u'支払の記録はありません\n'
            for payment in payments:
                uid = payment["payment_uid"]
                amount = payment["amount"]
                text += u'{}さんが{}円支払いました\n'.format(get_name(uid), get_commad_number_str(amount))
            text += '\n'

        reply_msgs.append(TextSendMessage(text = text))

    elif cmd == 'check_start':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'精算実行確認',
            template=ConfirmTemplate(
                text = u'新しい精算を開始します。よろしいですか?以前に実行した精算情報は全て消えてしまいます。',
                actions=[
                    PostbackTemplateAction(
                        label=u'実行する',
                        # text=cmd_prefix + u'精算実行・更新実行',
                        data=json.dumps({'cmd': 'check_start_yes'})
                    ),
                    PostbackTemplateAction(
                        label=u'中止する',
                        # text=cmd_prefix + u'精算実行・更新中止',
                        data=json.dumps({'cmd': 'check_start_no'})
                    ),
                ]
            )
        ))
    elif cmd == 'check_start_yes':
        text = u''
        groups = db.get_user_groups(_id)
        for gid in groups:
            ginfo = db.get_group_info(gid)
            if len(groups) > 1:
                text += u'グループ：{}\n'.format(db.get_group_info(gid).get("name"))
            payments = db.get_groups_payments(gid)
            totals = {}
            for payment in payments:
                _id = payment["payment_uid"]
                amount = payment["amount"]
                totals[_id] = totals.get(_id,0) + amount

            warikan_payments = []
            for payment in payments:
                warikan_payments.append({
                    'payment_uid': payment['payment_uid'],
                    'amount': payment['amount'],
                    'debt_uid': payment.get('debt_uid', ginfo['users']),
                })

            users = db.get_group_users(gid)

            transfer_text = u''
            # transfer_list = warikan.calc_warikan2(users, totals)
            transfer_list = warikan.calc_warikan3(users, warikan_payments, ginfo['round_value'], ginfo['additionals'], ginfo['rates'])
            if len(transfer_list) == 0:
                transfer_text += u'精算の必要はありません\n'
            for transfer in transfer_list:
                transfer_text += u'{}さんは{}さんに{}円支払ってください\n'.format(get_name(transfer["from"]), get_name(transfer["to"]), get_commad_number_str(transfer["amount"]))
                pay_text = u'{}さんに{}円支払ってください\n'.format(get_name(transfer["to"]), get_commad_number_str(transfer["amount"]))
                rec_text = u'{}さんから{}円受け取ってください\n'.format(get_name(transfer["from"]), get_commad_number_str(transfer["amount"]))
                # print pay_text
                # print rec_text
                # print transfer["from"]
                if transfer["from"] == _id:
                    text += pay_text
                else:
                    # line_bot_api.push_message(transfer["from"], TextSendMessage(text = push_text))
                    pass
                if transfer["to"] == _id:
                    text += rec_text
                else:
                    pass

            line_bot_api.push_message(gid, TextSendMessage(text = transfer_text))

        reply_msgs.append(TextSendMessage(text = text))
        # reply_msgs.append(TextSendMessage(text = transfer_text))
    elif cmd == 'check_start_no':
        reply_msgs.append(TextSendMessage(text = u'精算処理を中止しました'))
    elif cmd == 'check_report':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'精算報告',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                title=u'精算報告',
                text = u'『対象ユーザ』さんに『未精算金額』円払払いました か? or『対象ユーザ』さんに『未精算金額』円もらいました',
                actions=[
                    PostbackTemplateAction(
                        label=u'完了した',
                        # text=cmd_prefix + u'精算完了',
                        data=json.dumps({'cmd': 'check_finished'})
                    ),
                    PostbackTemplateAction(
                        label=u'まだしてない',
                        # text=cmd_prefix + u'精算まだ',
                        data=json.dumps({'cmd': 'check_not_finished'})
                    ),
                ]
            )
        ))
    elif cmd == 'check_finished':
        reply_msgs.append(TextSendMessage(text = u'ありがとうございます!『対象ユーザ』さんに確認します!'))
        reply_msgs.append(TextSendMessage(text = u'『対象ユーザ』さんに確認しました!あなたの精算は完了です！ or 『対象ユーザ』さんの確認が取れませんでした。再度精算をしてから報告してください。'))
    elif cmd == 'check_not_finished':
        reply_msgs.append(TextSendMessage(text = u'早く払ってください!! or 早くもらってください!!'))
    elif cmd == 'check_status':
        reply_msgs.append(TextSendMessage(text = u'''現在の精算結果をお知らせします
【精算済】『対象ユーザ』さん →『対象ユーザ』さ
ん:『未精算金額』円
『対象ユーザ』さん →『対象ユーザ』さん:『未精算
金額』円
・
・
・
【精算済】『対象ユーザ』さん →『対象ユーザ』さ
ん:『未精算金額』円'''))

    elif cmd == 'set_round':
        if value is None:
            reply_msgs.append(TemplateSendMessage(
                alt_text=u'丸め設定',
                template=ButtonsTemplate(
                    # thumbnail_image_url=udb[_id].get('image_url', None),
                    title=u'丸め設定',
                    text = u'端数の丸め設定値を選択してください。',
                    actions=[
                        PostbackTemplateAction(
                            label=u'設定しない',
                            data=json.dumps({'cmd': cmd, 'value': 1})
                        ),
                        PostbackTemplateAction(
                            label=u'100円',
                            data=json.dumps({'cmd': cmd, 'value': 100})
                        ),
                        PostbackTemplateAction(
                            label=u'500円',
                            data=json.dumps({'cmd': cmd, 'value': 500})
                        ),
                        PostbackTemplateAction(
                            label=u'1,000円',
                            data=json.dumps({'cmd': cmd, 'value': 1000})
                        ),
                    ]
                )
            ))
        else:
            if value < 2:
                reply_msgs.append(TextSendMessage(u'丸め設定値を解除しました'))
            else:
                reply_msgs.append(TextSendMessage(u'丸め設定値を{}円にしました'.format(get_commad_number_str(value))))

                groups = db.get_user_groups(_id)
                for gid in groups:
                    db.update_group(gid, round_value = value)

    elif cmd == 'set_slope':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'傾斜種類選択',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                title=u'傾斜種類選択',
                text = u'設定をしたい傾斜の種類を選択してください',
                actions=[
                    PostbackTemplateAction(
                        label=u'傾斜割合',
                        # text=cmd_prefix + u'傾斜割合',
                        data=json.dumps({'cmd': 'set_rates'})
                    ),
                    PostbackTemplateAction(
                        label=u'傾斜額',
                        # text=cmd_prefix + u'傾斜額',
                        data=json.dumps({'cmd': 'set_additionals'})
                    ),
                    MessageTemplateAction(
                    # PostbackTemplateAction(
                        label=u'傾斜設定確認',
                        text=cmd_prefix + u'傾斜設定確認',
                        # data=json.dumps({'cmd': 'input_amount_by_image'})
                    ),
                ]
            )
        ))
    elif cmd in ['set_rates', 'set_additionals']:
        gid = db.get_user_groups(_id)[0]
        ginfo = db.get_group_info(gid)
        users = db.get_group_users(gid)
        page = data.get('page', 0)
        page_max = len(users) / 2 - 1
        if page == 0:
            actions = [
                PostbackTemplateAction(
                    label=u'全ユーザー初期化',
                    # text=cmd_prefix + u'全ユーザー初期化',
                    data=json.dumps({'cmd': cmd + '_reset'})
                ),
            ]
        else:
            actions = [
                PostbackTemplateAction(
                    label=u'前のページ',
                    # text=cmd_prefix + u'全ユーザー初期化',
                    data=json.dumps({'cmd': cmd, 'page': page - 1})
                ),
            ]
        if page_max < 1 or page_max == page:
            for uid in users[page*2:]:
                label = get_name(uid)
                # if cmd == 'set_rates':
                #     label += '({})'.format(ginfo['rates'].get(uid, 1.0))
                # else:
                #     label += '({})'.format(ginfo['additionals'].get(uid, 0))
                actions.append(
                    PostbackTemplateAction(
                        label=label,
                        # text=cmd_prefix + u'全ユーザー初期化',
                        data=json.dumps({'cmd': cmd + '_user', 'uid': uid})
                    )
                )
        else:
            for uid in users[page*2:page*2+2]:
                label = get_name(uid)
                # if cmd == 'set_rates':
                #     label += '({})'.format(ginfo['rates'].get(uid, 1.0))
                # else:
                #     label += '({})'.format(ginfo['additionals'].get(uid, 0))
                actions.append(
                    PostbackTemplateAction(
                        label=label,
                        # text=cmd_prefix + u'全ユーザー初期化',
                        data=json.dumps({'cmd': cmd + '_user', 'uid': uid})
                    )
                )
            actions.append(
                PostbackTemplateAction(
                    label=u'次のページ',
                    # text=cmd_prefix + u'全ユーザー初期化',
                    data=json.dumps({'cmd': cmd, 'page': page + 1})
                ),
            )

        reply_msgs.append(TemplateSendMessage(
            alt_text=u'傾斜対象選択',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                title=u'傾斜対象選択',
                text = u'傾斜設定をしたいユーザーを選択してください',
                actions = actions,
            )
        ))
    elif cmd == 'set_rates_reset':
        gid = db.get_user_groups(_id)[0]
        reply_msgs.append(TextSendMessage(text = u'全てのユーザーの傾斜割合をリセットしました'))
        db.update_group(gid, rates = {})

    elif cmd == 'set_rates_user':
        uid = data['uid']
        actions=[]
        gid = db.get_user_groups(_id)[0]
        rate_now = db.get_group_info(gid)['rates'].get(uid, 1.0)
        diff_rates_str = ['-0.2', '-0.1', '+0.1', '+0.2']
        diff_rates = [-0.2, -0.1, 0.1, 0.2]
        for i in range(len(diff_rates)):
            actions.append(PostbackTemplateAction(
                label='{}'.format(diff_rates_str[i]),
                data = json.dumps({'cmd': 'set_rates_user_value', 'uid': uid, 'value': diff_rates[i]}),
            ))
        # TODO: 任意のレートは未実装
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'傾斜割合設定',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                title=u'傾斜割合設定',
                text = u'{}さんの傾斜割合は現在{}です\n処理を選んでください'.format(get_name(uid), rate_now),
                actions=actions,
            )
        ))

    elif cmd == 'set_rates_user_value':
        uid = data['uid']
        value = data['value']
        gid = db.get_user_groups(_id)[0]
        rates = db.get_group_info(gid)['rates']
        rate_new = round(rates.get(uid, 1.0) + value, 1)
        if rate_new < 0.0:
            reply_msgs.append(TextSendMessage(text = u'傾斜割合は0.0以下には設定できません'.format(get_name(uid), rate_new)))
            rate_new = 0.0
        else:
            reply_msgs.append(TextSendMessage(text = u'{}さんの傾斜割合を{}にしました'.format(get_name(uid), rate_new)))
        rates[uid] = rate_new
        db.update_group(gid, rates=rates)


    elif cmd == 'set_additionals_reset':
        gid = db.get_user_groups(_id)[0]
        reply_msgs.append(TextSendMessage(text = u'全てのユーザーの傾斜額をリセットしました'))
        db.update_group(gid, additionals = {})

    elif cmd == 'set_additionals_user':
        uid = data['uid']
        actions=[]
        gid = db.get_user_groups(_id)[0]
        rate_now = db.get_group_info(gid)['additionals'].get(uid, 0)
        diff_rates_str = [u'-2,000円', u'-1,000円', u'+1,000円', u'+2,000円']
        diff_rates = [-2000, -1000, 1000, 2000]
        for i in range(len(diff_rates)):
            actions.append(PostbackTemplateAction(
                label=u'{}'.format(diff_rates_str[i]),
                data = json.dumps({'cmd': 'set_additionals_user_value', 'uid': uid, 'value': diff_rates[i]}),
            ))
        # TODO: 任意のレートは未実装
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'傾斜額設定',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                title=u'傾斜額設定',
                text = u'{}さんの傾斜額は現在{}です\n処理を選んでください'.format(get_name(uid), rate_now),
                actions=actions,
            )
        ))

    elif cmd == 'set_additionals_user_value':
        uid = data['uid']
        value = data['value']
        gid = db.get_user_groups(_id)[0]
        additionals = db.get_group_info(gid)['additionals']
        additional_new = additionals.get(uid, 0) + value
        reply_msgs.append(TextSendMessage(text = u'{}さんの傾斜割合を{}にしました'.format(get_name(uid), additional_new)))
        additionals[uid] = additional_new
        db.update_group(gid, additionals=additionals)


    elif cmd == 'show_check_config':
        gid = db.get_user_groups(_id)[0]
        ginfo = db.get_group_info(gid)
        users = db.get_group_users(gid)
        text = u'精算設定は以下のようになっています\n'
        text += u'丸め設定：{}円\n'.format(ginfo['round_value'])
        for uid in users:
            rate = ginfo['rates'].get(uid)
            additional = ginfo['additionals'].get(uid)
            text += u'{}さんに'.format(get_name(uid))
            if rate is not None and additional is not None:
                text += u'は{}，{}円の傾斜があります\n'.format(
                    ginfo['rates'][uid],
                    get_commad_number_str(ginfo['additionals'][uid]),
                )
            elif rate is not None:
                text += u'は{}の傾斜があります\n'.format(
                    ginfo['rates'][uid],
                )
            elif additional is not None:
                text += u'は{}円の傾斜があります\n'.format(
                    get_commad_number_str(ginfo['additionals'][uid]),
                )
            else:
                text += u'傾斜はありません\n'

        reply_msgs.append(TextSendMessage(text))

    elif cmd == 'set_accountant':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'会計係の設定',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                # title=u'会計係の設定',
                text = u'企業や団体の経費立替係を入れる場合に設定します。',
                actions=[
                    PostbackTemplateAction(
                        label=u'設定する',
                        # text=cmd_prefix + u'会計係設定する',
                        data=json.dumps({'cmd': 'set_accountant_yes'})
                    ),
                    PostbackTemplateAction(
                        label=u'設定しない',
                        # text=cmd_prefix + u'会計係設定しない',
                        data=json.dumps({'cmd': 'set_accountant_no'})
                    ),
                ]
            )
        ))
    elif cmd == 'set_accountant_yes':
        reply_msgs.append(TextSendMessage(text = u'会計係設定しました'))
    elif cmd == 'set_accountant_no':
        reply_msgs.append(TextSendMessage(text = u'会計係設定を解除しました'))

    elif cmd == 'initialize':
        reply_msgs.append(TemplateSendMessage(
            alt_text=u'初期化',
            template=ButtonsTemplate(
                # thumbnail_image_url=udb[_id].get('image_url', None),
                # title=u'初期化',
                text = u'全ての設定を初期化します。よろしいですか？',
                actions=[
                    PostbackTemplateAction(
                        label=u'はい',
                        # text=cmd_prefix + u'初期化する',
                        data=json.dumps({'cmd': 'initialize_yes'})
                    ),
                    PostbackTemplateAction(
                        label=u'いいえ',
                        # text=cmd_prefix + u'初期化しない',
                        data=json.dumps({'cmd': 'initialize_no'})
                    ),
                ]
            )
        ))
    elif cmd == 'initialize_yes':
        reply_msgs.append(TextSendMessage(text = u'初期化しました'))
    elif cmd == 'initialize_no':
        reply_msgs.append(TextSendMessage(text = u'初期化を中止しました'))

    elif cmd == 'report':
        reply_msgs.append(TextSendMessage(text = u'''以下のリンクからお問い合わせください
{}'''.format(checkun_url)))

    db.update_status_info(_id, udb[_id])

    send_msgs(reply_msgs, reply_token = event.reply_token)

@handler.add(BeaconEvent)
def handle_beacon_event(event):
    _id = get_id(event.source)
    if event.source.type == 'user':
        update_profile(_id)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
    # app.run(debug=True, port=5001)
