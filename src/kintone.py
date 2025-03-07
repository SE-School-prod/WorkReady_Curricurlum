"""
@file kintone.py
@date 2025/02/28(金)
@author 藤原光基
@brief Kintoneマネージャー
@bar 編集日時 編集者 編集内容
@bar 2025/02/28(金) 藤原光基 新規作成
"""

import os
import requests
import urllib.parse
import datetime


KINTONE_SUBDOMAIN = os.environ["KINTONE_SUBDOMAIN"]
KINTONE_APP_ID = int(os.environ["KINTONE_APP_ID"])
KINTONE_API_TOKEN = os.environ["KINTONE_API_TOKEN"]


class Kintone:

    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(Kintone, cls).__new__(cls)
            cls._url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"
            cls._headers = {
                "X-Cybozu-API-Token": KINTONE_API_TOKEN,
                "Content-Type": "application/json; charset=utf-8"
            }

        return cls._instance

    def select(self, user_id=None, fields=None):
        # url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"
        # headers = {
        #     "X-Cybozu-API-Token": KINTONE_API_TOKEN,
        #     "Content-Type": "application/json; charset=utf-8"
        # }
        params = {
            "app": KINTONE_APP_ID,
            "totalCount": True
        }

        if user_id is not None:
            query = f"生徒DiscordID = {user_id}"
            params["query"] = query

        if fields is not None:
            params["fields"] = fields

        print(f"params: {params}")

        response = requests.get(self._url, headers=self._headers, json=params)
        # response = requests.get(url, headers=headers, json=params)

        if 200 <= response.status_code < 300:
            response = response.json()["records"]

        else:
            response = {
                "status_code": response.status_code,
                "message": response.text
            }

        return response

    def create(self, create_info):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN,
            "Content-Type": "application/json; charset=utf-8"
        }

        create_data = self._exchange_update_info_format(create_info)

        data = {
            "app": KINTONE_APP_ID,
            "record": create_data
        }

        response = requests.post(url, headers=headers, json=data)

        return response

    def update(self, user_id, update_info):
        # url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"  # 複数件更新時
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/record.json"  # 1件更新時
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN,
            "Content-Type": "application/json; charset=utf-8"
        }

        id = int(self.select(user_id, fields=["$id"])[0]["$id"]["value"])

        update_data = {}
        for key, value in update_info.items():
            update_data[key] = {"value": value}

        data = {
            "app": KINTONE_APP_ID,
            "id": id,
            "record": update_data
        }
        print(f"data: {data}")

        response = requests.put(url, headers=headers, json=data)

        return response

    """
    update_infos=[
        {"user_id": user_id1, "update_info": {"column1": value1, "column2": value2}},
        {"user_id": user_id2, "update_info": {"column3": value3, "column4": value4}},...
    ]
    """
    def updates(self, update_infos):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"  # 複数件更新時
        # url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/record.json"  # 1件更新時
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN,
            "Content-Type": "application/json; charset=utf-8"
        }

        for update_info in update_infos:
            for key, value in update_info["update_info"].items():
                update_info["update_info"][key] = {"value": value}

        data = {
            "app": KINTONE_APP_ID,
            "record": update_infos
        }

        response = requests.put(url, headers=headers, json=data)

        return response

    def _check_table_info(self):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/app/form/fields.json"
        params = {
            "app": KINTONE_APP_ID
        }
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN,
            "Content-Type": "application/json; charset=utf-8"
        }

        response = requests.get(url, headers=headers, params=params)

        return response

    def _check_apps_infos(self):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/apps.json"
        params = {
            "offset": 0,
            "limit": 100
        }
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN,
            "Content-Type": "application/json; charset=utf-8"
        }

        response = requests.get(url, headers=headers, params=params)

        return response

    def _exchange_update_info_format(self, update_info):
        result = {}
        for key, value in update_info.items():
            result[key] = {"value": value}
        return result

    def _get_now_tz_last_progress_updated(self):
        now = datetime.datetime.now()
        now_tz = now.strftime('%Y/%m/%d')
        return now_tz

    def _get_now_last_updated(self):
        now = datetime.datetime.now()
        now_tz = now.strftime('%Y-%m-%d %H:%M')
        return now_tz

    def _get_now_admission_date(self):
        now = datetime.datetime.now()
        now_tz = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        return now_tz
