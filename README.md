# Yolov5_DeepSort_Face

##########################################
# create env
##########################################
conda create --name pipeline python=3.8.10

# activate
conda activate pipeline


##########################################
# Install Yolov5_DeepSort_Face repo
##########################################
git clone https://github.com/yjwong1999/Yolov5_DeepSort_Face.git
cd Yolov5_DeepSort_Face
cd Yolov5_DeepSort_Face
cd yolov5
pip install -r requirements.txt
cd ../


##########################################
# Install Yolov5_DeepSort_Face repo
##########################################
python3 track.py --source dataset_cam1.mp4 --yolo_model best.pt --img 640 --save-vid --show-vid
