# APM: Copter landing assistant

## Introduction

<p align = "center">
  <img src = "https://raw.githubusercontent.com/hafiz-kamilin/apm_copter_landing_assistant/master/02_readme_img/1.png" width = "396" height = "462"/>
</p>

This programs are created to augment the user video feeds streamed from the drone to a personal computer. The augmented video will display the distance from the ground and utilize circle Hough Transform (CHT) to find and mark the red circle.

## Test run

<p align = "center">
  <img src = "https://raw.githubusercontent.com/hafiz-kamilin/apm_copter_landing_assistant/master/02_readme_img/2.png" width = "905" height = "387"/>
</p>

1. Install [Win32 Disk Imager](https://sourceforge.net/projects/win32diskimager/) on a Windows PC and write the custom [Raspbian Lite](https://github.com/hafiz-kamilin/custom_raspbian_lite_dronekit) image on a blank SD card to be inserted inside Raspberry Pi 3 model B. As an extra, refer to [Ardupilot guide](http://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html) to set up Raspberry Pi connection with Pixhawk on your own.
2. Install [Advanced IP Scanner](https://www.advanced-ip-scanner.com/) on Windows PC to find the Raspberry Pi IP address and use [Bitvise SSH Client](https://www.bitvise.com/ssh-client-download) to establish the Secure Shell (SSH) connection between Windows PC and Raspberry Pi.
3. Copy [00_pc_windows](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/tree/master/00_pc_windows) folder to a Windows PC and copy [01_rpi_raspian](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/tree/master/01_rpi_raspbian) folder to the Raspberry Pi.
4. Edit the a_prefix_variable.py file inside the folder [00_pc_windows](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/blob/master/00_pc_windows/a_prefix_variable.py) and folder [01_rpi_raspian](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/blob/master/01_rpi_raspbian/a_prefix_variable.py) with Raspberry Pi and Windows PC IP addresss found earlier.
5. Execute [b_tcp_copter_interface.py](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/blob/master/01_rpi_raspbian/b_tcp_copter_interface.py) on the Raspberry Pi and execute [b_drone_landing_assistant.py](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/blob/master/00_pc_windows/b_drone_landing_assistant.py) on the Windows PC. 
6. User will be presented with a video live stream on the Windows PC and the stream will show the distance from the ground and mark any red circle that it found. Prior calibration on [a_prefix_variable.py](https://github.com/hafiz-kamilin/apm_copter_landing_assistant/blob/master/00_pc_windows/a_prefix_variable.py) setting might be needed to detect red in YCrCb color range.