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

from settings.settings_dict import settings_dict


KINTONE_SUBDOMAIN = os.environ["KINTONE_SUBDOMAIN"]
YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID = os.environ["YOOM_WEBHOOK_URL_UPDATE_INSTRUCTOR_ID"]


class Kintone:

    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(Kintone, cls).__new__(cls)
            cls._url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"

        return cls._instance

    def select(self, app_id, user_id=None, fields=None, query_info=None):
        headers = {
            "X-Cybozu-API-Token": self._get_token_from_app_id(app_id),
            "Content-Type": "application/json; charset=utf-8"
        }
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

        response = requests.get(self._url, headers=headers, json=params)

        if 200 <= response.status_code < 300:
            response = response.json()["records"]

        else:
            response = {
                "status_code": response.status_code,
                "message": response.text
            }

        return response

    def select_(self, app_id, query_info=None, fields=None):
        params = {
            "app": app_id,
            "totalCount": True
        }
        headers = {
            "X-Cybozu-API-Token": self._get_token_from_app_id(app_id),
            "Content-Type": "application/json; charset=utf-8"
        }

        if fields is not None:
            params["fields"] = fields

        if query_info is not None:
            query = self._get_query(query_info)
            params["query"] = query

        print(f"params: {params}")

        response = requests.get(self._url, headers=headers, json=params)

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
            "X-Cybozu-API-Token": self._get_token_from_app_id(app_id),
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
            "X-Cybozu-API-Token": self._get_token_from_app_id(app_id),
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
            "X-Cybozu-API-Token": self._get_token_from_app_id(app_id),
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

    def _get_token_from_app_id(self, app_id):
        app_info = {}
        app_infos = settings_dict["KINTONE"]["APP_INFOS"]
        try:
            for info in app_infos:
                if info["APP_ID"] == app_id:
                    app_info = info["TOKEN"]
                    break
            return app_info

        except:
            print(f"アプリケーションIDに合致するトークンが見つかりませんでした: app_id: {app_id}")

    # def _check_table_info(self, app_id):
    #     url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/app/form/fields.json"
    #     params = {
    #         "app": app_id
    #     }
    #     headers = {
    #         "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
    #         "Content-Type": "application/json; charset=utf-8"
    #     }

    #     response = requests.get(url, headers=headers, params=params)

    #     return response

    # def _check_apps_infos(self):
    #     url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/apps.json"
    #     params = {
    #         "offset": 0,
    #         "limit": 100
    #     }
    #     headers = {
    #         "X-Cybozu-API-Token": KINTONE_API_TOKEN_PROGRESS_UPDATE_T,
    #         "Content-Type": "application/json; charset=utf-8"
    #     }

    #     response = requests.get(url, headers=headers, params=params)

    #     return response

    def _get_query(self, query_infos):
        query = ''
        for key, value in query_infos.items():
            if len(query) > 0:
                query += ' '

            if key == "column":
                query_column = ''
                for column_info in value:
                    if len(query_column) > 0:
                        query_column += ' and '
                    # query_column += f'{column_info["column_name"]} {column_info["condition"]} {column_info["value"]}'
                    query_column += f'{column_info["column_name"]} {column_info["condition"]} '
                    if isinstance(column_info["value"], int):
                        query_column += column_info["value"]
                    else:
                        # query_column += f'"{column_info['value']}"'
                        query_column += '"' + column_info['value'] + '"'
                query += query_column

            if key == "range":
                query_range = ''
                for range_info in value:
                    if len(query_range) > 0:
                        query_range += ' and '
                    # query_range += f'{range_info["column_name"]} {range_info["condition"]} {range_info["value"]}'
                    query_range += f'{range_info["column_name"]} {range_info["condition"]} '
                    if isinstance(range_info["value"], int):
                        query_column += range_info["value"]
                    else:
                        # query_column += f'"{range_info['value']}"'
                        query_column += '"' + range_info['value'] + '"'
                if len(query) > 0:
                    query += 'and '
                query += query_range

            if key == "order":
                query_order = ''
                for order_info in value:
                    if len(query_order) == 0:
                        query_order +='order by '
                    else:
                        query_order +=', '
                    query_order += f'{order_info["column_name"]} {order_info["value"]}'
                query += query_order
        return query

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
