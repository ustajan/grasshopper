#!/usr/bin/python3


class PSTAR_API():
    """
    Controls the NIST PSTAR database website.
    """
    def __init__(self, options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None,
                 chrome_options=None, keep_alive=True):
        """
        Creates a new instance of the NIST PSTAR API.

        Starts the service and then creates new instance of NIST PSTAR API.

        :Args:
         - executable_path - path to the executable. If the default is used it assumes the executable is in the $PATH
         - port - port you would like the service to run, if left as 0, a free port will be found.
         - options - this takes an instance of ChromeOptions
         - service_args - List of args to pass to the driver service
         - desired_capabilities - Dictionary object with non-browser specific
           capabilities only, such as "proxy" or "loggingPref".
         - service_log_path - Where to log information from the driver.
         - chrome_options - Deprecated argument for options
         - keep_alive - Whether to configure NIST PSTAR API to use HTTP keep-alive.
        """
        self.options = options
        self.service_args = service_args
        self.desired_capabilities = desired_capabilities
        self.service_log_path = service_log_path
        self.chrome_options = chrome_options
        self.keep_alive = keep_alive

