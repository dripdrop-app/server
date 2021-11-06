import datetime


def convert_db_response(response):
    return {
        key: value.__str__() if isinstance(value, datetime.datetime) else value
        for key, value in response.items()
    }
