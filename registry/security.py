from functools import wraps

import flask

import registry.util
from registry.util import is_registered, is_soteria_researcher

__all__ = ["researcher_required"]


def registration_required(f):
    """Check that the user has completed the registration flow"""
    @wraps(f)
    def wrapper():
        if not is_registered():
            return flask.make_response(
                flask.render_template(
                    "error.html",
                    code=403,
                    message="You must complete registration before accessing this page.<br>"
                            "<a class='btn btn-primary mt-3' href='https://soteria.osg-htc.org/registration'>Register Now</a>"
                ), 403
            )

        return f()

    return wrapper


def researcher_required(f):
    """Check that the user has researcher status"""
    @wraps(f)
    def wrapper():
        if not is_soteria_researcher():
            return flask.make_response(
                flask.render_template(
                    "error.html",
                    code=403,
                    message="You must be a researcher to view this page, "
                            "<a href='https://soteria.osg-htc.org/researcher-registration'>apply now!</a>"
                ), 403)

        return f()

    return wrapper
