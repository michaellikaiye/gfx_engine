# final project Team Clockworks: Jiayang Chen and Michael Ye
#Period 4
## Features:

- mesh

  - accepts input of vertices and face

- adding nonlinear time functions to vary (EXPONENTIAL, LOGARITHMIC)

  - ex. vary spiny initFrame termFrame initValue termValue [EXPONENTIAL]

- "path" command to define a path (using bezier curve) and then allow "move" to accept a path and move along that path.
Just don't specify anything if you want a linear path.

  - ex. path whirl x0 y0 x1 y1 x2 y2 x3 y3 \n move whirl

- new shapes: cone, cylinder 
 
  - ex. cone centerX centerY centerZ r h (of base circle)

  - ex. cylinder centerX centerY centerZ r h (of base circle, height is the other base)
