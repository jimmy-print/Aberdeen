import random

import js
import asyncio
import lang
import atoms
import copy

from pyscript import window, document
from pyscript import when
from pyscript import web


all_code_ast = []
all_code_vis = []
NO_EXECUTION_SPECIAL = -100000  # represents the state of no program having been loaded
stack = NO_EXECUTION_SPECIAL
on_line = NO_EXECUTION_SPECIAL
EDITING = 'EDITING'
RUNNING = 'RUNNING'
state = EDITING
def edit_to_run():
    global all_code_ast, all_code_vis, stack, on_line, state
    state = RUNNING
    on_line = 0
    stack = [0]
    update_visual_representation(do_lines())
    atoms.global_variables = {}
def run_to_edit():
    global all_code_ast, all_code_vis, stack, on_line, state
    state = EDITING
    on_line = NO_EXECUTION_SPECIAL
    stack = NO_EXECUTION_SPECIAL
    all_code_vis, all_code_ast = [], []
    atoms.global_variables = {}


indice = [-1, -1]  # default values to prevent
# text from being highlighted when website just loaded.
current_highlight_action_completed = False

debug = True

def get_coords_and_lines_from_transformed_unrooted_tree(unrooted_tree):
    pkg = atoms.iterate_through_node_not_root(unrooted_tree) 
    depth = max(i[0] for i in pkg)

    x = 200
    y = 70
    min_vert_step = 40

    horz_step = None
    vert_step = None
    depth = 0
    coords = []
    lines = []
    xs = [None]
    max_horzs = [200]
    eager = list(atoms.iterate_through_node_not_root(unrooted_tree))
    for i, DFF in enumerate(atoms.iterate_through_node_not_root(unrooted_tree)):
        if DFF[1] == atoms.INDEX_TOO_BIG:
            assert i == len(eager) - 1
            break


        if i != 0:
            last_depth = eager[i - 1][0]
        else:
            last_depth = DFF[0]
        depth = DFF[0]

        if depth > last_depth:
            max_horzs.append(max_horzs[-1] - 40)

            max_horz = max_horzs[-1]
            length = len(DFF[1].parent.nodes)
            try:
                horz_step = ((length - 1) / 2) * (max_horz / (length - 1))
            except ZeroDivisionError:
                horz_step = 0

            x -= horz_step

            xs.append(x)


            y += min_vert_step * (depth - last_depth)
        elif depth < last_depth:

            #horz_step = max_horz_step / len(DFF[1].parent.nodes)
            length = len(DFF[1].parent.nodes)
            [max_horzs.pop() for i in range(last_depth - depth)]
            max_horz = max_horzs[-1]
            try:
                horz_step = ((length - 1) / 2) * (max_horz / (length - 1))
            except ZeroDivisionError:
                horz_step = 0


            y -= min_vert_step * (last_depth - depth)

            [xs.pop() for i in range(last_depth - depth)]

            x = xs[-1] + horz_step
            xs[-1] = x
        else:
            length = len(DFF[1].parent.nodes)
            max_horz = max_horzs[-1]
            try:
                horz_step = max_horz / (length - 1)
            except ZeroDivisionError:
                horz_step = 0
            x += horz_step
            xs[-1] = x

        coords.append((x, y, DFF[1].v, tuple(DFF[3])      ))

    for i, (coord, DFF) in enumerate(zip(coords, atoms.iterate_through_node_not_root(unrooted_tree))):
        parent_node = DFF[1].parent
        try:
            ii = [i[1] for i in atoms.iterate_through_node_not_root(unrooted_tree)].index(parent_node)
            lines.append(
            (
                coord, coords[ii]
            ))
        except ValueError:
            pass


    return coords, lines


def update_visual_representation(raw_code):
    global all_code_vis, all_code_ast
    all_code_ast = []
    all_code_vis = []
    # TODO: *breadth* first search should allow for detection of neighbouring node
    # (on the same level) collisions, which would allow for 'perfect' non-intersecting
    # graph visualisations.
    raw_code_wo_front_back_whitespace = raw_code.strip()
    raw_exprs = raw_code_wo_front_back_whitespace.split(';')
    if raw_exprs[-1] == '':
        raw_exprs.pop()

    exprs = []
    for raw_expr in raw_exprs:
        no_newlines = lang.rm_char_instances(raw_expr, '\n')
        also_no_redundant_spaces = lang.compress_whitespace(no_newlines)
        exprs.append(also_no_redundant_spaces)


    for line in exprs:
        if line[0] == lang.COMMENT_PREFIX:
            continue
        res = lang.get_tokens(line)
        tokens = [a[0] for a in res]
        indices = [b[1] for b in res]
        
        tokens, indices = lang.expand_sigil(tokens, indices)
        tokens_no_whitespace = list(filter(lambda token: not lang.is_whitespace(token), tokens))


        rooted_tree = lang.get_tree(tokens_no_whitespace, indices)
        transformed_tree = atoms.transform_ast(rooted_tree)
        unrooted_tree = transformed_tree.nodes[0]
        
        tree_ = copy.deepcopy(transformed_tree)
        orig_tree_ = copy.deepcopy(tree_)

        coords, lines = get_coords_and_lines_from_transformed_unrooted_tree(unrooted_tree)

        all_code_ast.append(
            {
                'tree': tree_,
                'orig_tree': orig_tree_,
             })
        all_code_vis.append(
            {
             'coords': coords,
             'lines': lines,
             })


code_input_box = web.page.find("#codeinputbox")[0]
@when("click", "#loadbutton")
def callback_load_button():
    edit_to_run()

@when("click", "#stopbutton")
def callback_stop_button():
    run_to_edit()

@when("input", "#codeinputbox")
def do_lines():
    raw_code = code_input_box.value
    lines_n = len(raw_code.split('\n'))
    lines_root_elem = web.page.find("#linenumbers")[0]
    lines_root_elem.textContent = ''

    to_insert = ''
    for i in range(1, lines_n + 1):
        to_insert += f'<span class=\"lineN\">{i}</span><br>'
    lines_root_elem.innerHTML = to_insert;

    return raw_code
do_lines()  # for the first line number to be inserted upon webpage load.


def assign_copybuttons_onclick():
    copybuttons = web.page.find(".copybutton")
    for i, copybutton in enumerate(copybuttons):
        # Factory function captures the copybutton variable properly instead
        # of it being overwritten by the last one in the loop
        def factory(COPY):
            def copy_button_onclick_function(__):
                run_to_edit()
                
                raw_code = COPY.parentElement.children[0].innerText;
                tmp = ''
                splitted = raw_code.split(';')
                splitted.pop()
                for line in splitted:
                    tmp += line
                    tmp += ';';
                    code_input_box.value = tmp;

                # Manually dispatch input event to update code_input_box code lines.
                event = document.createEvent("HTMLEvents")
                event.initEvent("input", True, True)
                event.eventName = "input"
                code_input_box.dispatchEvent(event)
            return copy_button_onclick_function

        copybutton.onclick = factory(copybutton)


def terminal_print(print_msg):
    def escape_html(s):
        return s.replace('&', '&amp;').replace('\"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    msg = escape_html(print_msg)
    box = web.page.find("#towriteinto")[0]
    potential_alr_there_msgs = web.page.find("#towriteinto span")

    max_msgs = 10
    if len(potential_alr_there_msgs) > 0:
        alr_there = len(web.page.find("#towriteinto span"))
        if (alr_there >= max_msgs):
            web.page.find("#towriteinto span")[0].first().remove()

    box.innerHTML += f'<span>{msg}<br></span>'


@when("click", "#nextnodebutton")
def next_node():
    global on_line, stack, indice

    if on_line == NO_EXECUTION_SPECIAL:
        return

    tree = all_code_ast[on_line]['tree']
    orig_tree = all_code_ast[on_line]['orig_tree']
    status, print_msg, indice = atoms.run_onestep(tree, orig_tree, stack)
    if status == atoms.ONESTEP_DONE:
        terminal_print(print_msg)
    elif status == atoms.FINISHED:
        on_line += 1
        stack = [0]


async def run_canvases():
    global on_line, indice, current_highlight_action_completed, all_code_ast, all_code_vis

    header_canvas = web.page.find("#header_canvas")[0]
    def randomHsl():
        return f'hsla({random.random() * 360}, 100%, 50%, 1)'
    def get_random_color():
        padding = 6
        random_hexadecimal_in_int = int((1<<24) * random.random()) | 0
        random_hex_color_str = f'{random_hexadecimal_in_int:#0{padding}x}'
        return ''.join(['#', *random_hex_color_str.split('0x')])
    header_ctx = header_canvas.getContext("2d")
    header_canvas.width = 920;
    header_canvas.height = 90;
    
    squares = []
    gap = 20
    size = 5
    spring = 0.005;
    damping = 0.05
    init_disturbance = 10;
    max_x = header_canvas.width
    max_y = header_canvas.height

    i, j = 0, 0

    while i < max_x:
        j = 0
        while j < max_y:
            squares.append([i, j, i, j, init_disturbance * random.random(), init_disturbance * random.random(), 0, 0, get_random_color()])
            j += gap
        i += gap


    # Process other canvas: ast_canvas.
    ast_canvas = web.page.find("#ast_canvas")[0]
    ast_canvas.width = ast_canvas.offsetWidth;
    ast_canvas.height = ast_canvas.offsetHeight;

    ast_ctx = ast_canvas.getContext("2d")

    ast_ctx.font = "15px Arial"
    highlight_radius = 20

    FPS = 60;
    frames = 0;
    while True:
        if frames < (3 * FPS):
            header_ctx.clearRect(0, 0, header_canvas.width, header_canvas.height)
            for point in squares:
                header_ctx.beginPath()
                # point indices 0 and 1 are x and y
                # point indices 2 and 3 are original vals for x and y.
                # point indices 4 and 5 are dx, dy
                # point indices 6 and 7 are ddx, ddy.
                point[6] = ((point[0] - point[2]) * -1 * spring) - damping * point[4];
                point[7] = ((point[1] - point[3]) * -1 * spring) - damping * point[5];

                point[4] += point[6];
                point[5] += point[7];

                point[0] += point[4];
                point[1] += point[5];

                header_ctx.rect(point[0], point[1], size, size);
                header_ctx.fillStyle = point[8];
                header_ctx.fill();

        # process AST canvas
        ast_ctx.clearRect(0, 0, ast_canvas.width, ast_canvas.height)

        # if on_line is greater than all_code_* variables' length:
        # this means that the entire program has finished running
        if on_line == len(all_code_vis):
            assert on_line == len(all_code_ast)
            # as the two lists should always be the same size.
            run_to_edit()

        if state == RUNNING:
            for coord in all_code_vis[on_line]['coords']:
                node_is_being_ran = list(coord[3]) == stack[1:len(stack)]
                # need to chop off initial element in global currently-on-stack
                # when comparing to each coord's own stack.
                # this is because global currently-on-stack variable ("stack") is 
                # assuming a rooted tree.
                # then, the individual stack in each coord for each node is
                # generated when the tree is still unrooted. Hence it lacks the 0 at the start of [0, ... ]

                ast_ctx.beginPath()
                ast_ctx.rect(coord[0], coord[1], node_size:=5, node_size:=5)
                ast_ctx.fillStyle = '#9ab0ff'
                ast_ctx.fill()
                ast_ctx.font = '15px Consolas'
                if node_is_being_ran:
                    s = '█' * len(str(coord[2]))
                    ast_ctx.fillStyle = '#FF0000'
                    ast_ctx.fillText(s, coord[0], coord[1])

                ast_ctx.fillStyle = '#222222'  if not node_is_being_ran else '#FFFFFF'
                ast_ctx.fillText(coord[2], coord[0], coord[1])

            # draw lines between nodes.
            for line in all_code_vis[on_line]['lines']:
                ast_ctx.beginPath()
                ast_ctx.moveTo(line[0][0], line[0][1])
                ast_ctx.lineTo(line[1][0], line[1][1])
                ast_ctx.lineWidth = 0.5 
                ast_ctx.strokeStyle = '#222222'
                ast_ctx.stroke()

        if state == RUNNING:
            web.page.find("#codeinputbox")[0].disabled = True
            js.document.getElementById("lockimg").style.display = 'block';
        elif state == EDITING:
            web.page.find("#codeinputbox")[0].disabled = False
            js.document.getElementById("lockimg").style.display = 'none';

        # Display which line is being ran in the AST canvas
        raw_code = web.page.find("#codeinputbox")[0].value
        top_level_functions = raw_code.split(';')
        # the last ; generates a trailing empty element
        top_level_functions.pop() if top_level_functions[-1] == '' else None

        if state == RUNNING:
            current_line = top_level_functions[on_line].strip()
            ast_ctx.beginPath()
            ast_ctx.fillStyle = "#000000"
            ast_ctx.font = "15px consolas"
            display_char_limit = 35  # ast_canvas width is too narrow to always preview the whole line.

            ast_ctx.fillText(f'Executing function #{on_line+1}: {current_line if len(current_line) < 20 else f"{current_line[:display_char_limit]}, ..."}', 10, 20)
            ast_ctx.stroke()

        # Highlight the line that is being executed in the line numbers bar.

        # we need a mapping between on_line, which counts an entire (while... ) as
        # one line despite it spanning across several lines in textarea (since the functions
        # inside have whitespace), and the actual line number in the bar #linenumbers.

        # to do this, iterate through top_level_functions, and for each 'line', count the whitespace.
        # count leading whitespace and middle whitespace.
        def leading_whitespace(s):
            i = 0
            for c in s:
                if c == '\n':
                    i += 1
                else:
                    return i
            return 0
        def non_leading_whitespace(s):
            return s.count('\n') - leading_whitespace(s)
        for i, _ in enumerate(top_level_functions):
            if i == 0:
                o = 1 + leading_whitespace(top_level_functions[0])
                out = [(o, i + 1, top_level_functions[i])]
            else:
                o += leading_whitespace(top_level_functions[i]) + non_leading_whitespace(top_level_functions[i - 1])
                out.append((o, i + 1, top_level_functions[i]))
        for display_line_num, internal_line_num, line_text in out:
            # on_line starts from 0 while these loop variables start from 1.
            # so do on_line + 1
            if internal_line_num == on_line + 1:
                # Find the num in the line numbers div that matches with current display_line_num.
                for span_elem in web.page.find("#linenumbers")[0].children:
                    if span_elem.textContent != '':
                        # So if the span_elem isn't the empty br element
                        if int(span_elem.textContent) == display_line_num:
                            ast_ctx.fillText(f'Located on line {display_line_num}', 10, 40)
                            span_elem.style = 'color: #00DD00; text-decoration: underline; font-weight: bold;'
                        else:
                            span_elem.style = 'color: grey'

        if state == EDITING:
            # reset the green line number when running has stopped.
            # just reset all of them.
            for span_elem in web.page.find("#linenumbers")[0].children:
                span_elem.style = 'color: grey'


        # Display variables
        step = 15
        variables_table_y = 50
        ast_ctx.font = '15px Arial'
        ast_ctx.fillText('Variables: ', 350, variables_table_y)
        ast_ctx.font = '11px consolas'
        for k, key in enumerate(atoms.global_variables):
            ast_ctx.fillText(f'{key} = {atoms.global_variables[key]}', 350, variables_table_y + step * (k + 1))

        # Debug
        if debug:
            ast_ctx.fillText(f'Debug vars', 50, 330)
            ast_ctx.fillText(f'On_line: {on_line}', 50, 350)


        # assert consistency of state variables.
        if state == EDITING:
            assert stack == NO_EXECUTION_SPECIAL
            assert on_line == NO_EXECUTION_SPECIAL
            assert all_code_ast == []
            assert all_code_vis == []
        elif state == RUNNING:
            assert on_line != NO_EXECUTION_SPECIAL


        await asyncio.sleep(1/FPS);
        frames += 1


    


if __name__ == '__main__':
    # Signal to a.js that pyscript has loaded, to
    # make the loading screen disappear.
    event = document.createEvent("Events")
    event.initEvent("custom_event_", True, True)
    event.eventName = "custom_event_"
    window.dispatchEvent(event)

    assign_copybuttons_onclick()
    await run_canvases()

