from flask import Flask, jsonify, make_response
from app.extensions import init_app

from app.config import config

app = Flask(__name__)
init_app(app)

from flask import jsonify, make_response

@app.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({
        'error': True,
        'message': getattr(error, 'description', 'Not found')
    }), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({
        'error': True,
        'message': 'Internal server error'
    }), 500)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({
        'error': True,
        'message': getattr(error, 'description', 'Bad request')
    }), 400)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response(jsonify({
        "error": True,
        "message": "Method not allowed",
        "allowed_methods": e.valid_methods if hasattr(e, 'valid_methods') else None
    }), 405)

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception (optional)
    app.logger.error(f"Unhandled Exception: {e}")
    
    # Return a generic error response
    return jsonify({
        "error": True,
        "message": "An unexpected error occurred. Please contact support."
    }), 500

if __name__ == '__main__':
     app.run(host=config.ZEN_HOST,
            port=config.ZEN_PORT, debug=config.DEBUG)