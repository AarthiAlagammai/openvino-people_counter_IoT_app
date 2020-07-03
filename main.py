"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit person to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import os
import sys
import time
import socket
import json
import cv2
import numpy as np
import logging as log
import paho.mqtt.client as mqtt
from random import randint
from argparse import ArgumentParser
from inference import Network

# MQTT server environment variables
HOSTNAME = socket.gethostname()
IPADDRESS = socket.gethostbyname(HOSTNAME)
MQTT_HOST = IPADDRESS
MQTT_PORT = 3001
MQTT_KEEPALIVE_INTERVAL = 60
cpu_extension = "/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so"



def build_argparser():
    """
    Parse command line arguments.

    :return: command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument("-m", "--model", required=True, type=str,
                        help="Path to an xml file with a trained model.")
    parser.add_argument("-i", "--input", required=True, type=str,
                        help="Path to image or video file or webcam feed,use'0' for webcam")
    parser.add_argument("-l", "--cpu_extension", required=False, type=str,
                        default=None,
                        help="MKLDNN (CPU)-targeted custom layers."
                             "Absolute path to a shared library with the"
                             "kernels impl.")
    parser.add_argument("-d", "--device", type=str, default="CPU",
                        help="Specify the target device to infer on: "
                             "CPU, GPU, FPGA or MYRIAD is acceptable. Sample "
                             "will look for a suitable plugin for device "
                             "specified (CPU by default)")
    parser.add_argument("-pt", "--prob_threshold", type=float, default=0.5,
                        help="Probability threshold for detections filtering"
                        "(0.5 by default)")
    
    return parser
a=[]
bb=[]
def draw_boxes(frame, result, width, height,prob_threshold):
    '''
    Draw bounding boxes onto the frame.
    '''
    global frame_count,a
    current_count=0
    current_count_total=0
    for box in result[0][0]: # Output shape is 1x1x100x7
        class_name=box[0]
        count_boxes=(len(box.shape))
        conf = box[2]
        
        if conf >= prob_threshold:
            #frame_count+=1
            xmin = int(box[3] * width)
            ymin = int(box[4] * height)
            xmax = int(box[5] * width)
            ymax = int(box[6] * height)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 1)
            
            x1=(xmax-xmin)/2
            y1=(ymax-ymin)/2
            cx=xmin+x1
            cy=ymin+y1
            cv2.circle(frame,(int(cx),int(cy)),2,(255,0,0),-1)
            a.append([cx,cy])
            current_count+=1
            bd=np.asarray(a)
            if len(bd)>1:
              diff=bd[-1]-bd[-2]
              if (abs(diff[0])>30 and abs(diff[1])>30): 
               #if frame_count>25:
                  current_count_total+=1
                 
            #print(len(a))
        else:
            bb.append(0)
    return len(a),current_count,frame,current_count_total#count_boxes

def connect_mqtt():
    ### TODO: Connect to the MQTT client ###
    client = mqtt.Client()
    client.connect(MQTT_HOST,MQTT_PORT,MQTT_KEEPALIVE_INTERVAL)

    return client


def infer_on_stream(args, client):
    """
    Initialize the inference network, stream video to network,
    and output stats and video.

    :param args: Command line arguments parsed by `build_argparser()`
    :param client: MQTT client
    :return: None
    """
    # Initialise the class
    
    #infer_network = Network()
    current_request_id=0
    last_count=0
    last_count_total=0
    total_count=0
    start_time=0
    last_duration=0
    # Set Probability threshold for detections
    prob_threshold = args.prob_threshold

    ### TODO: Load the model through `infer_network` ###
    #n, c, h, w = infer_network.load_model(args.model, args.device)
    #print(n,c,h,w)
    plugin = Network()

    # Load the network model into the IE
    plugin.load_model(args.model, args.device, cpu_extension)
    net_input_shape = plugin.get_input_shape()
    if args.input == 'CAM':
        input_stream = 0
    elif args.input.endswith('.jpg') or args.input.endswith('.bmp') :
        single_image_mode = True
        input_stream = args.input
    elif  (not args.input.endswith('.jpg')) or (not(args.input.endswith('.bmp'))) :
        input_stream = args.input
        assert os.path.isfile(args.input), "Specified input file doesn't exist"
    else:
        log.error("The file is unsupported.please pass a supported file")
    # Get and open video capture
    cap = cv2.VideoCapture(input_stream)
    if input_stream:
        cap.open(args.input)

    if not cap.isOpened():
        log.error("Unable to open video please specify a correct input file")
   

    # Grab the shape of the input 
    width = int(cap.get(3))
    height = int(cap.get(4))

    # Process frames until the video ends, or process is exited
    while cap.isOpened():
        # Read the next frame
        
        flag, frame = cap.read()
        if not flag:
            break
        key_pressed = cv2.waitKey(60)
        inference_start = time.time()
        # Pre-process the frame
        p_frame = cv2.resize(frame, (net_input_shape[3], net_input_shape[2]))
        p_frame = p_frame.transpose((2,0,1))
        p_frame = p_frame.reshape(1, *p_frame.shape)

        # Perform inference on the frame
        plugin.exec_net(current_request_id,p_frame)

        # Get the output of inference
        if plugin.wait(current_request_id) == 0:
            detection_time = time.time() - inference_start
            result = plugin.get_output(current_request_id)
            # Draw the output mask onto the input
            centroid,current_count,out_frame,current_count_total = draw_boxes(frame,result, width, height,prob_threshold)
            inference_timetaken_message = "Inference time tyaken: {:.4f}ms" \
                .format(detection_time * 1000)
            cv2.putText(frame,inference_timetaken_message, (15, 15),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 10, 0), 1)
            
            if current_count_total >last_count_total:
                
                #start_time = time.time()
                total_count = total_count + current_count_total - last_count_total
                
            if total_count>0:
             if last_duration <= total_count:
                start_time = time.time()
                
                # Publish messages to the MQTT server
                if last_duration < total_count :
                    
                    duration = float(start_time)
                    client.publish("person/duration",
                               json.dumps({"duration": duration}))
               
            
            client.publish("person", json.dumps({"count": current_count,"total": total_count}))
            last_count_total=current_count_total
            last_duration=total_count
            last_count = current_count                
            
                    ### TODO: Send frame to the ffmpeg server
        sys.stdout.buffer.write(out_frame)
        sys.stdout.flush()

        # Break if escape key pressed
        if key_pressed == 27:
            break

    # Release the capture and destroy any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    ### TODO: Disconnect from MQTT
    client.disconnect()




def main():
    """
    Load the network and parse the output.

    :return: None
    """
    # Grab command line args
    args = build_argparser().parse_args()
    # Connect to the MQTT server
    client = connect_mqtt()
    #print("am in main")
    # Perform inference on the input stream
    infer_on_stream(args, client)


if __name__ == '__main__':
    main()
