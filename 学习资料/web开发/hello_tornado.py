import tornado.web
import tornado.ioloop
from tornado.options import options, define, parse_command_line

# 定义端口的默认值为8000
define('port', default=8000, type=int)


class IndexHandler(tornado.web.RequestHandler):

    # HTTP行为方法， GET,POST,PUT,PATCH,DELETE
    def get(self):
        # http://127.0.0.1:8000/index/?name=12112
        # 只用于获取数据
        self.write('hello tornado')

    def post(self, *args, **kwargs):
        # 只用于创建数据
        self.write('解析POST提交请求的行为方法')

    def put(self, *args, **kwargs):
        # 只用于修改全部字段
        self.write('解析PUT提交请求的行为方法')

    def patch(self, *args, **kwargs):
        # 只用于修改部分字段
        self.write('解析PATCH提交请求的行为方法')

    def delete(self, *args, **kwargs):
        # 只用于删除
        self.write('解析DELETE提交请求的行为方法')


class ReqHandler(tornado.web.RequestHandler):

    def get(self):
        # flask中获取GET请求中传递的参数： request.args
        #           POST请求中传递的参数: request.form
        # tornado中获取GET请求传递的参数: self.request.arguments[key]
        #  self.get_argument(key)  self.get_arguments(key)
        #  self.get_query_argument(key)  self.get_query_arguments(key)

        # 获取请求方式
        # self.request.method
        # 获取cookie内容
        # self.request.cookies
        # 获取请求路由
        # self.request.path
        # 获取上传文件
        # self.request.files

        # flask创建响应对象： res = make_response(’响应内容‘, ’响应状态码‘)
        # 设置响应状态码
        self.set_status(200)
        # 设置cookie和获取cookie
        self.set_cookie('token', '123457890', expires_days=1)
        self.get_cookie('token')
        # redirect: 重定向
        # self.redirect('/index/')
        # render: 渲染页面
        self.render('index.html')

        self.write('获取请求参数')

    def post(self):
        # tornado中获取POST请求传递的参数
        # self.get_argument(key)   self.get_arguments(key)
        # self.get_body_argument(key)  self.get_body_arguments(key)

        self.write('获取post传递参数')

    def put(self):

        self.write('获取put传递参数')


def make_app():
    return tornado.web.Application(handlers=[
        ('/index/', IndexHandler),  # ('路由地址', ‘处理业务逻辑方法‘)
        ('/req/', ReqHandler),
    ]
    # 调试模式
    # debug=True
    )


if __name__ == '__main__':
    # 解析命令行中的参数
    parse_command_line()
    # make_app方法，返回一个Application对象
    app = make_app()
    # 监听端口, python hello.py --port=8080
    app.listen(options.port)
    # 启动一个IO事件循环，监听端口请求（启动tornado程序）
    tornado.ioloop.IOLoop.current().start()


