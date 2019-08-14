### Tornado框架

##### 1.最小应用

```
# 导包
import tornado.web
import tornado.ioloop
from tornado.options import options, define, parse_command_line

# 视图函数控制器
class IndexHandler(tornado.web.RequestHandler):
	def fun(self):
		retrun

# 应用与路由定义
def make_app():
	return tornado.web.Application(handlers=[
        ('/index/, IndexHandler'),
        ('/req/', ReqHandler),
	]
	# 调试模式
	debug=True
	)

# 项目入口main
if __name__ == '__main__':
	# 解析命令行中的参数
	parse_command_line()
	# 调用make_app方法，返回一个Application对象
	app = make_app()
	# 监听端口 可在外面定义默认端口:define('port', default=8000, type=int)
	app.listen(options.port)
	# 启动一个IO事件循环，监听端口请求(启动tornado程序)
	tornado.ioloop.IOLoop.current().start()
```

##### 2.请求的内置参数

```
# 请求传值获取,get
self.get_argument(key)
self.get_query_argument(key)

# post、其它
self.get_argument(key)
self.get_body_argument(key)

self.request.cookies
self.request.path
self.request.files
self.request.method
self.get_cookie('token')
```

##### 3.响应

```
set_status
set_cookie
redirect：用于地址跳转
render：多用于模板页面返回
write:多用于数据返回
```

##### 4.路由定义高级匹配

```
('/day/(?<year>\d+)/\d+/\d+', IndexHandler)

def get(self, *args, **kwargs):  # 从kwargs中取值

普通的路由定义，则是从args中取值，且一一对应
```

##### 5.模板位置和静态文件路径指定

```
# 依然是在make_app方法中配置，这个方法就类似于Django的settings文件
template_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
    static_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
```

##### 6.连接数据库

```
# 安装sqlalchemy,并单独写一个settings文件连接数据库
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建连接
url = 'mysql + pymysql://root:@127.0.0.1:3306/test'
engine = create_engine(url)

# 创建session（事务增强版本)
SessionMaker = sessionmaker(bind=engine)
session = SessionMaker()

# 生成一个指定模型和数据库中的表的关联关系基类
Base = declarative_base(bind=engine)

# 在models.py文件中导入并调用 
def create_db():
	# 迁移模型，映射成表
	Base.metadata.create_all()
	
class Student(Base):
	id = Column(Integer, primary_key=True, autoincrease=True)
	__tablename__ = 'stu'
```

##### 7.数据操作

```
# 查询，与flask，Django对比
stus = session.query(Student).filter(Student.sname='coco').all()
# flask
stus = Student.query.filter()
# django
stus = Student.object.filter()

# 增加
session.add(stu)
session.commit()
# 可以自己封装为save()方法

# 删除
session.delete(stu)

# 更新直接给对象赋新值保存即可
```

##### 8.模拟耗时操作

```
# asynchronous装饰器，表示IO不主动关闭
@tornado.web.asynchronous
def get(self, *args, **kwargs):
    wd = self.get_argument('wd')
    # 同步操作
    # client = tornado.httpclient.HTTPClient()
    # fetch():获取某个地址的响应结果
    response = client.fetch(f'https://www.baidu.com/s?wd={wd}')
    print(response)
	
	
    # 异步操作
    client = tornado.httpclient.AsyncHTTPClient()
    # 需指定回调函数，但无需等待
    client.fetch(f'https://www.baidu.com/s?wd={wd}', callback=self.on_response)

def on_response(self, response)：
	print(response)
	# 主动关闭IO
	self.on_finish()
```

##### 9.将异步回调程序写成类似同步代码，但有异步效果

```
# 使用协程，yield
@tornado.web.gen.coroutine
def get(self, *args, **kwargs):
    wd = self.get_argument('wd')
    # 异步操作
    client = tornado.httpclient.AsyncHTTPClient()
    # 需指定回调函数，但无需等待
    response = yield client.fetch(f'https://www.baidu.com/s?wd={wd}')
    print(response)
    
    
# python 3.7后加入新关键字实现
async def get(self, *args, **kwargs):
    wd = self.get_argument('wd')
    # 异步操作
    client = tornado.httpclient.AsyncHTTPClient()
    # 需指定回调函数，但无需等待
    response = await client.fetch(f'https://www.baidu.com/s?wd={wd}')
    print(response)
```

##### 10.登录校验装饰器写法

```
def login_required(func):
	def check(self, *args, **kwargs):
		# 校验逻辑
		
		# 校验失败跳转登录
		self.redirect('/login/')
	return check
```

##### 11.tornado内置钩子函数

```
def open(self, *args, **kwargs):
	# open()在建立连接时，默认调用的方法
	self.many_user_online.append(self) # 此处的self即代表一个长连接对象
	
def on_close(self):
	# on_close在关闭连接时自动调用
	pass
	
对象.write_message('')  # 发送消息
```

