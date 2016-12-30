# -*- coding: utf-8 -*-
import hashlib
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from app import db
from app.model import DBEnum


class UserTypeEnum(DBEnum):
    standard = "standard"
    disabled = "disabled"


class UserInfo(db.Model):
    __tablename__ = "user_info"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(30), nullable=False, index=True)
    sha_pwd = db.Column(db.String(56), nullable=False)

    nickname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Integer, default=0)
    city = db.Column(db.String(20))

    type = db.Column(db.Enum(*UserTypeEnum.get_enum_labels()), default=UserTypeEnum.standard.value)

    def __repr__(self):
        return '<UserInfo {}>'.format(self.nickname)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return None

        cur_user_id = data["id"]
        cur_user = UserInfo.query.get(cur_user_id)

        return cur_user

    @staticmethod
    def get_user(user_id):
        if user_id is None:
            return None
        return UserInfo.query.get(user_id)

    @staticmethod
    def generate_sha_pwd(key_data):
        return hashlib.sha224(bytes(key_data, "utf-8")).hexdigest()

    def to_json(self):
        json_user = {
            "name": self.nickname,
            "gender": self.gender,
            "city": self.city or "NA",
        }

        return json_user
