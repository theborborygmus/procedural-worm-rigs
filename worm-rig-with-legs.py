import maya.cmds as cmds
import math as m

w_count = 1
w_length = input("Length of worm: \n")
while w_length < 3:
    w_length = input("Please choose a length of at least 3:\n")

cmds.delete(cmds.ls('worm*'))

#loops for creating appendages
def LEFTchildjoint(parentjoint, parentcontrol, i, j, k):
    jointname = 'worm{}_joint_Lleg{}_joint{}'.format(i, j+1, k)
    controlname = 'worm{}_Lleg{}_joint{}'.format(i, j+1, k)
    cmds.select(cl = True)
    x = cmds.getAttr('locator{}_lleg{}_joint{}.translateX'.format(i, j+1, k)) 
    y = cmds.getAttr('locator{}_lleg{}_joint{}.translateY'.format(i, j+1, k))
    z = cmds.getAttr('locator{}_lleg{}_joint{}.translateZ'.format(i, j+1, k))
    cmds.joint(p = (x, y, z), name = jointname)
    cmds.parent(jointname, parentjoint)
    cmds.circle(nr = (0, -0.5, -1*(1-k*.5)), r = 0.3, name = controlname)
    cmds.setAttr(controlname+".overrideEnabled", 1)
    cmds.move(x, y ,z, controlname)
    cmds.parent(controlname, parentcontrol)
    cmds.parentConstraint(controlname, jointname)
    return jointname, controlname
def RIGHTchildjoint(parentjoint, parentcontrol, i, j, k):
    jointname = 'worm{}_joint_Rleg{}_joint{}'.format(i, j+1, k)
    controlname = 'worm{}_Rleg{}_joint{}'.format(i, j+1, k)
    cmds.select(cl = True)
    x = cmds.getAttr('locator{}_rleg{}_joint{}.translateX'.format(i, j+1, k)) 
    y = cmds.getAttr('locator{}_rleg{}_joint{}.translateY'.format(i, j+1, k))
    z = cmds.getAttr('locator{}_rleg{}_joint{}.translateZ'.format(i, j+1, k))
    cmds.joint(p = (x, y, z), name = jointname)
    cmds.parent(jointname, parentjoint)
    cmds.circle(nr = (0, -0.5, 1*(1-k*.5)), r = 0.3, name = controlname)
    cmds.setAttr(controlname+".overrideEnabled", 1)
    cmds.move(x, y ,z, controlname)
    cmds.parent(controlname, parentcontrol)
    cmds.parentConstraint(controlname, jointname)
    return jointname, controlname


for i in range(0, w_count):
    cmds.circle(r = (w_length+1)*0.5, nr = (0, 1, 0), name = "worm{}_master".format(i))
    cmds.move(0.5*(w_length-1), 0, 0)
    cmds.makeIdentity("worm{}_master".format(i), apply=True, translate=True, rotate=True)
    #creating drivers, joints, controls
    cmds.group(em = True, name = 'worm{}'.format(i))
    for j in range(0, w_length):
        spherename = 'worm{}_body{}'.format(i, j)
        jointname = 'worm{}_joint{}'.format(i, j)
        #drivers & controls
        cmds.sphere(r = 1, name = spherename)
        cmds.move(j, 0, 0, spherename)
        cmds.setAttr(spherename+"Shape.overrideEnabled", 1)
        cmds.setAttr(spherename+"Shape.overrideShading", 0)
        cmds.setAttr(spherename+"Shape.overrideTexturing", 0)
        #joints
        cmds.select(cl = True)
        location = (cmds.getAttr(spherename+'.translateX'), cmds.getAttr(spherename+'.translateY'), cmds.getAttr(spherename+'.translateZ'))  
        cmds.joint(p = location, name = jointname)
        #freeze transformation
        cmds.makeIdentity(spherename, apply=True, translate=True, rotate=True)
        #cmds.hide(spherename)

    #creating legs
    for j in range(0, w_length-2):
        #left legs
        parentjoint = 'worm{}_joint{}'.format(i, j+1)
        parentcontrol = 'worm{}_body{}'.format(i, j+1)
        for k in range(0,3):
            parentjoint, parentcontrol = LEFTchildjoint(parentjoint, parentcontrol, i, j, k)
        #rightlegs
        parentjoint = 'worm{}_joint{}'.format(i, j+1)
        parentcontrol = 'worm{}_body{}'.format(i, j+1)
        for k in range(0,3):
            parentjoint, parentcontrol = RIGHTchildjoint(parentjoint, parentcontrol, i, j, k)

    #setting up joint hierarchy & drivers
    for j in range(0, w_length-1):
        cmds.parent('worm{}_joint{}'.format(i, j+1), 'worm{}_joint{}'.format(i, j))
        cmds.geometryConstraint('worm{}_body{}'.format(i, j), 'worm{}_body{}'.format(i, j+1))
        cmds.aimConstraint('worm{}_body{}'.format(i, j+1), 'worm{}_body{}'.format(i, j), mo = True)
    cmds.aimConstraint('worm{}_body{}'.format(i, w_length-2), 'worm{}_body{}'.format(i, w_length-1), mo = True)
    #binding drivers to joints
    for j in range(0, w_length):
        spherename = 'worm{}_body{}'.format(i, j)
        jointname = 'worm{}_joint{}'.format(i, j)
        cmds.pointConstraint(spherename, jointname, mo = True)
        cmds.orientConstraint(spherename, jointname, mo = True)
    
    #book keeping / grouping
    for j in range(0, w_length):        
        cmds.parent('worm{}_body{}'.format(i, j), 'worm{}_master'.format(i), r = True)
    cmds.parent('worm{}_master'.format(i), 'worm{}'.format(i))
    cmds.parent('worm{}_joint0'.format(i), 'worm{}'.format(i)) 
                
cmds.select(cl = True) 