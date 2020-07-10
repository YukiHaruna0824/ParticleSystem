import bpy
from bpy.props import *
from mathutils import Vector, Euler, Matrix

from .particle import *
from .spring import *
from .wall import *

import time
import math

class EnvironmentManager():
    gravity_scale = 1
    frame_rate = 50
    delta_t = 0.02
    isPlaying = False
    moving_method = 'euler'

class WallManager():
    wall_counts = 0
    walls = []

class ParticleManager():
    particle_counts = 0
    # key : 'Ptc' + uid, value : paricle object
    particles = {}

    def checkCollision():
        ptc_list = list(ParticleManager.particles.values())
        length = len(ptc_list)
        for i in range(0, length):
            for j in range(i + 1, length):
                ptc1 = ptc_list[i]
                ptc2 = ptc_list[j]
                if (ptc1.obj.location - ptc2.obj.location).length < ptc1.radius + ptc2.radius:
                    v1 = ((ptc1.mass - ptc2.mass) * ptc1.velocity + 2 * ptc2.mass * ptc2.velocity) / (ptc1.mass + ptc2.mass)
                    v2 = ((ptc2.mass - ptc1.mass) * ptc2.velocity + 2 * ptc1.mass * ptc1.velocity) / (ptc1.mass + ptc2.mass)
                    ptc1.velocity = v1
                    ptc2.velocity = v2
                    ptc1.simVel = v1
                    ptc2.simVel = v2

class SpringManager():
    spring_counts = 0
    #key : 'Ptc' + uid + '_' + 'Ptc' + uid, value : spring object
    springs = {}

#update by frame rate
def update():
    #tick = time.time()
    if EnvironmentManager.isPlaying:
        if EnvironmentManager.moving_method == 'euler':
            for step in range(2):
                for ptc in ParticleManager.particles.values():
                    ptc.euler(EnvironmentManager.delta_t, step)
        elif EnvironmentManager.moving_method == 'runge_kutta2':
            for step in range(4):
                for ptc in ParticleManager.particles.values():
                    ptc.runge_kutta2(EnvironmentManager.delta_t, step)
        elif EnvironmentManager.moving_method == 'runge_kutta4' or EnvironmentManager.moving_method == 'implicit euler':
            for step in range(8):
                for ptc in ParticleManager.particles.values():
                    ptc.runge_kutta4(EnvironmentManager.delta_t, step)
        elif EnvironmentManager.moving_method == 'verlet':
            for step in range(4):
                for ptc in ParticleManager.particles.values():
                    ptc.verlet(EnvironmentManager.delta_t, step)
        elif EnvironmentManager.moving_method == 'leapfrog':
            for step in range(4):
                for ptc in ParticleManager.particles.values():
                    ptc.leapfrog(EnvironmentManager.delta_t, step)
        elif EnvironmentManager.moving_method == 'symplectic':
            for step in range(2):
                for ptc in ParticleManager.particles.values():
                        ptc.symplectic(EnvironmentManager.delta_t, step)

        for ptc in ParticleManager.particles.values():
            ptc.update()
        for spring in SpringManager.springs.values():
            spring.update()

        ParticleManager.checkCollision()

    '''
    tick1 = time.time()
    print(tick1 - tick)
    '''

    return float(1 / EnvironmentManager.frame_rate)


class MyPreferece(bpy.types.PropertyGroup):
    def updateFrameRate(self, context):
        EnvironmentManager.frame_rate = self.frame_rate
    frame_rate = IntProperty(name='Frame Rate', default=40, update=updateFrameRate, min=1, max=60)

    def updateGravityScale(self, context):
        EnvironmentManager.gravity_scale = self.gravity_scale
    gravity_scale = FloatProperty(name='Gravity Scale', default=1, update=updateGravityScale, min=0, max=2)

    def updateDeltaTime(self, context):
        EnvironmentManager.delta_t = self.delta_t
    delta_t = FloatProperty(name='deltaTime', default=0.02, update=updateDeltaTime, min=0.01, max=0.1)

    def loadMethod(self, context):
        method = [('euler','euler',''),('runge_kutta2','runge_kutta2',''),('runge_kutta4','runge_kutta4',''),('verlet', 'verlet', ''),('leapfrog', 'leapfrog', ''), ('symplectic', 'symplectic', ''), ('implicit euler', 'implicit euler', '')]
        return method
    def updateMethod(self, context):
        EnvironmentManager.moving_method = self.moving_method
    moving_method = EnumProperty(name='Moving Method', items = loadMethod, update = updateMethod)


#Panel
class Test_Panel(bpy.types.Panel):
    bl_idname = 'Test_Panel'
    bl_label = 'Test Panel'
    bl_category = 'ParticleSystem'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pref = scene.setting

        #Particle Operatrion
        col = layout.column()
        col.label(text="Particle Operation")
        row = col.row()
        row.operator('ops.addparticle', text='Add Particle')
        row.operator('ops.editparticle', text='Edit Particle')
        row.operator('ops.deleteparticle', text='Delete Particle')

        #Spring Operatrion
        col = layout.column()
        col.label(text='Spring Operation')
        row = col.row()
        row.operator('ops.addspring', text='Add Spring')


        #Grid Operation
        col = layout.column()
        col.label(text='Grid Operation')
        row = col.row()
        row.operator('ops.addcloth', text='Add Cloth')

        col = layout.column()
        col.label(text='Wall Operation')
        row = col.row()
        row.operator('ops.addwall', text='Add Wall')

        col = layout.column()
        col.label(text='Environment Setting')
        row = col.row()
        row.prop(pref, 'gravity_scale')
        row = col.row()
        row.prop(pref, 'delta_t')

        row = col.row() 
        row.prop(pref, 'frame_rate')
        if EnvironmentManager.isPlaying:
            row.operator('ops.playbutton', text='Pause', icon='PAUSE')
        else:
            row.operator('ops.playbutton', text='Play', icon='PLAY')

        row = layout.row()
        row.prop(pref, 'moving_method')


#Operator Method
class PlayButton(bpy.types.Operator):
    bl_idname = 'ops.playbutton'
    bl_label = ''
    
    def execute(self, context):
        EnvironmentManager.isPlaying = not EnvironmentManager.isPlaying
        return {'FINISHED'} 
    
class AddParticle(bpy.types.Operator):
    bl_idname = 'ops.addparticle'
    bl_label = 'Add Particle'

    kinematic = BoolProperty(name='Kinematic', default=False)
    mass = FloatProperty(name='Mass', default=1)
    radius = FloatProperty(name='radius', default=0.5, min=0.1, max=5)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Particle Property")

        row = col.row()
        row.prop(self, 'mass')
        row.prop(self, 'radius')
        row = col.row()
        row.prop(self, 'kinematic')
    
    def execute(self, context):
        name = 'Ptc' + str(ParticleManager.particle_counts)
        ParticleManager.particle_counts += 1
        cursor_location = context.scene.cursor.location
        
        bpy.ops.mesh.primitive_uv_sphere_add()
        obj = context.object
        obj.name = name 
        obj.scale = (self.radius, self.radius, self.radius)

        ptc = Particle(obj, cursor_location, self.mass, self.radius, self.kinematic)
        ParticleManager.particles[name] = ptc

        return {'FINISHED'}

class EditParticle(bpy.types.Operator):
    bl_idname = 'ops.editparticle'
    bl_label = 'Edit Particle'

    kinematic = BoolProperty(name='Kinematic')
    mass = FloatProperty(name="Mass")
    radius = FloatProperty(name='radius', default=0.5, min=0.1, max=5)

    @classmethod
    def poll(self, context):
        for obj in context.selected_objects:
            if not obj.name in ParticleManager.particles.keys():
                return False
        return len(context.selected_objects) > 0

    def invoke(self, context, event):
        objs = context.selected_objects
        self.kinematic = ParticleManager.particles[objs[0].name].kinematic
        self.mass = ParticleManager.particles[objs[0].name].mass 
        self.radius = ParticleManager.particles[objs[0].name].radius
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Particle Property")

        row = col.row()
        row.prop(self, 'mass')
        row.prop(self, 'radius')
        row = col.row()
        row.prop(self, 'kinematic')
    
    def execute(self, context):
        for obj in context.selected_objects:
            ptc = ParticleManager.particles[obj.name]
            ptc.mass = self.mass
            ptc.kinematic = self.kinematic
            ptc.radius = self.radius
            obj.scale = (self.radius, self.radius, self.radius)
        return {'FINISHED'}

class DeleteParticle(bpy.types.Operator):
    bl_idname = 'ops.deleteparticle'
    bl_label = 'Delete Particle'
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if not obj.name in ParticleManager.particles.keys():
                return False
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selected_objects:
            del ParticleManager.particles[obj.name]
        bpy.ops.object.delete()
        return {'FINISHED'}


class AddSpring(bpy.types.Operator):
    bl_idname = 'ops.addspring'
    bl_label = 'Add Spring'

    ks = FloatProperty(name='Ks', default=1.0)
    kd = FloatProperty(name='Kd', default=1.0)
    rest_length = FloatProperty(name='rest_length', default=4.0)

    @classmethod
    def poll(cls, context):
        objs = context.selected_objects
        ptc_names = ParticleManager.particles.keys()
        for obj in objs:
            if not obj.name in ptc_names:
                return False 
        
        return len(objs) > 1

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text='Spring Property')
        row = col.row()
        row.prop(self, 'ks')
        row = col.row()
        row.prop(self, 'kd')
        row = col.row()
        row.prop(self, 'rest_length')

    def execute(self, context):
        objs = context.selected_objects
        ptcs = ParticleManager.particles
        
        for i in range(0, len(objs)):
            for j in range(i + 1, len(objs)):
                ptc1 = ptcs[objs[i].name]
                ptc2 = ptcs[objs[j].name]
                
                spring_name = objs[i].name + '_' + objs[j].name
                curve = bpy.data.curves.new(spring_name, type='CURVE')
                curve.dimensions = '3D'
                polyline = curve.splines.new('POLY')
                polyline.points.add(1)
                locat1 = ptc1.obj.location
                locat2 = ptc2.obj.location
                polyline.points[0].co = (locat1.x, locat1.y, locat1.z, 1)
                polyline.points[1].co = (locat2.x, locat2.y, locat2.z, 1)
                curveObj = bpy.data.objects.new(spring_name, curve)
                context.collection.objects.link(curveObj)

                spring = Spring(curveObj, self.ks, self.kd, self.rest_length, ptc1, ptc2)
                ptc1.springs.append(spring)
                ptc2.springs.append(spring)
                SpringManager.springs[spring_name] = spring
                SpringManager.spring_counts += 1
        return {'FINISHED'}

class AddCloth(bpy.types.Operator):
    bl_idname = 'ops.addcloth'
    bl_label = 'Add Cloth'

    mass = FloatProperty(name="Mass", default=1)
    radius = FloatProperty(name='radius', default=0.5, min=0.1, max=5)

    width = IntProperty(name='Width', default=10)
    height = IntProperty(name='Height', default=10)

    ks = FloatProperty(name='Ks', default=1.0)
    kd = FloatProperty(name='Kd', default=1.0)
    bdf = FloatProperty(name='bending_force', default=1)

    rest_length = FloatProperty(name='rest_length', default=3.0)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text='Cloth Property')
        row = col.row()
        row.prop(self, 'width')
        row.prop(self, 'height')
        row = col.row()
        row.prop(self, 'mass')
        row.prop(self, 'radius')

        col = layout.column()
        col.label(text='Spring Property')
        row = col.row()
        row.prop(self, 'ks')
        row = col.row()
        row.prop(self, 'kd')
        row = col.row()
        row.prop(self, 'bdf')
        row = col.row()
        row.prop(self, 'rest_length')

    def addSpring(self, context, ptc1, ptc2, spring_const, rest_length):
        spring_name = ptc1.obj.name + '_' + ptc2.obj.name
        curve = bpy.data.curves.new(spring_name, type='CURVE')
        curve.dimensions = '3D'
        polyline = curve.splines.new('POLY')
        polyline.points.add(1)
        locat1 = ptc1.obj.location
        locat2 = ptc2.obj.location
        polyline.points[0].co = (locat1.x, locat1.y, locat1.z, 1)
        polyline.points[1].co = (locat2.x, locat2.y, locat2.z, 1)
        curveObj = bpy.data.objects.new(spring_name, curve)
        context.collection.objects.link(curveObj)

        spring = Spring(curveObj, spring_const, self.kd, rest_length, ptc1, ptc2)
        ptc1.springs.append(spring)
        ptc2.springs.append(spring)
        SpringManager.springs[spring_name] = spring
        SpringManager.spring_counts += 1

    def execute(self, context):
        cursor_location = context.scene.cursor.location
        offset = self.rest_length

        p_record = []
        for i in range(0, self.height):
            temp = []
            for j in range(0, self.width):
                name = 'Ptc' + str(ParticleManager.particle_counts)
                ParticleManager.particle_counts += 1
        
                bpy.ops.mesh.primitive_uv_sphere_add()
                obj = context.object
                obj.name = name 
                obj.scale = (self.radius, self.radius, self.radius)

                pos = cursor_location + offset * Vector((j, i, 0))
                ptc = Particle(obj, pos, self.mass, self.radius, False)
                ParticleManager.particles[name] = ptc
                temp.append(ptc)
            p_record.append(temp)

        ptcs = ParticleManager.particles
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        #bend_dirs = [(0, 2), (2, 0), (2, 2), (2, -2)]
        for i in range(0, self.height):
            for j in range(0, self.width):
                ptc1 = p_record[i][j]
                for direction in directions:
                    if 0 <= i + direction[0] < self.height and 0 <= j + direction[1] < self.width:
                        mult = math.sqrt(abs(direction[0]) + abs(direction[1]))
                        ptc2 = p_record[i + direction[0]][j + direction[1]]
                        self.addSpring(context, ptc1, ptc2, self.ks, self.rest_length * mult)
                '''
                for bend_dir in bend_dirs:
                    if 0 <= i + bend_dir[0] < self.height and 0 <= j + bend_dir[1] < self.width:
                        mult = math.sqrt(abs(bend_dir[0]) + abs(bend_dir[1]))
                        ptc2 = p_record[i + bend_dir[0]][j + bend_dir[1]]
                        self.addSpring(context, ptc1, ptc2, self.bdf, self.rest_length * mult) 
                '''
                
             
        return {'FINISHED'}

class AddWall(bpy.types.Operator):
    bl_idname = 'ops.addwall'
    bl_label = 'Add Wall'

    length = FloatProperty(name='length', default=6, min=1, max=100)
    width = FloatProperty(name='width', default=6, min=1, max=100)
    height = FloatProperty(name='height', default=1, min=1, max=100)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Wall Property")

        row = col.row()
        row.prop(self, 'length')
        row.prop(self, 'width')
        row.prop(self, 'height')
        
    def execute(self, context):
        cursor_location = context.scene.cursor.location
        bpy.ops.mesh.primitive_cube_add()
        obj = context.object
        #obj.name = name 
        obj.scale = (self.length, self.width, self.height)
        
        wall = Wall(obj, self.length, self.width, self.height)
        WallManager.walls.append(wall)
        
        return {'FINISHED'}


def register():
    bpy.app.timers.register(update)
    bpy.utils.register_class(MyPreferece)

    bpy.utils.register_class(AddParticle)
    bpy.utils.register_class(EditParticle)
    bpy.utils.register_class(DeleteParticle)

    bpy.utils.register_class(AddSpring)

    bpy.utils.register_class(AddCloth)
    bpy.utils.register_class(AddWall)

    bpy.utils.register_class(PlayButton)
    bpy.utils.register_class(Test_Panel)

    bpy.types.Scene.setting = PointerProperty(type = MyPreferece)

def unregister():
    bpy.app.timers.unregister(update)
    bpy.utils.unregister_class(MyPreferece)

    bpy.utils.unregister_class(AddParticle)
    bpy.utils.unregister_class(EditParticle)
    bpy.utils.unregister_class(DeleteParticle)

    bpy.utils.unregister_class(AddSpring)

    bpy.utils.unregister_class(AddCloth)
    bpy.utils.unregister_class(AddWall)

    bpy.utils.unregister_class(PlayButton)
    bpy.utils.unregister_class(Test_Panel)

    del bpy.types.Scene.setting