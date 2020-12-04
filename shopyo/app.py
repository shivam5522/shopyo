import importlib
import os
import sys
import json

from flask import Flask
from flask import redirect
from flask import url_for

from flask_wtf.csrf import CSRFProtect


import sys

sys.path.append(".")

from flask_uploads import configure_uploads

from config import app_config

from shopyoapi.init import db
from shopyoapi.init import login_manager
from shopyoapi.init import ma
from shopyoapi.init import migrate
from shopyoapi.init import productphotos
from shopyoapi.enhance import get_setting

base_path = os.path.dirname(os.path.abspath(__file__))


def create_app(config_name):
    app = Flask(__name__)
    configuration = app_config[config_name]
    app.config.from_object(configuration)
    migrate.init_app(app, db)
    db.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)  # noqa

    configure_uploads(app, productphotos)

    for module in os.listdir(os.path.join(base_path, "modules")):
        if module.startswith("__"):
            continue
        mod = importlib.import_module("modules.{}.view".format(module))
        app.register_blueprint(getattr(mod, "{}_blueprint".format(module)))

    @app.route("/")
    def index():
        return redirect(configuration.HOMEPAGE_URL)

    @app.context_processor
    def inject_global_vars():
        theme_dir = os.path.join(
            app.config["BASE_DIR"], "themes", get_setting("ACTIVE_THEME")
        )
        info_path = os.path.join(theme_dir, "info.json")
        with open(info_path) as f:
            info_data = json.load(f)


        APP_NAME = get_setting("APP_NAME")
        SECTION_NAME = get_setting("SECTION_NAME")
        SECTION_ITEMS = get_setting("SECTION_ITEMS")
        ACTIVE_THEME = get_setting("ACTIVE_THEME")
        ACTIVE_THEME_VERSION = info_data["version"]
        ACTIVE_THEME_STYLES_URL = url_for('resource.active_theme_css', active_theme=ACTIVE_THEME, v=ACTIVE_THEME_VERSION)

        base_context = {
            "APP_NAME": APP_NAME,
            "SECTION_NAME": SECTION_NAME,
            "SECTION_ITEMS": SECTION_ITEMS,
            "ACTIVE_THEME": ACTIVE_THEME,
            "ACTIVE_THEME_VERSION": ACTIVE_THEME_VERSION,
            "ACTIVE_THEME_STYLES_URL": ACTIVE_THEME_STYLES_URL
        }

        return base_context

    # end of func
    return app


app = create_app("development")


if __name__ == "__main__":

    app.run(debug=False, host="0.0.0.0")
