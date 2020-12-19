# auto-lights-control


## This is an automatic lights switching system based on image recognition and motion detection
This application was built as a pet-project by me as an opencv and PyQT introduction.

### App's flow

Application has ***2 modes of motion capture***

1. General motion recognition (uses whole frame to detect motion):
<img src="screenshots/motion_capture_general.png" width="320" height="240">

2. Motion recognition with zone selection (uses zone area to detect motion):
<img src="screenshots/motion_capture_zones.png" width="320" height="240">


### App's settings

You can change motion detection sensitivity (threshold, area and kernel size) and choose timer that will be decreased if zone has no motion and updated if zone has motion.

If timer expires, the light in the specific zone will be switched off.

If the light is off and zone receives motion, it will be then switched on again.


<img src="screenshots/settings.png" width="400" height="300">
