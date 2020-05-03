import time
import logging
logging.basicConfig(level=logging.INFO)



def set_gain(camera, gain, value):
    """Set the analog gain of a PiCamera.
    
    camera: the picamera.PiCamera() instance you are configuring
    gain: either MMAL_PARAMETER_ANALOG_GAIN or MMAL_PARAMETER_DIGITAL_GAIN
    value: a numeric value that can be converted to a rational number.
    """
    # lazy loading so node does not complain
    from picamera import mmal, mmalobj, exc
    from picamera.mmalobj import to_rational
    
    
    # keys must match the _name attribute of the corresponding class
    SENSOR_GAINS = {
        "analog_gain": mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x59,
        "digital_gain": mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x5A
    }
    ##
    logging.info(f"Setting {gain} to {value}")

    if gain not in ["analog_gain", "digital_gain"]:
        raise ValueError("The gain parameter was not valid")

    gain_int = SENSOR_GAINS[gain]
    rational_value = to_rational(value)
    port = camera._camera.control._port

    logging.warning(gain_int)
    logging.warning(rational_value)
    logging.warning(port)

    ret = mmal.mmal_port_parameter_set_rational(port, gain_int, rational_value)
    # PLEASE NOTE
    # if queried now, it will still show the old value
    time.sleep(2)

    if ret == 4:
        raise exc.PiCameraMMALError(ret, "Are you running the latest version of the userland libraries? Gain setting was introduced in late 2017.")
    elif ret != 0:
        raise exc.PiCameraMMALError(ret)
