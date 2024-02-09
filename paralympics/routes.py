from flask import json, make_response, current_app as app, request, abort, jsonify
from sqlalchemy import exc
from paralympics import db
from paralympics.models import Region, Event, User
from paralympics.schemas import RegionSchema, EventSchema
from werkzeug.exceptions import HTTPException
from paralympics.helpers import encode_auth_token, token_required

# Flask-Marshmallow Schemas
regions_schema = RegionSchema(many=True)
region_schema = RegionSchema()
events_schema = EventSchema(many=True)
event_schema = EventSchema()


@app.get("/regions")
def get_regions():
    """Returns a list of NOC region codes and their details in JSON.

    Returns:
        JSON for all the regions
    """
    # Select all the regions using Flask-SQLAlchemy
    all_regions = db.session.execute(db.select(Region)).scalars()
    # Dump the data using the Marshmallow regions schema; '.dump()' returns JSON.
    result = regions_schema.dump(all_regions)
    # Return the data in the HTTP response
    return result


@app.get('/regions/<code>')
def get_region(code):
    """ Returns one region in JSON.

    Returns 404 if the region code is not found in the database.

    Args:
        code (str): The 3 digit NOC code of the region to be searched for

    Returns: 
        JSON for the region if found otherwise 404
    """
    # Query structure shown at https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/queries/#select
    # Try to find the region, if it is ot found, catch the error and return 404
    try:
        region = db.session.execute(db.select(Region).filter_by(NOC=code)).scalar_one()
        result = region_schema.dump(region)
        return result
    except exc.NoResultFound as e:
        app.logger.error(f'Region code {code} was not found. Error: {e}')
        abort(404, description="Region not found")


@app.get("/events")
def get_events():
    """Returns a list of events and their details in JSON.

    Returns: 
        JSON for all events
    """
    all_events = db.session.execute(db.select(Event)).scalars()
    result = events_schema.dump(all_events)
    return result


@app.get('/events/<event_id>')
def get_event(event_id):
    """ Returns the event with the given id JSON.

    Args:
        event_id (int): The id of the event to return
    Returns:
        JSON
    """
    event = db.session.execute(db.select(Event).filter_by(id=event_id)).scalar_one()
    result = event_schema.dump(event)
    return result


@app.post('/events')
@token_required
def add_event():
    """ Adds a new event.

   Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow
   event_schema.loads()

   Returns: 
        JSON
   """
    ev_json = request.get_json()
    event = event_schema.load(ev_json)
    db.session.add(event)
    db.session.commit()
    return {"message": f"Event added with id= {event.id}"}


@app.post('/regions')
@token_required
def add_region():
    """ Adds a new region.

    Gets the JSON data from the request body and uses this to deserialise JSON to an object using Marshmallow
   region_schema.loads()

    Returns: 
        JSON
    """
    json_data = request.get_json()
    region = region_schema.load(json_data)
    db.session.add(region)
    db.session.commit()
    return {"message": f"Region added with NOC= {region.NOC}"}


@app.delete('/events/<int:event_id>')
@token_required
def delete_event(event_id):
    """ Deletes the event with the given id.

    Args: 
        event_id (int): The id of the event to delete
    Returns: 
        JSON
    """
    event = db.session.execute(db.select(Event).filter_by(id=event_id)).scalar_one()
    db.session.delete(event)
    db.session.commit()
    return {"message": f"Event {event_id} deleted."}


@app.delete('/regions/<noc_code>')
@token_required
def delete_region(noc_code):
    """ Deletes the region with the given code.

    Args:
        param code (str): The 3-character NOC code of the region to delete
    Returns:
        JSON If successful, return success message, other return 404 Not Found
    """
    try:
        region = db.session.execute(db.select(Region).filter_by(NOC=noc_code)).scalar_one()
        db.session.delete(region)
        db.session.commit()
        return {"message": f"Region {noc_code} deleted."}
    except exc.SQLAlchemyError as e:
        # Log the exception
        app.logger.error(f"A database error occurred: {str(e)}")
        # Return a 404 error to the user who made the request
        msg_content = f'Region {noc_code} not found'
        msg = {'message': msg_content}
        return make_response(msg, 404)


@app.patch("/events/<event_id>")
@token_required
def event_update(event_id):
    """ Updates changed fields for the specified event.
    
    Returns:
        JSON message
    """
    # Find the event in the database
    existing_event = db.session.execute(
        db.select(Event).filter_by(event_id=event_id)
    ).scalar_one_or_none()
    # Get the updated details from the json sent in the HTTP patch request
    event_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes from the json
    event_update = event_schema.load(event_json, instance=existing_event, partial=True)
    # Commit the changes to the database
    db.session.add(event_update)
    db.session.commit()
    # Return json success message
    response = {"message": f"Event with id={event_id} updated."}
    return response


@app.patch("/regions/<noc_code>")
@token_required
def region_update(noc_code):
    """Updates changed fields for the specified region.
    
    Args:
        noc_code (str): 3 character NOC region code

    Returns:
        JSON message
    """
    # Find the region in the database
    existing_region = db.session.execute(
        db.select(Region).filter_by(NOC=noc_code)
    ).scalar_one_or_none()
    # Get the updated details from the json sent in the HTTP patch request
    region_json = request.get_json()
    # Use Marshmallow to update the existing records with the changes from the json
    region_update = region_schema.load(region_json, instance=existing_region, partial=True)
    # Commit the changes to the database
    db.session.add(region_update)
    db.session.commit()
    # Return json message
    response = {"message": f"Region {noc_code} updated."}
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle non-HTTP exceptions as 500 Server error in JSON format."""

    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": 500,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(404)
def resource_not_found(e):
    """Handle a specific HTTP error (404 in this case) with custom message for the app when Flask.abort() is called.
    """
    return jsonify(error=str(e)), 404


@app.post("/register")
@token_required
def register():
    """Register a new user for the REST API

    If successful, return 201 Created.
    If email already exists, return 409 Conflict (resource already exists).
    If any other error occurs, return 500 Server error
    """
    # Get the JSON data from the request
    post_data = request.get_json()
    # Check if user already exists, returns None if the user does not exist
    user = db.session.execute(
        db.select(User).filter_by(email=post_data.get("email"))
    ).scalar_one_or_none()
    if not user:
        try:
            # Create new User object
            user = User(email=post_data.get("email"))
            # Set the hashed password
            user.set_password(password=post_data.get("password"))
            # Add user to the database
            db.session.add(user)
            db.session.commit()
            # Return success message
            response = {
                "message": "Successfully registered.",
            }
            return make_response(jsonify(response)), 201
        except Exception as err:
            response = {
                "message": "An error occurred. Please try again.",
            }
            return make_response(jsonify(response)), 500
    else:
        response = {
            "message": "User already exists. Please Log in.",
        }
        return make_response(jsonify(response)), 409


@app.post('/login')
@token_required
def login():
    """Logins in the User and generates a token

    If the email and password are not present in the HTTP request, return 401 error
    If the user is not found in the database, or the password is incorrect, return 401 error
    If the user is logged in and the token is generated, return the token and 201 Success
    """
    auth = request.get_json()

    # Check the email and password are present, if not return a 401 error
    if not auth or not auth.get('email') or not auth.get('password'):
        msg = {'message': 'Missing email or password'}
        return make_response(msg, 401)

    # Find the user in the database
    user = db.session.execute(
        db.select(User).filter_by(email=auth.get("email"))
    ).scalar_one_or_none()

    # If the user is not found, or the password is incorrect, return 401 error
    if not user or not user.check_password(auth.get('password')):
        msg = {'message': 'Incorrect email or password.'}
        return make_response(msg, 401)

    # If all OK then create the token
    token = encode_auth_token(user.id)

    # Return the token and the user_id of the logged in user
    return make_response(jsonify({"user_id": user.id, "token": token}), 201)