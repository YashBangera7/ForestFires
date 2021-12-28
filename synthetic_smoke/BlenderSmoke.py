import bpy

plane_pos = [(-5.7, 0, 0), (-11, 0, 3.5), (-11, 0, 1.5), (-5.7, 0, 0), (-5.7, 0, 0)]
surface = [1, 1, 0.8, 0.8, 1.5] 
temp_diff = [0, 0, .01, .1, .1]
smoke_dom_pos = [(0,0,7), (-1.5, 0, 6.7), (-1.5, 0, 6.7), (0,0,7), (-1.5, 0, 6.7)]
turbulence_pos = [(7.5, 0, 6.8), (-8.5, 0, 3), (-8.5, 0, 3), (2.5, 0, 3.5), (-1, 2.5, 4.5)]
camera_pos = [(0, -26, 5.5),(0, -26, 5.5),(0, 26, 5.5),(0, -26, 5.5),(0, -26, 12)]
camera_rot = [(90, 0, 0),(90, 0, 0),(90, 0, 180),(90, 0, 0),(70, 0, 0)]
wind_rot = [(0, 60, 0), (0, 82, 0), (0, 75.5, 0), (-56, 73, -54), (-11, 73, -3)]
wind_str = [5.5, 4, 5.7, 7, 2.5]

def degrees_to_radians(degrees):
  convert = lambda x: x/360*6.283
  return (convert(degrees[0]), convert(degrees[1]), convert(degrees[2]))

def remove_objs():
    bpy.data.objects['Plane'].select_set(True)
    bpy.data.objects['Field'].select_set(True)
    bpy.data.objects['Field.001'].select_set(True)
    bpy.data.objects['Smoke Domain'].select_set(True)
    bpy.ops.object.delete(use_global=False, confirm=False)

#remove initial cube
bpy.ops.object.delete(use_global=False)

for i in range(5):
    #add plane
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=plane_pos[i])

    #add quick smoke
    bpy.ops.object.modifier_add(type='SMOKE')
    bpy.ops.object.material_slot_add()
    bpy.ops.object.quick_smoke()

    #scale up
    bpy.data.objects['Smoke Domain'].scale = (12, 8 , 8)

    #set location
    bpy.data.objects['Smoke Domain'].location = smoke_dom_pos[i]

    #reduce temp difference to zero
    bpy.context.object.modifiers["Smoke"].domain_settings.beta = temp_diff[i]

    #remove borders
    bpy.context.object.modifiers["Smoke"].domain_settings.collision_extents = 'BORDERCLOSED'

    #change gravity
    bpy.context.object.modifiers['Smoke'].domain_settings.effector_weights.gravity = 0.2

    #checkbox 'use high resolution' should be checked
    bpy.context.object.modifiers["Smoke"].domain_settings.use_high_resolution = True

    #add wind
    bpy.ops.object.effector_add(type='WIND', enter_editmode=False, location=(0, 0, 0))

    #rotate the wind
    bpy.data.objects['Field'].rotation_euler = degrees_to_radians(wind_rot[i])

    #increase strength
    bpy.context.object.field.strength = wind_str[i]

    #increase flow
    bpy.context.object.field.flow = 3

    #add turbulence
    bpy.ops.object.effector_add(type='TURBULENCE', enter_editmode=False, location=turbulence_pos[i])

    #set turbulence strength to 20
    bpy.context.object.field.strength = 20

    #set turbulence flow to 0.2
    bpy.context.object.field.flow = 0.2

    #make the smoke emit from a relatively small source of 1 (size of plane)
    bpy.data.objects['Plane'].modifiers["Smoke"].flow_settings.surface_distance = surface[i]
    if (i == 4):
        bpy.data.objects['Plane'].modifiers["Smoke"].flow_settings.temperature = 0.1
    bpy.context.scene.eevee.use_volumetric_shadows = True

    #change light to sun type
    bpy.data.objects['Light'].data.type = 'SUN'

    #change light energy to 4
    bpy.data.objects['Light'].data.energy = 4

    #change light location on the y axis
    bpy.data.objects['Light'].location[1] = -3

    #rotate the light towards the smoke
    bpy.data.objects['Light'].rotation_euler[2] = 1

    #dissable nodes for the background
    bpy.context.scene.world.use_nodes = False

    #set the color to red
    bpy.context.scene.world.color = (1, 0, 0)

    bpy.data.objects['Camera'].location = camera_pos[i]
    bpy.data.objects['Camera'].rotation_euler = degrees_to_radians(camera_rot[i])

    #save file
    bpy.ops.wm.save_as_mainfile(filepath='./smoke%s.blend' % (i+1))
    
    remove_objs()