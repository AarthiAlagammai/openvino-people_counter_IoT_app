# openvino-people_counter_IoT_app
People counter app helps in counting the number of people in the frame in real time, average duration of people in the frame and the total count of people

People counting applications can be used in various scenarios and applications like retail store, supermarket, shopping malls, airport. For example, Once a person is detected, We can follow or track the object which can be used for further analysis to understand certain behaviours like time spent shopping , to avoid long queues in billing counters etc.
## Requirements
 ### Hardware
  * 6th to 10th generation Intel® Core™ processor with Iris® Pro graphics or Intel® HD Graphics.
  * OR  Intel® Neural Compute Stick 2 (NCS2)

 ### Software
  * Intel® Distribution of OpenVINO™ toolkit 2019 R3 or higher release
  * Node v6.17.1
  * Npm v3.10.10
  * CMake
  * MQTT Mosca server
## Stepup
### Openvino installation:
  To run the application in this tutorial, the OpenVINO™ toolkit and its dependencies must already be installed and verified using the included demos.
  The installion guide for
  [Windows](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_windows.html)
  [Linux](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html)
  [Mac](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_macos.html)
  
  ### Install Npm:
  There are three components that need to be running in separate terminals for this application to work:
  * MQTT Mosca server
  * Node.js* Web server
  * FFmpeg server
  * For mosca server:

```
cd <app_dir>/webservice/server
npm install 
```

* For Web server:
```
cd ../ui
npm install
```
Note: If any configuration errors occur in mosca server or Web server while using npm install, use the below commands:
```
sudo npm install npm -g 
rm -rf node_modules
npm cache clean
npm config set registry "http://registry.npmjs.org"
npm install
```
## Steps for Running the Application
 ### Generate IR Files
 Based on initial experimental work, I used SSD based object detection
 * Download the pre-trained model from here:- http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
 * Extract the files:-
```
tar -xvf ssd_mobilenet_v2_coco_2018_03_29.tar.gz
```
* Go to the ssd_mobilenet_v2 directory and run the following command line:-
```
python /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py --input_model frozen_inference_graph.pb --tensorflow_object_detection_api_pipeline_config pipeline.config --tensorflow_use_custom_operations_config /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json --reverse_input_channel
```
* Create model directory in the app directory and move the generated .xml and .bin file into created model directory
### Running the Application
Terminal 1: Start the Mosca server
```
cd webservice/server/node-server
node ./server.js
```
 You should see the following message, if successful:
```
Mosca server started.
```
Terminal 2: Start webserver GUI
```
cd webservice/ui
npm run dev
```
You should see the following message in the terminal.
```
webpack: Compiled successfully
```
Terminal 3: FFmpeg Server
```
sudo ffserver -f ./ffmpeg/server.conf
```
Terminal 4: Run the Demo
Source the terminal
```
source /opt/intel/openvino/bin/setupvars.sh -pyver 3.5
```
Now run following commands on same terminal.

For running on the CPU-Depending on whether you are using Linux or Mac, the filename will be either libcpu_extension_sse4.so or libcpu_extension.dylib, respectively. (The Linux filename may be different if you are using a AVX architecture)
```
python3 main.py -i resources/Pedestrain_Detect_2_1_1.mp4 -m model/frozen_inference_graph.xml -l /opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_sse4.so -d CPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://localhost:8090/fac.ffm
```
To To see the output on a web based interface, open the link http://0.0.0.0:3004/ in a browser.

For running on the GPU
```
python3 main.py -i resources/Pedestrian_Detect_2_1_1.mp4 -m model/frozen_inference_graph.xml -d GPU -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://localhost:8090/fac.ffm
```
To see the output on a web based interface, open the link http://0.0.0.0:3004/ in a browser.

For running on  Intel® Neural Compute Stick
```
python3.5 main.py -d MYRIAD -i resources/Pedestrian_Detect_2_1_1.mp4 -m model/frozen_inference_graph.xml  -pt 0.6 | ffmpeg -v warning -f rawvideo -pixel_format bgr24 -video_size 768x432 -framerate 24 -i - http://0.0.0.0:3004/fac.ffm
```
