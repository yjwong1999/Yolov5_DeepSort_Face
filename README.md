# Yolov5_DeepSort_Face


### Features
Yolov5 Object Detection with DeepSORT Tracking, using OpenSphere Face Recognition Module


### Steps to run Code

- Create a conda environment, and activate it
```
conda create --name pipeline python=3.8.10
conda activate pipeline
```


- Clone the repository
```
git clone https://github.com/yjwong1999/Yolov5_DeepSort_Face.git
```

- Goto cloned folder
```
cd Yolov5_DeepSort_Face/Yolov5_DeepSort_Face
cd yolov5
```

- Install the yolov5 package
```
pip install -r requirements.txt
```

- Back to pipeline directory.
```
cd ../
```

- Do Tracking with mentioned command below
```
# video file
python3 track.py --source dataset_cam1.mp4 --yolo_model best.pt --img 640 --save-vid --show-vid
```

# Acknowledgement

