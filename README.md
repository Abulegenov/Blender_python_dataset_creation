# Blender_python_dataset_creation
This script helps to iterate over BLENDER objects (.obj) (3d clothes were considered) files and collect annotation for each of the object in COCO format
Two types of clothes: 1) with sleeves 2) without sleeves
Two functions for each of two types of clothes.
Two types of task to create the annotation files - keypoint detection, object segmentation. - Need to indicate within script
Pseudo code:
0) FACE vertices of objects are known
1) blender camera capture the frontal view of the object
2) Same position is reserved to collect correct vertices for the keypoint and object detection tasks and converted into COCO format (+area calculation, bbox indication)
3) object is reversed to back view
4) step 2

