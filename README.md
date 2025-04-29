**Dressing Site Analyzer**

This repo holds the python code to run on a laptop and simulates a controller to trigger a camera to take pictures at set intervals. 

**Code**

ai.py
- Not in use. It runs the images taken from the computer directly to the Roboflow API url. However, we have changed the code to have a firebase server take in a raw photo and automatically run images through the model API there instead.

gui.py
- The graphical interface of the application. Holds the method calls to ai.py/uploader.py to give the actions to the buttons.
- Can take images manually, or set a timer to automatically take images a set interval of seconds.

uploader.py
- Holds the code that uploads the images to the firebase storage buckets as well as the firestore DB itself.

main.py
- The entrance point of the program. Call this to run the program.

**IMPORTANT NOTES**

- Requires python 3.11 to run
  - i.e. py -3.11 main.py
- Requires the .env file to properly connect and run to the backend.
  - Message sponsor for file.
 
**Code Creator**
- Daniel Chang
  dsc5504@psu.edu
  
