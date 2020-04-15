import unittest

from picamera_attributes.variables import Iso, ShutterSpeed, ExposureMode, AWBGains, AWBGain, AWBMode, Zoom, ParameterSet

iso = Iso(value = 100)
iso.validate()

shutter_speed = ShutterSpeed(value=30000)
shutter_speed.validate()

exposure_mode = ExposureMode(value = "auto")
exposure_mode.validate()

awb_gains = AWBGains(value='1,1')
awb_gains.validate()

awb_mode = AWBMode(value='off')
awb_gains.validate()


zoom = Zoom(value = (0,0,1,1))
zoom.validate()

class TestParameterSetInitializationFromCameraParam(unittest.TestCase):

    def setUp(self):        
        self.param_set = ParameterSet({"zoom": zoom, "iso": iso, "shutter_speed": shutter_speed, "exposure_mode": exposure_mode, "awb_gains": awb_gains})

    def test_validate(self):
        self.param_set.validate()
        
    def test_cross_verify(self):
        self.param_set.cross_verify()


class TestParameterSetInitializationFromRaw(unittest.TestCase):

    def setUp(self):        
        self.param_set = ParameterSet({"zoom": (0,0,1,1), "iso": 0, "shutter_speed": 25000, "exposure_mode": "off", "awb_mode": "off", "awb_gains": (1.8,1.5)})
        self.param_set.validate()
        self.param_set.cross_verify()
              
    def test_init(self):
        self.assertEqual(self.param_set["awb_gains"].val, '1.8,1.5')
        self.assertIs(type(self.param_set["awb_gains"]), AWBGains)

class TestParameterCrossVerifyWorks(unittest.TestCase):
    
    def setUp(self):        
        self.param_set_auto = ParameterSet({"zoom": (0,0,1,1), "iso": 0, "shutter_speed": 25000, "exposure_mode": "auto", "awb_mode": "auto", "awb_gains": (1.8,1.5)})
        self.param_set_auto.validate()
        self.param_set_auto.cross_verify()

        self.param_set_off = ParameterSet({"zoom": (0,0,1,1), "iso": 0, "shutter_speed": 25000, "exposure_mode": "off", "awb_mode": "auto", "awb_gains": (1.8,1.5)})
        self.param_set_off.validate()
        self.param_set_off.cross_verify()
        
    def test_auto_exposure_mode(self):

        self.assertFalse(self.param_set_auto.params["shutter_speed"]._active)
        
        self.assertFalse(self.param_set_off.params["awb_gains"]._active)
        self.assertTrue(self.param_set_off.params["shutter_speed"]._active)

        
class TestParameterSetTransfer(unittest.TestCase):

    def setUp(self):
        self.param_set = ParameterSet({"zoom": zoom, "iso": iso, "shutter_speed": shutter_speed, "exposure_mode": exposure_mode, "awb_gains": awb_gains})
        self.param_set.validate()
        self.param_set.cross_verify()

        self.qs  = self.param_set.urlencode()
        self.param_set_restore = ParameterSet({})
        
    def test_restore(self):
        
        self.param_set_restore.restore_qs(self.qs)
        self.param_set_restore.validate()
        self.param_set_restore.cross_verify()

    def test_equal(self):

        self.param_set_restore.restore_qs(self.qs)
        self.param_set_restore.validate()
        self.param_set_restore.cross_verify()


        self.assertTrue(self.param_set == self.param_set_restore)
            

if __name__ == '__main__':
    unittest.main()


    


    
