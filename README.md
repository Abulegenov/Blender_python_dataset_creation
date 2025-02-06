# Blender_python_dataset_creation

This script helps to iterate over BLENDER objects (.obj) (3D clothes) and collect annotations in COCO format.

### **Types of Clothes**
1. **With Sleeves** (2 parts: back & front)  
2. **Without Sleeves** (6 parts: body back & front + each sleeve's back & front)  

### **Annotation Tasks**
- **Keypoint Detection**  
- **Object Segmentation**  
(*Need to indicate within the script which one to use.*)  

## **🔹 Pseudo Code**
1. Known **FACE vertices** of objects.  
2. Blender **camera captures the front view** of the object.  
3. The same **position is used to collect** vertices for COCO format:  
   - **Keypoint detection**  
   - **Object segmentation**  
   - **Area calculation & BBox indication**  
4. Object is **flipped to back view**.  
5. Step 3 repeats for the **back view**.  
