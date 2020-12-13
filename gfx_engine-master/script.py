import mdl
from display import *
from matrix import *
from draw import *
import math

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    name = 'a'
    num_frames = 1
    for command in commands:
        if command['op'] == 'basename':
            name = command['args'][0]
        elif command['op'] == 'frames':
            num_frames = command['args'][0]

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [{} for i in range(int(num_frames)) ]
    for command in commands:
        print(command)
        if command['op'] == "vary":
            knob = command['knob']
            args = command['args']
            length = args[1] - args[0]
            dv = args[3] - args[2]
            if command['type'] == 'LINEAR':
                dvdt = dv/length
                for i in range(int(length)):
                    frames[int(i+args[0])][knob] = args[2] + dvdt * i
            elif command['type'] == 'EXPONENTIAL':
                #http://www.pmean.com/10/ExponentialInterpolation.html
                a = args[0]
                b = args[1]
                c = args[2]
                d = args[3]
                k = (1.5*(d-c))/(b-a)
                u = (c-d) / (math.exp(k*a)-math.exp(k*b))
                v = c - u * math.exp(k*a)
                for i in range(int(length)):
                    x = i + a
                    y = u * math.exp(k*x) + v
                    frames[int(x)][knob] = y
            elif command['type'] == 'LOGARITHMIC':
                a = args[0]
                b = args[1]
                c = args[2]
                d = args[3]
                k = -1*(1.5*(d-c))/(b-a)
                u = (c-d) / (math.exp(k*a)-math.exp(k*b))
                v = c - u * math.exp(k*a)
                for i in range(int(length)):
                    x = i + a
                    y = u * math.exp(k*x) + v
                    frames[int(x)][knob] = y
        elif command['op'] == 'path':
            args = command['args']
            pathname = command['pathname']
            ifr = int(args[0])
            efr = int(args[1])
            x0,y0,x1,y1,x2,y2,x3,y3 = args[2:10]
            pts = get_bezier_points(x0,y0,x1,y1,x2,y2,x3,y3,efr-ifr)
            for i in range(efr-ifr):
                frames[int(i+ifr)][pathname] = pts[i]
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [255, 255, 255]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)
    indexcounterthing = 0
    for frame in frames:
        symbols.update(frame)
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for command in commands:
            c = command['op']
            args = command['args']
            knob_value = 1
            if c == 'mesh':
                if command['constants']:
                    reflect = command['constants']
                vets = []
                nors = []
                iz = 0
                gg = open(command['cs'] + '.obj', 'r')
                polymon = []
                for line in gg.readlines():
                    words = line.split()
                    if (len(words) == 0):
                        continue
                    if words[0] == 'v':
                        vets.append([float(words[1]), float(words[2]), float(words[3])])
                    if words[0] == 'vn':
                        nors.append([float(words[1]), float(words[2]), float(words[3])])
                    if words[0] == 'f':
                        f = []
                        for j in range(1, len(words)):
                            if words[j].count('/') == 0:
                                f.append(vets[int(words[j])-1])
                            else:
                                s = words[j].split('/')
                                f.append(vets[int(s[0])-1])
                        if len(f) > 2:
                            for i in range(2, len(f)):
                                add_polygon(polymon, f[0][0],f[0][1],f[0][2],
                                                 f[i-1][0],f[i-1][1],f[i-1][2],
                                                 f[i][0],f[i][1],f[i][2])
                                add_polygon(polymon, f[i][0],f[i][1],f[i][2],
                                                 f[i-1][0],f[i-1][1],f[i-1][2],
                                                 f[0][0],f[0][1],f[0][2])
                                
                matrix_mult( stack[-1], polymon)
                draw_polygons(polymon, screen, zbuffer, view, ambient, light, symbols, reflect)
                gg.close()
            elif c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,args[0], args[1], args[2],args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                               args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'cylinder':
                if command['constants'] is not None:
                    reflect = command['constants']
                add_cylinder(tmp, args[0],args[1],args[2],args[3],args[4], step_3d)
                matrix_mult(stack[-1],tmp)
                draw_polygons(tmp,screen,zbuffer,view,ambient,light,symbols,reflect)
                tmp = []
                reflect = '.white'
            elif c == 'cone':
                if command['constants'] is not None:
                    reflect = command['constants']
                add_cone(tmp, args[0],args[1],args[2],args[3],args[4],step_3d)
                matrix_mult(stack[-1],tmp)
                draw_polygons(tmp,screen.zubffer,view,ambient.light,symbols,reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                    add_edge(tmp,
                                     args[0], args[1], args[2], args[3], args[4], args[5])
                    matrix_mult( stack[-1], tmp )
                    draw_lines(tmp, screen, zbuffer, color)
                    tmp = []
            elif c == 'move':
                if command['path'] is not None:
                    path = symbols[command['path']]
                    tmp = make_translate(path[0], path[1], 0)
                    matrix_mult(stack[-1],tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
                else:
                    v=1
                    if command['knob'] is not None:
                        v = symbols[command['knob']]
                    tmp = make_translate(args[0] * v, args[1] * v, args[2] * v)
                    matrix_mult(stack[-1], tmp)
                    stack[-1] = [x[:] for x in tmp]
                    tmp = []
            elif c == 'scale':
                v=1
                if command['knob'] is not None:
                    v = symbols[command['knob']]
                tmp = make_scale(args[0] * v, args[1] * v, args[2] * v)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                v=1
                if command['knob'] is not None:
                    v = symbols[command['knob']]
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta*v)
                elif args[0] == 'y':
                    tmp = make_rotY(theta*v)
                else:
                    tmp = make_rotZ(theta * v)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        print('/anim/' + name + "%03d"%indexcounterthing)
        save_extension(screen, 'anim/' + name + "%03d"%indexcounterthing)
        indexcounterthing += 1
        # end operation loop
    make_animation(name)
