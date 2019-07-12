# Django API写法

### 1.准备工作：

#### 1.1 虚拟环境

命令： 

```
ptyhon -m venv 名称
```



#### 1.2 进入虚拟环境安装相关依赖包

​	pip install django==1.11.20

​	djangorestframework

​	django-redis

​	django-filter

### 2.创建项目

#### 2.1命令：

```
 django-admin startproject 名称
```



#### 2.2 修改配置文件settings.py

##### 常用配置如下:

##### 注册app和包

```
'rest_framework',
'django_filters',
'user.apps.UserConfig',	# 在创建app后添加
```



```
# 语言时区
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_TZ = False
```
##### 增加Redis缓存
```
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": "mysecret"
            "SOCKET_CONNECT_TIMEOUT": 5,  # 连接超时时间
            "SOCKET_TIMEOUT": 5,  # 获取数据超时时间
        }
    }
}
```
##### 增加日志
```
LOGGING_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用所有的已经存在的日志配置
    # 定义日志格式
    'formatters': {
        'simple': {  # 简单格式
            'format': '%(asctime)s %(levelname)s: %(message)s',
            # 'format': '%(asctime)s %(levelname)s %(pathname)s %(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 将 asctime 格式化
        },
        'verbose': {  # 详细格式
            'format': '%(asctime)s %(levelname)s [%(process)d-%(threadName)s] %(module)s.%(funcName)s line %(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 将 asctime 格式化
        }
    },
    'filters': {
        'require_debug_true': {  # 是否支持DEBUG级别日志过滤
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 用来定义具体处理日志的方式，可以定义多种
    # console 就是打印到控制台方式
    # default 将所有日志写入文件
    # error 将日志级别为 ERROR 的日志写入文件
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 仅当 DEBUG = True 时才将日志打印到控制台
        },
        'default': {
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 按时间切割
            'filename': '{}/all.log'.format(LOGGING_DIR),  # 日志输出文件
            'when': 'D',  # 每天切割日志
            'backupCount': 30,  # 日志保留 30 天
            'formatter': 'verbose',  # 日志格式
            'level': 'DEBUG',  # 日志级别
        },
        # file 处理器和 default 处理器 二选一即可
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',  # 按文件大小切割
            'filename': '{}/all.log'.format(LOGGING_DIR),  # 日志输出文件
            'maxBytes': 1024 * 1024 * 5,  # 5m 文件大小
            'backupCount': 10,  # 日志保留 10 个
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        # 记录日志级别为 ERROR 的信息
        'error': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '{}/error.log'.format(LOGGING_DIR),  # 日志输出文件
            'when': 'W0',  # 每周一切割日志
            'backupCount': 4,  # 日志保留 4 周
            'formatter': 'verbose',
            'level': 'ERROR'
        }
    },
    # 用来配置使用那种handlers来处理日志
    'loggers': {
        'django': {
            'handlers': ['console', 'default'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
        },
        'django.request': {
            'handlers': ['console', 'default'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': False,  # 是否向上传递日志，django.reqeust 会将日志传递到 django，若为 True，则打印两次
        },
        'django.db.backends': {
            'handlers': ['default'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': False,
        },
        'axf': {
            # '': {  # 代表 root  logger， logging.getLogger()
            'handlers': ['console', 'default', 'error'],
            'propagate': True,
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    }
}
```
##### 自定义DRF exceptions

 可在与manage.py同级目录中创建一个

```
common文件夹，增加exceptions.py文件

from rest_framework.exceptions import APIException


class MyAPIException(APIException):
    def __init__(self, detail):
        self.detail = detail
```
##### 自定义DRF renderer

在common文件夹下创建renderer.py文件

```
from rest_framework.renderers import JSONRenderer


class MyJsonRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
            {
                "code": 200,
                "msg": "请求成功",
                "data": data
            }
        """
        code = data.pop('code', 200)
        msg = data.pop('msg', '请求成功')
        result = data.pop('data', data)

        renderer_context['response'].status_code = 200

        output = {
            'code': code,
            'msg': msg,
            'data': result
        }

        return super().render(output, accepted_media_type=None, renderer_context=None)
```

##### DRF/Django-Filter相关配置:settings.py

```
INSTALLED_APPS = [
  	...
    'rest_framework',
    'django_filters',
  	...
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'common.renderers.MyJsonRenderer',
    ),
}
```

### 3.新建app

可以用快速创建命令:

```
python manage.py startapp 名称
```

#### 1.models.py

models中是数据库模型。

```python
# 补充，在models中自定义token的写法
import binascii
import os
from django.core.cache import cache

# 在class中写，因为需要用到self.id
def create_token(self):
	token = binascii.hexlify(os.urandom(20)).decode()
	cache.set(token, self.id, timeout=60*60*48)
	return token
```



#### 2.serializers.py

serializers.py文件作用是模型序列化器定义,连接了数据模型，与forms.py表单验证文件很相似，可以自定义验证规则

##### 示例代码：

```python
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password

from user.models import AXFUser
from common.exceptions import MyAPIException


class UserRegisterSerializer(serializers.Serializer):
    u_username = serializers.CharField(required=True,min_length=4,max_length=10,error_messages={
        'required': '用户名必填',
        'min_length': '用户名最少4个字符',
        'max_length': '用户名最多10个字符',
        'blank': '用户名不能为空',
    })

    u_password = serializers.CharField(required=True,min_length=4,max_length=10,error_messages={
        'required': '密码必填',
        'min_length': '密码最少4个字符',
        'max_length': '密码最多10个字符',
        'blank': '密码不能为空',
    })

    u_password2 = serializers.CharField(required=True,min_length=4,max_length=10,error_messages={
        'required': '密码必填',
        'min_length': '密码最少4个字符',
        'max_length': '密码最多10个字符',
        'blank': '密码不能为空',
    })

    u_email = serializers.EmailField(required=True,min_length=4,max_length=20,error_messages={
        'required': '邮箱必填',
        'blank': '邮箱不能为空',
    })

    def validate(self, attrs):
        u_username = attrs.get('u_username')
        u_password = attrs.get('u_password')
        u_password2 = attrs.get('u_password2')
        u_email = attrs.get('u_email')

        if u_username in ['admin']:
            raise MyAPIException({'code':1002, 'msg':'用户名非法'})

        if u_password != u_password2:
            # raise serializers.ValidationError("两次输入密码不一致!")
            raise MyAPIException({'code':1004, 'msg':"两次输入密码不一致"})

        if AXFUser.objects.filter(u_username=u_username).exists():
            raise MyAPIException({'code':1001, 'msg':"用户名已存在"})

        if AXFUser.objects.filter(u_email=u_email).exists():
            raise MyAPIException({'code':1003, 'msg':"邮箱已存在"})

        return attrs

    def create(self, validated_data):
        u_username = validated_data['u_username']
        u_password = validated_data['u_password']
        u_email = validated_data['u_email']
        hashed_password = make_password(u_password)

        return AXFUser.objects.create(u_username=u_username, u_password=hashed_password, u_email=u_email)

```

##### 分析：

- 类继承serializers.Serializer类
- 字段名依据前端的name属性值来定
- error_messages={key,value}可以修改系统检测出的验证信息
- 重写validate函数,可以新增验证规则；
- 传入的attrs参数可以看做request.POST的封装，即可通过.get['key']的形式获取到对应的值,validate函数运行完毕后attrs又会return出去
- 系统自带的serializers.ValidationError()达不到理想的输出格式，所以这里导入了自定义异常
- 重写create函数，传入的validated_data是被验证过的数据，可通过validated_data['key']的形式获取。
- 在函数结束时会return出创建的数据对象,在return之前可以做一些个性化操作，如把密码加密等。

#### 3.urls.py

在完成了模型和序列化器类的创建后，可以将路由配置添加到 urls.py文件中了。建议每个模块（app）中建一个urls.py文件，其中定义详细路由信息，然后在主文件夹（即一开始创建项目时自带的文件夹）下的urls.py文件中用include的方式添加到路由中

```python
# app的urls.py
from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^auth/register/$', views.register),
    url(r'^auth/login/$', views.login),
]
```



```python
# 主文件的urls.py
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('user.urls')),
]
```



#### 4.views.py

views.py文件作用就是实现具体业务代码的地方

##### 示例代码:

```python
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import AXFUser
from user.serializers import UserRegisterSerializer, UserLoginSerializer

logger = logging.getLogger('axf')

@api_view(['POST'])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        logger.info('new user reigster success, uid:{}'.format(user.id))
        return Response(data={'code':200, 'msg':'注册成功', 'data':{'user_id':user.id}})
    else:
        return Response(data={'code':1007, 'msg':'验证未通过', 'data': serializer.errors})

@api_view(['POST'])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        u_username = serializer.validated_data['u_username']
        user = AXFUser.objects.get(u_username=u_username)
        logger.info('user login success, uid:{}'.format(user.id))
        token = user.create_token()
        return Response(data={'code': 200, 'msg': '登录成功', 'data':{'token':token}})
    else:
        print(serializer.errors)
        return Response(data={'code': 1007, 'msg': '验证未通过', 'data':serializer.errors})

```

#####  分析：

- 函数名称和urls.py中定义的路由名相同（匹配）
- 导入api_view()装饰器，参数中的['POST']为可接受的请求方式
- 在函数体里，需先初始化一个需要的序列器对象serializer，配置（data=request.data),后续的数据操作都通过序列化器完成，其封装了许多操作。
- 验证字段需要调用一下is_valid()方法.
- 序列化器自带有创建数据对象的save()方法。
- 响应并返回数据，return Response(data={})的格式以具体情况而定