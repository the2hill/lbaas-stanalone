import pecan
from pecan import rest

class VersionController(rest.RestController):
    @pecan.expose('json')
    def get(self):
        return {"version": "0.0.1"}