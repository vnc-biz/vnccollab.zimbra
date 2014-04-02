

class MockZimbra(object):
    def __init__(self, nodes={}, attrs={}):
        self._attrs = attrs
        self._nodes = nodes

    def _getAttr(self, key):
        return self._attrs[key]

    def __getattr__(self, key):
        return self._nodes[key]
