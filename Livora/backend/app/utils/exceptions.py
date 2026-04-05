from flask import jsonify

class APIException(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

def register_error_handlers(app):
    from marshmallow import ValidationError
    from sqlalchemy.exc import SQLAlchemyError

    from app import db

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        response = jsonify({'error': error.message})
        response.status_code = error.status_code
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = jsonify({'error': 'Validation error', 'messages': error.messages if hasattr(error, 'messages') else str(error)})
        response.status_code = 422
        return response

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        db.session.rollback()
        response = jsonify({'error': 'Database error', 'details': str(error)})
        response.status_code = 500
        return response
