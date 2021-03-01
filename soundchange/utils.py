
def apply_sound_change(tokenlist, rb, p):
    for token in tokenlist:
        token.lemma = rb.transform(token.form, p)
    return tokenlist

