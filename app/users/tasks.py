# from app.users.models import User
# from app.utils.helpers import send_sms
# from FARMS.celery_app import app
#
#
# @app.task(name="send_otp", ignore_result=False)
# def send_otp(mobile_no: str, message: str):
#     resp = send_sms(numbers='91' + mobile_no, message=message)
#     return resp
