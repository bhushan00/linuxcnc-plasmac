import emccanon
from interpreter import *
import hal
throw_exceptions = 1

# REMAP = M10 modalgroup=4 argspec=PQ python=M10
def M10(self,**words):
    if self.params['P'] == 0: # thc-enable
        if self.params['Q'] == 0:
            hal.set_p('plasmac_panel.thc-enable-ext','0')
        else:
            hal.set_p('plasmac_panel.thc-enable-ext','1')
    elif self.params['P'] == 1: # cut-height
        hal.set_p('plasmac_panel.cut-height-ext',str(self.params['Q']))

# REMAP = F prolog=setfeed_prolog  ngc=setfeed epilog=setfeed_epilog
# exposed parameter: #<feed>
def plasmac_feed_prolog(self,**words):
    try:
        c = self.blocks[self.remap_level]
        if not c.f_flag:
            self.set_errormsg("F requires a value")
            return INTERP_ERROR
        self.params["feed"] = c.f_number
    except Exception,e:
        self.set_errormsg("F/setfeed_prolog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK

def plasmac_feed_epilog(self,**words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            return INTERP_ERROR
        if self.blocks[self.remap_level].builtin_used:
            self.params[31] = self.return_value
            hal.set_p('plasmac.requested-velocity', str(self.return_value))
            pass
        else:
            self.feed_rate = self.params["feed"]
            emccanon.enqueue_SET_FEED_RATE(self.feed_rate)
            hal.set_p('plasmac.requested-velocity', str(self.feed_rate))
        return INTERP_OK
    except Exception,e:
        self.set_errormsg("F/setfeed_epilog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK


