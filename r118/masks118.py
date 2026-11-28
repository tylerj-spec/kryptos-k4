"""R118 masks (PREREGISTRATION section 2): word tokens of a text, and the three forms U (unmasked), G (Germanic/Dutch-like
respelling, 12 ordered word rules) and T (telegraphese: drop THE, A, AN, OF; each full stop becomes STOP)."""
import re

DROP_WORDS = {"THE", "A", "AN", "OF"}


def tokens(text):
    """Word tokens [A-Z]+ and full stops, in order."""
    return re.findall(r"[A-Z]+|\.", text.upper())


def germanic_word(w):
    w = w.replace("PH", "F")
    w = w.replace("CK", "K")
    w = w.replace("QU", "KW")
    w = re.sub(r"C(?=[EIY])", "Z", w)
    w = w.replace("C", "K")
    w = w.replace("W", "V")
    w = w.replace("X", "KS")
    if w.startswith("Y"):
        w = "J" + w[1:]
    w = w.replace("Y", "IJ")
    w = w.replace("SH", "SJ")
    w = w.replace("OO", "OE")
    if w.startswith("F"):
        w = "V" + w[1:]
    return w


def form(toks, kind):
    """The letters of a token run in form U, G or T."""
    out = []
    for t in toks:
        if t == ".":
            if kind == "T":
                out.append("STOP")
            continue
        if kind == "G":
            out.append(germanic_word(t))
        elif kind == "T":
            if t not in DROP_WORDS:
                out.append(t)
        else:
            out.append(t)
    return "".join(out)
