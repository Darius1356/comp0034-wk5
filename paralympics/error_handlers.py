from flask import json, current_app as app, jsonify, make_response
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import HTTPException


# Error handlers
@app.errorhandler(ValidationError)
def register_validation_error(error):
    """ Error handler for marshmallow schema validation errors.

    Args:
        error (ValidationError): Marshmallow error.

    Returns:
        HTTP response with the validation error message and the 400 status code
    """
    response = error.messages
    return response, 400


@app.errorhandler(404)
def resource_not_found(e):
    """ Error handler for 404.

        Args:
            HTTP 404 error

        Returns:
            JSON response with the validation error message and the 404 status code
        """
    return jsonify(error=str(e)), 404