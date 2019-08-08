import os

from common import keys

from swiper import settings
from lib.qiniu import upload_to_qiniu
from worker import celery_app


@celery_app.task
def handler_upload_file(avatar, uid):
    filename = keys.AVATAR_KEY % uid
    filepath = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, filename)
    with open(filepath, mode='wb+') as fp:
        for chunk in avatar.chunks():
            fp.write(chunk)
    upload_to_qiniu(filepath, uid)


