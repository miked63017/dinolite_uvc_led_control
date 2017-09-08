from collections import OrderedDict
import os
import json
import subprocess
import time

class Device0890:
    def __init__(self, picroscopeObj):
        self.vid_address = "/dev/video0"
        self.product_id = "0890"
        self._load_controls()
        self.picroscopeObj = picroscopeObj
        self._ae_settings = OrderedDict([('1/1000s', "480301001609"),
                                         ('1/500s', "480301001612"),
                                         ('1/250s', "480301001623"),
                                         ('1/125s', "480301001647"),
                                         ('1/60s', "480301001500,480301001694"),
                                         ('1/30s', "480301001501"),
                                         ('1/15s', "480301001502"),
                                         ('1/8s', "480301001504"),
                                         ('1/4s', "480301001511"),
                                         ('1/2s', "480301001511"),
                                         ('1s', "480301001522")])
        self.led_on()
        self._ae_default_key = 7
        self._ae_default_value = self._ae_settings.items()[self._ae_default_key][0]
        self._current_exposure_key = self._ae_default_key
        self._ae_status = "off"
        self.toggle_auto_exposure()

    def _set_vid_address(self,address):
        self.vid_address = address

    def _load_controls(self):
        with open((os.path.dirname(os.path.realpath(__file__)) + "/device" + self.product_id + ".json")) as data_file:
            self.controls = json.load(data_file)

    def list_standard_controls(self):
        for control in self.controls:
            print control["Name"]

    def validate_control_name(self,control):
        valid_control = False
        for ctrl in self.controls:
            if control in ctrl["Name"]:
                valid_control = True
        return valid_control

    def validate_control_value(self,control,value):
        valid_control_value = False
        for ctrl in self.controls:
            if control in ctrl["Name"]:
                if int(value) <= int(control["max"]) and int(value) >= int(control["min"]):
                    valid_control_value = True
        return valid_control_value

    def set_standard_control_value(self,control, value):
        if validate_control_name(control) and validate_control_value(control,value):
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", control, "--", str(value)])
        else:
            print "Passed bad name or value to uvcdynctrl"

    def get_standard_control_value(self,control):
        if validate_control_name(control):
            current_value = subprocess.check_output(["uvcdynctrl", "-d", self.vid_address, "-g", control])
            return current_value.rstrip()
        else:
            print "Passed bad name or value to uvcdynctrl"
            return "Failed!"

    def _set_sane_defaults(self):
        pass

    def flc_on(self):
        return "FLC not available on this device"

    def flc_off(self):
        return "FLC not available on this device"

    def led_dim(self):
        return "FLC not available on this device"

    def led_brighten(self):
        return "FLC not available on this device"

    def led_on(self):
        #leds on
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:3", "8001f1"])

    def toggle_led_1(self):
        return "FLC not available on this device"

    def toggle_led_2(self):
        return "FLC not available on this device"

    def toggle_led_3(self):
        return "FLC not available on this device"

    def toggle_led_4(self):
        return "FLC not available on this device"

    def led_off(self):
        #leds off
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:3", "8001f0"])

    def toggle_auto_exposure(self):
        if self._ae_status == "on":
            #turn AE off
            #uvcdynctrl -S 4:2 05070003357810
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", "4803010380fe"])
            self._ae_status = "off"
            print "AE off"
            time.sleep(2)
            print "Exposure Time: " + self._ae_settings.items()[self._ae_default_key][0]
            self._current_exposure_key = self._ae_default_key
        elif self._ae_status == "off":
            #turn AE on
            #uvcdynctrl -S 4:2 05000003357810
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", "4803010380ff"])
            print "AE on"
            #set to 1/8second exposure time, or whatever we choose as self._ae_default_key
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", self._ae_settings.items()[self._ae_default_key][1]])
            self._ae_status = "on"
        else:
            #if its not on or off then somethng is messed up, lets turn it on anyway to fix the next try
            self._ae_status = "on"

    def increase_exposure_time(self):
        self._change_exposure_time("increase")

    def decrease_exposure_time(self):
        self._change_exposure_time("decrease")

    def _change_exposure_time(self, in_or_de):
        if self._ae_status == "on":
            print "AE must be off to change exposure time!"
            return
        if in_or_de == "increase":
            #increase exposure time
            if len(self._ae_settings.items()) == self._current_exposure_key + 1:
                #we have hit the max here, do nothing
                pass
            else:
                self._current_exposure_key = self._current_exposure_key + 1
                if "1/60s" in self._ae_settings.items()[self._current_exposure_key][0]:
                    #split because we need two commands for 1/60
                    uvc_codes = self._ae_settings.items()[self._current_exposure_key][1].split(",")
                    for code in uvc_codes:
                        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", code])
                else:
                    subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", self._ae_settings.items()[self._current_exposure_key][1]])
            print "Exposure Time: " + self._ae_settings.items()[self._current_exposure_key][0]
        elif in_or_de == "decrease":
            #decrease exposure time
            if self._current_exposure_key == 0:
                #we have hit the min here, do nothing
                pass
            else:
                self._current_exposure_key = self._current_exposure_key - 1
                if "1/60s" in self._ae_settings.items()[self._current_exposure_key][0]:
                    #split because we need two commands for 1/60
                    uvc_codes = self._ae_settings.items()[self._current_exposure_key][1].split(",")
                    for code in uvc_codes:
                        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", code])
                else:
                    subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:5", self._ae_settings.items()[self._current_exposure_key][1]])
            print "Exposure Time: " + self._ae_settings.items()[self._current_exposure_key][0]
        else:
            #IDK what to do here or why we ended up here, pass
            pass

    def _ae_luma_change(self):
        pass
