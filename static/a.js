let canvashtml = document.body.children[0].children[0].children[2];

function randomHsl() {
    return 'hsla(' + (Math.random() * 360) + ', 100%, 50%, 1)';
}

var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

canvas.width = 920;
canvas.height= 90;

let a = [];
let gap = 20;
let size = 5;
let spring = 0.005;
let damping = 0.05;
let init_disturbance = 20;

let max_x = canvas.width;
let max_y = canvas.height;

function get_random_color() {
	return "#" + ((1 << 24) * Math.random() | 0).toString(16).padStart(6, "0");
}

for (var i = 0; i < max_x; i += gap) {
    for (var j = 0; j < max_y; j += gap) {
        a.push([i, j, i, j, init_disturbance * Math.random(), init_disturbance * Math.random(), 0, 0, get_random_color()])
    }
}

b = [
	[20, 0, 20, 0],
	[40, 0, 40, 0],
	[0, 20, 0, 20],
	[20, 40, 20, 40],
	[40, 40, 40, 40],
	[60, 60, 60, 60],
	[40, 80, 40, 80],
	[20, 80, 20, 80],

	[100, 0, 100, 0],
	[120, 0, 120, 0],
	[140, 0, 140, 0],
	[160, 0, 160, 0],

	[120, 20, 120, 20],
	[140, 20, 140, 20],
	[120, 40, 120, 40],
	[140, 40, 140, 40],
	[120, 60, 120, 60],
	[140, 60, 140, 60],
	[120, 80, 120, 80],
	[140, 80, 140, 80],
	[100, 80, 100, 80],

	[160, 80, 160, 80],

]

b.forEach((elem) => {
	elem.push(init_disturbance * Math.random(), init_disturbance * Math.random(), 0, 0, get_random_color());


})

b = a;

var begin = Date.now();
function draw() {

    ctx.clearRect(0, 0, canvas.width, canvas.height);


    b.forEach(function(point){

		ctx.beginPath();

		point[6] = ((point[0] - point[2]) * -spring) - damping * point[4];
        point[7] = ((point[1] - point[3]) * -spring) - damping * point[5];

        point[4] += point[6];
        point[5] += point[7];

        point[0] += point[4];
        point[1] += point[5];

        ctx.rect(point[0], point[1], size, size);
        ctx.fillStyle = point[8];
		//ctx.fillStyle = '#FC6C85';
        ctx.fill();
    });

}

canvas_one_id = setInterval(draw, 30);
setTimeout(() => {clearInterval(canvas_one_id);}, 5 * 1000);


var cv2 = document.getElementById("secondcanvas");
cv2.setAttribute('width', cv2.offsetWidth);
cv2.setAttribute('height', $("#codeinputbox").height());
var c2 = cv2.getContext("2d");

//var coords = [];
//var lines = [];
var Response = [];
var on_line = 0;
var coords = [];
var lines = [];
var jj = 0;

function escapeHTML(s) { 
        return s.replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
function print_msg(msg) {
    

    msg = escapeHTML(msg);
    
    var box = $("#towriteinto");
    var alr_there = $("#towriteinto span").length;
    var max_msgs = 10;
    if (alr_there < max_msgs) {
        box.append(`<span>${msg}<br></span>`);
    } else {
        $("#towriteinto span").first().remove();
        box.append(`<span>${msg}<br></span>`);
    }
    jj++;
}

let NEXT_LINE = 'NEXT_LINE';
let START_NEW_PROGRAM = 'START_NEW_PROGRAM';

let CLEAR_VARIABLES = 'CLEAR_VARIABLES';
let KEEP_VARIABLES = 'KEEP_VARIABLES';
function run(type_) {
    if ($("#codeinputbox").text().trim() === "summer daze") {
        window.open('https://www.youtube.com/watch?v=gmcVvQjPMUU&list=RDMMgmcVvQjPMUU', '_blank').focus();
        return;
    }
    // Type can either be 'next line' (> button leading to a new line)
    // or 'start new program' (a button press i.e. a whole new program loaded.)

    // in the case that the code box is just one line, there is no <div> surrounding that one line.
    // this will cause an error.
    // therefore we check if $("#codeinputbox") has children elements.
    if ($("#codeinputbox").children().length === 0 && $("#codeinputbox").text() != "") {
        var past_oneliner = escapeHTML($("#codeinputbox").text());
        $("#codeinputbox").text("");
        $("#codeinputbox").append($(`<div>${past_oneliner}</div>`));
    }
    
    $.ajax({
        url: "receive",
        type: "POST",
        data: {
            code: $("#codeinputbox").text(),
            on_line: on_line,
            type_: type_
        },
        success: function (resp) {
            //service.php response
            console.log(resp);
            Response = resp;

            if (Response.variables_action == CLEAR_VARIABLES) {
                var datemod = new Date()
                print_msg(`*** L-- ${datemod.toLocaleString()} Program loaded ***`);
                global_variables = [];
                on_line = 0;
                on_stack = [0];
                started_running = false;
            }
            coords = Response.data[on_line].coords;
            lines = Response.data[on_line].lines;

        }
    });
}

var node_size = 15;
c2.font = "15px Arial";
$("#examplecodebox").width($("#rundiv").width() + $("#codeinputareadiv").width());
$("#terminal").width($("#visualiserdiv").width());

var pos_x, pos_y; // pos is the absolute position
var mouse_canvas_x, mouse_canvas_y; // relative to upper left of the canvas
var clicking = false;
var dox = 0;  // from origin
var doy = 0;
var x_before_drag = 0;
var y_before_drag = 0;// got* variables allow "one-time use" functionality within the render loop.
// For example, when the user clicks the mouse, it updates the *_before_drag
// variables. However, on the next iteration of the loop, the user is presumably
// still clicking, but the *_before_drag variables must not be changed again.
//     Thus, when the user's mouse is being clicked, we check the got variable
// and if it's false, we update the *_before_drag. We then set the got var to
// true. Then, when the user stops clicking, the got var is set to false.
//     The effect of this particular example is that across the render loop
// iterations where the mouse is held down, only the first iteration is when
// *_before_drag is updated.
var got = false;
var got1 = false;
var old_dox = 0;
var old_doy = 0;

var got5 = false;
function update_mouse_pos(e) {
    var canvas_rect = cv2.getBoundingClientRect();
    pos_x = Math.round(e.clientX - canvas_rect.left);
    pos_y = Math.round(e.clientY - canvas_rect.top);
}
function handle_keyboard(e) {
    switch (e.keyCode) {
    case 27:  // Escape key
        dox = 0;
        doy = 0;
        clicking = false;
        break;
    default:
        break;
    }
}
var clicking = false;
window.addEventListener("keydown", handle_keyboard, false);
cv2.addEventListener("mousedown", (function (e) {
    if (e.which == 1) {
        clicking = true;
    }
}), false);
cv2.addEventListener("mouseup", (function (e) {
    if (e.which == 1) {
        clicking = false;
    }
}), false);
cv2.addEventListener("mousemove", update_mouse_pos);
function point_in_tri(x1, y1, x2, y2, x3, y3, x, y) {
    var denominator = ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3));
    var a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominator;
    var b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominator;
    var c = 1 - a - b;

    return 0 <= a && a <= 1 && 0 <= b && b <= 1 && 0 <= c && c <= 1;
}
var started_running = false;
var on_stack;
var global_variables = [];
var indice = [-1, -1]
var highlighted = false;
function drawsecond() {
    mouse_canvas_x = pos_x - dox;
    mouse_canvas_y = pos_y - doy;
    if (clicking) {
        // change cursor
        document.body.style.cursor = 'grab';

        // TODO: refactor this part into event listener function?
        // That may make got* variables unnecessary.

        // update dox and doy for canvas transform
        if (!got) {
            x_before_drag = pos_x;
            y_before_drag = pos_y;
            got = true;
        }

        var dx = pos_x - x_before_drag;
        var dy = pos_y - y_before_drag;

        if (!got1) {
            old_dox = dox;
            old_doy = doy;
            got1 = true;
        }

        dox = old_dox + dx;
        doy = old_doy + dy;

    }
    //console.log(dx, dy, dox, doy);
    if (!clicking) {
        document.body.style.cursor = 'default';
        got = false;
        got1 = false;
    }
    c2.setTransform(1, 0, 0, 1, dox, doy);
    //    c2.translate(1, 1);


    c2.clearRect(-cv2.width, -cv2.height, cv2.width*5, cv2.height*5);//*5 to cover the tearing
    // as a result of the drag-to-move.

    coords.forEach(function(coord) {
        c2.beginPath();
        c2.rect(coord[0], coord[1], node_size, node_size);
        c2.fillStyle = '#9ab0ff';
        c2.fill();

        c2.fillStyle = '#222222';
        c2.fillText(coord[2], coord[0], coord[1]);
    });

    lines.forEach(function(line) {
        c2.beginPath();
        c2.moveTo(line[0][0], line[0][1]);
        c2.lineTo(line[1][0], line[1][1]);
        c2.lineWidth = 1;
        c2.strokeStyle='black';
        c2.stroke();
    });

    c2.fillStyle = '#00EE00';
    var run_x = 10;
    var run_width = 70;

    var run_height = 50;
    var margin = 30;
    var run_y = cv2.height - run_height - margin;

    if (point_in_tri(run_x, run_y, run_x, run_y + run_height, run_x + run_width, run_y + run_height / 2, pos_x, pos_y)) {
        c2.fillStyle = '#00AA00';
        document.body.style.cursor = 'grab';
        if (clicking && !got5 && !(coords.length === 0) && !(lines.length === 0)) {

            $.ajax({
                url: "next",
                type: "POST",
                data: {
                    on_line
                },
                success: function (response) {
                                highlighted = false;
                    //service.php response
                    console.log(response);

                    if (response.status == "whole line finished") {
                        var nohighlight = $("#codeinputbox").children()[on_line].textContent;
                        nohighlight = escapeHTML(nohighlight);
                        $($("#codeinputbox").children()[on_line]).replaceWith($(`<div>${nohighlight}</div>`));

                        console.log("whole line finished");
                        on_line ++;
                        if (on_line == Response.data.length) {
                            Response = [];
                            coords = [];
                            lines = [];
                            on_line = 0;
                        } else if (on_line < Response.data.length) {
                            run(NEXT_LINE)
                        }

                                                
                    } else if (response.status == "onestep finished no print") {
                        started_running = true;
                        on_stack = response.stack;
                        global_variables = response.global_variables;
                    }
                      else if (response.status == "onestep finished") {
                        started_running = true;
                        on_stack = response.stack;
                          global_variables = response.global_variables;
                          print_msg(response.print_msg);
                    } else {
                        console.warn("status");
                    }
                    indice = response.indice;
                }
            });
            got5 = true;
        }

        if (!clicking) {
            got5 = false;
        }
    }

    var highlight_radius = 20;
    if (started_running) {
        coords.forEach(function(coord) {
            if (coord[3].join() == on_stack.join()) {
                c2.beginPath();
                c2.arc(coord[0] +(node_size/2), coord[1] + (node_size/2), highlight_radius, 0, 2*Math.PI);

                c2.lineWidth = 2.5;
                c2.strokeStyle='#FF0000';
                c2.stroke();
            }
        });

        if (indice[0] >= 0 && indice[1] >= 0 && highlighted === false && !(indice[0] === null) && !(indice[1] === null)) {
            console.log(indice[0], indice[1]);
            var aa = $("#codeinputbox").children()[on_line].textContent;
            aa = aa.replace(/[\n\r\t]/gm, "");
            aa = aa.replace(/  +/g, ' ');

            var before = escapeHTML(aa.substring(0, indice[0]));
            var substr = escapeHTML(aa.substring(indice[0], indice[1]+2));
            var after = escapeHTML(aa.substring(indice[1]+2, aa.length));
            // Watch out for XSS here
            var newelem = $(`<div>${before}<span style="background-color:lightblue">${substr}</span>${after}</div>`);
            $($("#codeinputbox").children()[on_line]).replaceWith(newelem);  // the additional sigil wrapping
            // is to ensure keep using jquery method of replaceWith, instead of native method
            // which replaces wrongly ('[Object object]').
            highlighted = true;
        }
        
    }
    c2.beginPath();
    c2.moveTo(run_x - dox, run_y - doy);
    c2.lineTo(run_x- dox, run_y + run_height  - doy);
    c2.lineTo((run_x+run_width)- dox, run_y + run_height/2 - doy);
    c2.fill();

    c2.fillStyle = '#000000';
    c2.fillText('Next node', run_x - dox, run_y + run_height + margin / 2 - doy);


    c2.fillStyle = '#005500';
    if (point_in_tri(150, run_y, 150, run_y + run_height, 150 + run_width, run_y + run_height / 2, pos_x, pos_y) || point_in_tri(170, run_y, 170, run_y + run_height, 170 + run_width, run_y + run_height / 2, pos_x, pos_y)) {
        c2.fillStyle = '#003300';
        document.body.style.cursor = 'grab';

        if (clicking) {

        }
    }

    c2.beginPath();
    c2.moveTo(150 - dox, run_y - doy);
    c2.lineTo(150 - dox, run_y + run_height  - doy);
    c2.lineTo((150 +run_width)- dox, run_y + run_height/2 - doy);
    c2.fill();

    c2.beginPath();
    c2.moveTo(170 - dox, run_y - doy);
    c2.lineTo(170 - dox, run_y + run_height  - doy);
    c2.lineTo((170 +run_width)- dox, run_y + run_height/2 - doy);
    c2.fill();


    c2.fillStyle = '#000000';
    c2.fillText('Auto-run', 150 - dox, run_y + run_height + margin / 2 - doy);


    c2.fillStyle = '#000000';
    c2.fillText('Vars', 350 - dox, 25 - doy);
    var k = 1;
    var stepstep=15;
    Object.keys(global_variables).forEach(function(key) {
        c2.fillText(`${key} = ${global_variables[key]}`, 350 - dox, 25 + stepstep*k - doy);
        k++;
    });
}

var FPS = 30;
setInterval(drawsecond, 1000/FPS);


copybuttons = $(".copybutton")
for (var i = 0; i < copybuttons.length; i++) {
   let ii = i;  // capture lambda problem solution
    copybuttons[i].onclick = (()=>{
        var code = copybuttons[ii].parentElement.children[0].innerText;
        $("#codeinputbox").text("");


        var tmp = '';
        var splitted = code.split(';');
        splitted.pop()
        splitted.forEach((line)=>{
            tmp += '<div>';
            tmp += line;
            tmp += ';';
            tmp += '</div>';
            console.log(line);
        });

        $("#codeinputbox").append(tmp);

    });
}
