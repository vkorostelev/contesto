# coding: utf-8
import os
from datetime import datetime
from functools import wraps

from contesto import config
from contesto.utils.log import log


def _make_screenshot(driver, test_obj, path, clean=False):
    """
    Saves screenshot of the current window in ``path`` folder with file name combined of current test name and date.

    :type driver: WebDriver or WebElement or ContestoDriver
    """
    if clean:
        # todo clean screenshots directory
        pass
    if driver.capabilities['takesScreenshot']:
        date_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        fname = '%s%s.png' % (str(test_obj), date_time)
        scr_file = os.path.sep.join([path, fname])

        if driver.save_screenshot(scr_file):
            test_obj._meta_info['attachments'].append(
                {
                    'path': scr_file,
                    'mime_type': 'image/png',
                    'name': 'screenshot'
                }
            )
        else:
            log.warn("Could not save screenshot for %s" % str(test_obj))
    else:
        raise EnvironmentError(
            'Option "takesScreenshot" in Capabilities is disabled.\n'
            'Please enable option to save screenshot.')


def _try_make_screenshot(test_obj):
    path = config.utils.get('screenshots_path', None)
    if path is None:
        log.info("No 'screenshot_path' provided in config. Defaulting to 'screenshots'")
        path = 'screenshots'

    driver = getattr(test_obj, 'driver', None)
    if driver is None:
        log.info("%s has no driver object. Aborting taking error screenshot." % str(test_obj))
        return
    path = path.rstrip(os.path.sep)
    try:
        _make_screenshot(driver, test_obj, path)
    except Exception as e:
        log.warning("Unexpected exception %s occurred while trying to save screenshot", e)


def save_screenshot_on_error(func):
    """
    Saves screenshot if method raised exception and ``contesto.config.utils["save_screenshots"]`` is set.

    Screenshot can be saved only if ``driver`` is accessible as ``self.driver`` in decorated method.
    Screenshot is saved to folder defined in ``contesto.config.utils["screenshots_path"]``
    or ``"screenshots"`` if undefined.
    :param func: function
    """
    if hasattr(func, "__will_take_screenshot__"):
        return func

    setattr(func, "__will_take_screenshot__", True)

    @wraps(func)
    def wrapper(test, *args, **kwargs):
        try:
            return func(test, *args, **kwargs)
        except:
            _try_make_screenshot(test)
            raise

    return wrapper
