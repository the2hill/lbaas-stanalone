import pecan
import pkgutil

import json

# LOG = utils.getLogger(__name__)
MAX_BYTES_REQUEST_INPUT_ACCEPTED = 15000


class ApiResource(object):
    """Base class for API resources."""
    pass


def load_body(req, resp=None, validator=None):
    """Helper function for loading an HTTP request body from JSON.
    This body is placed into into a Python dictionary.

    :param req: The HTTP request instance to load the body from.
    :param resp: The HTTP response instance.
    :param validator: The JSON validator to enforce.
    :return: A dict of values from the JSON request.
    """
    try:
        body = req.body_file.read(3600)
    except IOError:
        # LOG.exception("Problem reading request JSON stream.")
        pecan.abort(500, 'Read Error')

    try:
        # jsonutils:
        #     parsed_body = json.loads(raw_json, 'utf-8')
        parsed_body = json.loads(body)
        strip_whitespace(parsed_body)
    except ValueError:
        # LOG.exception("Problem loading request JSON.")
        pecan.abort(400, 'Malformed JSON')

    if validator:
        try:
            parsed_body = validator.validate(parsed_body)
        except Exception:
            pass

    return parsed_body


def generate_safe_exception_message(operation_name, excep):
    pass


@pkgutil.simplegeneric
def get_items(obj):
    """This is used to get items from either
       a list or a dictionary. While false
       generator is need to process scalar object
    """

    while False:
        yield None


@get_items.register(dict)
def _json_object(obj):
    return obj.iteritems()


@get_items.register(list)
def _json_array(obj):
    return enumerate(obj)


def strip_whitespace(json_data):
    """This function will recursively trim values from the
       object passed in using the get_items
    """

    for key, value in get_items(json_data):
        if hasattr(value, 'strip'):
            json_data[key] = value.strip()
        else:
            strip_whitespace(value)