def bool_to_xliff(boolean):
    return "yes" if boolean else "no"


def xliff_to_bool(string):
    return True if string == "yes" else False
