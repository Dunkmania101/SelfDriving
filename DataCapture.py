import serial
import time
import cv2
import os
#import uuid # Should this be here?



def create_serial(port = "COM3", rateithink = 9600, timeout = 1):
    return serial.Serial(port, rateithink, timeout=timeout)

def read_serial(ser):
    if ser.is_open and ser.inWaiting() > 0:
        return ser.readline().decode('utf-8').rstrip()
    return None


def count_files_in_dir(dir_path):
    return sum([len(files) for _, _, files in os.walk(dir_path)])


def main(head_folder = 'data', img_folder = "img_data", pwm_folder = "pwm_data", desired_width = 640, desired_height = 480, camera_id = 1, fps = 8):
    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")


    # Set capture resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)


    img_folder = os.path.join(head_folder, img_folder)
    pwm_folder = os.path.join(head_folder, pwm_folder)

    if not os.path.exists(img_folder):
        # Create the directory
        os.makedirs(img_folder)
        os.makedirs(pwm_folder)

    prev_time = 0
    index = int(count_files_in_dir(img_folder))

    if index > 20:
        index -= 20

    print("sleeping")
    time.sleep(10)

    # Create a serial connection
    ser = create_serial()
    try:
        while True:
            curr_time = time.time()

            # If time elapsed is more than 1/fps, then capture image and read PWM signal
            if curr_time - prev_time > 1/fps:
                current_PWM = read_serial(ser)
                if current_PWM is not None:
                    prev_time = curr_time
                    index += 1

                    # Read the current frame from webcam
                    _, frame = cap.read()

                    # Save the image
                    img_name = f"{img_folder}/{index}.jpg"
                    pwm_name = f"{pwm_folder}/{index}.txt"
                    cv2.imwrite(img_name, cv2.resize(frame, (640, 480)))
            
                    with open(pwm_name, 'w') as f:
                        f.write(f'{current_PWM}')
                        print(current_PWM)
    finally:
        ser.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        exit()

