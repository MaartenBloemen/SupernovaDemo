import time
import cv2
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--location', type=str, help='Location to safe the data', default='/home/maarten/Documents/SupernovaTrainData/space')

    args = parser.parse_args()
    i = 1

    vc = cv2.VideoCapture(0)
    rval, frame = vc.read()

    time.sleep(3)

    while rval:
        print('Saved image {}'.format(i))
        cv2.imwrite('{}/{}.jpg'.format(args.location, i), frame)
        i += 1
        time.sleep(0.1)
        rval, frame = vc.read()
        if i == 51: break
