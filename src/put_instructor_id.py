"""
@file put_instructor_id.py
@date 2025/04/03(金)
@author 藤原光基
@brief 講師ID追記機能
@bar 編集日時 編集者 編集内容
@bar 2025/04/03(金) 藤原光基 新規作成
"""

import os
from collections import Counter  # リスト内の要素に対応する個数を算出するパッケージ

from src.kintone import Kintone
from src.logger import Logger


KINTONE_APP_ID_INSTRUCTOR_M = int(os.environ["KINTONE_APP_ID_INSTRUCTOR_M"])
KINTONE_APP_ID_CURRICURUM_UPDATE_T = int(os.environ["KINTONE_APP_ID_CURRICURUM_UPDATE_T"])
KINTONE_API_TOKEN_INSTRUCTOR_M = os.environ["KINTONE_API_TOKEN_INSTRUCTOR_M"]
KINTONE_API_TOKEN_PROGRESS_UPDATE_T = os.environ["KINTONE_API_TOKEN_PROGRESS_UPDATE_T"]
YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID = os.environ["YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID"]

# 「初期設定」チャンネルにて、講師ID
INIT_SETTING_CONTENT = "入校完了"


"""
@brief 講師ID割り当て
@param member Discrodサーバ上で記入されたメッセージ情報
"""
async def put_instructor_id(message):

    try:

        # 各種クラスのインスタンスを生成する。
        logger_ = Logger()
        logger = logger_.get()

        kintone = Kintone()

        # メッセージの内容を取得
        content = message.content

        # メッセージ内容が想定外の場合、
        if content != INIT_SETTING_CONTENT:
            error_message = "記入すべきメッセージが異なります。"
            await message.channel.send(error_message)

        else:

            # 最も割り当てられている数が少ない講師ID
            # min_instructor_id = get_min_num_instructor_id()
            min_instructor_id = 1

            # メッセージ情報からユーザー名(ニックネーム)を取得する。
            user_name = message.author.display_name

            # 講師IDが割り当てられていない受講生情報を取得し、更新するにあたり必要な情報(レコードID)を取得する。
            student_info = get_update_student_info(user_name)

            # 既存で
            if student_info:
                record_id = int(student_info["$id"]["value"])
                print(f"record_id: {record_id}")

                # 対象IDを更新する。
                kintone.update_from_yoom(record_id, min_instructor_id)

            else:
                error_message = f"講師ID割り当て時にエラーが発生しました。 "
                logger.error(error_message)
                await message.channel.send(error_message)

    except:
        error_message = f"講師ID割り当て時にエラーが発生しました。 "
        logger.error(error_message)
        # await message.channel.send(error_message)


def get_update_student_info(user_name: str) -> str:

    logger_ = Logger()
    logger = logger_.get()

    # Kintoneクラスのインスタンスを初期化する。
    kintone = Kintone()

    # 検索情報を定義する。(検索対象: 講師IDが割り振られていない、指定した名前のレコード一覧をレコードID昇順で取得する。)
    query_info = {
        "column": [
            {
                "column_name": "名前",
                "value": user_name,
                "condition": "="
            },
            {
                "column_name": "講師ID",
                "value": "",
                "condition": "="  # 完全一致
            }
        ],
        "order": [
            {
                "column_name": "$id",
                "value": "asc"  # 昇順
            },
        ]
    }

    # 取得するカラムを指定する。
    fields = []

    # 検索条件に合致するデータ一覧を取得する。
    select_infos = kintone.select_(KINTONE_APP_ID_CURRICURUM_UPDATE_T, KINTONE_API_TOKEN_PROGRESS_UPDATE_T, query_info, fields)
    logger.info(f"select_infos: {select_infos}")
    print(f"select_infos: {select_infos}")

    # 一番登録が早かった受講生を対象にする。
    select_info = select_infos[0].copy()
    logger.info(f"select_info: {select_info}")
    print(f"select_info: {select_info}")

    # 取得結果を返す。
    return select_info


def get_min_num_instructor_id():

    logger_ = Logger()
    logger = logger_.get()

    # 戻り値を初期化する。
    instructor_id_counts = []

    # Kintone「進捗管理T」「講師M」をすべて抽出する。
    kintone = Kintone()
    student_infos = kintone.select_(KINTONE_APP_ID_CURRICURUM_UPDATE_T, fields=["講師ID"])
    instructor_infos = kintone.select_(KINTONE_APP_ID_INSTRUCTOR_M, fields=["$id", "講師ID"])

    # 取得結果から講師IDを抽出し、値のみを格納していく。
    for student_info in student_infos:
        instructor_id_counts.append(student_info["講師ID"]["value"])

    # 格納した値の要素をカウントし、その中で最も少ない講師IDを取得する。(最小値となる講師IDが複数存在する場合、最も検索結果が最後尾の講師IDとなる)
    counts = dict(Counter(instructor_id_counts))
    logger.info(f"counts: {counts}")
    print(f"counts: {counts}")

    instructor_num_info = {}

    for instructor_info in instructor_infos:
        if instructor_info["講師ID"]["value"] in counts.keys():
            instructor_num_info[instructor_info["講師ID"]["value"]] = counts[instructor_info["講師ID"]["value"]]
        else:
            instructor_num_info[instructor_info["講師ID"]["value"]] = 0
    logger.info(f"instructor_num_info: {instructor_num_info}")
    print(f"instructor_num_info: {instructor_num_info}")

    # min_instructor_id_num = min(counts.values())
    # min_instructor_id = [instructor_id for instructor_id, instructor_num in counts.items() if instructor_num == min_instructor_id_num]
    min_instructor_id_num = min(instructor_num_info.values())
    min_instructor_id = [instructor_id for instructor_id, instructor_num in instructor_num_info.items() if instructor_num == min_instructor_id_num]

    if len(min_instructor_id) > 1:
        min_instructor_id = min(min_instructor_id)
    min_instructor_id = int(min_instructor_id[0])

    logger.info(f"min_instructor_id: {min_instructor_id}")
    print(f"min_instructor_id: {min_instructor_id}")

    # 講師IDを返す。
    return min_instructor_id
