import pygame.cursors

_cursors = {
    "pointer": (
        "     ..         ",
        "    .XX.        ",
        "    .XX.        ",
        "    .XX.        ",
        "    .XX.....    ",
        "    .XX.XX.X..  ",
        " .. .XX.XX.X.X. ",
        ".XX..XXXXXXXXX. ",
        ".XXX.XXXXXXXXX. ",
        " .XXXXXXXXXXXX. ",
        "  .XXXXXXXXXXX. ",
        "  .XXXXXXXXXX.  ",
        "   .XXXXXXXXX.  ",
        "    .XXXXXXX.   ",
        "     ........   ",
        "     ........   "),
    "scroll": (
        "       .        ",
        "      .X.       ",
        "     .XXX.      ",
        "    ...X...     ",
        "      .X.       ",
        "   .  .X.  .    ",
        "  ..  .X.  ..   ",
        " .X....X....X.  ",
        ".XXXXXXXXXXXXX. ",
        " .X....X....X.  ",
        "  ..  .X.  ..   ",
        "   .  .X.  .    ",
        "      .X.       ",
        "    ..XXX..     ",
        "     ..X..      ",
        "       .        "),
    }

_compiled = {
    "arrow": pygame.cursors.arrow
    }

def _compile(bm):
    _hcurs, _hmask = pygame.cursors.compile(bm, ".", "X")
    return ((16, 16), (5, 1), _hcurs, _hmask)

for c in _cursors:
    _compiled[c] = _compile(_cursors[c])

def set_cursor(name):
    if name in _compiled:
        pygame.mouse.set_cursor(*_compiled[name])
    else:
        pygame.mouse.set_cursor(*getattr(pygame.cursors, name))

