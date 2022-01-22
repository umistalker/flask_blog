from elasticsearch import Elasticsearch
from flask import Flask
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
lm = LoginManager(app)
lm.login_view = 'auth.login'
lm.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)
elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None


from blog.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from blog.main import bp as main_bp
app.register_blueprint(main_bp)

from blog.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')



# oid = OpenID(app, os.path.join(BASEDIR, 'tmp'))

# def create_app(config_class = config):
#     app = Flask(__name__)
#     app.config.from_object(config)
#
#     db.init_app(app)
#     migrate.init_app(app, db, render_as_batch=True)
#     lm.init_app(app)
#     mail.init_app(app)
#     bootstrap.init_app(app)
#     moment.init_app(app)
#     babel.init_app(app)
#
#     from blog.errors import bp as errors_bp
#     app.register_blueprint(errors_bp)
#
#     from blog.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
#     from blog.auth import bp as auth_bp
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#
#
#     return app
from blog import models
