import unittest

from picamera_attributes import variables

class TestAWBMode(unittest.TestCase):

    def setUp(self):
        self.var_off = variables.AWBMode(value="off")
        self.var_auto = variables.AWBMode(value="auto")
        self.var_invalid = variables.AWBMode(value="foo")

    def test_validate_off(self):
        self.var_off.validate()
        self.assertTrue(self.var_off._active)

    def test_validate_auto(self):

        self.var_auto.validate()
        self.assertTrue(self.var_auto._active)
    
    def test_validate_invalid(self):
        try:
            self.var_invalid.validate()
            valid = True
        except AssertionError:
            valid = False

        self.assertFalse(valid)
        

if __name__ == '__main__':
    unittest.main()
