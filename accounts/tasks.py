import logging
from celery import shared_task

from django.template.loader import render_to_string

from car.models import Car, Part, File

from .utils import send_email

from config.celery import CustomTask

logger = logging.getLogger('elastic_logger')


class BaseTaskWithRetry(CustomTask):
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 5}
    retry_backoff = True
    retry_jitter = False
    task_acks_late = True
    task_time_limit = 60


@shared_task(base=BaseTaskWithRetry)
def send_mail(user_email, file_id_list, car_id, part_id, unique_id):
    car = Car.objects.get(id=car_id)
    part = Part.objects.get(id=part_id)
    files = File.objects.filter(id__in=file_id_list)

    template_path = "email_templates/car_info.html",

    context = {"car": car, "part": part, "files": files}

    email_body = render_to_string(template_path, context)
    email_data = {"email_body": email_body, "to_email": [user_email],
                  "email_subject": "car information", "content_subtype": "html"}
    send_email(email_data)





