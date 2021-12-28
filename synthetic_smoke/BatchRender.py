import bpy
import random
import os


def degs_to_rads(d):
  return d/360*6.283

def rand_range(min, max):
  return random.random()*(max-min)+min

NUM_RENDERS = 20 #this number should be divisible by 5

#set the parameters for constraining random variations
shared_range = {'surf':(.3, 1.5), 'sun_rot': (-45, 45)}
smoke_range = {'wind_rot':[(20, 70), (70, 82), (65, 82), (20, 82), (30, 82)],
               'wind_str':[(1.5, 6.5), (4, 7), (3, 6), (3, 7), (1.5, 3)],
               't_diff':[(0, .1), (0, 0), (0, .02), (0, .1), (0, .1)],
               'frame':[(70, 180), (70, 180), (140, 220), (90, 180), (140, 240)]}

#set a counter variable
count = 1

#render each of 5 blender files
for i in range(5): 
    for j in range(NUM_RENDERS // 5):
        #open one of the prototypes
        bpy.ops.wm.open_mainfile(filepath="./smoke%s.blend" % (i+1))

        #save file to allow for baking
        bpy.ops.wm.save_as_mainfile(filepath="./smoke%s_baked.blend" % (i+1)) 

        #perform a series of random alterations (within certain constraints)
        bpy.data.objects['Plane'].modifiers["Smoke"].flow_settings.surface_distance = rand_range(*shared_range['surf'])
        bpy.data.objects['Light'].rotation_euler[0] = degs_to_rads(rand_range(*shared_range['sun_rot']))
        bpy.data.objects['Light'].rotation_euler[1] = degs_to_rads(rand_range(*shared_range['sun_rot']))
        bpy.data.objects['Light'].rotation_euler[2] = degs_to_rads(rand_range(0, 360))

        bpy.data.objects['Field'].rotation_euler[1] = degs_to_rads(rand_range(*smoke_range['wind_rot'][i]))
        bpy.data.objects['Field'].field.strength = rand_range(*smoke_range['wind_str'][i])
        bpy.data.objects['Smoke Domain'].modifiers["Smoke"].domain_settings.beta = rand_range(*smoke_range['t_diff'][i])
        
        # bake to current frame
        bpy.ops.ptcache.bake_all()

        #set the frame near the end
        bpy.context.scene.frame_set(rand_range(*smoke_range['frame'][i]))
    
        #remove the plane, so as to avoid seeing it in the render
        bpy.ops.object.delete({"selected_objects": [bpy.data.objects['Plane']]})

        #choose a filepath for render
        bpy.data.scenes['Scene'].render.filepath = os.getcwd() + "\\smoke_render%s.jpg" % (count)

        #render the scene
        bpy.ops.render.render(write_still=True)

        count += 1
