### Django-RestFramework，API写法记录

#### 1.准备工作

进入事先创建的虚拟环境:

```
workon djangoenv
```

创建django项目

```
django-admin startproject douban
```

接着创建模块

```
python manage.py startapp movieAPI
```

接着将新创建的模块和rest_framework库加入到主目录的settings.py文件中的`INSTALLED_APPS`配置中，之后每创建新的模块都要加入到这里

```
	'rest_framework',
    'movieAPI.apps.MovieapiConfig',
```

然后，新建两个urls.py文件和serializers.py空文件放着，先写好数据库模型文件models.py,

```python
# 示例代码
from django.db import models

class HotMovie(models.Model):
    title = models.CharField(max_length=200, unique=True)
    img = models.CharField(max_length=200)
    rate = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    releases = models.CharField(max_length=200)
    descs = models.TextField()
    short = models.CharField(max_length=200)
    class Meta:
        db_table = 'hot_movie'
```

完成后，就可以写对应的serializes.py文件了，这个文件的作用就是将模型里的字段做序列化和将接收的数据进行反序列化，从而统一了models.py文件和用户提交的数据的格式

```python
# 示例代码
from rest_framework import serializers

from .models import HotMovie

class HotMovieSerializer(serializers.ModelSerializer):

    class Meta:
        model = HotMovie
        fields = "__all__"
```

至此，准备工作算是完成了，接下来就是在views.py中的API不同写法了，无论什么方式实现，上面基本的准备工作都是相同的。



#### 2.API写法

##### 2.1继承 View类

重写View类的get//post/put/putch/delete等方法，这个方法可以不写serializes.py文件，但需要手动实现数据的格式化

```python
from django.http import JsonResponse
from django.views import View


class MovieListView(View):
    def get(self, request):
        return JsonResponse({'data': '获取所有电影'}, status=200)

    def post(self, request):
        return JsonResponse({'data': '保存电影'}, status=200)

class MovieDetailView(View):
    def get(self, request, mid):
        return JsonResponse({'data': f'返回电影{mid}'}, status=200)
    
    def put(self, request, mid):
        return JsonResponse({'data': f'更新 post: {mid}'}, status=200)

    def patch(self, request, mid):
        return JsonResponse({'data': f'局部更新 post: {mid}'}, status=200)

    def delete(self, request, mid):
        return JsonResponse({'data': f'删除 post: {mid}'}, status=204)

```

我没有写具体的业务代码，这里只为做测试返回了不同的返回提示。

重写完对应的方法后就可以写本模块的urls.py文件了

```python
from django.conf.urls import url

from movieAPI.views import MovieListView, MovieDetailView

urlpatterns = [
    url(r'^movies/$', MovieListView.as_view(), name='movie-list')
    url(r'^movies/(?P<mid>)$', MovieListView.as_view(), name='movie-detail')
]
```

写好本模块的urls.py程序还起不来，因为还需要将本模块的urls配置到项目的主urls.py中

```python
from django.conf.urls import url, include

urlpatterns = [
    url(r'^api/', include('api.urls')),		# 这里的include中api是模块名，前面（第一个）api是自定义的名字
]
```

用PostMan测试，可以通过，服务器响应如下：

![1561550151262](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\1561550151262.png)

通过这种写法我们可以实现基本的rest framework思想，即每个请求方式可以对应一种操作，路由地址可以重用，内部会根据请求方式分发到对应的函数，如果有业务代码，会做完响应的业务在返回数据。



##### 2.2 APIView写法

接下来会加入一些业务代码，然后使用APIView来写，APIView是对View类的一个升级，加入了serializes.py的功能，可以自动序列化数据模型的数据和用户数据 ，减少了因为格式转化的重复代码

```python
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HotMovie
from .serializers import HotMovieSerializer

class MovieListView(APIView):
    def get(self, request):
        movies = HotMovie.objects.all()
        serializer = HotMovieSerializer(instance=movies, many=True)
        # 如果 instance 为集合，则需要 many 为 True
        # Serializer 会将 instance 序列化后，放到 serializer.data 属性中
        return Response(data=serializer.data, status=200)
    
    def post(self, request):
        # 使用 drf 的 request 对象，自动反序列化请求数据
        data = request.data
        serializer = HotMovieSerializer(data=data)
        if serializer.is_valid():
            serializer.save()   # 序列化器保存到数据库
            return Response(data=serializer.data, status=201)
        else:
            return Response(data=serializer.errors, status=400)

class MovieDetailView(APIView):
    # 因为这里是针对一部电影做修改和查询，先重写了对象的获取方法get_object()
    def get_object(mid):
        try:
            return HotMovie.objects.get(pk=mid)     # 返回找到的电影
        except HotMovie.DoesNotExist:
            return Response(data={'message': '找不到对象'})
    
    def get(self, request, mid):
        movie = self.get_object(mid)
        serializer = HotMovieSerializer(instance=movie)
        return Response(data=serializer.data)

    def put(self, request, mid):
        movie = self.get_object(mid)
        data = request.data     # 取出用户传过来的修改后的数据

        serializer = HotMovieSerializer(instance=movie, data=data)  # 用序列化器修改电影需要修改的部分

        if serializer.is_valid():   # 验证修改后对象是否符合序列化规则，合格就保存到数据库
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=400)

    def patch(self, request, mid):
        # 这里调用了继承时默认的put方法，默认就是全局更新
        return self.put(request, mid)

    def delete(self, request, mid):
        movie = self.get_object(mid)
        movie.delete()  # 得到了指定电影后删除即可，与序列化器无关
        return Response(data={'message': '对象已被删除'})
```

模块的urls.py中URL配置还是和**2.1**相同，测试结果如下：

![1561554927029](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\1561554927029.png)



这种写法加入了序列化器，简化了数据格式化的操作，其次还有一种装饰器的写法，优点是可以自定义路由名，简易，可以使用序列化器，缺点是如果请求方式多，就需要手动实现判断分发路由的工作

```python
# 示例代码
from rest_framework.decorators import api_view

from .models import HotMovie
from .serializers import HotMovieSerializer

@api_view(['GET', 'POST'])
def movie_list(request):
	if request.method == 'GET':
		movies = HotMovie.objects.all()
        serializer = HotMovieSerializer(isinstance=movies, many=True)
        # 如果 instance 为集合，则需要 many 为 True
        # Serializer 会将 instance 序列化后，放到 serializer.data 属性中
        return Response(data=serializer.data, status=200)
    elif request.method == 'POST':
    	# 使用 drf 的 request 对象，自动反序列化请求数据
        data = request.data
        serializer = HotMovieSerializer(data=data)
        if serializer.is_valid():
            serializer.save()   # 序列化器保存到数据库
            return Response(data=serializer.data, status=201)
        else:
            return Response(data=serializer.errors, status=400)
```

movie_detail的写法类似

##### 2.3 GenericAPIView + mixins 特殊类的写法

可以看到，**2.2**中每次对数据操作依然是要把将数据对象找到，放入序列化器，然后再放回去或返回出去，那么这个能简化吗？当然可以，GenericAPIView继承了APIView,并加入了queryset、serializer_class、lookup_field、filter_backends、pagination_class等属性，get_queryset()、get_object()、get_serializer()、filter_queryset()等方法，同时再配合mixns库，继承它的特殊类，它们已经帮我们写好了基本的响应方法，

```python
from rest_framework import generics, mixins

from .models import HotMovie
from .serializers import HotMovieSerializer

class MovieListView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = HotMovie.objects.all()
    serializer_class = HotMovieSerializer
    
    '''
    # 现在只需重写出对应的请求方式接收函数，然后调用父类(mixins的特殊类)的实现方法，
    # 如果有其它业务逻辑代码也可以重写对应实现方法加入自己的代码就能完成定制
    # get  -> list
    # post -> create, perform_create
    '''
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class MovieDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = HotMovie.objects.all()
    serializer_class = HotMovieSerializer

    '''
    # 同样，继承了相应的mixins的特殊类，就会有默认实现方法,
    # 我们只需要重写get/put/delete等方法时调用对应的实现方法就可以了
    # 这些请求会将传入的数据默认按pk(主键)得到对象，若修改需要重写get_object方法
    # 如果需要加入特定的业务逻辑，就重写对应的实现方法
    # get    -> retrieve
    # put    -> update,perform_update,partial_update
    # delete -> destroy,perform_destroy
    '''
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
```

结合代码里的注释，我们可以看到，在继承了mixins的特殊类后省了很多力气，不用再将数据对象放到序列化器了，系统会自动配置，若果没有特殊的业务代码，我们都不用写响应的代码了，直接调用父类的方法就可以完成响应了。

最后，模块的urls.py有点要注意，因为MovieDetailView是针对详细的一条数据的操作，系统默认是查找的关键字是pk(即主键)，那么对应urls.py处也要改为pk了

```python
from django.conf.urls import url

from movieAPI.views import MovieListView, MovieDetailView

urlpatterns = [
    url(r'^movies/$', MovieListView.as_view(), name='movie-list')
    url(r'^movies/(?P<pk>)$', MovieListView.as_view(), name='movie-detail')
]
```

如果还是想用自定义的字段名，那可以用到 lookup_field属性

```
lookup_field = 'title'
```

实现效果如下：

![2019-06-26_234615](E:\FS文件夹\2019-06-26_234615.png)

##### 2.4 GenericViewSet + mixins 特殊类结合开发

GenericViewSet继承了GenericAPIView的属性和方法，同时也补充了一些更加简化的操作和解决问题的方法和属性，首先看下简化代码的效果：

```python
from rest_framework import viewsets, mixins

from .models import HotMovie
from .serializers import HotMovieSerializer

class HotMovieViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = HotMovie.objects.all()
    serializer_class = HotMovieSerializer


class MovieViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = HotMovie.objects.all()
    serializer_class = HotMovieSerializer
```

以上这些代码就可以完成前面的操作，我们只需定义出 queryset 和 serializer_class 的属性值，系统就会自动帮我们完成请求方式的识别分发，然后调用mixinx的实现方法。

然后是路由定义有些区别，我们只需指定前缀对应的ViewSet，之后的路由分配就交给系统自己处理了

```python
from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from movieAPI import views

router = SimpleRouter()
router.register(r'hot_movies', views.HotMovieViewSet)
router.register(r'movie', views.MovieViewSet)

urlpatterns = [
    
] + router.urls
```

这里是我较常用的写法，当然也有更官方的写法，可以自己去了解。

然后我们再思考一些问题，当一个复杂的系统有很多的请求时，我们这几个现有的默认的请求方式够用吗？够用是够用，但当多个post请求对应着多种业务袭来时，系统又该怎么区分呢？系统默认的实现方式会好用吗？答案是否定的，这时候ViewSet 新增的属性和方法就应运而生了。

ViewSet支持 action 装饰器，从而可以实现自定义请求函数，这似乎又回到了写视图函数的时代，但不可忽略的是它也有了rest_framework的便利性

```python
# 示例代码
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HotMovie
from .serializers import HotMovieSerializer

class MovieViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = HotMovie.objects.all()
    serializer_class = HotMovieSerializer

    @action(methods=['GET'], detail=False)
    def get_movie_by_title(self, request, *args, **kwargs):
        title = request.query_params.get('title')   # 获取get请求的参数用request.query_params.get()
        movie = HotMovie.objects.filter(title=title)
        serializer = self.get_serializer(movie, many=True)  # 回到了传对象序列化的阶段
        return Response(serializer.data)
```

这里加入了一个get方式的action自定义路由函数，可以根据电影标题来查询电影，也可以用默认的pk(主键)的方式找到电影。

urls.py不用变，router 会自动生成对应路由，

```
# 默认请求方式
http://127.0.0.1:8000/api/movie/4/
# 响应
```

![1561598160375](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\1561598160375.png)

```
# 请求地址
http://127.0.0.1:8000/api/movie/get_movie_by_title/?title=千与千寻
# 响应
```

![1561598027736](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\1561598027736.png)



至此，基本的API写法都已经用过了，但django-restframework的功能还不仅仅如此，还有很多实用的属性、方法的功能没有具体体验，后续再补充。