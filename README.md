# Yolov5_DeepSort_Face

**To-be-filled with Conference Proceeding** </br>
Simulation for Conference Proceedings "doi-to-be-filled" </br>
Refer [link-to-be-filled](https://github.com/yjwong1999/Yolov5_DeepSort_Face) for the preprint

## Abstract
To-be-filled


## TLDR

### Features
Yolov5 Object Detection with DeepSORT Tracking, using OpenSphere Face Recognition Module


### TODO
- [ ] **Issue 1**     : Update requirements.txt
- [x] **Issue 2**     : Fix [video saving issue](https://stackoverflow.com/questions/73324872/cv2-videowriter-issues)
- [ ] **Issue 3**     : Video stream is jumpy when track on multiple pre-recorded videos
- [ ] **Issue 4**     : The inference time for multi-source is wrong
- [ ] **Feature 1**   : Integrate screenshot face data for model retraining

**Issue 1** is an existing problem in YOLOv5 repo. </br>
However, I found that it can be avoided if you don't stop the program by keyboard interrupt (ctrl + c). </br>
Instead, you stop the program by:</br>
1. Click on any of the windows showing the video frame
2. Press 'q' (small capital letter)



## Steps to run Code

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
pip install tabulate
pip install easydict
pip install numpy==1.23.1

cd ../
```

- Download pretrained OpenSphere Model
```
sudo apt-get install zip unzip

cd opensphere/project
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1mEAkIa9B89QzsamVhNp9mol5PZWxLthM' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1mEAkIa9B89QzsamVhNp9mol5PZWxLthM" -O sfnet20_ref.zip && rm -rf /tmp/cookies.txt
unzip sfnet20_ref.zip

wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1DIrZshYMNfKCOCN54_MN1KAB0XaCWnWA' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1DIrZshYMNfKCOCN54_MN1KAB0XaCWnWA" -O sfnet20_survface.zip && rm -rf /tmp/cookies.txt
unzip sfnet20_survface.zip

cd ../../
```

- Download test videos
```
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1pDXTOr-0dYScGnifNjhHuwMz08DHl0hz' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1pDXTOr-0dYScGnifNjhHuwMz08DHl0hz" -O dataset_cam1.mp4 && rm -rf /tmp/cookies.txt
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1iND5nKvGxqGWV4EFyT8EhJKB0acqQSvF' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1iND5nKvGxqGWV4EFyT8EhJKB0acqQSvF" -O dataset_cam2.mp4 && rm -rf /tmp/cookies.txt
```

- Find the port numbers connected with camera(s)
```
python3 find_port.py
```

- How to use ```source.txt``` for multli-cam or multi-streams
```
# In source.txt, each line should be one camera/streams
#
# 1. camera port number (which you get by running python3 find_port.py)
# 2. https or rtsp link (for online video)
# 3. <video>.mp4 or relevant video format
#
# Note that you can mix between the source format (live/video/rtsp/https)
```

- Do Tracking with mentioned command below
```
# single video cam
python3 track.py --source 0 --yolo_model yolo_face.pt --img 640 --deep_sort_model opensphere/project/sfnet20_survface --show-vid --save-vid --save-txt

# video file
python3 track.py --source dataset_cam2.mp4 --yolo_model yolo_face.pt --img 640 --deep_sort_model opensphere/project/sfnet20_survface --show-vid --save-vid --save-txt

# multi-streams (can mix between live/video/rtsp/https)
python3 track.py --source source.txt --yolo_model yolo_face.pt --img 640 --deep_sort_model opensphere/project/sfnet20_survface --show-vid --save-vid --save-txt
```

- Stop Tracking by
```
# Refer Issue 1 in TODO
# 
# DO NOT: stop the program by keyboard interrupt (ctrl + c)
# DO:     stop the program by:</br>
# 1. Click on any of the windows showing the video frame
# 2. Press 'q' (small capital letter)
```

## Acknowledgement
Many thanks to our funder Greatech Integration (M) Sdn Bhd for sponsoring this project

### Reference Code
1. [Yolov5 + DeepSort for Object Detection and Tracking](https://github.com/nicedaddy/Yolov5_DeepSort_Pytorch) </br>
2. [Yolov8 + DeepSort for Object Detection and Tracking](https://github.com/mikel-brostrom/yolov8_tracking) </br>
3. [OpenSphere Face Recognition](https://github.com/ydwen/opensphere) </br>
4. [Yolov5](https://github.com/ultralytics/yolov5) </br>
5. [How to list available cameras OpenCV/Python](https://stackoverflow.com/a/62639343)
6. [How to wget files from Google Drive](https://bcrf.biochem.wisc.edu/2021/02/05/download-google-drive-files-using-wget/)

- Technically, I used Reference [1] for detection & tracking, where Reference [2] is forked from a past version of Reference [2] </br>
- Reference [1] and [2] assign ID based on tracks (which means each tracking has an ID, disregarding the object identity itself) </br>
- Thus, [3] is used to learn the face identity, which is assigned as the ID for the tracking ID
