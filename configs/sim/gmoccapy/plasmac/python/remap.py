import emccanon
from interpreter import *
import hal
throw_exceptions = 1

# REMAP = F prolog=plasmac_feed_prolog ngc=plasmac_feed epilog=plasmac_feed_epilog
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

# REMAP = T prolog=plasmac_tool_prolog ngc=plasmac_tool epilog=plasmac_tool_epilog
# exposed parameters: #<tool> #<pocket>
def plasmac_tool_prolog(self,**words):
    import time
    try:
        cblock = self.blocks[self.remap_level]
        if not cblock.t_flag:
            self.set_errormsg("T requires a value")
            return INTERP_ERROR
        tool  = cblock.t_number
        if tool >= 0 and tool != hal.get_value('plasmac_run.tool-change-number'):
            hal.set_p('plasmac_run.tool-change-diameter','-1')
            hal.set_p('plasmac_run.tool-change-number', str(tool))
            start = time.time()
            # wait up to to 3 seconds for tool-change-diameter signal from plasmac
            while hal.get_value('plasmac_run.tool-change-diameter') == -1:
                if time.time() > start + 3:
                    self.set_errormsg("T%d: timeout waiting for tool-change-diameter value" % (tool))
                    return INTERP_ERROR
            if hal.get_value('plasmac_run.tool-change-diameter') >= 0:
                tool = 0
            else:
                self.set_errormsg("Tool #%d: does not exist" % (hal.get_value('plasmac_run.tool-change-number'))) # non existant tool
                return INTERP_ERROR
        else:
            tool = 0
        self.params["_kerf_width"] = hal.get_value('plasmac_run.tool-change-diameter')
        self.params["tool"] = tool
        self.params["pocket"] = tool
        return INTERP_OK
    except Exception, e:
        self.set_errormsg("T%d/prepare_prolog: %s" % (int(words['t']), e))
        return INTERP_ERROR

def plasmac_tool_epilog(self, **words):
    try:
        if self.return_value > 0:
            self.selected_tool = int(self.params["tool"])
            self.selected_pocket = int(self.params["pocket"])
            emccanon.SELECT_POCKET(self.selected_pocket, self.selected_tool)
            return INTERP_OK
        else:
            return "T%d: aborted (return code %.1f)" % (int(self.params["tool"]),self.return_value)

    except Exception, e:
        return "T%d/prepare_epilog: %s" % (tool,e)
