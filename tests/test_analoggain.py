import logging
import unittest
import time

from picamera_attributes import variables

class TestAnalogGain(unittest.TestCase):

    _value = 5.3

    def setUp(self):
        self.param = variables.AnalogGain(value = self._value)

    def test_valid_param(self):

        self.param.validate()
        self.assertTrue(self.param.validate())

    
    def test_valid_val(self):
        self.assertEqual(self.param.val, self._value)
        self.assertEqual(self.param.val, self._value)

    def test_updatecam(self):

        self.param.validate()
        try:
            import picamera
            camera = picamera.PiCamera()
            camera.exposure_mode = "off"

            camera = self.param.update_cam(camera)
            time.sleep(2)
            self.assertEqual(float(camera.analog_gain), self._value)
            logging.warning(camera.analog_gain)
     
        except ImportError as e:
            pass

       

if __name__ == '__main__':
    unittest.main()

    #import picamera
    #with picamera.PiCamera() as capture:
    #    ag = variables.AnalogGain(value = 2)
    #    ag.validate()
    #    ps = variables.ParameterSet({"analog_gain": ag})
    #    ps.validate()
    #    ps.cross_verify()
    #    time.sleep(5)
    #    capture.exposure_mode = "off"
    #    print(capture.analog_gain)
    #    capture, attrs = ps.update_cam(capture)
    #    print(capture.analog_gain)

