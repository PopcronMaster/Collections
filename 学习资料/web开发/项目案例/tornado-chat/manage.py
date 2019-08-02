
import tornado.web
import tornado.ioloop
from tornado.options import options, define, parse_command_line
from tornado_jinja2 import Jinja2Loader
import jinja2

from user.views import RegisterHandlers, LoginHandlers, HomeHandlers, InitDbHandlers, \
    ManyChatHandlers, ChatHandlers, OneChatHandlers, RoomChatHandlers, NewChatHandlers

from utils.settings import TEMPLATE_DIR, STATIC_DIR


# 定义默认的端口port值
define('port', default=7000, type=int)

# 使用jinja2模板引擎
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'), autoescape=False)
jinja2_loader = Jinja2Loader(jinja2_env)


def make_app():
    # 生成Application对象
    return tornado.web.Application(
        handlers=[
            ('/register/', RegisterHandlers),  # 注册页面
            ('/login/', LoginHandlers),  # 登陆页面
            ('/home/', HomeHandlers),  # 首页
            ('/init_db/', InitDbHandlers),  # 初始化数据库
            ('/many_chat/', ManyChatHandlers),  # 群聊
            ('/chat/', ChatHandlers),  # 群聊
            ('/room_chat/', RoomChatHandlers),  # 一对一聊天json
            ('/one_chat/', OneChatHandlers),  # 一对一聊天
            ('/new_chat/', NewChatHandlers),  # 一对一聊天
        ],
        # 静态模板文件地址
        static_path=STATIC_DIR,
        # 模板文件地址
        template_path=TEMPLATE_DIR,
        # debug调试模式，自动重启
        debug=True,
        # 使用jinja2引擎
        template_loader=jinja2_loader,
        # 加密cookie
        cookie_secret='akdhbgaigfoewuyr0qyrojb'
    )


if __name__ == '__main__':
    # 解析命令行中的参数
    parse_command_line()
    # 生成Application对象
    app = make_app()
    # 监听命令行中配置的端口
    app.listen(options.port)
    # 启动事件I/O循环
    tornado.ioloop.IOLoop.current().start()
