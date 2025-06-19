"""
@file mail.py
@date 2025/02/28(金)
@author 藤原光基
@brief メール送信機能
@bar 編集日時 編集者 編集内容
@bar 2025/02/28(金) 藤原光基 新規作成
"""

import smtplib

from email.mime.text import MIMEText
import email.utils


class Mail:

    def __init__(self):
        self._smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        self._smtp_obj.starttls()
        self._smtp_obj.login('workreadyschool@gmail.com', 'euyhubgultpeynqz')

        self._source_address = 'workreadyschool@gmail.com'

    def __del__(self):
        self._smtp_obj.close()

    def send_assigin_mail_to_mentor(self, mentor_info, student_info):
        subject = '【お知らせ】受講生割り当てのお知らせ'
        content = mentor_info["name"] + "様\n\n"\
            'いつもお世話になっております。\n'\
            'WorkReady運営です。\n\n'\
            'この度' + mentor_info["name"] + "様が下記受講生のご担当となりましたことをご連絡いたします。\n\n"\
            "・受講生氏名: " + student_info["name"] +"\n"\
            "・コース: " + student_info["course"] + "\n"\
            "・卒業予定日: " + student_info["graduate_date"] + "\n\n"\
            "つきましては「面談日程調整」チャンネルにて上記受講生と初回面談の日程調整をお願いいたします。\n"\
            "以上、よろしくお願いいたします。\n\n"\
            "WorkReady運営"

        self.send_mail(subject, content, mentor_info["mail"])

    def send_assigin_mail_to_mentor(self, mentor_info, student_info):
        subject = '【お知らせ】相談会申し込みのお知らせ'
        content = mentor_info["name"] + "様\n\n"\
            'いつもお世話になっております。\n'\
            'WorkReady運営です。\n\n'\
            'この度' + mentor_info["name"] + "様が相談会をご予約されましたことをご連絡いたします。\n\n"\
            "・受講生氏名: " + student_info["name"] +"\n"\
            "・コース: " + student_info["course"] + "\n"\
            "・卒業予定日: " + student_info["graduate_date"] + "\n\n"\
            "つきましては「面談日程調整」チャンネルにて上記受講生と初回面談の日程調整をお願いいたします。\n"\
            "以上、よろしくお願いいたします。\n\n"\
            "WorkReady運営"

        self.send_mail(subject, content, mentor_info["mail"])

    def send_mail(self, subject, content, to):
        message = MIMEText(content)
        message['Subject'] = subject
        message['From'] = email.utils.formataddr(
            ('Work Ready運営', self._source_address))
        message['To'] = to
        message['Bcc'] = 'workreadyschool@gmail.com'

        self._smtp_obj.send_message(message)
