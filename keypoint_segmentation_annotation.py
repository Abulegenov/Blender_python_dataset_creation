import bpy,bmesh
import bpy_extras
import json
import pandas as pd
from shapely.geometry import Polygon
import math
import random





scene = bpy.context.scene
obj = bpy.context.object   # object you want the coordinates of
vertices = obj.data.vertices   # you will get the coordinates of its vertices
camera = bpy.data.objects["Camera"]
bm = bmesh.from_edit_mesh(obj.data)

print(obj.active_material)
mat_dict = {mat.name: i for i, mat in enumerate(obj.data.materials)}
print(mat_dict)




names=[]
for i in obj.data.materials:
    names.append(i.name)
    
print(mat_dict[random.choice(names)])

type = 'segmentation'
# IF you want segmentation, just comment the next line
type = "keypoints"

f = open("DATA_ANNOTATION\\combined_faces_vertices.json")
combined_faces_vertices = json.load(f)

#For two parted 
def annnotate_two_parted(obj, type):
    
    type = type
    name = obj.name
    #change_color of faces:
    
    
    for f in bm.faces:
        if f.index in combined_faces_vertices['FACES'][name]['front']:
            f.material_index = mat_dict[random.choice(names)]
        elif f.index in combined_faces_vertices['FACES'][name]['back']:
            f.material_index = mat_dict[random.choice(names)]
            
    bmesh.update_edit_mesh(obj.data, True)
    
    
    #FRONT PART:
    if type == 'keypoints':
        print(True)
        bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\keypoint_front_'+name+'.png'
    else:
        bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\segmentation_front_'+name+'.png'
        
    if type == 'keypoints':
        f = open("DATA_ANNOTATION\\coco_keypoints_"+name+".json")
        dataset_dict = json.load(f)
    else: 
        f = open("DATA_ANNOTATION\\coco_segmentation_"+name+".json")
        dataset_dict = json.load(f)
        
    image_id = len(dataset_dict['images'])
    annotation_id = len(dataset_dict['annotations']) 
       
    if type == 'keypoints':
        dataset_dict['images'].append({
                          "license": 0, 
                          "file_name":'keypoint_front_'+name+'.png', 
                          "coco_url": "", 
                          "height": 1080, 
                          "width": 1920, 
                          "date_captured": "", 
                          "flickr_url": "", 
                          "id": image_id + 1
                        })
    else:
        dataset_dict['images'].append({
                          "license": 0, 
                          "file_name":'segmentation_front_'+name+'.png', 
                          "coco_url": "", 
                          "height": 1080, 
                          "width": 1920, 
                          "date_captured": "", 
                          "flickr_url": "", 
                          "id": image_id + 1
                        })
    
    category_name1 = 'front_'+name
    me = obj.data

    n=0
    pixel_coord_x = []
    pixel_coord_y = []
    bm = bmesh.from_edit_mesh(obj.data)
    segmentation_list1=[]
    area_calc1 =[]
    if type == 'keypoints':    
        keypoints_category1 = []
        for i in range(0, len(combined_faces_vertices['VERTICES'][name]['front_vertices']), 5):
            keypoints_category1.append(combined_faces_vertices['VERTICES'][name]['front_vertices'][i])
        keypoints_annotation1 = []
    #Put camera to front    
    
    for ind in combined_faces_vertices['VERTICES'][name]['front_vertices']:
        for v in bm.verts:
            if v.index == ind:                    
                n=n+1
                # local to global coordinates
                co = obj.matrix_world @ v.co
                # calculate 2d image coordinates
                co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                render_scale = scene.render.resolution_percentage / 100
    #                print(render_scale)
                render_size = (
                    int(scene.render.resolution_x * render_scale),
                    int(scene.render.resolution_y * render_scale),
                )
                pixel_coord_x.append(co_2d.x * render_size[0])
                pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                area_calc1.append([co_2d.x * render_size[0],
                                render_size[1] - co_2d.y * render_size[1]])
                segmentation_list1.append(co_2d.x * render_size[0])
                segmentation_list1.append(render_size[1] - co_2d.y * render_size[1])
    
    if type == 'keypoints':            
        for key in keypoints_category1:
            for v in bm.verts:
                if v.index==key:
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
        #                print(render_scale)
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )

                    keypoints_annotation1.append(co_2d.x * render_size[0])
                    keypoints_annotation1.append(render_size[1] - co_2d.y * render_size[1])
                    
                    # Include code of getting vertex visible in camera 
                    #Code goes here:
                    
                    #
                    
                    keypoints_annotation1.append(2)
    
                            
    
    x_max = max(pixel_coord_x)
    x_min = min(pixel_coord_x)
    y_max = max(pixel_coord_y) 
    y_min = min(pixel_coord_y)
    segmentation_list1 = [segmentation_list1]
    polygon = Polygon(area_calc1)
    area1 = polygon.area
    if type == 'keypoints':
        num_keypoints1 = len(keypoints_category1)
    bbox1 = [x_min, y_min, x_max-x_min,y_max-y_min]
    print(n)
    bmesh.update_edit_mesh(me)
    bpy.ops.render.render(write_still=True)    

    
    turn = True
    if turn == True:
        #Turn model to the back
#        bpy.context.active_object.rotation_euler[2] = math.radians(180)
#        bmesh.update_edit_mesh(obj.data, True)
        for f in bm.faces:
            if f.index in combined_faces_vertices['FACES'][name]['front']:
                f.hide = True
        turn = False 
    
    
    
    #BACK PART:

    if turn == False:
        
        
        if type == 'keypoints':
            bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\keypoint_back_'+name+'.png'
        else:
            bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\segmentation_back_'+name+'.png'
        
        
        if type == 'keypoints':
            dataset_dict['images'].append({
                              "license": 0, 
                              "file_name":'keypoint_back_'+name+'.png', 
                              "coco_url": "", 
                              "height": 1080, 
                              "width": 1920, 
                              "date_captured": "", 
                              "flickr_url": "", 
                              "id": image_id + 2
                            })
        else:
            dataset_dict['images'].append({
                              "license": 0, 
                              "file_name":'segmentation_back_'+name+'.png', 
                              "coco_url": "", 
                              "height": 1080, 
                              "width": 1920, 
                              "date_captured": "", 
                              "flickr_url": "", 
                              "id": image_id + 2
                            })
        

       
        category_name2 = 'back_'+name
        me = obj.data

        if type == 'keypoints':
            keypoints_category2 = []
            for i in range(0, len(combined_faces_vertices['VERTICES'][name]['back_vertices']), 5):
                keypoints_category2.append(combined_faces_vertices['VERTICES'][name]['back_vertices'][i])
            keypoints_annotation2 = [] 
            
        n=0
        pixel_coord_x = []
        pixel_coord_y = []
        bm = bmesh.from_edit_mesh(obj.data)
        segmentation_list2=[]
        area_calc2 =[]
            
        
        for ind in combined_faces_vertices['VERTICES'][name]['back_vertices']:
            for v in bm.verts:
                if v.index == ind:                    
                    n=n+1
                    # local to global coordinates
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
        
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )
                    pixel_coord_x.append(co_2d.x * render_size[0])
                    pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                    area_calc2.append([co_2d.x * render_size[0],
                                    render_size[1] - co_2d.y * render_size[1]])
                    segmentation_list2.append(co_2d.x * render_size[0])
                    segmentation_list2.append(render_size[1] - co_2d.y * render_size[1])
                    
        if type == 'keypoints':
            for key in keypoints_category2:
                for v in bm.verts:
                    if v.index==key:
                        co = obj.matrix_world @ v.co
                        # calculate 2d image coordinates
                        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                        render_scale = scene.render.resolution_percentage / 100
            #                print(render_scale)
                        render_size = (
                            int(scene.render.resolution_x * render_scale),
                            int(scene.render.resolution_y * render_scale),
                        )

                        keypoints_annotation2.append(co_2d.x * render_size[0])
                        keypoints_annotation2.append(render_size[1] - co_2d.y * render_size[1])
                        
                        # Include code of getting vertex visible in camera 
                        #Code goes here:
                        
                        #
                        
                        keypoints_annotation2.append(2)
            
        x_max = max(pixel_coord_x)
        x_min = min(pixel_coord_x)
        y_max = max(pixel_coord_y) 
        y_min = min(pixel_coord_y)
        segmentation_list2 = [segmentation_list2]
        polygon = Polygon(area_calc2)
        area2 = polygon.area
        if type == 'keypoints':
            num_keypoints2 = len(keypoints_category2)
            
        bbox2 = [x_min, y_min, x_max-x_min,y_max-y_min]
        all_keypoints_category = keypoints_category1 +  keypoints_category2 
      
        len_1 = len(keypoints_annotation1)
        len_2 = len(keypoints_annotation2)
        zero_1 = [0]*len_1
        zero_2 = [0]*len_2

        final_keypoints_annotation_1 = keypoints_annotation1 + zero_2 
        final_keypoints_annotation_2 = zero_1 + keypoints_annotation2 
        
        if type == 'keypoints':
            if len(dataset_dict['categories'])<1:
                
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 1,
                                                        "name": category_name1,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 2,
                                                        "name": category_name2,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )                                        
                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list1, 
                                      "num_keypoints": num_keypoints1,
                                      "id":annotation_id + 1,
                                      "area": area1, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_1,
                                      "image_id": image_id + 1, 
                                      "bbox": bbox1, 
                                      "category_id": 1 
                                      })
                                      
            
                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list2, 
                                      "num_keypoints": num_keypoints2,
                                      "id":annotation_id + 2,
                                      "area": area2, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_2,
                                      "image_id": image_id + 2, 
                                      "bbox": bbox2, 
                                      "category_id": 2 
                                      })
        else:
            if len(dataset_dict['categories'])<1:
                
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 1,
                                                        "name": category_name1, 
                                                        }
                                                        )
                                                        
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 2,
                                                        "name": category_name2,  
                                                        }
                                                        )
                                                                                            
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list1, 
                                      "id":annotation_id + 1,
                                      "area": area1, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 1, 
                                      "bbox": bbox1, 
                                      "category_id": 1 
                                      })
                                      
            
                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list2, 
                                      "id":annotation_id + 2,
                                      "area": area2, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 2, 
                                      "bbox": bbox2, 
                                      "category_id": 2 
                                      })            
    

        if type == 'keypoints':  
            with open("DATA_ANNOTATION\\coco_keypoints_"+name+".json", "w") as outfile:
                json.dump(dataset_dict, outfile)      
        else: 
            with open("DATA_ANNOTATION\\coco_segmentation_"+name+".json", "w") as outfile:
                json.dump(dataset_dict, outfile)            
         
        print(n)   
        bmesh.update_edit_mesh(me)
        bpy.ops.render.render(write_still=True)  
    else:
        print('SORRY')  




##For 6 parted with sleeves:


def annotate_multiple_parted(obj,type):
    
    type= type
    name = obj.name
    
   
    
    index_front = 0
    index_back = 1
    index_front_sleeves = 2
    index_back_sleeves = 3
    for f in bm.faces:
        if f.index in combined_faces_vertices['FACES'][name]['front']:
            f.material_index = mat_dict[random.choice(names)]
        elif f.index in combined_faces_vertices['FACES'][name]['back']:
            f.material_index = mat_dict[random.choice(names)]
        if f.index in combined_faces_vertices['FACES'][name]['front_sleeves']:
            f.material_index = mat_dict[random.choice(names)]
        elif f.index in combined_faces_vertices['FACES'][name]['back_sleeves']:
            f.material_index = mat_dict[random.choice(names)]
            
    bmesh.update_edit_mesh(obj.data, True)
    
    #FRONT PART:
    if type == 'keypoints':
        bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\keypoint_front_'+name+'.jpg'
    else:
        bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\segmentation_front_'+name+'.jpg'
        
    if type == 'keypoints':
        f = open("DATA_ANNOTATION\\coco_keypoints_"+name+".json")
        dataset_dict = json.load(f)
    else: 
        f = open("DATA_ANNOTATION\\coco_segmentation_"+name+".json")
        dataset_dict = json.load(f)  
        
    image_id = len(dataset_dict['images'])
    annotation_id = len(dataset_dict['annotations'])
       
    if type == 'keypoints':
        dataset_dict['images'].append({
                          "license": 0, 
                          "file_name":'keypoint_front_'+name+'.png', 
                          "coco_url": "", 
                          "height": 1080, 
                          "width": 1920, 
                          "date_captured": "", 
                          "flickr_url": "", 
                          "id": image_id + 1
                        })
    else:
        dataset_dict['images'].append({
                          "license": 0, 
                          "file_name":'segmentation_front_'+name+'.png', 
                          "coco_url": "", 
                          "height": 1080, 
                          "width": 1920, 
                          "date_captured": "", 
                          "flickr_url": "", 
                          "id": image_id + 1
                        })

    
    category_name1 = 'front_body_'+name
    me = obj.data

    
    n=0
    pixel_coord_x = []
    pixel_coord_y = []
    bm = bmesh.from_edit_mesh(obj.data)
    segmentation_list1=[]
    area_calc1 =[]
    if type == 'keypoints':
        keypoints_category1 = []
        for i in range(0, len(combined_faces_vertices['VERTICES'][name]['front_vertices']['body']), 5):
            keypoints_category1.append(combined_faces_vertices['VERTICES'][name]['front_vertices']['body'][i])
        keypoints_annotation1 = []
        
      
    
    for ind in combined_faces_vertices['VERTICES'][name]['front_vertices']['body']:
        for v in bm.verts:
            if v.index == ind:                    
                n=n+1
                # local to global coordinates
                co = obj.matrix_world @ v.co
                # calculate 2d image coordinates
                co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                render_scale = scene.render.resolution_percentage / 100
                render_size = (
                    int(scene.render.resolution_x * render_scale),
                    int(scene.render.resolution_y * render_scale),
                )
                pixel_coord_x.append(co_2d.x * render_size[0])
                pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                area_calc1.append([co_2d.x * render_size[0],
                                render_size[1] - co_2d.y * render_size[1]])
                segmentation_list1.append(co_2d.x * render_size[0])
                segmentation_list1.append(render_size[1] - co_2d.y * render_size[1])
    
    if type == 'keypoints':            
        for key in keypoints_category1:
            for v in bm.verts:
                if v.index==key:
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )

                    keypoints_annotation1.append(co_2d.x * render_size[0])
                    keypoints_annotation1.append(render_size[1] - co_2d.y * render_size[1])
                    
                    # Include code of getting vertex visible in camera 
                    #Code goes here:
                    
                    #
                    
                    keypoints_annotation1.append(2)
    
                            
    
    x_max = max(pixel_coord_x)
    x_min = min(pixel_coord_x)
    y_max = max(pixel_coord_y) 
    y_min = min(pixel_coord_y)
    segmentation_list1 = [segmentation_list1]
    polygon = Polygon(area_calc1)
    area1 = polygon.area
    if type == 'keypoints':
        num_keypoints1 = len(keypoints_category1)
        
    bbox1=[x_min, y_min, x_max-x_min,y_max-y_min]
    

    #Front right sleeve:
    
     
    category_name2 = 'front_right_sleeve_'+name
    me = obj.data
 
    n=0
    pixel_coord_x = []
    pixel_coord_y = []
    bm = bmesh.from_edit_mesh(obj.data)
    segmentation_list2=[]
    area_calc2 =[]
    if type == 'keypoints':
        keypoints_category2 = []
        for i in range(0, len(combined_faces_vertices['VERTICES'][name]['front_vertices']['right_sleeve']), 5):
            keypoints_category2.append(combined_faces_vertices['VERTICES'][name]['front_vertices']['right_sleeve'][i])
        keypoints_annotation2 = []   
    
    for ind in combined_faces_vertices['VERTICES'][name]['front_vertices']['right_sleeve']:
        for v in bm.verts:
            if v.index == ind:                    
                n=n+1
                # local to global coordinates
                co = obj.matrix_world @ v.co
                # calculate 2d image coordinates
                co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                render_scale = scene.render.resolution_percentage / 100
                render_size = (
                    int(scene.render.resolution_x * render_scale),
                    int(scene.render.resolution_y * render_scale),
                )
                pixel_coord_x.append(co_2d.x * render_size[0])
                pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                area_calc2.append([co_2d.x * render_size[0],
                                render_size[1] - co_2d.y * render_size[1]])
                segmentation_list2.append(co_2d.x * render_size[0])
                segmentation_list2.append(render_size[1] - co_2d.y * render_size[1])
                
    if type == 'keypoints':            
        for key in keypoints_category2:
            for v in bm.verts:
                if v.index==key:
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )

                    keypoints_annotation2.append(co_2d.x * render_size[0])
                    keypoints_annotation2.append(render_size[1] - co_2d.y * render_size[1])
                    
                    # Include code of getting vertex visible in camera 
                    #Code goes here:
                    
                    #
                    
                    keypoints_annotation2.append(2)
    
                            
    
    x_max = max(pixel_coord_x)
    x_min = min(pixel_coord_x)
    y_max = max(pixel_coord_y) 
    y_min = min(pixel_coord_y)
    segmentation_list2 = [segmentation_list2]
    polygon = Polygon(area_calc2)
    area2 = polygon.area
    if type == 'keypoints':
        num_keypoints2 = len(keypoints_category2)
    bbox2 = [x_min, y_min, x_max-x_min,y_max-y_min]
    
       
    #Front left sleeve
    
    
    category_name3 = 'front_left_sleeve_'+name
    me = obj.data
    
    n=0
    pixel_coord_x = []
    pixel_coord_y = []
    bm = bmesh.from_edit_mesh(obj.data)
    segmentation_list3=[]
    area_calc3 =[]
    if type == 'keypoints':
        keypoints_category3 = []
        for i in range(0, len(combined_faces_vertices['VERTICES'][name]['front_vertices']['left_sleeve']), 5):
            keypoints_category3.append(combined_faces_vertices['VERTICES'][name]['front_vertices']['left_sleeve'][i])
        keypoints_annotation3 = []
       
    
    for ind in combined_faces_vertices['VERTICES'][name]['front_vertices']['left_sleeve']:
        for v in bm.verts:
            if v.index == ind:                    
                n=n+1
                # local to global coordinates
                co = obj.matrix_world @ v.co
                # calculate 2d image coordinates
                co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                render_scale = scene.render.resolution_percentage / 100
                render_size = (
                    int(scene.render.resolution_x * render_scale),
                    int(scene.render.resolution_y * render_scale),
                )
                pixel_coord_x.append(co_2d.x * render_size[0])
                pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                area_calc3.append([co_2d.x * render_size[0],
                                render_size[1] - co_2d.y * render_size[1]])
                segmentation_list3.append(co_2d.x * render_size[0])
                segmentation_list3.append(render_size[1] - co_2d.y * render_size[1])
                
    if type == 'keypoints':
        for key in keypoints_category3:
            for v in bm.verts:
                if v.index==key:
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )

                    keypoints_annotation3.append(co_2d.x * render_size[0])
                    keypoints_annotation3.append(render_size[1] - co_2d.y * render_size[1])
                    
                    # Include code of getting vertex visible in camera 
                    #Code goes here:
                    
                    #
                    
                    keypoints_annotation3.append(2)
        
                            
    
    x_max = max(pixel_coord_x)
    x_min = min(pixel_coord_x)
    y_max = max(pixel_coord_y) 
    y_min = min(pixel_coord_y)
    segmentation_list3 = [segmentation_list3]
    polygon = Polygon(area_calc3)
    area3 = polygon.area
    if type == 'keypoints':
        num_keypoints3 = len(keypoints_category3)
        
    bbox3 = [x_min, y_min, x_max-x_min,y_max-y_min]


    print(n)
    bmesh.update_edit_mesh(me)    
    bpy.ops.render.render(write_still=True)
    
    

    
    turn = True
    if turn == True:
        #Turn model to the back
#        bpy.context.active_object.rotation_euler[2] = math.radians(180)
#        bmesh.update_edit_mesh(obj.data, True)
        for f in bm.faces:
            if f.index in combined_faces_vertices['FACES'][name]['front']:
                f.hide = True
            elif f.index in combined_faces_vertices['FACES'][name]['front_sleeves']:
                f.hide = True
                
                
        turn = False 
    
    
    
    
    #BACK PART:

    if turn == False:
    
        #BACK PART:
        
        if type == 'keypoints':
            bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\keypoint_back_'+name+'.jpg'
        else:
            bpy.context.scene.render.filepath = 'DATA_ANNOTATION\\segmentation_back_'+name+'.jpg'
        
        
        if type == 'keypoints':
            dataset_dict['images'].append({
                              "license": 0, 
                              "file_name":'keypoint_back_'+name+'.png', 
                              "coco_url": "", 
                              "height": 1080, 
                              "width": 1920, 
                              "date_captured": "", 
                              "flickr_url": "", 
                              "id": image_id + 2
                            })
        else:
            dataset_dict['images'].append({
                              "license": 0, 
                              "file_name":'segmentation_back_'+name+'.png', 
                              "coco_url": "", 
                              "height": 1080, 
                              "width": 1920, 
                              "date_captured": "", 
                              "flickr_url": "", 
                              "id": image_id + 2
                            })
        
        
        category_name4 = 'back_body_'+name
        me = obj.data

        if type == 'keypoints': 
            keypoints_category4 = []
            for i in range(0, len(combined_faces_vertices['VERTICES'][name]['back_vertices']['body']), 5):
                keypoints_category4.append(combined_faces_vertices['VERTICES'][name]['back_vertices']['body'][i])
            keypoints_annotation4 = [] 
        
        n=0
        pixel_coord_x = []
        pixel_coord_y = []
        bm = bmesh.from_edit_mesh(obj.data)
        segmentation_list4=[]
        area_calc4 =[]
            
        
        for ind in combined_faces_vertices['VERTICES'][name]['back_vertices']['body']:
            for v in bm.verts:
                if v.index == ind:                    
                    n=n+1
                    # local to global coordinates
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
        
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )
                    pixel_coord_x.append(co_2d.x * render_size[0])
                    pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                    area_calc4.append([co_2d.x * render_size[0],
                                    render_size[1] - co_2d.y * render_size[1]])
                    segmentation_list4.append(co_2d.x * render_size[0])
                    segmentation_list4.append(render_size[1] - co_2d.y * render_size[1])
        if type == 'keypoints':            
            for key in keypoints_category4:
                for v in bm.verts:
                    if v.index==key:
                        co = obj.matrix_world @ v.co
                        # calculate 2d image coordinates
                        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                        render_scale = scene.render.resolution_percentage / 100
                        render_size = (
                            int(scene.render.resolution_x * render_scale),
                            int(scene.render.resolution_y * render_scale),
                        )

                        keypoints_annotation4.append(co_2d.x * render_size[0])
                        keypoints_annotation4.append(render_size[1] - co_2d.y * render_size[1])
                        
                        # Include code of getting vertex visible in camera 
                        #Code goes here:
                        
                        #
                        
                        keypoints_annotation4.append(2)
        
        x_max = max(pixel_coord_x)
        x_min = min(pixel_coord_x)
        y_max = max(pixel_coord_y) 
        y_min = min(pixel_coord_y)
        segmentation_list4 = [segmentation_list4]
        polygon = Polygon(area_calc4)
        area4 = polygon.area
        if type == 'keypoints':
            num_keypoints4 = len(keypoints_category4)
        bbox4 = [x_min, y_min, x_max-x_min,y_max-y_min]

      
        #Back right sleeve
       
        category_name5 = 'back_right_sleeve_'+name
        me = obj.data
       
        
        n=0
        pixel_coord_x = []
        pixel_coord_y = []
        bm = bmesh.from_edit_mesh(obj.data)
        segmentation_list5=[]
        area_calc5 =[]
        if type == 'keypoints':
            keypoints_category5 = []
            for i in range(0, len(combined_faces_vertices['VERTICES'][name]['back_vertices']['right_sleeve']), 5):
                keypoints_category5.append(combined_faces_vertices['VERTICES'][name]['back_vertices']['right_sleeve'][i])
            keypoints_annotation5 = []
      
        
        for ind in combined_faces_vertices['VERTICES'][name]['back_vertices']['right_sleeve']:
            for v in bm.verts:
                if v.index == ind:                    
                    n=n+1
                    # local to global coordinates
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )
                    pixel_coord_x.append(co_2d.x * render_size[0])
                    pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                    area_calc5.append([co_2d.x * render_size[0],
                                    render_size[1] - co_2d.y * render_size[1]])
                    segmentation_list5.append(co_2d.x * render_size[0])
                    segmentation_list5.append(render_size[1] - co_2d.y * render_size[1])
                    
        if type == 'keypoints':            
            for key in keypoints_category5:
                for v in bm.verts:
                    if v.index==key:
                        co = obj.matrix_world @ v.co
                        # calculate 2d image coordinates
                        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                        render_scale = scene.render.resolution_percentage / 100
        
                        render_size = (
                            int(scene.render.resolution_x * render_scale),
                            int(scene.render.resolution_y * render_scale),
                        )

                        keypoints_annotation5.append(co_2d.x * render_size[0])
                        keypoints_annotation5.append(render_size[1] - co_2d.y * render_size[1])
                        
                        # Include code of getting vertex visible in camera 
                        #Code goes here:
                        
                        #
                        
                        keypoints_annotation5.append(2)
        
                                
        
        x_max = max(pixel_coord_x)
        x_min = min(pixel_coord_x)
        y_max = max(pixel_coord_y) 
        y_min = min(pixel_coord_y)
        segmentation_list5 = [segmentation_list5]
        polygon = Polygon(area_calc5)
        area5 = polygon.area
        if type == 'keypoints':
            num_keypoints5 = len(keypoints_category5)
        bbox5 = [x_min, y_min, x_max-x_min,y_max-y_min]

       
        #Back left sleeve
        
    
        category_name6 = 'back_left_sleeve_'+name
        me = obj.data
        
        n=0
        pixel_coord_x = []
        pixel_coord_y = []
        bm = bmesh.from_edit_mesh(obj.data)
        segmentation_list6=[]
        area_calc6 =[]
        if type == 'keypoints':
            keypoints_category6 = []
            for i in range(0, len(combined_faces_vertices['VERTICES'][name]['back_vertices']['left_sleeve']), 5):
                keypoints_category6.append(combined_faces_vertices['VERTICES'][name]['back_vertices']['left_sleeve'][i])
            keypoints_annotation6 = []
           
        
        for ind in combined_faces_vertices['VERTICES'][name]['back_vertices']['left_sleeve']:
            for v in bm.verts:
                if v.index == ind:                    
                    n=n+1
                    # local to global coordinates
                    co = obj.matrix_world @ v.co
                    # calculate 2d image coordinates
                    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                    render_scale = scene.render.resolution_percentage / 100
        
                    render_size = (
                        int(scene.render.resolution_x * render_scale),
                        int(scene.render.resolution_y * render_scale),
                    )
                    pixel_coord_x.append(co_2d.x * render_size[0])
                    pixel_coord_y.append(render_size[1] - co_2d.y * render_size[1])
                    area_calc6.append([co_2d.x * render_size[0],
                                    render_size[1] - co_2d.y * render_size[1]])
                    segmentation_list6.append(co_2d.x * render_size[0])
                    segmentation_list6.append(render_size[1] - co_2d.y * render_size[1])
                    
        if type == 'keypoints':
            for key in keypoints_category6:
                for v in bm.verts:
                    if v.index==key:
                        co = obj.matrix_world @ v.co
                        # calculate 2d image coordinates
                        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, co)
                        render_scale = scene.render.resolution_percentage / 100
           
                        render_size = (
                            int(scene.render.resolution_x * render_scale),
                            int(scene.render.resolution_y * render_scale),
                        )

                        keypoints_annotation6.append(co_2d.x * render_size[0])
                        keypoints_annotation6.append(render_size[1] - co_2d.y * render_size[1])
                        
                        # Include code of getting vertex visible in camera 
                        #Code goes here:
                        
                        #
                        
                        keypoints_annotation6.append(2)
        
                                
        
        x_max = max(pixel_coord_x)
        x_min = min(pixel_coord_x)
        y_max = max(pixel_coord_y) 
        y_min = min(pixel_coord_y)
        segmentation_list6 = [segmentation_list6]
        polygon = Polygon(area_calc6)
        area6 = polygon.area
        if type == 'keypoints':
            num_keypoints6 = len(keypoints_category6)
            
        bbox6 = [x_min, y_min, x_max-x_min,y_max-y_min]
        
        if type == 'keypoints':
            all_keypoints_category = []
            all_keypoints_category = keypoints_category1 +  keypoints_category2 + keypoints_category3 + keypoints_category4 + keypoints_category5 + keypoints_category6
            all_keypoint_annotations = keypoints_annotation1 +  keypoints_annotation2 + keypoints_annotation3 + keypoints_annotation4 + keypoints_annotation5 + keypoints_annotation6
            
            len_1 = len(keypoints_annotation1)
            len_2 = len(keypoints_annotation2)
            len_3 = len(keypoints_annotation3)
            len_4 = len(keypoints_annotation4)
            len_5 = len(keypoints_annotation5)
            len_6 = len(keypoints_annotation6)
            
            zero_1 = [0]*len_1
            zero_2 = [0]*len_2
            zero_3 = [0]*len_3
            zero_4 = [0]*len_4
            zero_5 = [0]*len_5
            zero_6 = [0]*len_6
            
            final_keypoints_annotation_1 = keypoints_annotation1 + zero_2 + zero_3 + zero_4 + zero_5 + zero_6
            final_keypoints_annotation_2 = zero_1 + keypoints_annotation2 + zero_3 + zero_4 + zero_5 + zero_6
            final_keypoints_annotation_3 = zero_1 + zero_2 + keypoints_annotation3 + zero_4 + zero_5 + zero_6
            final_keypoints_annotation_4 = zero_1 + zero_2 + zero_3 + keypoints_annotation4 + zero_5 + zero_6
            final_keypoints_annotation_5 = zero_1 + zero_2 + zero_3 + zero_4 + keypoints_annotation5 + zero_6
            final_keypoints_annotation_6 = zero_1 + zero_2 + zero_3 + zero_4 + zero_5 + keypoints_annotation6
        
        if type == 'keypoints':
                          
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list1, 
                                      "num_keypoints": num_keypoints1,
                                      "id":annotation_id + 1,
                                      "area": area1, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_1,
                                      "image_id": image_id + 1, 
                                      "bbox": bbox1, 
                                      "category_id": 1
                                      })
                                      
            
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list2, 
                                      "num_keypoints": num_keypoints2,
                                      "id":annotation_id + 2,
                                      "area": area2, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_2,
                                      "image_id": image_id + 1, 
                                      "bbox": bbox2, 
                                      "category_id": 2
                                      })
                                      
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list3, 
                                      "num_keypoints": num_keypoints3,
                                      "id":annotation_id + 3,
                                      "area": area3, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_3,
                                      "image_id": image_id + 1, 
                                      "bbox": bbox3, 
                                      "category_id": 3
                                      })
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list4, 
                                      "num_keypoints": num_keypoints4,
                                      "id":annotation_id + 4,
                                      "area": area4, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_4,
                                      "image_id": image_id + 2, 
                                      "bbox": bbox4, 
                                      "category_id": 4 
                                      })


                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list5, 
                                      "num_keypoints": num_keypoints5,
                                      "id":annotation_id + 5,
                                      "area": area5, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_5,
                                      "image_id": image_id + 2, 
                                      "bbox": bbox5, 
                                      "category_id": 5 
                                      })


                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list6, 
                                      "num_keypoints": num_keypoints6,
                                      "id":annotation_id + 6,
                                      "area": area6, 
                                      "iscrowd": 0, 
                                      "keypoints" : final_keypoints_annotation_6,
                                      "image_id": image_id + 2, 
                                      "bbox": bbox6, 
                                      "category_id": 6 
                                      })
            
            if len(dataset_dict['categories'])<1:
                                                                    
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 1,
                                                        "name": category_name1,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )                          
                
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 2,
                                                        "name": category_name2,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                                        
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 3,
                                                        "name": category_name3,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 4,
                                                        "name": category_name4,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                                                        
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 5,
                                                        "name": category_name5,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                                                        
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 6,
                                                        "name": category_name6,
                                                        "keypoints": all_keypoints_category    
                                                        }
                                                        )
                                                        
        else:
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list1, 
                                      "id":annotation_id + 1,
                                      "area": area1, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 1, 
                                      "bbox": bbox1, 
                                      "category_id": 1
                                      })
                                      
            
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list2, 
                                      "id":annotation_id + 2,
                                      "area": area2, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 1, 
                                      "bbox": bbox2, 
                                      "category_id": 2
                                      })
                                      
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list3, 
                                      "id":annotation_id + 3,
                                      "area": area3, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 1, 
                                      "bbox": bbox3, 
                                      "category_id": 3
                                      })
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list4, 
                                      "id":annotation_id + 4,
                                      "area": area4, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 2, 
                                      "bbox": bbox4, 
                                      "category_id": 4 
                                      })


                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list5, 
                                      "id":annotation_id + 5,
                                      "area": area5, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 2, 
                                      "bbox": bbox5, 
                                      "category_id": 5 
                                      })


                                                    
            dataset_dict['annotations'].append({
                                      "segmentation": segmentation_list6, 
                                      "id":annotation_id + 6,
                                      "area": area6, 
                                      "iscrowd": 0, 
                                      "image_id": image_id + 2, 
                                      "bbox": bbox6, 
                                      "category_id": 6 
                                      })                          
            if len(dataset_dict['categories'])<1:
                
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 1,
                                                        "name": category_name1,
                                                        }
                                                        )                          
                
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 2,
                                                        "name": category_name2,
                                                        }
                                                        )
                                        
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 3,
                                                        "name": category_name3,
                                                        }
                                                        )
                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 4,
                                                        "name": category_name4,
                                                        }
                                                        )

                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 5,
                                                        "name": category_name5,
                                                        }
                                                        )
                                                        

                dataset_dict['categories'].append({
                                                        "supercategory": "person",
                                                        "id": 6,
                                                        "name": category_name6,
                                                        }
                                                        )

                                  
                                  
        
        
        
        print(n)   
        bmesh.update_edit_mesh(me)
        bpy.ops.render.render(write_still=True)    

           
      
      
        if type == 'keypoints':  
            with open("DATA_ANNOTATION\\coco_keypoints_"+name+".json", "w") as outfile:
                json.dump(dataset_dict, outfile)      
        else: 
            with open("DATA_ANNOTATION\\coco_segmentation_"+name+".json", "w") as outfile:
                json.dump(dataset_dict, outfile)
                
                

#CODE goes here:


#IF there are no sleeves:

#annnotate_two_parted(obj,type)

#IF there are sleeves:

#annotate_multiple_parted(obj,type)