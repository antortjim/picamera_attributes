__author__ = 'antonio'

import logging
import math
import urllib.request, urllib.error, urllib.parse
from fractions import Fraction
import traceback

# inputs in html

# sliders -> numeric input
# radio buttons -> choice
# switch -> on / off

# Index of supported parameters
#
#              # analog_gain               GET / SET ? float
#              # digital_gain              GET / SET ? float
#  IMPLEMENTED # awb_gains                 GET / SET   fraction bounded 0,-8 length 2
#  IMPLEMENTED # awb_mode                  GET / SET   category
#  IMPLEMENTED # exposure_mode             GET / SET   category
#  IMPLEMENTED # shutter_speed                   SET   integer limited
#  IMPLEMENTED # exposure_speed            GET         integer limited
#  IMPLEMENTED # exposure_compensation     GET / SET   integer bounded -25,+25
#  IMPLEMENTED # iso                       GET / SET   integer bounded steps 100 200 320  400 500 740 800
#  IMPLEMENTED # brightness                GET / SET   integer bounded 0,+100
#  IMPLEMENTED # rotation                  GET / SET   integer bounded steps 0, 90, 180, 270
#  IMPLEMENTED # saturation                GET / SET   integer bounded -100, 100
#  IMPLEMENTED # sharpness                 GET / SET   integer bounded -100, 100
#  IMPLEMENTED # contrast                  GET / SET   integer bounded -100, 100
#              # color_effects             GET / SET   integer bounded 0,255+None length 2
#              # meter_mode                GET / SET   category (average, spot, backlit, matrix)
#              # video_denoise             GET / SET   boolean
#              # vflip                     GET / SET   boolean
#              # hflip                     GET / SET   boolean
#              # video_stabilization       GET / SET   boolean
#              # resolution                GET / SET   integer length 2 STARTUP
#              # framerate                 GET / SET   integer STARTUP
#              # framerate_delta                 SET   fraction 
#              # framerate_range           GET / SET   fraction
#  IMPLEMENTED # zoom                      GET / SET   float bounded 0,1 length 4



class CameraParameter:

    _length = 1
    _depends_on = None
    _var_type = None
    _name = None
    _default = None
    _value = None 

    def __init__(self, value=None):

        self._active = False

        # logging.warning(f'Running {self.__class__.__name__}.__init__()')

        # if the lenght of the data is 1
        # its _type and _var_type are the same
        # i.e. an item of length 1 could be str or int for both
        # but length 2 needs to be _var_type tuple 
        if self._length == 1:
            self._type = self._var_type

        # if no value is provided upon initialization
        # use _default
 
        if value is None:
            self._value = self._default

        # use the first element of value if it should be length 1
        # and we passed either a list or tuple of length 1
        # useful for initializing with the output of
        # urlllib.parse.parse_qs
        elif type(value) in [list, tuple] and len(value) == 1:
            self._value = self.coerce(value[0])
        
        else:
            self._value = self.coerce(value)

    def coerce(self, value):
        r"""Make sure the value entered is mapped to the _var_type and _type of the class
        In singular classes, they are the same, while in plurals, _var_type is tuple
        """

        # if it's plural!   
        if self._length > 1:

            # if the passed value is a str
            # split it,
            # coerce the parts to _type
            # and create a _var_type
            if type(value) is str:
                # assume csv
                try:
                    value = self._var_type([self._type(v) for v in  value.split(',')])
                except ValueError as e:
                    logging.error(f"Could not coerce {value} to var_type {self._var_type} with data of type {self._type}")
                    logging.error(traceback.format_exc())
                    raise e

            # if passed a fraction, coerce to float
            if type(value) is Fraction and self._type is float:
                value = float(value)
                # if the _type is not float, value should not be of type Fraction
            elif type(value) is Fraction and self._type is not float:
                raise Exception
                # check the result is of the expected length
            try:
                assert len(value) == self._length
            except AssertionError as e:
               logging.error(f"{self._name} expected data of length {self._length}")
               logging.error(f"Received data of length {len(self._value)}")
               raise e

        else:
            try:
                value = self._type(value)
            except ValueError as e:
                logging.error(f"Could not coerce {self._value} to type {self._var_type}")
                raise e

        return value
        

    @property
    def val(self):
        if self._length > 1:
            return self._var_type((self._type(v._value) for v in self._value))
        else:
            return self._var_type(self._value)

    def __eq__(self, other):
            
        try:
            assert isinstance(self, self.__class__) and isinstance(other, other.__class__)
        except AssertionError:
            logging.warning(f'Please ensure objects on both sides of equal sign are of type {self.__class__}')
            return False

        result = self._value == other._value and self._active == other._active
        return result

    def machine(self):
        return self._value
    
    def validate(self):

        if self._length > 1:
            try:
                assert len(self._value) == self._length
            except AssertionError as e:
                logging.error("value of {self._name} is not of length {self._length}")
                raise e
        
            try:
                tests = [type(v) in [self._var_type, type(None)] for v in self._value]
                for t in tests:
                    assert t
                    
            except AssertionError as e:
                logging.error(f"Passed value must be of type {self._var_type}. You passed {self._value} ({type(self._value).__name__} type)")
                raise e
        else:
            try:
                assert type(self._value) in [self._var_type, type(None)]
            except AssertionError as e: 
                logging.error(f"Passed value must be of type {self._var_type}. You passed {self._value} ({type(self._value).__name__} type)")
                raise e

        self._active = True
        return self._active

    def __str__(self):
        return f"{self.__class__.__name__}(value={self._value})"

    def __repr__(self):
        return  self.__str__()

    def __iter__(self):

        if self._var_type is not tuple:
            return [self._value]
        
        else:
            return self._value

    def __eval__(self):
        if type(self._var_type) is not tuple:
            return self._value
        else:
            return tuple((v._value for v in self._value))

    def update_cam(self, camera):
        camera = self._set(camera)
        return camera

    def _set(self, camera):

        if self._value != self._get(camera) and self._active:
            try:
                setattr(camera, self._name, self._value)
            except Exception as e:
                logging.error(f"Could not SET parameter {self._name} to {self._value}")
                logging.error(f"{type(self._value)}")
                
                logging.error(e)
                logging.error(traceback.format_exc())

        elif self._value == self._get(camera):
            logging.debug("value in camera already identical")
        elif not self._active:
            logging.warning(f"{self.__class__.__name__} is not active")

        
        return camera

    def _get(self, camera, name=None):
        try:
            if name is None: name = self._name
            value = getattr(camera, name)
            param = ParameterSet._supported[self._name](value=value)
            value = param.val

        except Exception as e:
            logging.error(f"Could not GET parameter {self._name}")
            logging.error(type(camera))
            logging.error(e)
            value = self._default
        
        return value

    def get(self, camera, name):
        return self._get(camera, name)

class BooleanParameter(CameraParameter):

    _var_type = bool


class CategoryParameter(CameraParameter):

    _options = []
    _var_type = str

    # TODO
    # Uncomment if I need to explictly inherit the __init__
    # Otherwise remove this!
    # def __init__(self, *args, **kwargs):
    #     super().__init_(*args, **kwargs)

    def validate(self):

        super().validate()
        try:
            assert self._value in self._options
        except AssertionError as e:
            logging.warning(f"Passed value must be one of {self._options}")
            raise e

        self._active = True 
        return self._active 

class BoundedParameter(CameraParameter):

    _min_val = None
    _max_val = None
    _options = [None]
    # subclasses need to define a min and a max or a list of options
   
    def validate(self):

        if not super().validate():
            return False
                
        if self._options[0] is not None:
            try:
                assert self._value in self._options
            except AssertionError as e:
                logging.error(f"Param: {self._name}. Passed value must be one of {self._options}. You passed {self._value}")
                raise e
        
        elif self._max_val is not None and self._min_val is not None:
            try:
                assert self._value >= self._min_val and self._value <= self._max_val
            except AssertionError as e:
                logging.error(f"Passed value must be within [{self._min_val}, {self._max_val}]")
                raise e
        else:
            raise AssertionError("Please define either _options OR (_min_val AND _max_val)")

        self._active = True
        return self._active



# Instantiate classes to capture PiCamera parameters

class IntegerBoundedParameter(BoundedParameter):

    _var_type = int

    # TODO
    # Uncomment if I need to explictly inherit the __init__
    # Otherwise remove this!
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

class FloatBoundedParameter(BoundedParameter):

    _var_type = float
    _type = float

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round()
        
    def round(self, digits=5):
        if self._length > 1:
            self._value = tuple((float(round(v, digits)) for v in self._value))
        else:
            self._value = float(round(self._value, digits))


class Saturation(IntegerBoundedParameter):

    _min_val = -100
    _max_val = 100
    _default = 0
    _name = "saturation"
            
class Sharpness(IntegerBoundedParameter):

    _min_val = -100
    _max_val = 100
    _default = 0
    _name = "sharpness"
    
class Contrast(IntegerBoundedParameter):

    _min_val = -100
    _max_val = 100
    _default = 0
    _name = "contrast"

class Brightness(IntegerBoundedParameter):

    _min_val = -100
    _max_val = 100
    _default = 50
    _name = "brightness"

class ExposureCompensation(IntegerBoundedParameter):

    _min_val = -25
    _max_val = 25
    _default = 0
    _name = "exposure_compensation"

class Iso(IntegerBoundedParameter):
    
    _options = [0, 100, 200, 320, 400, 500, 640, 800]
    _default = 0
    _name = "iso"

class Rotation(IntegerBoundedParameter):

    _options = [0, 90, 180, 270]
    _default = 0
    _name = "rotation"


class Framerate(FloatBoundedParameter):

    _min_val = 0.0
    _max_val = 30.0
    _name = "framerate"



class DigitalGain(FloatBoundedParameter):
    _min_val = 0.0
    _max_val = 30.0
    _name = "digital_gain"

    def update_cam(self, camera):
        return camera
 

class AnalogGain(FloatBoundedParameter):
    _min_val = 0.0
    _max_val = 30.0
    _name = "analog_gain"

    def update_cam(self, camera):
        return camera
    
# class ColorEffect(IntegerBoundedParameter):

#     # TODO

#     def __init__(self, value = None, *args, **kwargs):
#         super().__init__(value = value, min_val = 0, max_val = 255, name = "color_effect", *args, **kwargs)
    
#     def validate(self):
#         if self._value is None:
#             return
#         else:
#             super().validate()


class AWBGain(FloatBoundedParameter):
    _min_val = 0
    _max_val = 8
    _name = "awb_gain"
    _default = 0

    # TODO
    # def __init__(self, value, *args, **kwargs):
    #     super().__init__(value = value, *args, **kwargs)



class Plural:

    _length = 2
    _var_type = tuple
    _value = None

    def __init__(self, *args, **kwargs):
        # find the method resolution order chain
        mro = self.__class__.__mro__
        # find in which position Plural is
        t = [m is Plural for m in mro]    
        # the singular class is the one after Plural
        singular_index = [i for i, x in enumerate(t) if x][0] + 1                                                
        # get the singular cass
        self.singular_class = mro[singular_index]
        # run its init method
        mro[singular_index].__init__(self, *args, **kwargs)

    def machine(self):
        #import ipdb; ipdb.set_trace()

        if all([isinstance(v, self.singular_class) for v in self._value]):
            return tuple((v._value for v in self._value))
        else:
            return self._value

    def _set(self, camera):

        if self.machine() != self._get(camera) and self._active:
            try:
                setattr(camera, self._name, self.machine())
            except Exception as e:
                logging.error(f"Could not SET Parameter {self._name} to {self.machine()}")
                logging.error(e)
        elif self.machine() == self._get(camera, self._name):
            logging.debug("value in camera already identical")
        elif not self._active:
            logging.warning(f"{self.__class__.__name__} is not active")

        
        return camera


    @property
    def val(self):
        return ','.join([str(e) for e in self.machine()])

    def validate(self):
        # validate the parameter if
        # all elements are of the right type and each validates
        try:
            assert isinstance(self._value[0], self.singular_class) and isinstance(self._value[1], self.singular_class)
        except AssertionError as e:
            try:
                assert all([isinstance(v, self._type) for v in self._value])
                self._value = self._var_type((self.singular_class(value=v) for v in self._value))
            except AssertionError as e:
                logging.error(f"One of the elements in the tuple is not an {self.singular_class.__name__} or float")
                raise e
       
        try:
            for v in self._value:
                v.validate()
        except AssertionError as e:
            logging.error(f"At least one {self.singular_class.__name__} is not valid. Please see below:")
            logging.error(e)

        self._active = True
        return self._active 


class ZoomCoord(FloatBoundedParameter):
    _min_val = 0
    _max_val = 1
    _name = "zoom_coord"
    _default = 0

class Dimension(IntegerBoundedParameter):
    _min_val = 0
    _max_val = 3000
    _default = 500
    _name = "dimension"

class Resolution(Plural, Dimension):

    _length = 2
    _name = "resolution"
    _default = (1280, 960)

class Zoom(Plural, ZoomCoord):

    _length = 4
    _name = "zoom"
    _default = (0,0,1,1)
    
class AWBGains(Plural, AWBGain):

    _length = 2
    _name = "awb_gains"
    _depends_on = {"awb_mode": "off"}
    _default = (0, 0)

    # def __init__(self, value, *args, **kwargs):
    #     print(super(AWBGain, self))
    #     super().__init__(value = value, *args, **kwargs)


    #def __str__(self):
    #    return f"{self.__class__.__name__}(value={self.machine()})"


class AWBMode(CategoryParameter):

    _options = [
        "off", "auto", "sunlight", "cloudy", "shade",
        "tungsten", "fluorescent", "incandescent",
        "flash", "horizon"
    ]
    _default = "auto"
    _name = "awb_mode"


class ExposureMode(CategoryParameter):

    _options = [
        'off', 'auto', 'night', 'nightpreview', 'backlight',
        'spotlight', 'sports', 'snow', 'beach', 'verylong',
        'fixedfps', 'antishake', 'fireworks'
    ]
    _default = "auto"
    _name = "exposure_mode"


class ExposureSpeed(IntegerBoundedParameter):

    _min_val = 0
    _max_val = math.inf
    _default = 0
    _name = "exposure_speed"

    def _set(self, camera):
        if self._name == "exposure_speed":
            return camera
        else:
            return super()._set(camera)

    def _get(self, camera, name=None):
        value = super()._get(camera, name)
        logging.warning(f"{self.__class__.__name__}._get(camera) returns...")
        logging.warning(value)
        return value
 

class ShutterSpeed(ExposureSpeed):

    _depends_on = {"exposure_mode": "off"}
    _min_val = 0
    _max_val = math.inf
    _default = 0
    _name = "shutter_speed"

    def _get(self, camera, name=None):
        # use the get method of ExposureSpeed
        value = super()._get(camera, name = "exposure_speed")
        return value

supported = {
    "awb_gains" : AWBGains, "awb_mode": AWBMode,
    "exposure_mode": ExposureMode, "shutter_speed": ShutterSpeed,
    "exposure_speed": ExposureSpeed, "exposure_compensation": ExposureCompensation,
    "iso": Iso, "brightness": Brightness,
    "rotation": Rotation, "sharpness": Sharpness, "contrast": Contrast,
    "zoom": Zoom, "framerate": Framerate, "analog_gain": AnalogGain, "digital_gain": DigitalGain,
    "resolution": Resolution
}


class ParameterSet:

    _supported = supported

    def __init__(self, params: dict, default=False):
        
        self.input_params = params
        self.params = params.copy()

        if default:

            # set default params to the a dictionary with all the parameters
            # set to their default
            self.default_params = {}
            for k, v in self._supported.items():
                param = v()
                param.validate()
                self.default_params[k] = param
    
            # set self.params to a copy of default_params
            self.params = self.default_params.copy()

        # for each param in the input        
        for k, p in self.input_params.items():
            # ignore it if it not supported
            if k not in self._supported.keys():
                logging.warning(f"Parameter {k} not supported. Ignoring it for now")
                if k in self.keys(): self.pop(k)
                continue
    
            # add it if it is the correct instance
            if isinstance(p, self._supported[k]):
                # each param should be validated beforehand
                self.params[k] = p
            else:
                # assume the passed value is not a param but the value of the param
                # and create an instance of the param on the spot
                value = self._supported[k](value=p)
                value.validate()
                self[k] = value


    def validate(self):
                
        for k in self.keys():

            if k != self[k]._name or not isinstance(self[k], self._supported[k]):
                logging.warning(f"Parameter {k} mapped to {self[k]._name}. Ignoring instance")
                self.pop(k)
                continue

        return True


    def cross_verify(self):

        for p in self.values():

            # try:
            #     print(p)
            # except Exception as e:
            #     logging.error(e)
            #     print(p._name)

            # print(f"{p._name} is {p._active}")
            if p._depends_on is None or not p._active:
                pass
            else:
                dep_tests = []
                for dep_name, dep_value in p._depends_on.items():
                    try:
                        dep_inst = self.params[dep_name]
                    
                    except KeyError:
                        dep_tests.append(False)
                        continue

                    dep_tests.append(dep_inst._value == dep_value)
                
                if all(dep_tests):
                    p._active = True
                else:
                    logging.info(f"Parameter {p._name} cross verification failed")
                    #logging.warning(dep_tests)
                    p._active = False


    def as_dict(self):
        result = {p._name: p.val for p in self.values()}
        return result

    def urlencode(self, encoding='utf-8'):

        result = urllib.parse.urlencode(self.as_dict(), encoding=encoding)
        if encoding is not None:
            result = result.encode(encoding)
        return result

    def restore_qs(self, qs, encoding="utf-8"):
        if encoding is not None:
            result = qs.decode(encoding)

        result = urllib.parse.parse_qs(result)
        params_dict = {k: v[0] for k,v in result.items()}
        self.__init__(params_dict)

    def update_cam(self, camera):
        for p in self.values():
            if p._depends_on is None:
                logging.warning(p._value)
                camera = p.update_cam(camera)
        for p in self.values():
            if p._depends_on is not None:
                logging.warning(p._value)
                camera = p.update_cam(camera)


        attributes = {}        
        for p in self._supported.keys():
            attributes[p] = getattr(camera, p, None) 
            
        return camera, attributes

    def pickle(self, dst):
        import pickle
        with open(dst, 'wb') as fh:
            pickle.dump(self.as_dict(), fh)


    def copy(self):

        clu = self.__class__({})
        clu.params = self.params.copy()
        return clu


    def __str__(self):
        return f"ParameterSet({self.as_dict()})"

    def __eq__(self, other):

        keys_are_shared = sorted(list(self.keys())) == sorted(list(other.keys()))
        if not keys_are_shared:
            return False

        return all([self[k] == other[k] for k in self.keys()])

    def __sub__(self, other):

        final_set = self.copy()
        for k, p in self.items():
            if k in other.keys():
                if p == other[k]:
                    final_set.pop(k)

        return final_set

    def __setitem__(self, key, value):
        self.params[key] = value

    def __getitem__(self, name):
        return self.params[name]

    def __delitem__(self, name):
        del self.params[name]

    def pop(self, name):
        return self.params.pop(name)

    def keys(self):
        return self.params.keys()

    def values(self):
        return self.params.values()

    def items(self):
        return self.params.items()

    def __iter__(self):
        return self.params.keys()


    def __getattr__(self, name):

        if name in self._supported.keys():
            return self.params[name]
        else:
            super().__getattribute__(name)

