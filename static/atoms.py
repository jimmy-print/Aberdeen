import sys
import types
import time
from copy import copy, deepcopy

INDEX_TOO_BIG = 'INDEX_TOO_BIG'
NO_NODES = 'NO_NODES'

DEPTH_CHAR = '_'

ROOT = 'ROOT'

NOT_RAN = 'NOT_RAN'

global_variables = {}

ONESTEP_DONE_NO_PRINT = 'onestep finished no print'
ONESTEP_DONE = 'onestep finished'
FINISHED = 'whole line finished'


INTERPRETER_PREFIX = '@'
# when we are running a file, sometimes we want each line to be printed
# before evaluating it, for debugging purposes. this prefix lets one
# distinguish between debugging print calls and actual (print "...")
# in the .la file.


'''
def interpreter_print(*values, sep=' ', end='\n', file=sys.stdout, flush=False, color=Fore.GREEN):
    values_list = list(values)
    values_list.insert(0, INTERPRETER_PREFIX)

    print(color, end='')
    print(*values_list, sep=sep, end=end, file=file, flush=flush)
    print(Style.RESET_ALL, end='')
    '''


class LangError(Exception): pass

def dupe(s, n):
    out = []
    for _ in range(n):
        out += s
    return ''.join(out)

def get_with_stack(root_node, stack):
    node = root_node
    for i in stack:
        if i >= len(node.nodes) and len(node.nodes) > 0:
            return INDEX_TOO_BIG
        elif not node.nodes:
            return NO_NODES
        node = node.nodes[i]
    return node

def thru_giving_depth(root_node):
    '''
    This function, along with thru_giving_depth_and_stack, only works for Root ASTs.
    This is because the Root ASTs are guaranteed to have the below structure:
    Root
    - function
    -- a
    -- b
    -- c

    They are guaranteed to only have one node below the Root node.
    thru_giving_depth stops when the stack is [1]. [1] would give the second node below the Root node,
    which is guaranteed to not exist.

    TODO verify that thru_giving_depth is never used for non-Root ASTs in the rest of the program.
    '''
    yield (0, root_node, type(root_node))
    stack = [0]
    while True:
        node = get_with_stack(root_node, stack)
        yield (len(stack), node, type(node))

        stack.append(0)
        if issubclass(type(get_with_stack(root_node, stack)), Node):
            continue
        elif get_with_stack(root_node, stack) == NO_NODES:
            stack.pop()

        stack[-1] += 1
        while get_with_stack(root_node, stack) == INDEX_TOO_BIG and stack != [1]:
            stack.pop()
            stack[-1] += 1

        if stack == [1]:
            break


def thru_giving_depth_and_stack(root_node):
    yield (0, root_node, type(root_node), [])
    stack = [0]
    while True:
        node = get_with_stack(root_node, stack)
        yield (len(stack), node, type(node), stack)

        stack.append(0)
        if issubclass(type(get_with_stack(root_node, stack)), Node):
            continue
        elif get_with_stack(root_node, stack) == NO_NODES:
            stack.pop()

        stack[-1] += 1
        while get_with_stack(root_node, stack) == INDEX_TOO_BIG and stack != [1]:
            stack.pop()
            stack[-1] += 1

        if stack == [1]:
            break


def iterate_through_node_not_root(starting_node):
    yield (0, starting_node, type(starting_node), [])
    stack = [0]
    while True:
        node = get_with_stack(starting_node, stack)
        yield (len(stack), node, type(node), stack)

        stack.append(0)
        if issubclass(type(get_with_stack(starting_node, stack)), Node):
            continue
        elif get_with_stack(starting_node, stack) == NO_NODES:
            stack.pop()

        stack[-1] += 1
        while get_with_stack(starting_node, stack) == INDEX_TOO_BIG and stack != [1]:
            stack.pop()
            if stack == []:
                return
            stack[-1] += 1


def new_get_vis_stack_str(root_node, printid=False):
    '''For non root trees'''
    out = []
    for elem in iterate_through_node_not_root(root_node):
        out.append('|'+dupe(DEPTH_CHAR, elem[0])+str(elem[1]))
        if printid:
            out.append(str(id(elem)))
        out.append('\n')
    return ''.join(out)



def get_vis_stack_str(root_node, printid=False):
    out = []
    for elem in thru_giving_depth(root_node):
        out.append('|'+dupe(DEPTH_CHAR, elem[0])+str(elem[1]))
        if printid:
            out.append(str(id(elem)))
        out.append('\n')
    return ''.join(out)


# Do not use the recursive functions except for testing.
def get_vis_recursive_str(node, layer=0, in_testing=False):
    if not in_testing:
        raise DeprecationWarning('Do not use recursive functions.')
    def __(node, layer=0):
        if layer == 0:
            yield'|' + dupe(DEPTH_CHAR, layer) + str(node) + '\n'

        for NODE in node.nodes:
            yield '|' + dupe(DEPTH_CHAR, layer + 1) + str(NODE) + '\n'
            yield from __(NODE, layer + 1)
    return ''.join(__(node, 0))


def thru(root_node):
    for elem in thru_giving_depth(root_node):
        yield elem[1]

def index(root_node, i):
    for ii, node in enumerate(thru(root_node)):
        if ii == i:
            return node
    raise IndexError('tree index not found (out of range?)')


def get_function(c):
    global print_
    plus = sum
    def minus(iterable):
        return iterable[0] - iterable[1]
    def multiply(iterable):
        result = 1
        for arg in iterable:
            result *= arg
        return result
    def divide(iterable):
        return iterable[0] / iterable[1]
    equals = lambda iterable: iterable[0] == iterable[1]
    less_than = lambda iterable: iterable[0] < iterable[1]
    modulo = lambda iterable: iterable[0] % iterable[1]

    def print_(iterable):
        print(*iterable, sep="")
        return None
    def input_(iterable):
        format_string = iterable[0]
        return input(format_string.format(*iterable[1:]))

    if_ = lambda iterable: None
    while_ = lambda iterable: None

    def set(iterable):
        global_variables[iterable[0]] = iterable[1]
    def get(iterable):
        return global_variables[iterable[0]]
    def wait(iterable):
        time.sleep(iterable[0])
        return None

    int_ = lambda iterable: int(iterable[0])
    not_ = lambda iterable: not iterable[0]

    name_to_function = {
        '+': plus,
        '-': minus,
        '*': multiply,
        '/': divide,
        '=': equals,
        '<': less_than,
        '%': modulo,

        'print': print_,
        'input': input_,

        'if': if_,
        'while': while_,

        'set': set,
        '$': get,
        'get': get,

        'int': int_,

#        'wait': wait,

        '!': not_,
    }

    for expected_function in name_to_function.values():
        assert isinstance(expected_function,(types.FunctionType, types.BuiltinFunctionType))

    try:
        function = name_to_function[c]
    except KeyError:
        raise LangError(f'===LANG ERROR: The function \'{c}\' is not implemented.===')
        exit(1)
    else:
        return function


def transform_ast(root_node):
    elems_with_OPENING_BRACKET = list(thru_giving_depth(root_node))
    elems_with_OPENING_BRACKET.pop(0)

    # Restructure elems to be without OPENING_BRACKET.
    # (
    #  +
    #  1
    #  2
    # becomes..
    # +
    #  1
    #  2
    # Note that the operation is being done on the 2D list form of these ASTs,
    # not on the node objects themselves.
    elems = []
    for i, elem in enumerate(elems_with_OPENING_BRACKET):
        if i == 0 or len(elems_with_OPENING_BRACKET[i - 1][1].nodes) == 0:
            if len(elem[1].nodes) > 0:
                elem[1].v = elems_with_OPENING_BRACKET[i + 1][1].v
            elems.append(elem)

    # Reconstruct an AST, after restructuring the elems to not have OPENING_BRACKET nodes.
    tree = Root()
    tree.add(elems[0][2](elems[0][1].v, None, elems[0][1].orig_line_indices))
    node = tree.nodes[0]
    past_layer = elems[0][0]
    for elem in elems[1:]:
        if elem[0] > past_layer:
            new_node = Node(elem[1].v, None, elem[1].orig_line_indices)
            node.add(new_node)
        elif elem[0] == past_layer:
            new_node = Node(elem[1].v, None, elem[1].orig_line_indices)
            node.parent.add(new_node)
        elif elem[0] < past_layer:
            gap = past_layer - elem[0]
            new_node = Node(elem[1].v, None, elem[1].orig_line_indices)
            for _ in range(gap):
                node = node.parent
            node.parent.add(new_node)
        node = new_node
        past_layer = elem[0]

    orig_tree = deepcopy(tree)
    return tree

def run(tree):
    orig_tree = deepcopy(tree)

    # Execute on the AST.
    stack = [0]
    while stack != [1]:

        stack.append(0)
        if issubclass(type(get_with_stack(tree, stack)), Node):
            continue
        elif get_with_stack(tree, stack) == NO_NODES:
            stack.pop()
        stack[-1] += 1

        while get_with_stack(tree, stack) == INDEX_TOO_BIG and stack != [1]:
            # When you're falling off the end of a function (+ 1 1) <-
            #print(stack)
            last_arg_node_stack = list(stack)
            last_arg_node_stack[-1] -= 1

            last_arg_node = get_with_stack(tree, last_arg_node_stack)

            parent_func_node = last_arg_node.parent
            parent_func_node_stack = list(last_arg_node_stack)
            parent_func_node_stack.pop()

            f = get_function(parent_func_node.v)

            for current_level_node in parent_func_node.nodes:
                assert len(current_level_node.nodes) == 0
                # We MUST not evaluate this function if there are nodes
                # on our current level that still themselves have elements.
                # E.g. (+ (+ 1 2) 2)<- Say we were hypothetically falling
                # off the outermost + function. This assertion would catch
                # this failure.

            args = [node.v for node in parent_func_node.nodes]

            # Find the parent ifs and whiles, if there are any.
            ancestor_control_nodes = []
            ancestor_control_nodes_stacks = []

            assert(all(type(i) == int for i in last_arg_node_stack))
            # Trying to avoid deepcopy. So ensure that last_arg_node_stack is just
            # a one-dimensional int list.
            search_stack = last_arg_node_stack.copy()
            search_stack.pop()
            
            while get_with_stack(tree, search_stack).v != ROOT:
                # Keep going up the stack.

                potential_control_node = get_with_stack(tree, search_stack)
                if (potential_control_node.v == 'if' or potential_control_node.v == 'while') and search_stack != parent_func_node_stack:
                    # TODO fix cases where not sure if object comparison should be done with == or is.
                    ancestor_control_nodes_stacks.append(list(search_stack))
                    ancestor_control_nodes.append(potential_control_node)
                search_stack.pop()

            parent_func_is_toplevel = False
            if not ancestor_control_nodes:
                parent_func_is_toplevel = True

            if parent_func_is_toplevel:
                # Thus, if the parent_func is at the top level of the code file, or if it's the first arg of
                # a while or an if function, it will always run.
                r = f(args)
            else:
                all_ancestor_control_first_args_are_true = all(ancestor_control_node.nodes[0].v for ancestor_control_node in ancestor_control_nodes)
                if all_ancestor_control_first_args_are_true:
                    r = f(args)
                else:
                    r = NOT_RAN

            cond_was_false = parent_func_node.nodes[0].v is False
            nothing_ran = all(R == NOT_RAN for R in [node.v for node in parent_func_node.nodes[1:]])

            if parent_func_node.v == 'while' and not nothing_ran and not cond_was_false:
                # We are now falling off of a while loop.
                # Now, we replace!
                while_stack = list(stack)
                while_stack.pop()

                orig_while_node = get_with_stack(orig_tree, while_stack)

                lowers = []
                for i, O in enumerate(iterate_through_node_not_root(orig_while_node)):
                    if i != 0:
                        lowers.append(list(O[:3]))
                        lowers[i-1].append(O[3][:])

                to_be_replaced_while_node = get_with_stack(tree, while_stack)
                to_be_replaced_while_node.nodes = []
                for lower in lowers:
                    parent = get_with_stack(to_be_replaced_while_node, lower[-1][:-1])
                    val = lower[1].v
                    cl = lower[2]
                    parent.add(cl(val,None))

                stack.pop()
            else:  # so a normal function falling off or an if function falling off
                parent_func_node.v = r
                parent_func_node.nodes = []

                stack.pop()
                stack[-1] += 1


    assert len(tree.nodes) == 1
    return tree.nodes[0].v


def run_onestep(tree, orig_tree, stack):
    print_msg = None
    while stack != [1]:
        stack.append(0)

        if issubclass(type(get_with_stack(tree, stack)), Node):
            if print_msg is None:
                return (ONESTEP_DONE_NO_PRINT, None, get_with_stack(tree, stack).orig_line_indices)
            else:
                return ONESTEP_DONE, print_msg, get_with_stack(tree, stack).orig_line_indices
        
        elif get_with_stack(tree, stack) == NO_NODES:
            stack.pop()
        stack[-1] += 1

        while get_with_stack(tree, stack) == INDEX_TOO_BIG and stack != [1]:
            # When you're falling off the end of a function (+ 1 1) <-
            last_arg_node_stack = list(stack)
            last_arg_node_stack[-1] -= 1

            last_arg_node = get_with_stack(tree, last_arg_node_stack)


            parent_func_node = last_arg_node.parent
            parent_func_node_stack = list(last_arg_node_stack)
            parent_func_node_stack.pop()

            f = get_function(parent_func_node.v)

            for current_level_node in parent_func_node.nodes:
                assert len(current_level_node.nodes) == 0
                # We MUST not evaluate this function if there are nodes
                # on our current level that still themselves have elements.
                # E.g. (+ (+ 1 2) 2)<- Say we were hypothetically falling
                # off the outermost + function. This assertion would catch
                # this failure.

            args = [node.v for node in parent_func_node.nodes]

            ancestor_control_nodes = []
            ancestor_control_nodes_stacks = []

            assert(all(type(i) == int for i in last_arg_node_stack))
            # Trying to avoid deepcopy. So ensure that last_arg_node_stack is just
            # a one-dimensional int list.
            search_stack = last_arg_node_stack.copy()
            search_stack.pop()
            
            while get_with_stack(tree, search_stack).v != ROOT:
                # Keep going up the stack.

                potential_control_node = get_with_stack(tree, search_stack)
                if (potential_control_node.v == 'if' or potential_control_node.v == 'while') and search_stack != parent_func_node_stack:
                    ancestor_control_nodes_stacks.append(list(search_stack))
                    ancestor_control_nodes.append(potential_control_node)
                search_stack.pop()

            parent_func_is_toplevel = False
            if not ancestor_control_nodes:
                parent_func_is_toplevel = True

            if parent_func_is_toplevel:
                r = f(args)
                if f == print_:
                    print_msg = ''.join([str(arg) for arg in args])
            else:
                all_ancestor_control_first_args_are_true = all(ancestor_control_node.nodes[0].v for ancestor_control_node in ancestor_control_nodes)
                if all_ancestor_control_first_args_are_true:
                    r = f(args)
                    if f == print_:
                        print_msg = ''.join([str(arg) for arg in args])
                else:
                    r = NOT_RAN

            cond_was_false = parent_func_node.nodes[0].v is False
            nothing_ran = all(R == NOT_RAN for R in [node.v for node in parent_func_node.nodes[1:]])

            if parent_func_node.v == 'while' and not nothing_ran and not cond_was_false:
                # Now, we replace!
                while_stack = list(stack)
                while_stack.pop()

                orig_while_node = get_with_stack(orig_tree, while_stack)

                lowers = []
                for i, O in enumerate(iterate_through_node_not_root(orig_while_node)):
                    if i != 0:
                        lowers.append(list(O[:3]))
                        lowers[i-1].append(O[3][:])

                to_be_replaced_while_node = get_with_stack(tree, while_stack)
                to_be_replaced_while_node.nodes = []
                for lower in lowers:
                    parent = get_with_stack(to_be_replaced_while_node, lower[-1][:-1])
                    val = lower[1].v
                    cl = lower[2]
                    parent.add(cl(val,None,lower[1].orig_line_indices))

                stack.pop()

            else:  # so a normal function falling off or an if function falling off
                parent_func_node.v = r
                parent_func_node.nodes = []

                stack.pop()
                stack[-1] += 1
                
        if print_msg is None:
            if get_with_stack(tree, stack) == INDEX_TOO_BIG:
                return ONESTEP_DONE_NO_PRINT, None, (None, None)
            else:
                return ONESTEP_DONE_NO_PRINT, None, get_with_stack(tree, stack).orig_line_indices
        else:
            if get_with_stack(tree, stack) == INDEX_TOO_BIG:
                return ONESTEP_DONE, print_msg, (None, None)
            else:
                return ONESTEP_DONE, print_msg, get_with_stack(tree, stack).orig_line_indices
                
    assert len(tree.nodes) == 1
    return FINISHED, None, (None, None)



class Node:
    def __init__(self, v, parent, orig_line_indices):
        assert type(v) != Node
        # Each node may contain other node objects in its self.nodes list.
        # However, their values should not be node objects. They should be
        # function names, numbers, strings, or booleans.
        self.v = v

        self.nodes = []
        self.parent = parent

        self.orig_line_indices = orig_line_indices

    def __repr__(self):
        return f' *{self.v}, {type(self)}* '

    def add(self, n):
        n.parent = self
        self.nodes.append(n)

    @staticmethod
    def _thru(n, in_testing=False):
        if not in_testing:
            raise DeprecationWarning
        yield n
        for node in n.nodes:
            if node is not None:
                yield from Node._thru(node, in_testing)

    def get(self, index, in_testing=False):
        if not in_testing:
            raise DeprecationWarning
        for i, node in enumerate(Node._thru(self, in_testing)):
            if i == index:
                return node
        raise IndexError('tree index not found (out of range?)')

class Root(Node):
    def __init__(self, _=None, __=None, ___=None):
        super().__init__(ROOT, None, None)

class Data(Node): pass
