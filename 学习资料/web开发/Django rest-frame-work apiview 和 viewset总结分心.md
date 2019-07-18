### Django rest-frame-work apiview 和 viewset总结分心

#### 官方文档：http://www.django-rest-framework.org/

#### 关系图谱：

![view](https://user-gold-cdn.xitu.io/2018/1/23/16121a5c9d4871ab?imageView2/0/w/1280/h/960/ignore-error/1)

#### 主要分类：

![mixins](https://user-gold-cdn.xitu.io/2018/1/23/16121a5c9cb4894e?imageView2/0/w/1280/h/960/ignore-error/1)

#### 1.django View

首先，使用django 自带的 view 获取一个课程列表：

```python
# drf是通过json的格式进行数据交互的，所以这里也返回json数据
import json
from django.views.generic.base import View
from django.core import serializers
from django.http import HttpResponse,JsonResponse
from .models import Course

class CourseListView(View):
    def get(self, request):
        """
        通过django的view实现课程列表页
        """
        courses = Course.objects.all()[:10]
        json_data = serializers.serialize('json', Courses)
        json_data = json.loads(json_data)
        return JsonResponse(json_data, safe=False)

```

#### 2.APIView

接下来，使用APIView来实现

```python
from rest_framework.views import APIView
from rest_framework.response import Response
# 这个serializers是在其他文件自定义的，这里对这个不进行过多介绍
from .serializers import CourseSerializer

class CourseListView(APIView):
    def get(self, request, format=None):
        """
        通过APIView实现课程列表页
        """
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

```

在这个APIView的例子中，调用了drf本身的serializer以及Response方法

APIView对Django本身的View进行了封装，虽然分析代码，两者看起来去别不是很大，但实际中APIView做了很多东西，它定义了很多属性和方法

```
# 这三个是常用的属性
    authentication_classes : 用户登录认证方式，session或者token等等
    permission_classes : 权限设置，是否需要登录等
    throttle_classes : 限速设置，对用户进行一定的访问次数限制等等。

```

#### 3.GenericAPIView

```python
from rest_framework import mixins
from rest_framework import generics
class CourseListView(mixins.ListModelMixin, generics.GenericAPIView):
	"""
 	课程列表页
 	"""
 	queryset = Course.objects.all()
 	serialize_class = CourseSerializer
 	def get(self, request, *args, **kwargs):
 	# list方法是存在于mixins中的，同理，create等等也是
 	# GenericAPIView没有这些方法！
 		return self.list(request, *args, **kwargs)

```

在这个例子中，继承了mixins中的ListModelMixin，在get( )方法中，调用了它的list()方法，list方法会返回queryset的json数据。GenericAPIView是对APIView再次封装，从而实现了强大功能：

- 加入queryset属性，可以直接设置这个属性，不必再将实例化的courses，再次传给seriliazer,系统会自动检测到。除此之外，可以重载get_queryset()，这样就不必设置'queryset=*'，这样就变得更加灵活，可以进行完全的自定义。

- 加入serializer_class属性与实现get_serializer_class()方法。两者的存在一个即可，通过这个，在返回时，不必去指定某个serilizer

- 设置过滤器模板：filter_backends

- 设置分页模板：pagination_class

- 加入 lookup_field="pk"，以及实现了get_object方法:这个用得场景不多，但十分重要。它们两者的关系同1，要么设置属性，要么重载方法。它们的功能在于获取某一个实例时，指定传进来的后缀是什么。
  举个例子，获取具体的某个课程，假设传进来的ulr为：http://127.0.0.1:8000/course/1/，系统会默认这个1指的是course的id。那么，现在面临一个问题，假设我定义了一个用户收藏的model，我想要知道我id为1的课程是否收藏了，我传进来的url为：http://127.0.0.1:8000/userfav/1/,系统会默认获取userfav的id=1的实例，这个逻辑明显是错的，我们需要获取course的id=1的收藏记录，所以我们就需要用到这个属性或者重载这个方法 lookup_field="course_id"。 
      在generics除了GenericAPIView还包括了其他几个View: CreateAPIView、ListAPIView、RetrieveAPIView、ListCreateAPIView···等等，其实他们都只是继承了相应一个或多个mixins和GenericAPIView，这样，有什么好处？我们看一下同样一个例子的代码：

  ```python
  class CourseListView(ListAPIView):
  	"""
   	课程列表页
   	"""
   	queryset = Course.objects.all()
   	serialize_class = CourseSerializer
  
  ```

  #### 4.GenericViewSet

  - GenericAPIView的不足之处

    既然GenericAPIView以及它相关的View已经完成了许许多多的功能，那么还要ViewSet干嘛！
     首先，我们思考一个问题，同样上面的例子，我们在功能上，要获取课程的列表，也要获取某个课程的具体信息。那么怎么实现，按照GenericAPIView，我们可以这样实现：

  ```python
  class CourseView(ListAPIView，RetrieveAPIView):
   	＃&emsp;只需要在上面的基础上，再继承RetrieveAPIView就ok了。
   	queryset = Course.objects.all()
   	serialize_class = CourseSerializer
   	
  ```

    但这样实现有一个问题，关于serialize_class，显然，当获取课程列表时，只需要传回去所有课程的简要信息，如课程名字，老师，封面等等，但当获取课程的具体信息，我们还要将他们的章节以及相关下载资料（很明显，章节是另外一个model，有一个外键指向course），这些信息会很多，在获取课程列表，将这些传回去显然是不理智的。那么，还需要再定义一个CourseDetailSerializer，在get /courses/的时候，使用CourseSerializer，在get /courses/id/的时候，使用CourseDetailSerializer。
     那么，问题来了，我们怎么获取到是哪个action方法？这个时候，viewset就出场了！

  - viewset的功能
       GenericViewSet继承了GenericAPIView，依然有get_queryset,get_serialize_class相关属性与方法，GenericViewSet重写了as_view方法，可以获取到HTTP的请求方法。 解决刚刚的问题：

  ```python
  from rest_framework import viewsets
  import...
  class CourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
   	queryset = Course.objects.all()
   	
  	def get_serializer_class(self):
  	# 重写get_serializer_class方法
  	    if self.action == 'list':
  	        return CourseSerializer
  	    return CourseDetailSerializer
  ```

  - http请求方法与mixins的方法进行绑定
       但GenericViewSet本身依然不存在list, create方法，需要我们与mixins一起混合使用，那么新问题来了？我们依然需要自己写get、post方法，然后再return list或者create等方法吗？当然不！重写as_view的方法为我们提供了绑定的功能，我们在设置url的时候：

  ```python
  # 进行绑定
  courses = CourseViewSet.as_view({
  	'get': 'list',
  	'post': 'create'
  })
  urlpatterns = [
  	...
  	# 常规加入url匹配项
  	url(r'courses/', CourseViewSet.as_view(), name='courses'),]
  ```

    这样，我们就将http请求方法与mixins方法进行了关联。那么还有更简洁的方法吗？很明显，当然有，这个时候，route就登场了！

  - route方法注册与绑定

  ```
  from rest_framework.routers import DefaultRouter
  router = DefaultRouter() # 只需要实现一次
  router.register(r'courses', CourseViewSet, base_name='courses')
  urlpatterns = [
  	...
  	# 只需要加入一次
  	url(r'^', include(router.urls)),]
  ```

    route中使用的一定要是ViewSet，用router.register的方法注册url不仅可以很好的管理url，不会导致url过多而混乱，而且还能实现http方法与mixins中的相关方法进行连接。
     在viewset中，还提供了两个以及与mixins绑定好的ViewSet，当然，这两个ViewSet完全可以自己实现：

  ```
  class ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
      # 满足只有GET方法请求的情景
      pass
      
  class ModelViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
      # 满足所有请求都有的情景
      pass
  复制代码
  ```

    到这里，ViewSet的强大功能就介绍完了，强烈建议在做drf的时候，使用ViewSet与mixins方法结合进行开发。