#!/usr/bin/env python
import logging
import sys

try:
    from gi.repository import Gtk
except RuntimeError, e:
    print _("bugzilla-tracker requires a currectly running X server.")
    print "'%s: %r" % (e.__class__.__name__, str(e))
    sys.exit(1)
    
import mainWindow
mainWindow.mainWindow()