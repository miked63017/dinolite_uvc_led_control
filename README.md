# Dino Lite UVC Control

I needed this module to control various functions of a few Dino Lite USB
microscopes that were not working with standard UVC controls. I did a bunch of
reverse engineering to figure out what was being sent in windows to control
things like LEDs and autoexposure, that were either not working in Linux with
UVC or were not present at all.

## Getting Started

```python
import dinoliteuvccontrol

#debug allows some extra messages to be printed to console

class args: debug=True


worker = dinoliteuvccontrol.DinoLiteUVCControl(args)

# module is capable of controlling multiple devices simultaneously;
# if you only have one connected default to index 0

cam0 = worker.ourDevices[0]
cam1 = worker.ourDevices[1]

#Basic LED control
cam0.led_off()
cam0.led_on()

#FLC LED control
cam0.flc_on()
#turn off led 1-4
cam0.toggle_led_1()
cam0.toggle_led_2()
cam0.toggle_led_3()
cam0.toggle_led_4()

#turn led 1-4 back on
cam0.toggle_led_4()
cam0.toggle_led_2()
cam0.toggle_led_1()
cam0.toggle_led_3()

#FLC LED Dim and Brighten, 6 levels
cam0.led_dim()
cam0.led_brighten()

#List standard UVC controls available through this module
cam0.list_standard_controls()

#Get current value of standard controls
cam0.get_standard_control_value("Brightness")

#Set value of standard control
cam0.set_standard_control_value("Brightness", "27")

#Toggle autoexposure
cam0.toggle_auto_exposure()

#Increase and/or decrease exposure time when AE turned off
cam0.increase_exposure_time()
cam0.decrease_exposure_time()
```

### Prerequisites

Must have uvcdynctrl installed on your system, this module calls this command a
lot. Obviously you will also need a Dino Lite USB microscope, currently the 2
models that I know are working are a168:0980, and a168:0890(with kernel patch
applied). Most of the controls only work while the microscope is in use, you
can start it up in linux with a command similar to:

```shell
mplayer -tv driver=v4l2:gain=1:width=640:height=480:device=/dev/video1:outfmt=yuy2 tv://
```

### Installing

If you are using the older model a kernel patch will need to be applied. If you
are using the newer model no kernel patch is needed. Install uvcdynctrl and
video4linux2 if not already installed. Then install this module by doing the
following:

```shell
#clone this repo and cd into the directory
sudo python setup.py install
```

### Current status

Documentation and tests are few and far between, and this module will mainly be
consumed by another project that I will be uploading soon. With that in mind
pull requests are welcome, as long as it won't break the other project too
much.

### Kernel patch

Please look in kernelpatch.diff to see the details, it is a small one but you
will need to rebuild the kernel and boot into the newly built kernel for this
to work with the older Dino Lite models. A lot of credit goes to the author of
the original kernel patch that I just built upon, Alexandre Macabies
<web+oss@zopieux.com> and the helpful folks on the uvc mailing list

I have tested this patch on several newish versions of the kernel source and
have not had an instance where it has failed yet. This was also tested on
Raspberry Pi and Orange Pi kernels with no issue.

### Notes

Also please have a look in Notes.txt for random notes I made along the way
while reverse engineering all the proprietary calls. FWIW this was done via
virtualbox running on a linux host, with wireshark and usbmon running, and a
windows 10 vm with USB passthru.
