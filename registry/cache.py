"""
Use a local Python dictionary as a cache.
"""

import flask_caching

__all__ = ["cache"]

cache = flask_caching.Cache(config={"CACHE_TYPE": "SimpleCache"})
