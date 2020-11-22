import termios
import tty
import sys


def read_file(filepath):
    with open(filepath, encoding="utf-8") as fh:
        return fh.read()


def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as fh:
        return fh.write(content)


# adapted from <https://code.activestate.com/recipes/134892/>
def prompt_char(msg):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        eprint("%s: " % msg, end="")
        char = sys.stdin.read(1)
        eprint(char, end="")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    eprint("")
    return char


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)
