'''
Flask插件
'''

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
debugtoolbar = DebugToolbarExtension()
cache = Cache(config={'CACHE_TYPE':'simple'})


# 初始化插件
def init_exts(app):
    db.init_app(app)
    migrate.init_app(app, db)
    Bootstrap(app)
    debugtoolbar.init_app(app)
    cache.init_app(app)


