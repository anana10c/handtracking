from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import datetime
import argparse

splatters = []

detection_graph, sess = detector_utils.load_inference_graph()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-sth',
        '--scorethreshold',
        dest='score_thresh',
        type=float,
        default=0.2,
        help='Score threshold for displaying bounding boxes')
    parser.add_argument(
        '-fps',
        '--fps',
        dest='fps',
        type=int,
        default=1,
        help='Show FPS on detection/display visualization')
    parser.add_argument(
        '-src',
        '--source',
        dest='video_source',
        default=0,
        help='Device index of the camera.')
    parser.add_argument(
        '-wd',
        '--width',
        dest='width',
        type=int,
        default=320,
        help='Width of the frames in the video stream.')
    parser.add_argument(
        '-ht',
        '--height',
        dest='height',
        type=int,
        default=180,
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

    cap = cv2.VideoCapture(args.video_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    start_time = datetime.datetime.now()
    num_frames = 0
    im_width, im_height = (cap.get(3), cap.get(4))
    # max number of hands we want to detect/track
    num_hands_detect = 2

    cv2.namedWindow('Camvas', cv2.WINDOW_NORMAL)

    prev_areas = []
    prev_toplefts = []
    frame_count = 0
    
    while True:
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        ret, image_np = cap.read()
        # image_np = cv2.flip(image_np, 1)
        try:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        except:
            print("Error converting to RGB")

        # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
        # while scores contains the confidence for each of these boxes.
        # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

        boxes, scores = detector_utils.detect_objects(image_np,
                                                      detection_graph, sess)

        # draw bounding boxes on frame
        detector_utils.draw_box_on_image(num_hands_detect, args.score_thresh,
                                         scores, boxes, im_width, im_height,
                                         image_np)
        
        toplefts, bottomrights, areas = detector_utils.get_corners(cap_params['num_hands_detect'], cap_params["score_thresh"], scores, boxes, cap_params['im_width'], cap_params['im_height'])

        if frame_count >= 1:
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
                    print("current:", current_area)
                    print("prev:", prev_area)
                    splatters.append(Splatter(toplefts[current_index], bottomrights[current_index]))
                    frame_count = 0
                if len(toplefts) == 2 and len(prev_toplefts) == 2:
                    if compare_areas(areas[1-current_index], prev_areas[1-prev_index], 2):
                        print("current:", current_area)
                        print("prev:", prev_area)
                        splatters.append(Splatter(toplefts[1-current_index], bottomrights[1-current_index]))
                        frame_count = 0
        else:
            frame_count += 1

        # for x in range(0, len(toplefts)):
        #     splatters.append(Splatter(toplefts[x], bottomrights[x]))

        for splotch in splatters:
            if splotch.opacity == 0:
                splatters.remove(splotch)
                continue

            roi = image_np[splotch.topleft[1]:splotch.bottomright[1], splotch.topleft[0]:splotch.bottomright[0]]
            background = roi.copy()
            overlap = roi.copy()
            background[splotch.outline[:, :, 3] != 0] = (0, 0, 0)
            overlap[splotch.outline[:, :, 3] == 0] = (0, 0, 0)
            overlap_area = cv2.addWeighted(overlap, 1-splotch.opacity, splotch.outline[:, :, 0:3], splotch.opacity, 0)
            dst = cv2.add(overlap_area, background)
            image_np[splotch.topleft[1]:splotch.bottomright[1], splotch.topleft[0]:splotch.bottomright[0]] = dst
            splotch.fade()

        prev_areas = areas.copy()
        prev_toplefts = toplefts.copy()
    
        # Calculate Frames per second (FPS)
        num_frames += 1
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time

        if (args.display > 0):
            # Display FPS on frame
            if (args.fps > 0):
                detector_utils.draw_fps_on_image("FPS : " + str(int(fps)),
                                                 image_np)

            cv2.imshow('Single-Threaded Detection',
                       cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        else:
            print("frames processed: ", num_frames, "elapsed time: ",
                  elapsed_time, "fps: ", str(int(fps)))
