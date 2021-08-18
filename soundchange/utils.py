
def apply_sound_change(tokenlist, rb, p):
    transformed = []
    for token in tokenlist:
        transformed.append(rb.transform(token.form, p))
    return transformed

def to_file(tokenlist):
    return " ".join(tokenlist)+"\n"

