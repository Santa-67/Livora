from . import auth, user, property, match, chat, admin, ml, upload


def register_blueprints(app):
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(property.bp)
    app.register_blueprint(match.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(ml.bp)
    app.register_blueprint(upload.bp)
