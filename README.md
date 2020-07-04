# openvino-people_counter_IoT_app
People counter app helps in counting the number of people in the frame in real time, average duration of people in the frame and the total count of people

People counting applications can be used in various scenarios and applications like retail store, supermarket, shopping malls, airport. For example, Once a person is detected, We can follow or track the object which can be used for further analysis to understand certain behaviours like time spent shopping , to avoid long queues in billing counters etc.
## Stepup
### Openvino installation:
  To run the application in this tutorial, the OpenVINO™ toolkit and its dependencies must already be installed and verified using the included demos.
  The installion guide for
  [Windows](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_windows.html)
  [Linux](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html)
  [Mac](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_macos.html)
  
  ### Install Npm
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
