import json
from ricxappframe.xapp_frame import RMRXapp, rmr
from mdclogpy import Level
from ._BaseHandler import _BaseHandler

class KpmIndicationHandler(_BaseHandler):

    def __init__(self, rmr_xapp: RMRXapp, msgtype):
        super().__init__(rmr_xapp, msgtype)
        self.logger.set_level(Level.INFO)

    def request_handler(self, rmr_xapp, summary, sbuf):
        """
                Handles Indication messages.

                Parameters
                ----------
                rmr_xapp: rmr Instance Context

                summary: dict (required)
                    buffer content

                sbuf: str (required)
                    length of the message
        """
        print(f"KpmIndicationHandler.request_handler:: Handler processing request {summary[rmr.RMR_MS_PAYLOAD]} {sbuf}")
        try:
            req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
            self.logger.info("KpmIndicationHandler.request_handler:: Handler processing request")
        except (json.decoder.JSONDecodeError, KeyError):
            self.logger.error("KpmIndicationHandler.request_handler:: Handler failed to parse request")
            return

        if self.verify_indication(req):
            self.logger.info("KpmIndicationHandler.request_handler:: Handler processed request: {}".format(req))
        else:
            self.logger.error("KpmIndicationHandler.request_handler:: Request verification failed: {}".format(req))
            return
        self.logger.debug("KpmIndicationHandler.request_handler:: Request verification success: {}".format(req))

        self._rmr_xapp.rmr_free(sbuf)

    def verify_indication(self, req: dict):
        # TODO
        return True

