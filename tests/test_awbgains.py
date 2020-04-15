import unittest

from picamera_attributes import variables

class TestAWBGains(unittest.TestCase):

    def setUp(self):
        self.param = variables.AWBGains(value = '1,1')
        self.param_plural = variables.AWBGains(value = (1,1))


    def test_valid_param(self):

        self.param.validate()
        self.assertTrue(self.param.validate())

    def test_valid_param_plural(self):
    
        self.param_plural.validate()
        self.assertTrue(self.param.validate())

    
    def test_valid_val(self):
        self.assertTrue(self.param.val == '1.0,1.0')
        self.assertTrue(self.param_plural.val == '1.0,1.0')       
        

if __name__ == '__main__':
    unittest.main()
