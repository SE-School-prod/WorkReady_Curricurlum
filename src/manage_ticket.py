"""
@file change_status.py
@date 2023/11/17(木)
@author 林田翼
@brief 相談会チケットの枚数を管理するbot
@details 無料相談および有料相談に使用するチケットの枚数を管理する
@bar 編集日時 編集者 編集内容
@bar 2023/11/17(木) 林田翼 新規作成
@bar 2023/11/17(木) 林田翼 同一名前4
@bar 2025/03/07(金) 藤原光基 現状不要な処理削除、Kintoneから取得しなおすよう修正
"""


import datetime
import os

from pickle import FALSE
from token import STAR
from settings.settings_dict import settings_dict

from src.logger import Logger
from src.kintone import Kintone

KINTONE_APP_ID_CURRICURUM_UPDATE_T = int(os.environ["KINTONE_APP_ID_CURRICURUM_UPDATE_T"])

"""
@func confirm_ticket
@brief チケット枚数確認bot
@detail 各メンターカテゴリ内「チケット購入」チャンネルにて「現在のチケット枚数」とメッセージが送信された際、
@detail メッセージを送信した受講生の情報をKintoneから検索し下記を返す。
@detail ・「30分無料相談チケット」「30分有料相談チケット」「60分有料相談チケット」の各種枚数
@detail ・「30分無料相談チケット」の有効期限(4カ月を超過した場合枚数を0にする)
@detail ・チケット購入URL()  TODO これは今回GoogleFormから行う?
@param message bot発火メッセージオブジェクト
@param guild main側で定義されたDiscordサーバオブジェクト
@return なし
"""
async def confirm_ticket(message):

    # ロガーを初期化する。
    logger = Logger()
    logger = logger.get()

    try:

        # 送信メッセージが想定された内容の場合
        if(message.content == "現在のチケット枚数"):

            # 受講生のユーザIDを取得する。
            # user_id = str(message.author.id)
            user_id = message.author.id
    
            # 無料チケットの有効期限を確認する。
            expiration_date = confirm_ticket_expired(user_id)

            # 各種チケットの枚数を取得する。
            ticket_free,ticket_30,ticket_60 = get_ticket_num(user_id)

            expiration_date_str = ""
            if(expiration_date != ""):
                #チケットの有効期限を表示する
                expiration_date_str = (
                    f"30分無料チケットの有効期限：{expiration_date}\n"
                    f"\n"
                )

            reply = (
                f"<@{user_id}>さんの現在のチケット枚数は以下の通りです。\n"
                f"\n"
                f"30分無料相談チケット：{ticket_free}枚\n"
                f"30分有料相談チケット：{ticket_30}枚\n"
                f"60分有料相談チケット：{ticket_60}枚\n"
                f"\n"
                f"{expiration_date_str}"
                f"チケットを購入する場合は以下のURLよりお願いいたします。\n"
                f"★30分有料相談チケットはこちら\n"
                f"{os.environ['TICKET_URL_EASTCLOUD_30min']}\n"
                f"\n"
                f"★60分有料相談チケットはこちら\n"
                f"{os.environ['TICKET_URL_EASTCLOUD_60min']}\n"
                )
            await message.channel.send(reply)

        # 指定メッセージ以外エラーを出力する。
        else:
            reply = "コマンドが間違っています。\n「現在のチケット枚数」と入力してください。"
            await message.channel.send(reply)

    except Exception as e:
        logger.error(e)
        await message.channel.send("エラーが発生しました。「問い合わせ」チャンネルにて運営に問い合わせてください。")


"""
@func confirm_ticket_expired
@brief 無料チケット期限確認
@detail 各メンターカテゴリ内「チケット購入」チャンネルにて「現在のチケット枚数」とメッセージが送信された際、
@detail メッセージを送信した受講生の情報をKintoneから検索し下記を返す。
@detail ・「30分無料相談チケット」「30分有料相談チケット」「60分有料相談チケット」の各種枚数
@detail ・「30分無料相談チケット」の有効期限(4カ月を超過した場合枚数を0にする)
@param message bot発火メッセージオブジェクト
@param guild main側で定義されたDiscordサーバオブジェクト
@return なし
"""
def confirm_ticket_expired(user_id):

    try:
        # ロガー初期化する
        logger = Logger()
        logger = logger.get()

        # Kintoneから対象ユーザの30分無料相談チケット枚数、およびレコード入校日を取得する。
        kintone = Kintone()
        result = kintone.select(app_id=KINTONE_APP_ID_CURRICURUM_UPDATE_T, user_id=user_id, fields=["名前", "無料相談チケット30分", "入校日"])

        # 取得件数が1件以外の場合はエラーログを出力する。
        if len(result) == 1:
            result = result[0]

            result_ticket_free = result["無料相談チケット30分"]["value"]
            result_created = result["入校日"]["value"]
            result_name = result["名前"]["value"]

            # 作成日を取得したら、4か月を過ぎているかどうかを判定する
            result_created_dt = datetime.datetime.strptime(result_created, "%Y-%m-%d")
            now = datetime.datetime.now()

            expiration_dt = result_created_dt + datetime.timedelta(days=124)
            expiration_date = expiration_dt.strftime("%Y年%m月%d日")

            # データが登録されていない場合
            if result_ticket_free:
                ticket_free = int(result_ticket_free)
            else:
                ticket_free = 0

            # 無料相談チケットの有効期間を確認する。
            if ticket_free > 0:

                # 無料チケットが有効期限を超過した場合、無料チケットの枚数を0にする。
                if now > expiration_dt:
                    kintone.update(user_id, update_info={'無料相談チケット30分': 0})
                    log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(user_id, result_name, now)
                    logger.info("チケットの有効期限チェックを行い、アップデート成功: {}".format(log_message))

            else:
                logger.info("チケットの有効期限チェック不要")

            return expiration_date

        elif len(result) == 0:
            reply = f"該当するユーザが見つかりませんでした。"
            logger.error(reply)
            raise reply
        else:
            reply = f"該当するユーザが複数人いるため特定できませんでした。"
            logger.error(reply)
            raise reply
        
    except Exception as e:
        logger.error(e)


"""
@func get_ticket_num
@brief チケット枚数取得
@detail 受講生に紐づく各種チケット枚数を返す。
@param user_id 生徒DiscordID
@return ticket_free 30分無料チケット枚数
@return ticket_30 30分有料チケット枚数
@return ticket_60 60分有料チケット枚数
"""
def get_ticket_num(user_id):

    # ロガー初期化
    logger = Logger()
    logger = logger.get()

    # Kintoneマネージャを初期化する。
    kintone = Kintone()

    # 出力されるデータを制限する。
    fields = [
        "無料相談チケット30分",
        "有料相談チケット30分",
        "有料相談チケット60分"
    ]

    # Kintoneから「生徒DiscordID」に紐づくユーザ情報を
    result = kintone.select(app_id=KINTONE_APP_ID_CURRICURUM_UPDATE_T, user_id=user_id, fields=fields)

    if len(result) == 1:
        result = result[0]

        ticket_free = int(result["無料相談チケット30分"]["value"])
        ticket_30 = int(result["有料相談チケット30分"]["value"])
        ticket_60 = int(result["有料相談チケット60分"]["value"])

        return ticket_free, ticket_30, ticket_60

    elif len(result) == 0:
        reply = f"該当するユーザが見つかりませんでした。"
        logger.error(reply)
        raise reply

    else:
        reply = f"該当するユーザが複数人いるため特定できませんでした。"
        logger.error(reply)
        raise reply
