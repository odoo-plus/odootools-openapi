def pad_lines(text, pad):
    pad_text = "\n{}".format(" " * pad)
    return pad_text.join(text.split('\n')).strip()
