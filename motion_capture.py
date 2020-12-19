import cv2
import time
import pandas
# importing datetime class from datetime library
from datetime import datetime
import serial_manip


ix = -1
iy = -1
drawing = False
crop = False
rect = [(0, 0), (0, 0)]
selection_zones = []


def draw_rectangle_with_drag(event, x, y, flags, param):
    global ix, iy, drawing, rect
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rect = [(ix, iy), (x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rect = [(ix, iy), (x, y)]
        selection_zones.append([(ix, iy), (x, y)])


def process_frame(current_frame, selected_rect,  static_back, crop_enabled, bks, thrsh, a_size):
    motion = 0
    # Converting color image to gray_scale image
    gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur
    # so that change can be find easily
    gray = cv2.blur(gray, bks, cv2.BORDER_DEFAULT)
    gray_cropped = gray[selected_rect[0][1]:selected_rect[1][1], selected_rect[0][0]:selected_rect[1][0]].copy()

    # In first iteration we assign the value
    # of static_back to our first frame
    static_back_cropped = None
    if static_back is None:
        static_back = gray
        return static_back, motion
    if crop_enabled:
        static_back_cropped = static_back[selected_rect[0][1]:selected_rect[1][1],
                                          selected_rect[0][0]:selected_rect[1][0]].copy()

    # Difference between static background
    # and current frame(which is GaussianBlur)

    if not crop_enabled:
        diff_frame = cv2.absdiff(static_back, gray)
    else:
        diff_frame = cv2.absdiff(static_back_cropped, gray_cropped)

    # If change in between static background and
    # current frame is greater than 30 it will show white color(255)
    try:
        thresh_frame = cv2.threshold(diff_frame, thrsh, 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
        thresh_frame = cv2.blur(thresh_frame, bks, cv2.BORDER_DEFAULT)
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
    except Exception:
        pass

    # Finding contour of moving object
    try:
        cnts, _ = cv2.findContours(thresh_frame.copy(),
                               cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        return static_back, motion

    motion_index = 1
    for contour in cnts:
        if cv2.contourArea(contour) < a_size:
            continue
        motion = 1

        (x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle arround the moving object
        motion = 1
        if not crop_enabled:
            zone = cv2.rectangle(current_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(zone, 'moving object ' + str(motion_index), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 0, 0), 2)
        else:
            zone = cv2.rectangle(current_frame, (x + selected_rect[0][0], y + selected_rect[0][1]),
                          (x + w + selected_rect[0][0], y + h + selected_rect[0][1]),
                          (0, 255, 0), 3)
        motion_index += 1
    return static_back, motion


def start_detection(filename, thresh, area_size, blur_kernel_size, timer=-1):
    global rect, crop

    #com_port = serial_manip.open_serial_port('COM1', 9600)
    motion_map = {}

    # Assigning our static_back to None
    static_back = None

    # List when any moving object appear
    motion_list = [None, None]

    # Time of movement
    movement_time = []

    # Initializing DataFrame, one column is start
    # time and other column is end time
    df = pandas.DataFrame(columns=["Start", "End"])

    # Capturing video
    video = cv2.VideoCapture(filename)

    # Infinite while loop to treat stack of image as video

    start_time = time.time()
    lights_timer = timer
    light_timers = []
    last_run_time = 0
    delta_time = 0

    while True:
        # Reading frame(image) from video
        check, frame = video.read()

        # Initializing motion = 0(no motion)
        motion = 0

        run_time = time.time() - start_time

        delta_time = run_time - last_run_time
        last_run_time = run_time

        print('run time: ' + str(round(run_time)))
        if len(selection_zones) == 0:
            print('timer: ' + str(lights_timer))
        lights_timer -= delta_time

        if len(selection_zones) > 0 and len(light_timers) == 0:
            for i in range(len(selection_zones)):
                light_timers.append(timer)
        elif len(selection_zones) > 0 and len(light_timers) > 0:
            dif = len(selection_zones) - len(light_timers)
            for i in range(dif):
                light_timers.append(timer)

        if len(selection_zones) > 0 and crop:
            zone_index = 1
            for selection in selection_zones:
                static_back, motion = process_frame(frame, selection, static_back, crop, blur_kernel_size, thresh, area_size)
                motion_map[zone_index] = motion
                print('motion in zone ' + str(zone_index) + ': ' + str(motion_map[zone_index] == 1))
                zone_index += 1
        else:
            static_back, motion = process_frame(frame, rect, static_back, crop,
                                                blur_kernel_size, thresh, area_size)

        if not crop:
            if motion == 1 and lights_timer > 0:
                lights_timer = timer
            elif lights_timer < 0:
                print('turn off the lights')
        else:
            for zone, has_motion in motion_map.items():
                current_zone_index = zone-1
                print('timer in zone ' + str(zone) + ': ' + str(light_timers[current_zone_index]))
                if has_motion == 1 and light_timers[current_zone_index] > 0:
                    light_timers[current_zone_index] = timer
                elif has_motion == 1 and light_timers[current_zone_index] <= 0:
                    print('turn on the lights in the zone ' + str(current_zone_index+1))
                    #serial_manip.write_to_serial_port(str(current_zone_index+1))
                    light_timers[current_zone_index] = timer
                elif has_motion == 0 and light_timers[current_zone_index] <= 0:
                    print('turn off the lights in the zone ' + str(current_zone_index+1))
                    #serial_manip.write_to_serial_port(str(current_zone_index + 1) + '0')
                elif has_motion == 0 and light_timers[current_zone_index] > 0:
                    light_timers[current_zone_index] -= delta_time

        if len(selection_zones) > 0:
            zone_index = 0
            for selection in selection_zones:
                if zone_index+1 not in motion_map.keys():
                    motion_map[zone_index+1] = 0
                zone = cv2.rectangle(frame, selection[0], selection[1], (0, 0, 255), 3)
                cv2.putText(zone, 'zone ' + str(zone_index+1) + ', has motion: ' + str(motion_map[zone_index+1]),
                            (selection[0][0]-20, selection[0][1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(zone, 'lights: ' + str(light_timers[zone_index] > 0) + ', timer: ' +
                            str(round(light_timers[zone_index], 2)),
                            (selection[0][0]-20, selection[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                zone_index += 1
        else:
            cv2.rectangle(frame, rect[0], rect[1], (0, 0, 255), 3)

            # Appending status of motion
        motion_list.append(motion)

        motion_list = motion_list[-2:]

        # Appending Start time of motion
        if motion_list[-1] == 1 and motion_list[-2] == 0:
            movement_time.append(datetime.now())

            # Appending End time of motion
        if motion_list[-1] == 0 and motion_list[-2] == 1:
            movement_time.append(datetime.now())

            # Displaying image in gray_scale
        #cv2.imshow("Gray Frame", gray)

        # Displaying the difference in currentframe to
        # the staticframe(very first_frame)
        #cv2.imshow("Difference Frame", diff_frame)

        # Displaying the black and white image in which if
        # intensity difference greater than 30 it will appear white
        #cv2.imshow("Threshold Frame", thresh_frame)

        # Displaying color frame with contour of motion of object
        cv2.imshow("Color Frame", frame)

        key = cv2.waitKey(1)
        # if q entered whole process will stop
        try:
            if key == ord('q'):
                # if something is moving then it append the end time of movement
                if motion == 1:
                    movement_time.append(datetime.now())
                break
            elif key == ord('e'):
                crop = True
            elif key == ord('c'):
                crop = False
                rect = [(0, 0), (0, 0)]
                selection_zones.clear()  # clear selection zones

                lights_timer = timer  # update timer

                # update timers
                for i in range(len(light_timers)):
                    light_timers[i] = timer
        except:
            print("Input error")

    # Appending time of motion in DataFrame
    for i in range(0, len(movement_time), 2):
        df = df.append({"Start": movement_time[i], "End": movement_time[i + 1]}, ignore_index=True)

    # Creating a CSV file in which time of movements will be saved
    df.to_csv("Time_of_movements.csv")

    video.release()

    # Destroying all the windows
    cv2.destroyAllWindows()


def set_call_back():
    cv2.namedWindow(winname='Color Frame')
    cv2.setMouseCallback('Color Frame', draw_rectangle_with_drag)


