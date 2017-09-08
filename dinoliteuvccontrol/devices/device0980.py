from collections import OrderedDict
import os
import json
import subprocess
import time

class Device0980:
    def __init__(self, picroscopeObj):
        self.vid_address = "/dev/video0"
        self.product_id = "0980"
        self._load_controls()
        self.picroscopeObj = picroscopeObj
        self._ae_settings = OrderedDict([('1/1000s', "05000001357810"),
                                         ('1/500s', "05010001357810"),
                                         ('1/250s', "05020001357810"),
                                         ('1/125s', "05040001357810"),
                                         ('1/60s', "05080001357810"),
                                         ('1/30s', "05100001357810"),
                                         ('1/15s', "0500000d387810"),
                                         ('1/8s', "051f0001357810"),
                                         ('1/4s', "0508000c387810"),
                                         ('1/2s', "053e0001357810"),
                                         ('1s', "05510035307810"),
                                         ('2s', "050d000c387810"),
                                         ('4s', "05610035307810"),
                                         ('8s', "050f000c387810"),
                                         ('16s', "0510000c387810")])
        self._ae_default_key = 7
        self._ae_default_value = self._ae_settings.items()[self._ae_default_key][0]
        self._current_exposure_key = self._ae_default_key
        self._ae_status = "off"
        self.toggle_auto_exposure()
        #this will ensure AE is on during startup
        self._led1 = 0x0e
        self._led2 = 0x0d
        self._led3 = 0x0b
        self._led4 = 0x07
        self._listOfLights = list()
        self._flc_status = "off"
        self.flc_off()
        self._led_status = "on"
        self.led_on()
        self._flc_led_brightness = 6

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
        if self.validate_control_name(control) and self.validate_control_value(control,value):
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", control, "--", str(value)])
        else:
            print "Passed bad name or value to uvcdynctrl"

    def get_standard_control_value(self,control):
        if self.validate_control_name(control):
            current_value = subprocess.check_output(["uvcdynctrl", "-d", self.vid_address, "-g", control])
            return current_value.rstrip()
        else:
            print "Passed bad name or value to uvcdynctrl"
            return "Failed!"

    def _set_sane_defaults(self):
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Brightness", "--", str(49)])
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Contrast", "--", str(16)])
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Saturation", "--", str(16)])
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Hue", "--", str(0)])
        #subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "White Balance Temperature, Auto", "--", str(1)])
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Gamma", "--", str(64)])
        #subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Power Line Frequency", "--", str(2)])
        #subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "White Balance Temperature", "--", str(4500)])
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Sharpness", "--", str(1)])
        #subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Focus (absolute)", "--", str(1)])
        #subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-s", "Focus, Auto", "--", str(1)])

    def _build_flc_hex_string(self,list_of_lights_to_turn_off):
        if len(list_of_lights_to_turn_off) > 3:
            return "05100004006200"
        elif len(list_of_lights_to_turn_off) < 1:
            return "050f0004006200"
        else:
            flc_hex = None
            for hex_piece in list_of_lights_to_turn_off:
                if flc_hex is None:
                    flc_hex = hex_piece
                else:
                    flc_hex = flc_hex & hex_piece
            baseString = "05" + format(flc_hex, '02x') + "0004006200"
            return baseString

    def flc_on(self):
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "f3010000000000"])
        self._flc_status = "on"
        return "FLC on"

    def flc_off(self):
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "f3000000000000"])
        self._flc_status = "off"
        return "FLC off"

    def led_dim(self):
        #dim
        if self._flc_status == "off":
            print "FLC must be on to dim LEDs!"
            return
        if self._flc_led_brightness == 0:
            #as dim as it gets
            pass
        elif self._flc_led_brightness == 1:
            self._flc_led_brightness -= 1
            #Need to send this to get to 0 brightness
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05000003006200"])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05100004006200"])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05000003006200"])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05100004006200"])
            print "LED 0 Brightness"
        else:
            self._flc_led_brightness -= 1
            #for some reason these get called twice by dino lite software
            code = "050" + str(self._flc_led_brightness) + "0003006200"
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            print "LED " + str(self._flc_led_brightness) + " Brightness"

    def led_brighten(self):
        #brighten
        if self._flc_status == "off":
            print "FLC must be on to brighten LEDs!"
            return
        if self._flc_led_brightness == 6:
            #as bright as it gets
            pass
        elif self._flc_led_brightness == 0:
            self._flc_led_brightness += 1
            #Need to send this to recover from 0 status
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "050f0004006200"])
            code = "050" + str(self._flc_led_brightness) + "0003006200"
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            print "LED " + str(self._flc_led_brightness) + " Brightness"
        else:
            self._flc_led_brightness += 1
            #for some reason these get called twice by dino lite software
            code = "050" + str(self._flc_led_brightness) + "0003006200"
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", code])
            print "LED " + str(self._flc_led_brightness) + " Brightness"

    def led_on(self):
        #leds on
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "f2010000000000"])

    def toggle_led_1(self):
        #led 1 on
        if self._flc_status == "off":
            print "FLC must be on to toggle LED 1!"
            return
        if self._led1 in self._listOfLights:
            newList = list()
            for light in self._listOfLights:
                if light == self._led1:
                    continue
                else:
                    newList.append(light)
            self._listOfLights = newList
            print "LED 1 On"
        else:
            self._listOfLights.append(self._led1)
            print "LED 1 Off"
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._build_flc_hex_string(self._listOfLights)])

    def toggle_led_2(self):
        #led 2 on
        if self._flc_status == "off":
            print "FLC must be on to toggle LED 2!"
            return
        if self._led2 in self._listOfLights:
            newList = list()
            for light in self._listOfLights:
                if light == self._led2:
                    continue
                else:
                    newList.append(light)
            self._listOfLights = newList
            print "LED 2 On"
        else:
            self._listOfLights.append(self._led2)
            print "LED 2 Off"
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._build_flc_hex_string(self._listOfLights)])

    def toggle_led_3(self):
        #led 3 on
        if self._flc_status == "off":
            print "FLC must be on to toggle LED 3!"
            return
        if self._led3 in self._listOfLights:
            newList = list()
            for light in self._listOfLights:
                if light == self._led3:
                    continue
                else:
                    newList.append(light)
            self._listOfLights = newList
            print "LED 3 On"
        else:
            self._listOfLights.append(self._led3)
            print "LED 3 Off"
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._build_flc_hex_string(self._listOfLights)])

    def toggle_led_4(self):
        #led 4 on
        if self._flc_status == "off":
            print "FLC must be on to toggle LED 4!"
            return
        if self._led4 in self._listOfLights:
            newList = list()
            for light in self._listOfLights:
                if light == self._led4:
                    continue
                else:
                    newList.append(light)
            self._listOfLights = newList
            print "LED 4 On"
        else:
            self._listOfLights.append(self._led4)
            print "LED 4 Off"
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._build_flc_hex_string(self._listOfLights)])

    def led_off(self):
        #leds off
        subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "f2000000000000"])

    def toggle_auto_exposure(self):
        if self._ae_status == "on":
            #turn AE off
            #uvcdynctrl -S 4:2 05070003357810
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05070003357810"])
            self._ae_status = "off"
            print "AE off"
            time.sleep(2)
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._ae_settings.items()[self._ae_default_key][1]])
            print "Exposure Time: " + self._ae_settings.items()[self._ae_default_key][0]
            self._current_exposure_key = self._ae_default_key
        elif self._ae_status == "off":
            #turn AE on
            #uvcdynctrl -S 4:2 05000003357810
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", "05000003357810"])
            print "AE on"
            #set to 1/8second exposure time, or whatever we choose as self._ae_default_key
            subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._ae_settings.items()[self._ae_default_key][1]])
            self._current_exposure_key = self._ae_default_key
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
                subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._ae_settings.items()[self._current_exposure_key][1]])
            print "Exposure Time: " + self._ae_settings.items()[self._current_exposure_key][0]
        elif in_or_de == "decrease":
            #decrease exposure time
            if self._current_exposure_key == 0:
                #we have hit the min here, do nothing
                pass
            else:
                self._current_exposure_key = self._current_exposure_key - 1
                subprocess.call(["uvcdynctrl", "-d", self.vid_address, "-S", "4:2", self._ae_settings.items()[self._current_exposure_key][1]])
            print "Exposure Time: " + self._ae_settings.items()[self._current_exposure_key][0]
        else:
            #IDK what to do here or why we ended up here, pass
            pass

    def _ae_luma_change(self):
        pass
