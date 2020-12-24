from .util import eprint


ELEMENTS = {
    "h1": {
        "type": "block",
        "prefix": "== ",
        "suffix": " =="
    },
    "p": {
        "type": "block"
    },
    "notice": {
        "type": "block",
        "prefix": "----\n",
        "suffix": "\n----"
    }
}


class LUI:
    """
    line-based user interface
    """

    def __init__(self):
        self.first = True
        self.separator = False

    def print(self, element, msg=None):
        if msg == None: # `element` is optional
            msg, element = element, msg

        el = {} if element is None else ELEMENTS[element]
        is_block = el.get("type") == "block"
        if (is_block or self.separator) and not self.first:
            eprint("")
        if not isinstance(msg, str):
            msg = "\n".join(msg)
        eprint(el.get("prefix", "") + msg + el.get("suffix", ""))
        self.separator = is_block

        if self.first:
            self.first = False


lui = LUI() # singleton
