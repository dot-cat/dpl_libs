import logging

LOGGER = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO

except ImportError:
    LOGGER.warning("RPi GPIO module is not installed. Falling back to dummy GPIO...")
    import dpl.libs.gpio_dummy as GPIO

except RuntimeError:
    LOGGER.warning("RPi GPIO module can't be loaded on this system. "
                   "Falling back to dummy GPIO...")
    import dpl.libs.gpio_dummy as GPIO
