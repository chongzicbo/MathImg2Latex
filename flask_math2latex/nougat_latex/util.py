# -*- coding:utf-8 -*-
# create: @time: 10/8/23 11:55

import re


def process_raw_latex_code(s: str):
    """Remove unnecessary whitespace from LaTeX code.

    Args:
        s (str): Input string

    Returns:
        str: Processed image
    """
    text_reg = r"(\\(operatorname|mathrm|text|mathbf)\s?\*? {.*?})"
    letter = "[a-zA-Z]"
    noletter = "[\W_^\d]"
    names = [x[0].replace(" ", "") for x in re.findall(text_reg, s)]
    s = re.sub(text_reg, lambda match: str(names.pop(0)), s)
    news = s
    while True:
        s = news
        news = re.sub(r"(?!\\ )(%s)\s+?(%s)" % (noletter, noletter), r"\1\2", s)
        news = re.sub(r"(?!\\ )(%s)\s+?(%s)" % (noletter, letter), r"\1\2", news)
        news = re.sub(r"(%s)\s+?(%s)" % (letter, noletter), r"\1\2", news)
        if news == s:
            break
    return s


if __name__ == "__main__":
    formula_text = "d s ^ { 2 } = ( 1 - { \frac { q c o s \theta } { r } } ) ^ { \frac { 2 } { 1 + \alpha ^ { 2 } } } \lbrace d r ^ { 2 } + r ^ { 2 } d \theta ^ { 2 } + r ^ { 2 } s i n ^ { 2 } \theta d \varphi ^ { 2 } \rbrace - { \frac { d t ^ { 2 } } { ( 1 - { \frac { q c o s \theta } { r } } ) ^ { \frac { 2 } { 1 + \alpha ^ { 2 } } } } } \, ."
    print(process_raw_latex_code(formula_text))
