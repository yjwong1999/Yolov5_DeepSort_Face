# limit the number of cpus used by high performance libraries
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"


import cv2
from PIL import Image as Im
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, required=True, help='source') 

opt = parser.parse_args()

# get video filenames
# opt.source = 'runs/track/exp5'
file_dir = opt.source
video_mot_pair = {}
for filename in os.listdir(file_dir):
    if filename.endswith('.mp4'):
        video_filename = os.path.join(file_dir, filename)
        mot_filename = os.path.join(file_dir, filename[:filename.rindex('.')] + '.txt')
        video_mot_pair[video_filename] = mot_filename


# create a directory to store cropped face
new_data_parent_dir = 'opensphere/customize/new_face_data'
if not os.path.isdir(new_data_parent_dir):
    os.mkdir(new_data_parent_dir)


# load the video
all_frame_idx = []
all_corresponding_details = []
for video_filename in video_mot_pair:
    # get the corresponding mot file
    mot_filename = video_mot_pair[video_filename]
    with open(mot_filename, 'r') as file:
        line = file.readline()
        while line:
            frame_idx = int(line.split()[0])
            all_frame_idx.append(frame_idx)
            all_corresponding_details.append(line)
            line = file.readline()

    # get the directory name for new data
    new_data_dir = os.path.split(video_filename)[1]
    new_data_dir = new_data_dir[:new_data_dir.rindex('.')]
    new_data_dir = os.path.join(new_data_parent_dir, new_data_dir)
    try:
        os.mkdir(new_data_dir)
    except:
        print(f'You had already create extract faces from this directory: {new_data_dir}!')
        print('Delete the previously extracted faces if you wish to re-extract!')
        raise StopIteration

    # loop the videos
    cap = cv2.VideoCapture(video_filename)
    frame_count = 0
    next_frame_idx = all_frame_idx.pop(0)
    next_details = all_corresponding_details.pop(0)
    last_seen_of_this_id = {} # to know what is the last time we seen this ID
    track_count = 0
    id_and_cropped = {}
    while cap.isOpened():
        ret, frame = cap.read()
        # if no more frames in the video, stop looping
        if ret:
            frame_count += 1
            while frame_count == next_frame_idx:
                # extract the bbox details
                _, id, bbox_left, bbox_top, bbox_w, bbox_h, _, _, _, _ = next_details.split()
                bbox_left, bbox_top, bbox_w, bbox_h = int(bbox_left), int(bbox_top), int(bbox_w), int(bbox_h)
                id = int(id)

                # track id
                if id not in list(last_seen_of_this_id.keys()):
                    last_seen_of_this_id[id] = 0
                    id_and_cropped[id] = []

                # see if any tracking should be ended
                #print(last_seen_of_this_id)
                reference_id_to_be_deleted = []
                for reference_id in last_seen_of_this_id.keys():
                    if reference_id != id:
                        last_seen_of_this_id[reference_id] += 1
                        #print(last_seen_of_this_id[reference_id])
                        if last_seen_of_this_id[reference_id] >= 10:
                            os.mkdir(os.path.join(new_data_dir, str(track_count)))
                            for i, cropped in enumerate(id_and_cropped[reference_id]):
                                cropped.save(os.path.join(new_data_dir, str(track_count), f'{i}.jpg'))
                            track_count += 1
                            reference_id_to_be_deleted.append(reference_id)
                    else:
                        last_seen_of_this_id[reference_id] = 0

                # delete and and this tracking
                for reference_id in reference_id_to_be_deleted:
                    del id_and_cropped[reference_id]
                    del last_seen_of_this_id[reference_id]

                # cropped + convert from bgr to rgb
                cropped = frame[bbox_top:int(bbox_top+bbox_h),bbox_left:int(bbox_left+bbox_w),:]
                cropped = cropped[3:-2,3:-2,:] # remove the bbox borderline
                #plt.imshow(cropped)
                #plt.show()
                cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                cropped = Im.fromarray(cropped)

                id_and_cropped[id].append(cropped)

                # get next line
                try:
                    next_frame_idx = all_frame_idx.pop(0)
                    next_details = all_corresponding_details.pop(0)
                except:
                    print('EXTRACTION DONE!')

            # if no more faces in the video, stop looping
            if len(all_frame_idx) == 0:
                break
        else:
            break
        # if use want to quick earlier
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

for reference_id in last_seen_of_this_id.keys():
    os.mkdir(os.path.join(new_data_dir, str(track_count)))
    for i, cropped in enumerate(id_and_cropped[reference_id]):
        cropped.save(os.path.join(new_data_dir, str(track_count), f'{i}.jpg'))
    track_count += 1

cap.release()
cv2.destroyAllWindows()

