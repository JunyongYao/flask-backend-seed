import logging


class Permission(object):
    @classmethod
    def validate(cls, user_id):
        # Override when subclassing to add additional checks
        pass


class AlwaysPass(Permission):
    @classmethod
    def validate(cls, user_id):
        logging.info("Pass!")
        return True


class AlwaysFail(Permission):
    @classmethod
    def validate(cls, user_id):
        logging.info("Fail!")
        return False
