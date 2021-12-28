## Installation Instructions

1. Download / Open Blender 2.8 (newest version)
2. Select the scripting tab at the top of the screen
3. Select Text->Open and open the BlenderSmoke.py script
4. Click 'Run Script' at the upper righthand corner
5. If everything went smoothly, you should now have 5 blender files in the folder (titled smoke1.blend, smoke2.blend, etc.)

## Performing a Batch Render 

1. Open one of the files you previously made
2. Open the scripting tab
3. Open the BatchRender.py script 
4. Save the blend file and run the script (this might take several minutes)
5. If everything went as planned, you should now have 5 additional files such as smoke1_baked.blend, as well as 20 rendered .png images with a red background.

## Converting Red Channel to Alpha

1. Open a command prompt and install opencv (if you have not done so already)

pip install opencv-python

2. Navigate to the folder where you have the renders
3. Run the Alpha-fix Script:

python RGB_Alpha_fix.py

4. You should now have 20 additional png images with the red channel converted to alpha.

## Increasing the Number of Renders:
1. change NUM_RENDERS in BatchRender.py
2. change NUM_RENDERS in RGB_Alpha_fix.py

## Future Improvements:
- Make it easier to increase the number of renders (reference a common file)
- Create a script to remove smoke that is too similar (based on iou)
- Decrease the chances of similar images by creating a parameter grid (rather than sampling with replacement)
