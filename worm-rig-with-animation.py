import maya.cmds as cmds
import math as m
import random as rd

w_count = input("Number of worms (at least 1): \n")
w_length = input("Length of worm (at least 3): \n")
#inputs
while w_length < 1:
    w_length = input("Number of worms (at least 1): \n")
while w_length < 3:
    w_length = input("Length of worm (at least 3): \n")
#clear space
if len(cmds.ls('worm*')) > 0:
    cmds.delete(cmds.ls('worm*'))
#joints, drivers, puppets
for i in range(w_count):
    cmds.group(em = True, name = 'worm{}'.format(i))
    cmds.group(em = True, name = "worm{}_driver".format(i))
    cmds.group(em = True, name = "worm{}_puppet".format(i))
    #drivers
    for j in range(w_length):
        spherename = 'worm{}_body{}'.format(i, j)
        cmds.sphere(r = 1, name = spherename)
        cmds.move(j, 0, 2*i, spherename)
        cmds.setAttr(spherename+".visibility", 0)
    #puppets
    for j in range(w_length):
        puppetname = 'worm{}_puppet{}'.format(i,j)
        cmds.sphere(r = 1, name = puppetname)
        cmds.move(j, 0, 2*i, puppetname)
        cmds.setAttr(puppetname+".visibility", 0)
    #joints
    cmds.select(cl = True)
    for j in range(w_length):
        spherename = 'worm{}_body{}'.format(i, j)
        jointname = 'worm{}_joint{}'.format(i, j)
        location = (cmds.getAttr(spherename+'.translateX'), cmds.getAttr(spherename+'.translateY'), cmds.getAttr(spherename+'.translateZ'))  
        cmds.joint(p = location, name = jointname)
    #trailing
    for j in range(w_length-1):
        cmds.geometryConstraint('worm{}_puppet{}'.format(i, j), 'worm{}_puppet{}'.format(i, j+1))
    for j in range(w_length):
        puppetname = 'worm{}_puppet{}'.format(i,j)
        spherename = 'worm{}_body{}'.format(i, j)
        jointname = 'worm{}_joint{}'.format(i, j)
        cmds.pointConstraint(spherename, jointname)
        #puppeting constraint
        cmds.expression(s="\n%s.translateX = %s.translateX;\n%s.translateZ = %s.translateZ;"%(spherename, puppetname,spherename,puppetname), name = puppetname+"_exp")
    #joint aim
    for j in range(w_length-1):
        cmds.aimConstraint('worm{}_body{}'.format(i, j+1), 'worm{}_joint{}'.format(i, j), mo = True)
    #book keeping / grouping
    for j in range(w_length):        
        cmds.parent('worm{}_body{}'.format(i, j), 'worm{}_driver'.format(i), r = True)
        cmds.parent('worm{}_puppet{}'.format(i, j), 'worm{}_puppet'.format(i), r = True)
    cmds.parent('worm{}_driver'.format(i), 'worm{}'.format(i))
    cmds.parent('worm{}_puppet'.format(i), 'worm{}'.format(i))
    cmds.parent('worm{}_joint0'.format(i), 'worm{}'.format(i)) 
    #making start position   
    cmds.polyCone(sa = 6, h = 0.9, r = 0.5, name = "worm{}_start".format(i))
    cmds.move(0, 3, 2*i)
    cmds.rotate( 180, 0, 0, r=True )
    cmds.parent("worm{}_start".format(i), 'worm{}'.format(i))
    #crawl towards target
    random = rd.uniform(-1, 1)
    crawl = "$sum = "
    for j in range(w_length):
        selves = 'worm{}_body{}'.format(i, j)
        crawl += selves + ".translateY + "
    crawl += "0;\n$height = $sum/float(%s);" % (w_length)
    head = 'worm{}_puppet0'.format(i)
    start = 'worm{}_start'.format(i)
    crawl += "\nvector $head = <<%s.translateX, 0, %s.translateZ>>;\nvector $target = <<target.translateX, 0, target.translateZ>>;\nvector $vector = $target - $head;\nvector $unit = unit($vector);\nvector $perp = <<-$unit.z, 0, $unit.x>>*sin(time)*%s;\n$mod = ($height*0.5+1.5);\n$dist = mag($vector);\nif (target.edit_enabled == 1 || frame == 1) {\n\t%s.translateX = %s.translateX;\n\t%s.translateZ = %s.translateZ;\n} else {if ($dist > 0.5) {\n\t%s.translateX += $unit.x*0.06*(time/time)*$mod+$perp.x*0.06*(time/time);\n\t%s.translateZ += $unit.z*0.06*(time/time)*$mod+$perp.z*0.06*(time/time);\n}}" % (head, head, random, head, start, head, start, head, head)
    cmds.expression(s = crawl, name = start+"_exp")
cmds.select(cl = True) 

#movement
for i in range(w_count):
    #collsions
    otherworms = list(range(w_count))
    otherworms.remove(i)
    if len(otherworms) > 0:
        for j in range(w_length):
            expression = ''
            selves = 'worm{}_body{}'.format(i, j)
            expression += 'vector $self = <<%s.translateX, %s.translateY, %s.translateZ>>;\nvector $targetXZ = <<target.translateX, 0, target.translateZ>>;\n$self2targ = mag($targetXZ - $self);\nif (%s.translateY < 0) {\n\t%s.translateY = 0;\n}' % (selves, selves, selves, selves, selves)
            for k in otherworms:
                for l in range(w_length):
                    l = w_length-l-1
                    coordinate = "{}{}".format(k,l)
                    other = 'worm{}_body{}'.format(k, l)
                    expression += "\n\nvector $other%s = <<%s.translateX, %s.translateY, %s.translateZ>>;\n$dist%s = mag($other%s - $self);\n$other%starg = mag($targetXZ - $other%s);\nif ($self2targ > $other%starg) {\n\tif ($dist%s > 2.1 && %s.translateY > 0) {\n\t\t%s.translateY -= 0.1*(time/time);\n\t}\n\tif ($dist%s < 2) {\n\t\t%s.translateY += 0.1*(time/time);\n\t}\n} else if ($self2targ < $other%starg) {\n\tif ($dist%s > 2.1 && %s.translateY > 0) {\n\t\t%s.translateY -= 0.1*(time/time);\n\t}\n} else {\n\t%s.translateY += 0;\n}" % (coordinate, other, other, other, coordinate, coordinate, coordinate, coordinate, coordinate, coordinate, selves, selves, coordinate, selves, coordinate, coordinate, selves, selves, selves)
            #cmds.expression(s = expression, name = selves+'_exp')
    