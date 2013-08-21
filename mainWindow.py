#!/usr/bin/env python
import logging
import sys

from gi.repository import Gtk

import bugzilla
import getpass

from bugzilla.bugzilla3 import Bugzilla34
from bugzilla.bugzilla4 import Bugzilla4
from bugzilla.rhbugzilla import RHBugzilla4
from string import rsplit

logger = logging.getLogger()

console_handler = logging.StreamHandler(stream=sys.stdout)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

gladefile = "/home/phracek/work/bugzillatracker/bugzilla-tracker.glade"

default_bz = 'https://bugzilla.redhat.com/xmlrpc.cgi'


class mainWindow(Gtk.Window):
    
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(gladefile)
        handlers = {"onBugzillaListRowActivated":self.bugzillaRowActivated,
                    "onCancelBtn":self.cancelBtn,
                    "onOKBtn":self.OKBtn,
                    "onBugzillaExitEvent":Gtk.main_quit,
                    "on_ntbBugzilla_switch_page":self.ntbSwitchPage,
                    "onBugzillaPopupMenu": self.bugzillaPopupMenu,
                    "onCommentActivateItem": self.bugzillaCommentActivate,
                    "onCommentBtn_clicked": self.CommentBtn,
                    "onBugzillaListRowActivated": self.bugzillaListRowActivated
                        }
        builder.connect_signals(handlers)
        self.mainWin = builder.get_object("bugzillatracker")
        self.listView = builder.get_object("bugzillaList")
        self.listViewClosed = builder.get_object("bugzillaListClosed")
        self.ntbBugzilla = builder.get_object("ntbBugzilla")
        
        bzclass = bugzilla.Bugzilla
        self.creatingListView()
        self.creatingListViewClosed()
        self.bz = bzclass(url=default_bz)
        self.bz.login("phracek","$Oldfield;53")
        include_fields = ["name", "id"]
        include_fields.append("versions")
        '''products = bz.getproducts(include_fields=include_fields)
        for name in sorted([p["name"] for p in products]):
            logging.info("%s" % name)
        '''
        compList = ["amanda","bacula","screen","emacs","openldap","autoconf", "libtool"]
        bug_status = ['NEW', 'ASSIGNED', 'NEEDINFO', 'ON_DEV',
                'MODIFIED', 'POST', 'REOPENED']
        built_query = self.bz.build_query(component=compList,status=bug_status)
        result = self.bz.query(built_query)
        self.store = Gtk.ListStore(str,str,str,str,str,str,str)
        self.storeClosed = Gtk.ListStore(str,str,str,str,str)
        for ret in result:
            strbug_id = "#%s" % ret.bug_id
            if ret.status != "CLOSED":
                logger.info("%s=%s" % (strbug_id,ret.status))
                self.store.append([strbug_id, ret.product, ret.version, ret.component, ret.short_desc, ret.bug_severity, ret.priority])
            else:
                logger.info("%s=%s" % (strbug_id,ret.status))
                self.storeClosed.append([strbug_id, ret.product, ret.version, ret.component, ret.short_desc])
        self.listView.set_model(self.store)
        self.store.set_sort_func(5,self.severityPrioritySort,None)
        self.store.set_sort_func(6,self.severityPrioritySort,None)
        self.listViewClosed.set_model(self.storeClosed)        
        self.mainWin.show_all()
        Gtk.main()

    def severityPrioritySort(self, model, row1, row2, user_data):
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1,sort_column)
        value2 = model.get_value(row2, sort_column)
        if value1 == "high":
            if value2 == "medium":
                return 1
            if value2 == "low":
                return 1
            if value2 == "high":
                return 0
            if value2 == "unspecified":
                return 1
        if value1 == "medium":
            if value2 == "medium":
                return 0
            if value2 == "low":
                return 1
            if value2 == "high":
                return -1
            if value2 == "unspecified":
                return 1
        if value1 == "low":
            if value2 == "medium":
                return -1
            if value2 == "low":
                return 0
            if value2 == "high":
                return -1
            if value2 == "unspecified":
                return 1
        if value1 == "unspecified":
            if value2 == "medium":
                return -1
            if value2 == "low":
                return -1
            if value2 == "high":
                return -1
            if value2 == "unspecified":
                return 0
        
    def creatingListView(self):
        bugRenderer = Gtk.CellRendererText()
        bugColumn = Gtk.TreeViewColumn("Bug ID", bugRenderer, text=0)
        bugColumn.set_sort_column_id(0)
        self.listView.append_column(bugColumn)
        prodRenderer = Gtk.CellRendererText()
        prodColumn = Gtk.TreeViewColumn("Product", prodRenderer, text=1)
        self.listView.append_column(prodColumn)
        versRenderer = Gtk.CellRendererText()
        versColumn = Gtk.TreeViewColumn("Version", versRenderer, text=2)
        versColumn.set_max_width(40)
        self.listView.append_column(versColumn)
        compRenderer = Gtk.CellRendererText()
        compColumn = Gtk.TreeViewColumn("Component", compRenderer, text=3)
        compColumn.set_sort_column_id(3)
        self.listView.append_column(compColumn)
        descRenderer = Gtk.CellRendererText()
        descColumn = Gtk.TreeViewColumn("Description", descRenderer, text=4)
        descColumn.set_max_width(300)
        self.listView.append_column(descColumn)
        sevRenderer = Gtk.CellRendererText()
        sevColumn = Gtk.TreeViewColumn("Severity", sevRenderer, text=5)
        sevColumn.set_sort_column_id(5)
        self.listView.append_column(sevColumn)
        priorityRenderer = Gtk.CellRendererText()
        priorityColumn = Gtk.TreeViewColumn("Priority", priorityRenderer, text=6)
        priorityColumn.set_sort_column_id(6)
        self.listView.append_column(priorityColumn)
        
    def creatingListViewClosed(self):
        bugClosedRenderer = Gtk.CellRendererText()
        bugClosedColumn = Gtk.TreeViewColumn("Bug ID", bugClosedRenderer, text=0)
        self.listViewClosed.append_column(bugClosedColumn)
        prodClosedRenderer = Gtk.CellRendererText()
        prodClosedColumn = Gtk.TreeViewColumn("Product", prodClosedRenderer, text=1)
        self.listViewClosed.append_column(prodClosedColumn)
        versClosedRenderer = Gtk.CellRendererText()
        versClosedColumn = Gtk.TreeViewColumn("Version", versClosedRenderer, text=2)
        self.listViewClosed.append_column(versClosedColumn)
        compClosedRenderer = Gtk.CellRendererText()
        compClosedColumn = Gtk.TreeViewColumn("Component", compClosedRenderer, text=3)
        self.listViewClosed.append_column(compClosedColumn)
        descClosedRenderer = Gtk.CellRendererText()
        descClosedColumn = Gtk.TreeViewColumn("Description", descClosedRenderer, text=4)
        self.listViewClosed.append_column(descClosedColumn)
        
    def get_main_win(self):
        return self.__mainWin


    def get_list_view(self):
        return self.__listView


    def get_store(self):
        return self.__store


    def set_main_win(self, value):
        self.__mainWin = value


    def set_list_view(self, value):
        self.__listView = value


    def set_store(self, value):
        self.__store = value


    def del_main_win(self):
        del self.__mainWin


    def del_list_view(self):
        del self.__listView


    def del_store(self):
        del self.__store

    
    def windowQuit(self,*args):
        Gtk.main_quit(*args)

    def cancelBtn(self,widget,*args):
        logger.info("Cancel window")
        Gtk.main_quit
    
    def OKBtn(self,widget,*args):
        logger.info("Correctly close window")
        Gtk.main_quit
    
    def bugzillaRowActivated(self,widget,row,col):
        logger.info("handler for switch between tools")
    
    def ntbSwitchPage(self,widget,page,page_num):
        logger.info("Handler for ntbSwitchPaht")
    
    def bugzillaPopupMenu(self):
        logger.info("Bugzilla popup Menu")
    
    def bugzillaCommentActivate(self):
        logger.info("Bugzilla Comment Activate")
        
    def CommentBtn(self,widget):
        logger.info("Comment Button clicked")
        
    
    def bugzillaListRowActivated(self,widget,row,col):
        logger.info("Bugzilla List Row Activated:")
        model = widget.get_model()
        bug_id = model[row][0]
        logger.info("Bugzilla bugISD: %s" % bug_id[1:])
        built_query = self.bz.build_query(bug_id=bug_id[1:])
        result = self.bz.query(built_query)
        logger.info("%s" % result)
        for ret in result:
            logger.info("%s" % ret.comment)
       
        
    mainWin = property(get_main_win, set_main_win, del_main_win, "mainWin's docstring")
    listView = property(get_list_view, set_list_view, del_list_view, "listView's docstring")
    store = property(get_store, set_store, del_store, "store's docstring")
                
        

