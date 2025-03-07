"""
@file logger.py
@date 2025/03/07(金)
@author 藤原光基
@brief ロガー
@bar 編集日時 編集者 編集内容
@bar 2025/03/07(金) 藤原光基 シングルトン化することでインスタンスを一つに姓ゲインするよう修正
"""


import os
import datetime

from logging import StreamHandler, FileHandler, Formatter, getLogger, ERROR, DEBUG
from settings.settings_dict import settings_dict


class DatetimeFormatter(Formatter):
    def formatTime(self, record, datefmt):
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S,%d"
        tz = datetime.timezone(datetime.timedelta(hours=9), 'JST')
        time = datetime.datetime.fromtimestamp(record.created, tz=tz)
        strftime = time.strftime(datefmt)
        return strftime


class Logger:

    _instance = None
    
    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

            logger = getLogger(__name__)
            logger.setLevel(ERROR)

            formatter = DatetimeFormatter(
                "%(asctime)s -  [%(levelname)-8s] - %(filename)s:%(lineno)s %(funcName)s %(message)s")

            # 画面出力用ハンドラ
            sh = StreamHandler()
            sh.setLevel(DEBUG)
            sh.setFormatter(formatter)

            # ファイル書き込みハンドラ
            fh = FileHandler(
                filename=cls._generate_log_file(cls), 
                encoding='utf-8'
            )
            fh.setLevel(DEBUG)
            fh.setFormatter(formatter)

            if not logger.hasHandlers():
                logger.addHandler(sh)
                logger.addHandler(fh)

            cls._instance.logger = logger

        return cls._instance

    def get(self):
        return self._instance.logger

    def _generate_log_file(self):
        now = datetime.datetime.today() + datetime.timedelta(hours=9)

        save_file_name = str(now)[:10].replace(
            '-', '') + '.log'  # YYYYMMDD.log

        # get save dir
        # save_dir = settings_dict["DIR"]["LOG_SAVE_DIR"]
        save_dir = 'notion_api_logs'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_dir_name = os.path.join(save_dir, save_file_name)

        return save_dir_name
