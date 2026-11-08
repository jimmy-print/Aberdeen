import sys
from atoms import *

OPENING_BRACKET = '('
CLOSING_BRACKET = ')'

QUOTE_CHAR = '"'

COMMENT_PREFIX = '#'
SIGIL_CHAR_STR = '$'
assert len(COMMENT_PREFIX) == 1
 

def is_whitespace(s):
    for c in s:
        if c != ' ':
            return False
    return True


def is_int(v):
    try:
        int(v)
        return True
    except ValueError:
        return False


def is_str(v):
    """
    Check if a token is a string in Lang.
    :param s: A token, e.g. '(', '"name"', '12'.
    :returns: True if 
    """
    # not that v can be converted into a string type,
    # but that it is literally a string in the code file
    # (set name "john")
    if v[0] == '"' and v[-1] == '"':
        return True
    return False


def rm_char_instances(s: str, c: str):
    """
    Remove all instances of an unwanted character in a string.
    :param s: the string in which we take out all instances of the unwanted character.
    :param c: the unwanted character. Must be single character string.

    :returns: a copy of s without any instance of the unwanted character.
    """
    out = []
    for C in s:
        if C != c:
            out.append(C)

    return ''.join(out)


def compress_whitespace(s: str):
    """
    Convert consecutive spaces of length greater than 1 into a single space
    :param s: eg. ' 123  34   3 '
    :returns: eg. ' 123 34 3 '
    """

    out = []
    for i, c in enumerate(s):
        tmp = ''
        if i != len(s) - 1:
            tmp = c
            if c == ' ' and s[i + 1] == ' ':
                pass
            else:
                out.append(tmp)
    out.append(s[-1])
    return ''.join(out)

allowed_exposed_chars = [
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
	'1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
	'_',
    '.',
]

operator_chars = [
	'+', '-', '*', '/',
	'!',
	'<', '>',
	'$',
    '%',
	'=',
]
def get_tokens(expression):
    processing_a_string = False
    on_last_char = False

    tok = ""
    toks = []
    for i, char in enumerate(expression):
        try:
            next_char = expression[i + 1]
        except IndexError:
            pass
        if i + 1 == len(expression):
            on_last_char = True

        i += 1
        cut_off_tok = False

        if char == QUOTE_CHAR:
            processing_a_string = not processing_a_string

        if processing_a_string:
            tok += char
            if on_last_char:
                raise RuntimeError("unbalanced closing apostrophe")
            if next_char == QUOTE_CHAR:
                tok += QUOTE_CHAR
                cut_off_tok = True
        else:
            if char == OPENING_BRACKET or char == CLOSING_BRACKET:
                tok += char
                cut_off_tok = True
            if char in allowed_exposed_chars:
                tok += char
                if on_last_char:
                    cut_off_tok = True
                else:
                    if next_char not in allowed_exposed_chars:
                        cut_off_tok = True
            if char in operator_chars:
                tok += char
                cut_off_tok = True
        if cut_off_tok:

            toks.append((tok, (i-len(tok), i-1)))
            tok = ""
    return toks

def expand_sigil(toks, indices):
    new_toks = []
    new_indices = []
    next_iter_dont_push = False
    i = 0
    while i < len(toks):
        if toks[i] == SIGIL_CHAR_STR:
            new_indices.append((indices[i][0], indices[i][1]))
            new_indices.append((indices[i][0], indices[i][1]))
            new_indices.append((indices[i][0], indices[i][1]))
            new_indices.append((indices[i][0], indices[i][1]))

            new_toks.append(OPENING_BRACKET)
            new_toks.append(SIGIL_CHAR_STR)
            new_toks.append(f"{QUOTE_CHAR}{toks[i + 1]}{QUOTE_CHAR}")
            new_toks.append(CLOSING_BRACKET)

            i += 2
        else:
            new_indices.append((indices[i][0], indices[i][1]))
            new_toks.append(toks[i])
            i += 1
    return new_toks, new_indices
            
def get_tree(tokens, indices):
    tree = Root()

    on_tok = index(tree, 0)

    II = -1
    for __, tok in enumerate(tokens):
        II += 1
        if tok == CLOSING_BRACKET:
            # now we change on_tok to the nicht above the on_tok
            on_tok = on_tok.parent

            II -= 1

            continue

        if tok == OPENING_BRACKET:
            on_tok.add(Node(tok, None, indices[__]))
        else:
            if is_int(tok):
                on_tok.add(Data(int(tok), None, indices[__]))
            elif is_str(tok):
                on_tok.add(Data(str(tok.strip('"')), None, indices[__]))
            else:
                on_tok.add(Node(tok, None, indices[__]))

        if tok == OPENING_BRACKET:
            on_tok = index(tree, II + 1)

    return tree

