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
KINTONE_APP_ID_PROGRESS_UPDATE_T = int(os.environ["KINTONE_APP_ID_PROGRESS_UPDATE_T"])
KINTONE_API_TOKEN_PROGRESS_UPDATE_T = os.environ["KINTONE_API_TOKEN_PROGRESS_UPDATE_T"]
YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID = os.environ["YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID"]


class Kintone:

    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(Kintone, cls).__new__(cls)
            cls._url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"

        return cls._instance

    def select(self, app_id, user_id=None, fields=None, query_info=None):
        params = {
            "app": app_id,
            "totalCount": True
        }

        if user_id is not None:
            query = f"生徒DiscordID = {user_id}"
            params["query"] = query

        if fields is not None:
            params["fields"] = fields

        if query_info is not None:
            add_query = " "

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

    def create(self, app_id, create_info):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
            "Content-Type": "application/json; charset=utf-8"
        }

        create_data = self._exchange_update_info_format(create_info)

        data = {
            "app": app_id,
            "record": create_data
        }

        response = requests.post(url, headers=headers, json=data)

        return response

    def update(self, app_id, user_id, update_info):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/record.json"  # 1件更新時
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
            "Content-Type": "application/json; charset=utf-8"
        }

        id = int(self.select(user_id, fields=["$id"])[0]["$id"]["value"])
        print(f"id: {id}")

        update_data = {}
        for key, value in update_info.items():
            update_data[key] = {"value": value}

        data = {
            "app": app_id,
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
    def updates(self, app_id, update_infos):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"  # 複数件更新時
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
            "Content-Type": "application/json; charset=utf-8"
        }

        for update_info in update_infos:
            for key, value in update_info["update_info"].items():
                update_info["update_info"][key] = {"value": value}

        data = {
            "app": app_id,
            "record": update_infos
        }

        response = requests.put(url, headers=headers, json=data)

        return response

    def update_from_yoom(self, record_id, updated_master_id):
        url = YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID
        payload = {
            "$id": record_id,
            "講師ID": updated_master_id
        }
        response = requests.post(url, json=payload)

        try:
            response = response.json()
            print(f"update instructor_id response: {response}")
        except:
            print(f"update instructor_id status_code: {response.status_code}, error: {response.text}")

    def _check_table_info(self, app_id):
        url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/app/form/fields.json"
        params = {
            "app": app_id
        }
        headers = {
            "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
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
            "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
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
