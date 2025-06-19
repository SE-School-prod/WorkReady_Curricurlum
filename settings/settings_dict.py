"""
@file settings_dict.py
@date 2025/02/28(金)
@author 藤原光基
@brief bot諸々設定
@bar 編集日時 編集者 編集内容
@bar 2025/02/28(金) 藤原光基 新規作成
"""


import os

settings_dict = {
    "GUILD": {
        "ID": 1338762943793201222,
        "BOT_ID": 1338760612985049098,
        "CHANNEL": {
            "BUY_TICKET": {
                "NAME": "チケット購入",
                "ID": 1338776458931339304
            },
            "INIT_SETTING": {
                "NAME": "初期設定",
                "ID": 1358294819386163241
            }
        }
    },
    "KINTONE": {
        "APP_INFOS": [
            {
                "APP_NAME": "生徒M",
                "APP_ID": int(os.environ["KINTONE_APP_ID_STUDENT_M"]),
                "TOKEN": os.environ["KINTONE_APP_TOKEN_STUDENT_M"]
            },
            {
                "APP_NAME": "進捗更新T",
                "APP_ID": int(os.environ["KINTONE_APP_ID_CURRICURUM_UPDATE_T"]),
                "TOKEN": os.environ["KINTONE_APP_TOKEN_CURRICURUM_UPDATE_T"]
            },
            {
                "APP_NAME": "講師M",
                "APP_ID": int(os.environ["KINTONE_APP_ID_INSTRUCTOR_M"]),
                "TOKEN": os.environ["KINTONE_APP_TOKEN_INSTRUCTOR_M"]
            },
            {
                "APP_NAME": "転職EM",
                "APP_ID": int(os.environ["KINTONE_APP_ID_TENSHOKU_EM"]),
                "TOKEN": os.environ["KINTONE_APP_TOKEN_TENSHOKU_EM"]
            }
        ]
    }
}