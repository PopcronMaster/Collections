# 使用多 settings 文件

为什么要使用多 settings 文件？

将各个环境中差异化的配置分开维护。(生产环境和开发环境的数据库配置)

1、在项目目录下创建 settings 包，并创建 settings 的基础配置 base.py

base.py 内容来自于原有的 settings.py，由于目录结构改变，所以需要修改 BASE_DIR 的值

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 修改为
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

```shell
mysite/
 |-- mysite/
 |    |-- __init__.py
 |    |-- settings/         
 |    |    |-- __init__.py  
 |    |    +-- base.py      # 基础配置
 |    |-- urls.py
 |    +-- wsgi.py
 +-- manage.py
```

2、为每个环境创建响应的 settings 文件

```shell
mysite/
 |-- mysite/
 |    |-- __init__.py
 |    |-- settings/
 |    |    |-- __init__.py
 |    |    |-- base.py          # 基础配置
 |    |    |-- development.py   # 开发环境配置
 |    |    |-- production.py    # 生产环境配置
 |    |    +-- test.py          # 测试环境配置
 |    |-- urls.py
 |    +-- wsgi.py
 +-- manage.py
```

base.py

```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
```

production.py

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['mysite.com', ]

SECRET_KEY = 'hcd_ox&t*l$ts5*8e125zm#pex83+rdo0198xx*_6jis*t@c4a'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'myapp',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USERNAME': 'root',
        'PASSWORD': 'password',
    }
}
```

development.py

```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = []

SECRET_KEY = 'develoment'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

3、使用

```shell
python manage.py runserver --settings=mysite.settings.development
```

```shell
python manage.py migrate --settings=mysite.settings.production
```

4、修改 manage.py 的 DJANGO_SETTINGS_MODULE 默认指向 mysite.settings.development，在开发时启动服务器不需要使用 —settings 选项

```python
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)

```

