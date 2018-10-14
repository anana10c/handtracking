from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import multiprocessing
from multiprocessing import Queue, Pool
import time
from utils.detector_utils import WebcamVideoStream
import datetime
import argparse
from splatter import Splatter
import math

frame_processed = 0
score_thresh = 0.2
splatters = []

"""
prev_areas = []
prev_left_corners = []
after every frame does its thing, prev_areas beceomes equal to whats in areas

if prev_areas length != 0
check if the len(areas) == len(prev_areas)
if not
"""


# Create a worker thread that loads graph and
# does detection on images in an input queue and puts it on an output queue

def worker(input_q, output_q, cap_params, frame_processed):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph()
    sess = tf.Session(graph=detection_graph)
    prev_areas = []
    prev_toplefts = []
    frame_count = 0
    while True:
        #print("> ===== in worker loop, frame ", frame_processed)
        frame = input_q.get()
        if (frame is not None):
            # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
            # while scores contains the confidence for each of these boxes.
            # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

            boxes, scores = detector_utils.detect_objects(frame, detection_graph, sess)

	    #fist/palm differentiation here but let's ignore that for now

            # draw bounding boxes
            detector_utils.draw_box_on_image(
                cap_params['num_hands_detect'], cap_params["score_thresh"],
                scores, boxes, cap_params['im_width'], cap_params['im_height'],
                frame)

            toplefts, bottomrights, areas = detector_utils.get_corners(cap_params['num_hands_detect'], cap_params["score_thresh"], scores, boxes, cap_params['im_width'], cap_params['im_height'])

            if frame_count == 3:
                frame_count = 0
                if len(prev_areas) == 0 or len(areas) == 0:
                    pass
                # elif len(toplefts) > len(prev_left_corners): #YOU GOTTA GET RID OF THE AREA THAT IS FARTHER FROM PREV-AREAS
                #     prev_area = prev_areas[0]
                #     if point_distance(prev_left_corners[0], toplefts[0]) > point_distance(prev_left_corners[0], toplefts[1]):
                #         current_area = areas[1]
                #     else:
                #         current_area = areas[0]
                # elif len(toplefts) < len(prev_left_corners): #YOU GOTTA GET RID OF THE PREV-AREA THAT IS FURTHER AWAY FROM AREA
                #     current_area = areas[0]
                #     if point_distance(prev_left_corners[0], toplefts[0]) > point_distance(prev_left_corners[1], toplefts[0]):
                #         prev_area = [1]
                #     else:
                #         prev_area = [0]
                # elif len(toplefts) == 1:
                #     current_area = areas[0]
                #     prev_area = prev_areas[0]
                else:
                    dist = {}
                    for current_index in range(len(toplefts)):
                        for prev_index in range(len(prev_toplefts)):
                            dist[point_distance(toplefts[current_index], prev_toplefts[prev_index])] = (current_index, prev_index)
                    indices = dist[min(dist.keys())]
                    current_area = areas[current_index]
                    prev_area = prev_areas[prev_index]
                    if compare_areas(current_area, prev_area, 2):
                        splatters.append(Splatter(toplefts[current_index], bottomrights[current_index]))
                    if len(toplefts) == 2 and len(prev_toplefts) == 2:
                        if compare_areas(areas[1-current_index], prev_areas[1-prev_index], 2):
                            splatters.append(Splatter(toplefts[1-current_index], bottomrights[1-current_index]))
            else:
                frame_count += 1
            
            # for x in range(0, len(toplefts)):
            #     splatters.append(Splatter(toplefts[x], bottomrights[x]))

            for splotch in splatters:
                if splotch.opacity == 0:
                    splatters.remove(splotch)
                    continue

                roi = frame[splotch.topleft[1]:splotch.bottomright[1], splotch.topleft[0]:splotch.bottomright[0]]
                background = roi.copy()
                overlap = roi.copy()
                background[splotch.outline[:, :, 3] != 0] = (0, 0, 0)
                overlap[splotch.outline[:, :, 3] == 0] = (0, 0, 0)
                overlap_area = cv2.addWeighted(overlap, 1-splotch.opacity, splotch.outline[:, :, 0:3], splotch.opacity, 0)
                dst = cv2.add(overlap_area, background)
                frame[splotch.topleft[1]:splotch.bottomright[1], splotch.topleft[0]:splotch.bottomright[0]] = dst
                splotch.fade()

            prev_areas = areas.copy()
            prev_toplefts = toplefts.copy()


	    # add frame with splatters to queue (below)
            output_q.put(frame)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()

def point_distance(p1, p2): #p1 and p2 are tuples of two integers
	return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def compare_areas(current_area, prev_area, factor):
	return (current_area >= factor * prev_area)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-src',
        '--source',
        dest='video_source',
        type=int,
        default=0,
        help='Device index of the camera.')
    parser.add_argument(
        '-nhands',
        '--num_hands',
        dest='num_hands',
        type=int,
        default=2,
        help='Max number of hands to detect.')
    parser.add_argument(
        '-fps',
        '--fps',
        dest='fps',
        type=int,
        default=1,
        help='Show FPS on detection/display visualization')
    parser.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=300,
        help='Width of the frames in the video stream.')
    parser.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=200,
        help='Height of the frames in the video stream.')
    parser.add_argument(
        '-ds',
        '--display',
        dest='display',
        type=int,
        default=1,
        help='Display the detected images using OpenCV. This reduces FPS')
    parser.add_argument(
        '-num-w',
        '--num-workers',
        dest='num_workers',
        type=int,
        default=4,
        help='Number of workers.')
    parser.add_argument(
        '-q-size',
        '--queue-size',
        dest='queue_size',
        type=int,
        default=5,
        help='Size of the queue.')
    args = parser.parse_args()

    input_q = Queue(maxsize=args.queue_size)
    output_q = Queue(maxsize=args.queue_size)

    video_capture = WebcamVideoStream(
        src=args.video_source, width=args.width, height=args.height).start()

    cap_params = {}
    frame_processed = 0
    cap_params['im_width'], cap_params['im_height'] = video_capture.size()
    cap_params['score_thresh'] = score_thresh

    # max number of hands we want to detect/track
    cap_params['num_hands_detect'] = args.num_hands

    print(cap_params, args)

    # spin up workers to paralleize detection.
    pool = Pool(args.num_workers, worker,
                (input_q, output_q, cap_params, frame_processed))

    start_time = datetime.datetime.now()
    num_frames = 0
    fps = 0
    index = 0

    cv2.namedWindow('Multi-Threaded Detection', cv2.WINDOW_NORMAL)

    while True:
        frame = video_capture.read()
        frame = cv2.flip(frame, 1)
        index += 1

        input_q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        output_frame = output_q.get()

        output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        num_frames += 1
        fps = num_frames / elapsed_time
        #print("frame ",  index, num_frames, elapsed_time, fps)

        if (output_frame is not None):
            if (args.display > 0):
                if (args.fps > 0):
                    #detector_utils.draw_fps_on_image("FPS : " + str(int(fps)), output_frame)
                    pass
                cv2.imshow('Multi-Threaded Detection', output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                if (num_frames == 400):
                    num_frames = 0
                    start_time = datetime.datetime.now()
                else:
                    print("frames processed: ", index, "elapsed time: ",
                          elapsed_time, "fps: ", str(int(fps)))
        else:
            # print("video end")
            break
    elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
    fps = num_frames / elapsed_time
    print("fps", fps)
    pool.terminate()
    video_capture.stop()
    cv2.destroyAllWindows()
