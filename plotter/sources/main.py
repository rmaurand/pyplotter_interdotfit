# This Python file uses the following encoding: utf-8
from PyQt5 import QtGui, QtCore, QtWidgets, QtTest
import os
from pprint import pformat
from typing import Generator, Union, Callable, List, Tuple
import uuid
import numpy as np
import time
import sys
sys.path.append('ui')

# Correct bug with pyqtgraph and python3.8 by replacing function name
try:
    import pyqtgraph as pg
except AttributeError:
    import time
    time.clock = time.perf_counter
    import pyqtgraph as pg


from .importcsv import ImportCSV
from .importbluefors import ImportBlueFors
from .qcodesdatabase import QcodesDatabase
from .runpropertiesextra import RunPropertiesExtra
from .mytablewidgetitem import MyTableWidgetItem
from .importdatabase import ImportDatabaseThread
from .loaddata import LoadDataThread
from .loaddatafromcache import LoadDataFromCacheThread
from .config import config
from .plot_1d_app import Plot1dApp
from .plot_2d_app import Plot2dApp
from ..ui import main

pg.setConfigOption('background', config['styles'][config['style']]['pyqtgraphBackgroundColor'])
pg.setConfigOption('useOpenGL', config['pyqtgraphOpenGL'])
pg.setConfigOption('antialias', config['plot1dAntialias'])

# Get the folder path for pictures
PICTURESPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../ui/pictures/')

class MainApp(QtWidgets.QMainWindow, main.Ui_MainWindow, RunPropertiesExtra):



    def __init__(self, parent=None):

        super(MainApp, self).__init__(parent)
        self.setupUi(self)

        
        # Connect UI
        self.tableWidgetFolder.clicked.connect(self.itemClicked)
        self.pushButtonOpenFolder.clicked.connect(self.openFolderClicked)
        
        # Resize the cell to the column content automatically
        self.tableWidgetDataBase.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidgetParameters.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidgetFolder.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidgetParameters.setColumnHidden(0, True)
        self.tableWidgetParameters.setColumnHidden(1, True)

        # Connect event
        self.tableWidgetDataBase.currentCellChanged.connect(self.runClicked)
        self.tableWidgetDataBase.doubleClicked.connect(self.runDoubleClicked)
        self.tableWidgetDataBase.keyPressed.connect(self.tableWidgetDataBasekeyPress)
        self.tableWidgetParameters.cellClicked.connect(self.parameterCellClicked)
        
        self.pushButtonLivePlot.clicked.connect(self.livePlotPushButton)
        self.spinBoxLivePlot.setValue(int(config['livePlotTimer']))
        self.spinBoxLivePlot.valueChanged.connect(self.livePlotSpinBoxChanged)
        
        self.checkBoxHidden.stateChanged.connect(lambda : self.checkBoxHiddenState(self.checkBoxHidden))

        self.lineEditFilter.textChanged.connect(self.lineEditFilterTextEdited)


        self.setStatusBarMessage('Ready')

        # Default folder is the dataserver except if we are on test mode
        if 'test' in os.listdir('.'):

            self.currentPath = os.path.abspath(os.path.curdir)
            config['path'] = self.currentPath
            config['root'] = self.currentPath
        # If we are unable to detect the config folder, we switch in local mode
        elif not os.path.isdir(os.path.normpath(config['path'])):
            
            # Ask user to chose a path
            self.currentPath = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                          caption='Open folder',
                                                                          directory=os.getcwd(),
                                                                          options=QtWidgets.QFileDialog.ReadOnly|QtWidgets.QFileDialog.ShowDirsOnly)

            # Set config parameter accordingly
            config['path'] = os.path.abspath(self.currentPath)
            config['root'] = os.path.splitdrive(self.currentPath)[0]
        else:
            
            self.currentPath = os.path.normpath(config['path'])

        # References of all opened plot window.
        # Structure:
        # {plotRef : plotApp}
        self._plotRefs = {}

        # Attribute to control the display of data file info when user click of put focus on a item list
        self._folderUpdating  = False # To avoid calling the signal when updating folder content
        self._guiInitialized = True # To avoid calling the signal when starting the GUI
        
        
        # Flag
        self._dataDowloadingFlag = False
        self._progressBars = {}

        self._currentDatabase    = None
        self._oldTotalRun        = None
        self._livePlotFetchData  = False
        self._livePlotTimer      = None

        # Handle connection and requests to qcodes database
        self.qcodesDatabase = QcodesDatabase(self.setStatusBarMessage)
        # Handle log files from bluefors fridges
        self.importblueFors = ImportBlueFors(self._plotRefs,
                                             self.lineEditFilter,
                                             self.labelFilter,
                                             self.tableWidgetDataBase,
                                             self.tableWidgetParameters,
                                             self.textEditMetadata,
                                             self.setStatusBarMessage,
                                             self.addPlot,
                                             self.removePlot,
                                             self.isParameterPlotted,
                                             self.getDataRef)
        # Handle csv files
        self.importcsv      = ImportCSV(self)


        # By default, we browse the root folder
        self.folderClicked(directory=self.currentPath)

        self.threadpool = QtCore.QThreadPool()



    ###########################################################################
    #
    #
    #                           Folder browsing
    #
    #
    ###########################################################################



    def openFolderClicked(self) -> None:
        """
        Call when user click on the 'Open folder' button.
        Allow user to chose any available folder in his computer.
        """

        # Ask user to chose a path
        path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                          caption='Open folder',
                                                          directory=os.getcwd(),
                                                          options=QtWidgets.QFileDialog.ReadOnly|QtWidgets.QFileDialog.ShowDirsOnly)
        if path != '':
            # Set config parameter accordingly
            self.currentPath = path
            config['path'] = os.path.abspath(self.currentPath)
            config['root'] = os.path.splitdrive(self.currentPath)[0]

            self.folderClicked(directory=self.currentPath)



    def updateLabelPath(self) -> None:
        """
        Update the label path by creating a horizontal list of buttons to
        quickly browse back the folder arborescence.
        """

        self.clearLayout(self.labelPath)

        path = os.path.normpath(self.currentPath).split(os.sep)
        root = os.path.normpath(config['root']).split(os.sep)
        
        # Display path until root 
        for i, text in enumerate(path):

            # Build button text depending of where we are
            if text==root[0]:
                bu_text = 'root'
            elif text not in root:
                bu_text = text
            else:
                bu_text = None

            # Create, append and connect buttons
            if bu_text is not None:
                bu = QtWidgets.QPushButton(bu_text)
                width = bu.fontMetrics().boundingRect(bu_text).width() + 15
                bu.setMaximumWidth(width)
                d = os.path.join(path[0], os.sep, *path[1:i+1])
                bu.clicked.connect(lambda bu, directory=d : self.folderClicked(directory))
                self.labelPath.addWidget(bu)

        self.labelPath.setAlignment(QtCore.Qt.AlignLeft)



    def folderClicked(self, directory: str) -> None:
        """
        Basically display folder and csv file of the current folder.

        Parameters
        ----------
        directory : str
            Path of the folder to be browsed.
        """
        
        # When signal the updating of the folder to prevent unwanted item events
        self._folderUpdating = True
        self.currentPath = directory

        self.updateLabelPath()


        # Load runs extra properties
        self.jsonLoad()
        databaseStared = self.getDatabaseStared()

        ## Display the current dir content
        self.clearTableWidget(self.tableWidgetFolder)
        self.tableWidgetFolder.setSortingEnabled(True)
        row = 0
        for file in sorted(os.listdir(self.currentPath), reverse=True): 
            
            abs_filename = os.path.join(self.currentPath, file)
            file_extension = os.path.splitext(abs_filename)[-1][1:]

            # Only display folder and Qcodes database
            # Add icon depending of the item type

            # If folder
            if os.path.isdir(abs_filename):
                
                # If looks like a BlueFors log folder
                if self.importblueFors.isBlueForsFolder(file):
                    item =  QtGui.QTableWidgetItem(file)
                    item.setIcon(QtGui.QIcon(PICTURESPATH+'bluefors.png'))

                    self.tableWidgetFolder.insertRow(row)
                    self.tableWidgetFolder.setItem(row, 0, item)
                    row += 1
                # Other folders
                else:   
                    item =  QtGui.QTableWidgetItem(file)
                    if file in config['enhancedFolder']:
                        item.setIcon(QtGui.QIcon(PICTURESPATH+'folderEnhanced.png'))
                    else:
                        item.setIcon(QtGui.QIcon(PICTURESPATH+'folder.png'))
                    self.tableWidgetFolder.insertRow(row)
                    self.tableWidgetFolder.setItem(row, 0, item)
                    row += 1
            # If files
            else:
                if file not in config['forbiddenFile']:
                    if file_extension.lower() in config['authorizedExtension']:
                        

                        # We look if the file is already opened by someone else
                        DatabaseAlreadyOpened = False
                        for subfile in os.listdir(self.currentPath): 
                            if subfile==file[:-2]+'db-wal':
                                DatabaseAlreadyOpened = True

                        if file_extension.lower()=='csv':
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'csv.png'))
                        elif file_extension.lower()=='s2p':
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'s2p.png'))
                        elif DatabaseAlreadyOpened and file in databaseStared:
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseOpenedStared.png'))
                            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                        elif DatabaseAlreadyOpened:
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseOpened.png'))
                            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                        elif file in databaseStared:
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseStared.png'))
                        else:
                            item =  QtGui.QTableWidgetItem(file)
                            item.setIcon(QtGui.QIcon(PICTURESPATH+'database.png'))
                        self.tableWidgetFolder.insertRow(row)
                        self.tableWidgetFolder.setItem(row, 0, item)
                        
                        # Get file size in hman readable format
                        fileSizeItem = QtGui.QTableWidgetItem(self.sizeof_fmt(os.path.getsize(abs_filename)))
                        fileSizeItem.setTextAlignment(QtCore.Qt.AlignRight)
                        fileSizeItem.setTextAlignment(QtCore.Qt.AlignVCenter)
                        self.tableWidgetFolder.setItem(row, 1, fileSizeItem)
                        row += 1
                    
        # Allow item event again
        self._folderUpdating = False



    def itemClicked(self) -> None:
        """
        Handle event when user clicks on datafile.
        The user can either click on a folder or a file.
        If it is a folder, we launched the folderClicked method.
        If it is a file, we launched the dataBaseClicked method.
        """
        
        # We check if the signal is effectively called by user
        if not self._folderUpdating and self._guiInitialized:
            
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

            # Get current item
            currentRow = self.tableWidgetFolder.currentIndex().row()
            self._currentDatabase =  self.tableWidgetFolder.model().index(currentRow, 0).data()
            nextPath = os.path.join(self.currentPath, self._currentDatabase)

            # If the folder is a BlueFors folder
            if self.importblueFors.isBlueForsFolder(self._currentDatabase):
                
                self.importblueFors.blueForsFolderClicked(directory=nextPath)
                self.folderClicked(directory=self.currentPath)
            # If the folder is a regulat folder
            elif os.path.isdir(nextPath):
                self.statusBar.showMessage('Update')
                self.folderClicked(directory=nextPath)
                self.statusBar.showMessage('Ready')\
            # If it is a csv or a s2p file
            elif nextPath[-3:].lower() in ['csv', 's2p']:

                self.importcsv.csvFileClicked(nextPath)
                self.folderClicked(directory=self.currentPath)
            # If it is a QCoDeS database
            else:
                
                # folderClicked called after the worker is done
                self.dataBaseClicked()

            # Job done, we restor the usual cursor 
            QtGui.QApplication.restoreOverrideCursor()
        
        # When the signal has been called at least once
        if not self._guiInitialized:
            self._guiInitialized = True



    ###########################################################################
    #
    #
    #                           Database browsing
    #
    #
    ###########################################################################



    def dataBaseClicked(self) -> None:
        """
        Display the content of the clicked dataBase into the database table
        which will then contain all runs.
        """

        self.databaseClicking = True
        
        # We show the database is now opened
        if self.isDatabaseStared():

            currentRow = self.tableWidgetFolder.currentIndex().row()
            item = self.tableWidgetFolder.item(currentRow, 0)
            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseOpenedStared.png'))
        else:
            currentRow = self.tableWidgetFolder.currentIndex().row()
            item = self.tableWidgetFolder.item(currentRow, 0)
            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseOpened.png'))

        # Disable interactivity
        self.checkBoxHidden.setChecked(False)
        self.checkBoxHidden.setEnabled(False)

        # Update label
        self.labelCurrentDataBase.setText(self._currentDatabase[:-3])

        # Remove all previous row in the table
        self.clearTableWidget(self.tableWidgetDataBase)

        self.qcodesDatabase.databasePath = os.path.join(self.currentPath, self._currentDatabase)

        # Add a progress bar in the statusbar
        progressBarKey = self.addProgressBarInStatusBar()

        # Create a thread which will read the database
        worker = ImportDatabaseThread(self.qcodesDatabase.getRunInfos, progressBarKey)

        # Connect signals
        worker.signals.setStatusBarMessage.connect(self.setStatusBarMessage)
        worker.signals.addRows.connect(self.dataBaseClickedAddRows)
        worker.signals.updateProgressBar.connect(self.updateProgressBar)
        worker.signals.updateDatabase.connect(self.dataBaseClickedDone)

        # Execute the thread
        self.threadpool.start(worker)



    def dataBaseClickedAddRows(self, lrunId          : List[int],
                                     ldim            : List[str],
                                     lexperimentName : List[str],
                                     lsampleName     : List[str],
                                     lrunName        : List[str],
                                     lstarted        : List[str],
                                     lcompleted      : List[str],
                                     lrunRecords     : List[str],
                                     nbTotalRun     : int,
                                     progressBarKey : str) -> None:
        """
        Called by another thread to fill the database table.
        Each call add n rows into the table.
        """
        
        # We go through all lists of parameters and for each list element, we add
        # a row in the table
        for (runId, dim, experimentName, sampleName, runName, started, completed,
             runRecords) in zip(lrunId,
             ldim, lexperimentName, lsampleName, lrunName, lstarted, lcompleted,
             lrunRecords):

            if runId==1:
                self.statusBar.clearMessage()
                self.tableWidgetDataBase.setRowCount(nbTotalRun)

            self.updateProgressBar(progressBarKey, int(runId/nbTotalRun*100), text='Displaying database: run '+str(runId)+'/'+str(nbTotalRun))
            
            itemRunId = MyTableWidgetItem(str(runId))
            
            # If the run has been stared by an user
            if runId in self.getRunStared():
                itemRunId.setIcon(QtGui.QIcon(PICTURESPATH+'star.png'))
                itemRunId.setForeground(QtGui.QBrush(QtGui.QColor(*config['runStaredColor'])))
            # If the user has hidden a row
            elif runId in self.getRunHidden():
                itemRunId.setIcon(QtGui.QIcon(PICTURESPATH+'trash.png'))
                itemRunId.setForeground(QtGui.QBrush(QtGui.QColor(*config['runHiddenColor'])))
            else:
                itemRunId.setIcon(QtGui.QIcon(PICTURESPATH+'empty.png'))
            
            self.tableWidgetDataBase.setItem(runId-1, 0, itemRunId)
            self.tableWidgetDataBase.setItem(runId-1, 1, QtGui.QTableWidgetItem(dim))
            self.tableWidgetDataBase.setItem(runId-1, 2, QtGui.QTableWidgetItem(experimentName))
            self.tableWidgetDataBase.setItem(runId-1, 3, QtGui.QTableWidgetItem(sampleName))
            self.tableWidgetDataBase.setItem(runId-1, 4, QtGui.QTableWidgetItem(runName))
            self.tableWidgetDataBase.setItem(runId-1, 5, QtGui.QTableWidgetItem(started))
            self.tableWidgetDataBase.setItem(runId-1, 6, QtGui.QTableWidgetItem(completed))
            self.tableWidgetDataBase.setItem(runId-1, 7, MyTableWidgetItem(runRecords))

            if runId in self.getRunHidden():
                self.tableWidgetDataBase.setRowHidden(runId, True)



    def dataBaseClickedDone(self,
                            progressBarKey : str,
                            error          : bool,
                            nbTotalRun     : int) -> None:
        """
        Called when the database table has been filled

        Parameters
        ----------
        progressBarKey : str
            Key to the progress bar in the dict progressBars.
        error : bool

        nbTotalRun : int
            Total number of run in the current database.
            Simply stored for other purposes and to avoid other sql queries.
        """

        self.removeProgressBar(progressBarKey)
        
        if not error:
            self.tableWidgetDataBase.setSortingEnabled(True)
            self.tableWidgetDataBase.sortItems(0, QtCore.Qt.DescendingOrder)

            # Enable database interaction
            self.checkBoxHidden.setEnabled(True)

            self.setStatusBarMessage('Ready')


        # We store the total number of run
        self.nbTotalRun = nbTotalRun

        # Done 
        self.databaseClicking = False

        # We show the database is now closed
        if self.isDatabaseStared():

            currentRow = self.tableWidgetFolder.currentIndex().row()
            item = self.tableWidgetFolder.item(currentRow, 0)
            item.setIcon(QtGui.QIcon(PICTURESPATH+'databaseStared.png'))
        else:
            currentRow = self.tableWidgetFolder.currentIndex().row()
            item = self.tableWidgetFolder.item(currentRow, 0)
            item.setIcon(QtGui.QIcon(PICTURESPATH+'database.png'))



    def runDoubleClicked(self) -> None:
        """
        Called when user double click on the database table.
        Display the measured dependent parameters in the table Parameters.
        Simulate the user clicking on the first dependent parameter, effectively
        launching its plot.
        """

        # We simulate a single click
        self.runClicked()

        # We click on the first parameter, which will launch a plot
        self.parameterCellClicked(0, 2)



    def runClicked(self) -> None:
        """
        When clicked display the measured dependent parameters in the 
        tableWidgetPtableWidgetParameters
        """
        
        # When the user click on another database while having already clicked
        # on a run, the runClicked event is happenning even if no run have been clicked
        # This is due to the "currentCellChanged" event handler.
        # We catch that false event and return nothing
        if self.databaseClicking:
            return

        
        runId = self.getRunId()
        experimentName = self.getRunExperimentName()

        runId = str(self.getRunId())

        self.setStatusBarMessage('Loading run parameters')

        # Get independent parameters list without the independent parameters
        # Get parameters list without the independent parameters
        dependentList, snapshotDict = self.qcodesDatabase.getDependentSnapshotFromRunId(runId)


        ## Update label
        self.labelCurrentRun.setText(runId)
        self.labelCurrentMetadata.setText(runId)


        ## Fill the tableWidgetParameters with the run parameters

        self.clearTableWidget(self.tableWidgetParameters)
        for dependent in dependentList:
            
            rowPosition = self.tableWidgetParameters.rowCount()

            self.tableWidgetParameters.insertRow(rowPosition)

            cb = QtWidgets.QCheckBox()

            # We check if that parameter is already plotted
            if self.isParameterPlotted(dependent['name']):
                cb.setChecked(True)

            self.tableWidgetParameters.setItem(rowPosition, 0, QtGui.QTableWidgetItem(str(runId)))
            self.tableWidgetParameters.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(experimentName)))
            self.tableWidgetParameters.setCellWidget(rowPosition, 2, cb)
            self.tableWidgetParameters.setItem(rowPosition, 3, QtGui.QTableWidgetItem(dependent['name']))
            self.tableWidgetParameters.setItem(rowPosition, 4, QtGui.QTableWidgetItem(dependent['unit']))


            independentString = config['sweptParameterSeparator'].join(dependent['depends_on'])
            self.tableWidgetParameters.setCellWidget(rowPosition, 5, QtWidgets.QLabel(independentString))

            # Each checkbox at its own event attached to it
            cb.toggled.connect(lambda state,
                                      dependentParamName = dependent['name'],
                                      runId              = runId,
                                      dependent          = dependent,
                                      dataRef            = self.getDataRef(): self.parameterClicked(state, dependentParamName, runId, dependent, dataRef))
        

        self.tableWidgetParameters.setSortingEnabled(True)

        ## Fill the listWidgetMetada with the station snapshot
        self.textEditMetadata.clear()
        self.lineEditFilter.setEnabled(True)
        self.labelFilter.setEnabled(True)
        self.originalSnapshot = snapshotDict
        self.lineEditFilterTextEdited('')

        self.setStatusBarMessage('Ready')



    def parameterCellClicked(self, row: int, column: int) -> None:
        """
        Handle event when user click on the cell containing the checkbox.
        Basically toggle the checkbox and launch the event associated to the
        checkbox

        Parameters
        ----------
            row, column : int, int
            Row and column where the user clicked
        """
        
        # If user clicks on the cell containing the checkbox
        if column==2:
            cb = self.tableWidgetParameters.cellWidget(row, 2)
            cb.toggle()



    def parameterClicked(self,
                         state              : bool,
                         dependentParamName : str,
                         runId              : int,
                         paramDependent     : dict,
                         dataRef            : str) -> None:
        """
        Handle event when user clicked on data line.
        Either get data and display them or remove the data depending on state.

        Parameters
        ----------
        state : bool
            State of the checkbox
        dependentParamName : str
            Name of the dependent parameter from which data will be downloaded.
        runId : int
            Data run id in the current database
        paramDependent : dict
            Dependent parameter the user wants to see the data.
            This should be a qcodes dependent parameter dict.
        dataRef : str
            Reference of the plot, see getDataRef.
        """
        
        plotRef = self.getPlotRef(dataRef, paramDependent)

        # If the checkbutton is checked, we downlad and plot the data
        if state:
            
            if len(paramDependent['depends_on'])>2:

                self.setStatusBarMessage('Plotter does not handle data whose dim>2', error=True)
                return
            else:
                self.getData(plotRef            = plotRef,
                             dependentParamName = dependentParamName)

        # If the checkbox is unchecked, we remove the plotted data
        else:
            
            self.removePlot(plotRef = plotRef,
                            label   = paramDependent['name'])



    ###########################################################################
    #
    #
    #                           Progress bar
    #
    #
    ###########################################################################



    def addProgressBarInStatusBar(self) -> str:
        """
        Add the progress bar in the status bar.
        Usually called before a thread is launched to load something.

        Return
        ------
        progressBarKey : str
            An unique key coming from uuid.uuid4().
        """


        # Add a progress bar in the statusbar
        progressBarKey = str(uuid.uuid4())
        self._progressBars[progressBarKey] = QtWidgets.QProgressBar(self)
        self._progressBars[progressBarKey].setAlignment(QtCore.Qt.AlignCenter)
        self._progressBars[progressBarKey].setValue(0)
        self._progressBars[progressBarKey].setTextVisible(True)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.addPermanentWidget(self._progressBars[progressBarKey])

        return progressBarKey



    def removeProgressBar(self, progressBarKey: str) -> None:
        """
        Remove the progress bar in the status bar.
        Usually called after a thread has loaded something.
        """

        self.statusBar.removeWidget(self._progressBars[progressBarKey])
        del self._progressBars[progressBarKey]



    def updateProgressBar(self, key: str, val: int, text: str=None) -> None:
        """
        Update the progress bar in the status bar

        Parameters
        ----------
        key : str
            key from addProgressBarInStatusBar.
        val : int
            Value of the progress.
            Must be an int between 0 and 100.
        text : str
            Text to be shown on the progress bar.
        """

        if text is not None:
            self._progressBars[key].setFormat(text)
        self._progressBars[key].setValue(val)



    ###########################################################################
    #
    #
    #                           Snapshot
    #
    #
    ###########################################################################



    def findKeyInDict(self, key : str, dictionary : dict) -> Generator:
        """
        Find all occurences of a key in nested python dictionaries and lists.
        Adapted from:
        https://gist.github.com/douglasmiranda/5127251

        Parameters
        ----------
        key : str
            Part of the text looked as key in the nested dict.
        dictionary : dict
            Dictionnary to be looked up
        
        Return
        ------
        list of all paired of {key : val} found
        """

        for k, v in dictionary.items():
            if key in k:
                yield {k: v}
            elif isinstance(v, dict):
                for result in self.findKeyInDict(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in self.findKeyInDict(key, d):
                            yield result



    def lineEditFilterTextEdited(self, text : str) -> None:
        """
        Called when user types text in the filter lineEdit widget.
        Looked for the all keys which contains the entered string

        Parameters
        ----------
        text : str
            Text to be found in the run snapshot
        """

        if len(text) != 0:
            snapshotNew = list(self.findKeyInDict(text, self.originalSnapshot))
            
            self.textEditMetadata.setText(pformat(snapshotNew)
                                        .replace('{', '')
                                        .replace('}', '')
                                        .replace("'", '')
                                        .replace('\n', '<br>')
                                        .replace(' ', '&nbsp;')
                                        .replace(text, '<span style="font-weight: bold;color: red;">'+text+'</span>'))
        else:
            snapshotNew = self.originalSnapshot
            self.textEditMetadata.setText(pformat(snapshotNew)
                                        .replace('{', '')
                                        .replace('}', '')
                                        .replace("'", ''))



    ###########################################################################
    #
    #
    #                           GUI
    #
    #
    ###########################################################################



    def isParameterPlotted(self, parameterLabel : str) -> bool:
        """
        Return True when the displayed parameter is currently plotted.

        Parameters
        ----------
        parameterLabel : str
            Label of the dependent parameter we are checking.
        """

        if len(self._plotRefs) > 0:

            dataRef = self.getDataRef()
            
            # We iterate over all plotWindow
            for plot in self._plotRefs.values():
                
                if plot.plotType=='1d':
                    if dataRef in plot.plotRef:
                        if parameterLabel in [curve.curveLegend for curve in plot.curves.values()]:
                            return True
                if plot.plotType=='2d':
                    if dataRef in plot.plotRef:
                        if plot.zLabelText==parameterLabel:
                            return True

        return False



    @staticmethod
    def sizeof_fmt(num: float, suffix: str='B') -> str:
        """
        Return human readable number of Bytes
        Adapted from:
        https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size

        Parameters
        ----------
        num : float
            Size of a file to be transformed in human readable format
        suffix : str
            Suffix to be added after the unit size

        Return
        ------
        humanReadableSize : str
            Size of the file in an easily readable format.
        """
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, 'Y', suffix)



    @staticmethod
    def clearTableWidget(tableWidget : QtWidgets.QTableWidget) -> None:
        """
        Method to remove all row from a table widget.
        When this function is called, it should be followed by:
        tableWidget.setSortingEnabled(True)
        to allowed GUI sorting
        """

        tableWidget.setSortingEnabled(False)
        tableWidget.setRowCount(0)



    def setStatusBarMessage(self, text: str, error: bool=False) -> None:
        """
        Display message in the status bar.

        Parameters
        ----------
        text : str
            Text to be displayed.
            if text=='Ready', display the text in green and bold.
        error : bool, default False
            If true display the text in red and bold.
        """
        
        if error:
            self.statusBar.setStyleSheet('color: red; font-weight: bold;')
        elif text=='Ready':
            self.statusBar.setStyleSheet('color: green; font-weight: bold;')
        else:
            self.statusBar.setStyleSheet('color: '+config['styles'][config['style']]['dialogTextColor']+'; font-weight: normal;')

        self.statusBar.showMessage(text)


    @staticmethod
    def clearLayout(layout: QtWidgets.QLayout) -> None:
        """
        Clear a pyqt layout, from:
        https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt

        Parameters
        ----------
        layout : QtWidgets.QLayout
            Qt layout to be cleared
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()



    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Method called when closing the main app.
        Close every 1d and 2d plot opened.
        """

        plotRefs = [plot for plot in self._plotRefs.keys()]
        # plot1d window open from a plo1d window are taken care by the plot1d itself
        # we so remove them from the selection
        plotRefs = [plotRef for plotRef in plotRefs if 'fft' not in plotRef]
        plotRefs = [plotRef for plotRef in plotRefs if 'derivative' not in plotRef]
        plotRefs = [plotRef for plotRef in plotRefs if 'primitive' not in plotRef]
        
        # Close everything
        [self._plotRefs[plotRef].o() for plotRef in plotRefs]



    def cleanCheckBox(self, plotRef     : str,
                            windowTitle : str,
                            runId       : int,
                            label       : str) -> None:
        """
        Method called by the plot1d or plot2d plot when the user close the plot
        window. We propagate that event to the mainWindow to uncheck the
        checkbox and clean the reference, see self._plotRefs.

        Parameters:
        plotRef : str
            Reference of the plot, see getplotRef.
        windowTitle : str
            Window title, see getWindowTitle.
        runId : int
            Data run id of the database.
        label : str
            Label of the dependent parameter.
            Will be empty for signal from Plot1dApp since this parameter is only
            usefull for Plot2dApp.
        """
        
        # If the close plot window is a liveplot one
        if plotRef in self.getLivePlotRef():
            if hasattr(self, '_livePlotDataSet'):
                if self._plotRefs[plotRef].plotType=='1d':
                    labels = [i.curveLabel for i in self._plotRefs[plotRef].curves.values()]
                    [self.removePlot(plotRef, label) for label in labels]
                else:
                    self.removePlot(plotRef, label)
                del(self._livePlotDataSet)
        else:
            if self.getWindowTitle(runId)==windowTitle and self.getRunId()==runId:
                
                # If 1d plot
                if self._plotRefs[plotRef].plotType=='1d':
                
                    # If the current displayed parameters correspond to the one which has
                    # been closed, we uncheck all the checkbox listed in the table
                    for row in range(self.tableWidgetParameters.rowCount()):
                        widget = self.tableWidgetParameters.cellWidget(row, 2)
                        widget.setChecked(False)
                # If 2d plot
                else:
                    # We uncheck only the plotted parameter
                    for row in range(self.tableWidgetParameters.rowCount()):
                        if label==self.tableWidgetParameters.item(row, 3).text():
                            widget = self.tableWidgetParameters.cellWidget(row, 2)
                            widget.setChecked(False)

            # Unchecking the checkbox automatically called the removeplot method
            # However this method must be called even if the dependent parameter
            # closed was not in the parameter table
            else:
                self.removePlot(plotRef, label)



    ###########################################################################
    #
    #
    #                           QCoDes data handling methods
    #
    #
    ###########################################################################



    def getRunId(self, livePlot: bool=False) -> int:
        """
        Return the current selected run id.
        if Live plot mode, return the total number of run.
        """

        if livePlot:
            return self._livePlotRunId
        else:

            # If not in liveplot mode we get the runId from the gui to avoid
            # a sql call
            # First we try to get it from the database table
            currentRow = self.tableWidgetDataBase.currentIndex().row()
            runId = self.tableWidgetDataBase.model().index(currentRow, 0).data()

            # If it doesn't exist, we try the parameter table
            if runId is None:
                
                item = self.tableWidgetParameters.item(0, 0)
                
                # This occurs when user is looking to csv, s2p of bluefors files
                # In this case the runid is 0
                if item is None:
                    runId = 0
                else:
                    runId = item.text()

            return int(runId)



    def getCurveId(self, label: str,
                         livePlot: bool=False) -> str:
        """
        Return an id for a curve in a plot.
        Should be unique for every curve.

        Parameters
        ----------
        label : str
            Parameter label from which the curveId is obtained.
        livePlot : bool
            If the plot displaying the curve is a liveplot
        """ 
        
        if livePlot:
            return self._livePlotPath+str(self._livePlotRunId)+str(label)
        else:
            return self._currentDatabase+str(self.getRunId())+str(label)



    def getRunExperimentName(self) -> str:
        """
        Return the experiment name of the current selected run.
        if Live plot mode, return the experiment name of the last recorded run.
        """
        
        currentRow = self.tableWidgetDataBase.currentIndex().row()
        experimentName =  self.tableWidgetDataBase.model().index(currentRow, 2).data()
        if experimentName is None:
            experimentName = self.tableWidgetParameters.item(0, 1).text()

        return str(experimentName)



    def getWindowTitle(self, runId: int=None, livePlot:bool=False) -> str:
        """
        Return a title which will be used as a plot window title.
        """
        if config['displayRunIdInPlotTitle']:
            if livePlot:
                return os.path.basename(self._livePlotPath)+' - '+str(self._livePlotRunId)
            else:
                return str(self._currentDatabase)+' - '+str(runId)
        else:
            if livePlot:
                return os.path.basename(self._livePlotPath)
            else:
                return str(self._currentDatabase)



    def getPlotTitle(self, livePlot:bool=False) -> str:
        """
        Return a plot title in a normalize way displaying the folders and
        file name.
        """
        
        if livePlot:
            # If user only wants the database path
            if config['displayOnlyDbNameInPlotTitle']:
                title = os.path.basename(self._livePlotPath)
            # If user wants the database path
            else:
                title = os.path.basename(self._livePlotPath)
            return title+'<br>'+str(self._livePlotRunId)+' - '+self._livePlotDataSet.exp_name+config['livePlotTitleAppend']

        else:
            # If no database have been selected ever
            if self._currentDatabase is None:
                return ''
            # If BlueFors log files
            elif self.importblueFors.isBlueForsFolder(self._currentDatabase):
                return self._currentDatabase
            # If csv or s2p files we return the filename without the extension
            elif self._currentDatabase[-3:].lower() in ['csv', 's2p']:
                return self._currentDatabase[:-4]
            else:
                # If user only wants the database path
                if config['displayOnlyDbNameInPlotTitle']:
                    title = self._currentDatabase
                # If user wants the database path
                else:
                    title = os.path.normpath(self.currentPath).split(os.path.sep)[2:]
                    title = '/'.join(title)

                title = title+'<br>'+str(self.getRunId())+' - '+self.getRunExperimentName()
                return title



    def getDataRef(self, livePlot: bool=False) -> str:
        """
        Return a reference for the data.
        This should be unique for a given set of data.
        Composed of the absolute path of the file and, for qcodes db, of the 
        runid.
        """

        if livePlot:
            return self._livePlotPath + str(self._livePlotRunId)
        else:
            path = os.path.abspath(self._currentDatabase)
            
            # If BlueFors log files
            if self.importblueFors.isBlueForsFolder(self._currentDatabase):
                return path
            # If csv or s2p files we return the filename without the extension
            elif self._currentDatabase[-3:].lower() in ['csv', 's2p']:
                return path
            else:
                return path+str(self.getRunId())



    def getPlotRef(self, dataRef        : str,
                         paramDependent : dict) -> str:
        """
        Return a reference for a plot window.
        Handle the difference between 1d plot and 2d plot.
        
        Parameters
        ----------
        dataRef : str
            Reference of the data, see getDataRef
        paramDependent : dict
            qcodes dictionary of a dependent parameter
        
        Return
        ------
        plotRef : str
            Unique reference for a plot window.
        """

        if len(paramDependent['depends_on'])==2:
            return dataRef+paramDependent['name']
        else:
            return dataRef



    ###########################################################################
    #
    #
    #                           Live plotting
    #
    #
    ###########################################################################



    def getLivePlotRef(self) -> list:
        """
        Return a list of the live plot windows references.
        Return an empty list if no liveplot window
        """
        refs = []
        # We get which open plot window is the liveplot one
        for ref, plot in self._plotRefs.items():
            if plot.livePlot:
                refs.append(ref)
        
        return refs



    def livePlotUpdatePlotData(self, plotRef        : str,
                                     data           : tuple,
                                     yLabelText     : str) -> None:
        """
        Methods called in live plot mode to update plot.
        This method must have the same signature as addPlot.

        Parameters
        ----------
        plotRef : str
            Reference of the plot, see getDataRef.
        data : tuple
            For 1d plot: (xData, yData)
            For 2d plot: (xData, yData, zData)
        yLabelText : str
            Label text for the yAxis.
        """

        # 1d plot
        if len(data)==2:
            self._plotRefs[plotRef].updatePlotDataItem(x           = data[0],
                                                       y           = data[1],
                                                       curveId     = self.getCurveId(yLabelText, livePlot=True),
                                                       curveLegend = None,
                                                       autoRange   = True)
        # 2d plot
        elif len(data)==3:
            self._plotRefs[plotRef].livePlotUpdate(x=data[0],
                                                   y=data[1],
                                                   z=data[2])

            # If there are slices, we update them as well
            # plotSlice = self.getPlotSliceFromRef(plotRef)
            # if plotSlice is not None:
            for curveId, lineItem in self._plotRefs[plotRef].infiniteLines.items():

                # We find its orientation
                if lineItem.angle==90:
                    sliceOrientation = 'vertical'
                else:
                    sliceOrientation = 'horizontal'

                # We need the data of the slice
                sliceX, sliceY, sliceLegend = self._plotRefs[plotRef].getDataSlice(lineItem)

                # Get the 1d plot of the slice
                plotSlice = self._plotRefs[plotRef].getPlotRefFromSliceOrientation(sliceOrientation)

                # We update the slice data
                plotSlice.updatePlotDataItem(x           = sliceX,
                                             y           = sliceY,
                                             curveId     = curveId,
                                             curveLegend = sliceLegend,
                                             autoRange   = True)



    def livePlotGetPlotParameters(self) -> List[list]:
        """
        Gather the information from the current live plot dataset and sort them
        into iterables.
        """
        
        # Get dataset params
        paramsIndependent = [i for i in self._livePlotDataSet.get_parameters() if len(i.depends_on)==0]
        paramsDependent   = [i for i in self._livePlotDataSet.get_parameters() if len(i.depends_on)!=0]
        
        # We prepare the plot window parameters depending on the plot dimension
        if len(paramsIndependent)>2:
            return
        elif len(paramsIndependent)==2:
            xLabelText   = [paramsIndependent[0].label for i in paramsDependent]
            xLabelUnits  = [paramsIndependent[0].unit for i in paramsDependent]
            yLabelTexts  = [paramsIndependent[1].label for i in paramsDependent]
            yLabelUnitss = [paramsIndependent[1].unit for i in paramsDependent]
            zLabelTexts  = [i.label for i in paramsDependent]
            zLabelUnitss = [i.unit for i in paramsDependent]
            plotRefs     = [self.getDataRef(livePlot=True)+i.name for i in paramsDependent]
        else: 
            xLabelText   = [paramsIndependent[0].label for i in paramsDependent]
            xLabelUnits  = [paramsIndependent[0].unit for i in paramsDependent]
            yLabelTexts  = [i.label for i in paramsDependent]
            yLabelUnitss = [i.unit for i in paramsDependent]
            zLabelTexts  = ['' for i in paramsDependent]
            zLabelUnitss = ['' for i in paramsDependent]
            plotRefs     = [self.getDataRef(livePlot=True) for i in paramsDependent]
            
        return xLabelText, xLabelUnits, yLabelTexts, yLabelUnitss, zLabelTexts, zLabelUnitss, plotRefs



    def livePlotLaunchPlot(self) -> None:
        """
        Method called by the livePlotUpdate method.
        Obtain the info of the current live plot dataset cache, treat them and
        send them to the addPlot method.
        """

        #    1d.  We launch a plot window with all the dependent parameters
        #         plotted as plotDataItem.
        #    2d.  We launch as many plot window as dependent parameters.
        # Get dataset params
        paramsIndependent = [i for i in self._livePlotDataSet.get_parameters() if len(i.depends_on)==0]
        
        plotTitle   = self.getPlotTitle(livePlot=True)
        windowTitle = self.getWindowTitle(runId=self._livePlotRunId,
                                            livePlot=True)
        
        for xLabelText, xLabelUnits, yLabelText, yLabelUnits, zLabelText, zLabelUnits, plotRef in zip(*self.livePlotGetPlotParameters()):
            # Only the first dependent parameter is displayed per default
            if yLabelText==paramsIndependent[0].label:
                hidden = False
            else:
                hidden = True
            
            # Create empty data for the plot window launching
            if zLabelText=='':
                data = [[],[]]
            else:
                data = [np.array([0., 1.]),
                        np.array([0., 1.]),
                        np.array([[0., 1.],
                                  [0., 1.]])]
            
            self.addPlot(plotRef        = plotRef,
                         data           = data,
                         xLabelText     = xLabelText,
                         xLabelUnits    = xLabelUnits,
                         yLabelText     = yLabelText,
                         yLabelUnits    = yLabelUnits,
                         zLabelText     = zLabelText,
                         zLabelUnits    = zLabelUnits,
                         cleanCheckBox  = self.cleanCheckBox,
                         plotTitle      = plotTitle,
                         windowTitle    = windowTitle,
                         runId          = self._livePlotRunId,
                         linkedTo2dPlot = False,
                         curveId        = self.getCurveId(label=yLabelText, livePlot=True),
                         timestampXAxis = False,
                         livePlot       = True,
                         hidden         = hidden)



    def livePlotUpdatePlot(self) -> None:
        """
        Method called by livePlotUpdate.
        Obtain the info of the current live plot dataset cache, treat them and
        send them to the livePlotUpdatePlotData method.
        """
        
        # Get dataset params
        paramsIndependent = [i for i in self._livePlotDataSet.get_parameters() if len(i.depends_on)==0]
        
        for xLabelText, xLabelUnits, yLabelText, yLabelUnits, zLabelText, zLabelUnits, plotRef in zip(*self.livePlotGetPlotParameters()):
            
            worker = LoadDataFromCacheThread(plotRef,
                                       self._livePlotDataSet.cache.data(),
                                       xLabelText,
                                       yLabelText,
                                       zLabelText)
            
            worker.signals.dataLoaded.connect(self.livePlotUpdatePlotData)

            # Execute the thread
            self.threadpool.start(worker)
        
        # We keep track of the last number of results, see below why
        self._livePlotLastNbResults = self._livePlotDataSet.number_of_results



    def livePlotUpdate(self) -> None:
        """
        Method called periodically by a QTimer.
        1. Obtain the last runId of the livePlotDatabase
        2. If this run is not marked as completed, load its dataset and plot its
           parameters
        3. Update the plots until the run is marked completed
        4. When the run is completed, remove its dataset from memory
        """
        
        # We get the last run id of the database
        self._livePlotRunId = self._livePlotDatabase.getNbTotalRun()
        # While the run is not completed, we update the plot
        if not self._livePlotDatabase.isRunCompleted(self._livePlotRunId):
            
            ## 1. We get the livePlot dataset
            # We access the db only once.
            # The next iteration will access the cache of the dataset.
            if not hasattr(self, '_livePlotDataSet'):
                self._livePlotDataSet = self._livePlotDatabase.load_by_id(self._livePlotRunId)
            ## 2. If at least one active livePlot window is missing
            if len(self.getLivePlotRef())!=len(self._livePlotDatabase.getListIndependentFromRunId(self._livePlotRunId)):
                self.livePlotLaunchPlot()
            ## 3. If an active livePlot window is detected
            else:
                self.livePlotUpdatePlot()
            
        
        else:
            # If the livePlot has been completed since the last method's call
            if hasattr(self, '_livePlotDataSet'):
                
                # Sometimes the database is marked as completed by the cache does
                # not contains the last block of data. To go around that we keep
                # track of the las number of results and compare it to the current one.
                if self._livePlotLastNbResults!=self._livePlotDataSet.number_of_results:
                    
                    # We update the plot one last time so that the display curved is complete
                    self.livePlotUpdatePlot()
                    
                elif self._livePlotLastNbResults==self._livePlotDataSet.number_of_results:
                    # We mark all completed livePlot as not livePlot anymore
                    for plotRef in self.getLivePlotRef():
                        title = self._plotRefs[plotRef].plotItem.titleLabel.text
                        self._plotRefs[plotRef].plotItem.setTitle(title.replace(config['livePlotTitleAppend'], ''))
                        self._plotRefs[plotRef].livePlot = False
                    
                    del(self._livePlotDataSet)



    def livePlotSpinBoxChanged(self, val):
        """
        When user modify the spin box associated to the live plot timer.
        When val==0, stop the liveplot monitoring.
        """
        
        # If a Qt timer is running, we modify it following the user input.
        if self._livePlotTimer is not None:
            
            # If the timer is 0, we stopped the liveplot
            if val==0:
                self._livePlotTimer.stop()
                self._livePlotTimer.deleteLater()
                self._livePlotTimer = None
                
                self.labelLivePlotDataBase.setText('')
                self.groupBoxLivePlot.setStyleSheet('QGroupBox:title{color: white}')
                self.setStatusBarMessage('LivePlot disable')
                del(self._livePlotPath)
                del(self._livePlotDatabase)
                if hasattr(self, '_livePlotDataSet'):
                    del(self._livePlotDataSet)
            else:
                self._livePlotTimer.setInterval(val)



    def livePlotPushButton(self) -> None:
        """
        Call when user click on the 'LivePlot' button.
        Allow user to chose any available qcodes database in his computer.
        This database will be monitored and any new run will be plotted.
        """
        
        fname = QtWidgets.QFileDialog.getOpenFileName(self,
                                                      'Open QCoDeS database', 
                                                      self.currentPath,
                                                      'QCoDeS database (*.db).')
        
        if fname[0]!='':
            self._livePlotPath = os.path.abspath(fname[0])
            self._livePlotDataBaseName = os.path.basename(fname[0])[:-3]
            self.labelLivePlotDataBase.setText(self._livePlotDataBaseName)
            self.groupBoxLivePlot.setStyleSheet('QGroupBox:title{color: green}')

            self.labelLivePlotDataBase.adjustSize()
            self.setStatusBarMessage('LivePlot enable for: {}.'.format(self._livePlotDataBaseName))
            self.statusBar.setStyleSheet('color: green; font-weight: bold;')
            
            self._livePlotDatabase = QcodesDatabase(self.setStatusBarMessage)
            self._livePlotDatabase.databasePath = self._livePlotPath

            # We call the liveplot function once manually to be sure it has been
            # initialized properly
            self.livePlotUpdate()

            # Launch a Qt timer which will periodically check if a new run is
            # launched
            # If the user disable the livePlot previously
            if self.spinBoxLivePlot.value()==0:
                self.spinBoxLivePlot.setValue(1)
            self._livePlotTimer = QtCore.QTimer()
            self._livePlotTimer.timeout.connect(self.livePlotUpdate)
            self._livePlotTimer.setInterval(self.spinBoxLivePlot.value()*1000)
            self._livePlotTimer.start()



    ###########################################################################
    #
    #
    #                           Plotting
    #
    #
    ###########################################################################



    def updateList1dCurvesLabels(self) -> None:
        """
        Is called when the user add or delete a plot.
        See addPlot and removePlot
        The method creates a list of all displayed 1d plot window object and
        send it to all displayed 1d plot windows via the updatePlottedCurvesList
        method.
        """

        if len(self._plotRefs) > 0:
            
            # Build the list of 1d plot windows
            plots = [plot for plot in self._plotRefs.values() if plot.plotType=='1d']

            # Send the list to every 1d plot windows
            [plot.updatePlottedCurvesList(plots) for plot in plots]



    def addPlotFromThread(self, plotRef        : str,
                                progressBarKey : str,
                                data           : List[np.ndarray],
                                xLabelText     : str,
                                xLabelUnits    : str,
                                yLabelText     : str,
                                yLabelUnits    : str,
                                zLabelText     : str,
                                zLabelUnits    : str) -> None:
        """
        Call from loaddata thread.
        Just past the argument to the addPlot method.
        Usefull because progressBarKey is an optional parameter
        """
        
        self.addPlot(plotRef        = plotRef,
                     data           = data,
                     xLabelText     = xLabelText,
                     xLabelUnits    = xLabelUnits,
                     yLabelText     = yLabelText,
                     yLabelUnits    = yLabelUnits,
                     zLabelText     = zLabelText,
                     zLabelUnits    = zLabelUnits,
                     progressBarKey = progressBarKey)



    def addPlot(self, plotRef        : str,
                      data           : List[np.ndarray],
                      xLabelText     : str,
                      xLabelUnits    : str,
                      yLabelText     : str,
                      yLabelUnits    : str,

                      cleanCheckBox  : Callable[[str, str, int, Union[str, list]], None]=None,
                      plotTitle      : str  = None,
                      windowTitle    : str  = None,
                      runId          : int  = None,
                      linkedTo2dPlot : bool = False,
                      curveId        : str  = None,
                      curveLegend    : str  = None,
                      hidden         : bool = False,
                      curveLabel     : str  = None,
                      curveUnits     : str  = None,
                      timestampXAxis : bool = False,
                      livePlot       : bool = False,
                      progressBarKey : str  = None,
                      zLabelText     : str  = None,
                      zLabelUnits    : str  = None) -> None:
        """
        Methods called once the data are downloaded to add a plot of the data.
        Discriminate between 1d and 2d plot through the length of data list.
        For 1d plot, data having the sample plotRef do not launch a new plot
        window but instead are plotted in the window sharing the same plotRef.
        Once the data are plotted, run updateList1dCurvesLabels.

        Parameters
        ----------
        plotRef : str
            Reference of the plot.
        progressBarKey : str
            Key to the progress bar in the dict progressBars.
        data : list
            For 1d plot: [xData, yData]
            For 2d plot: [xData, yData, zData]
        xLabelText : str
            Label text for the xAxix.
        xLabelUnits : str
            Label units for the xAxix.
        yLabelText : str
            Label text for the yAxix.
        yLabelUnits : str
            Label units for the yAxix.
        zLabelText : str, default None
            Only for 2d data.
            Label text for the zAxis.
        zLabelUnits : str, default None
            Only for 2d data.
            Label units for the zAxis.
        """

        # If the method is called from a thread with a progress bar, we remove
        # it
        if progressBarKey is not None:
            if progressBarKey in self._progressBars:
                self.removeProgressBar(progressBarKey)
        
        # If data is None it means the data download encounter an error.
        # We do not add plot
        if data is None:
            return
    
        self.setStatusBarMessage('Launching '+str(len(data)-1)+'d plot')


        # If some parameters are not given, we find then from the GUI
        if runId is None:
            runId = int(self.getRunId())
        if plotTitle is None:
            plotTitle = self.getPlotTitle()
        if windowTitle is None:
            windowTitle = self.getWindowTitle(runId=runId)
        if cleanCheckBox is None:
            cleanCheckBox = self.cleanCheckBox

            
        # 1D plot
        if len(data)==2:

            
            # Specific 1d optional parameter
            if curveId is None:
                curveId = self.getCurveId(yLabelText)
            if timestampXAxis is None:
                timestampXAxis = self.importblueFors.isBlueForsFolder(self._currentDatabase)
            
            # If the plotRef is not stored we launched a new window
            # Otherwise we add a new PlotDataItem on an existing plot1dApp
            if plotRef not in self._plotRefs:
                

                p = Plot1dApp(x              = data[0],
                              y              = data[1],
                              title          = plotTitle,
                              xLabelText     = xLabelText,
                              xLabelUnits    = xLabelUnits,
                              yLabelText     = yLabelText,
                              yLabelUnits    = yLabelUnits,
                              windowTitle    = windowTitle,
                              runId          = runId,
                              cleanCheckBox  = cleanCheckBox,
                              plotRef        = plotRef,
                              addPlot        = self.addPlot,
                              getPlotFromRef = self.getPlotFromRef,
                              curveId        = curveId,
                              curveLegend    = curveLegend,
                              livePlot       = livePlot,
                              timestampXAxis = timestampXAxis)

                self._plotRefs[plotRef] = p
                self._plotRefs[plotRef].show()
            else:
                
                if curveLabel is None:
                    curveLabel = yLabelText
                if curveUnits is None:
                    curveUnits = yLabelUnits
                if curveLegend is None:
                    curveLegend = yLabelText

                self._plotRefs[plotRef].addPlotDataItem(x           = data[0],
                                                        y           = data[1],
                                                        curveId     = curveId,
                                                        curveLabel  = curveLabel,
                                                        curveUnits  = curveUnits,
                                                        curveLegend = curveLegend,
                                                        hidden      = hidden)
            

        # 2D plot
        elif len(data)==3:
            
            # Determine if we should open a new Plot2dApp
            if plotRef not in self._plotRefs:
                p = Plot2dApp(x               = data[0],
                              y               = data[1],
                              z               = data[2],
                              title           = plotTitle,
                              xLabelText      = xLabelText,
                              xLabelUnits     = xLabelUnits,
                              yLabelText      = yLabelText,
                              yLabelUnits     = yLabelUnits,
                              zLabelText      = zLabelText,
                              zLabelUnits     = zLabelUnits,
                              windowTitle     = windowTitle,
                              runId           = runId,
                              cleanCheckBox   = cleanCheckBox,
                              plotRef         = plotRef,
                              addPlot         = self.addPlot,
                              removePlot      = self.removePlot,
                              getPlotFromRef  = self.getPlotFromRef,
                              livePlot        = livePlot)

                self._plotRefs[plotRef] = p
                self._plotRefs[plotRef].show()
        
        self.setStatusBarMessage('Ready')
        self.updateList1dCurvesLabels()

        # Flag
        self._dataDowloadingFlag = False



    def removePlot(self, plotRef: str, label: str=None) -> None:
        """
        Method call when data are remove from the GUI.
        If the data plot window is open, close it.
        Then remove the reference of the plot window from self._plotRefs.
        
        Once the data are closed, run updateList1dCurvesLabels.

        Parameters
        ----------
        plotRef : str
            Reference of the plot.
        label : str, default None
            Label of the data to be removed, usefull for 1d plot.
        """
        
        if self._plotRefs[plotRef].plotType=='1d':
            # If there is more than one curve, we remove one curve
            if len(self._plotRefs[plotRef].curves) > 1:
                for curveId, plotDataItem in self._plotRefs[plotRef].curves.items():
                    if label==plotDataItem.curveLabel:
                        break
                self._plotRefs[plotRef].removePlotDataItem(curveId=curveId)
            # If there is one curve we close the plot window
            else:
                self._plotRefs[plotRef].o()
                del(self._plotRefs[plotRef])

            # Update the list of currently plotted dependent parametered on all
            # the plotted window
            self.updateList1dCurvesLabels()
        elif self._plotRefs[plotRef].plotType=='2d':
            self._plotRefs[plotRef].o()
            del(self._plotRefs[plotRef])



    def getPlotSliceFromRef(self, plotRef          : str,
                                  sliceOrientation : str) -> Union[Plot1dApp, None]:
        """
        Return the 1d plot containing the slice data of a 2d plot.

        Parameters
        ----------
        plotRef : str
            Reference of the 2d plot from which the data comes from.
        sliceOrientation : str
            Orientation of the slice we are interested in.
        """

        ref = plotRef+sliceOrientation

        if ref in self._plotRefs.keys():
            return self._plotRefs[ref]
        else:
            return None



    def getPlotFromRef(self, plotRef   : str,
                             curveType : str) -> Union[Plot1dApp, None]:
        """
        Return the 1d plot containing the FFT of a 1d plot.

        Parameters
        ----------
        plotRef : str
            Reference of the 1d plot from which the data comes from.
        curveType : str ['fft', 'derivative']
            curveType of the data looked for
        """

        ref = plotRef+curveType

        if ref in self._plotRefs.keys():
            return self._plotRefs[ref]
        else:
            return None



    ###########################################################################
    #
    #
    #                           Data 
    #
    #
    ###########################################################################



    def getData(self, plotRef: str, dependentParamName: str) -> None:
        """
        Called when user wants to plot qcodes data.
        Create a progress bar in the status bar.
        Launched a thread which will download the data, display the progress in
        the progress bar and call addPlot when the data are downloaded.

        Parameters
        ----------
        plotRef : str
            Reference of the plot window.
        dependentParamName : str
            Name of the dependent parameter from which data will be downloaded.
        """

        # Flag
        self._dataDowloadingFlag = True

        progressBarKey = self.addProgressBarInStatusBar()
        
        runId = self.getRunId()
        worker = LoadDataThread(runId,
                                dependentParamName,
                                plotRef,
                                progressBarKey,
                                self.qcodesDatabase.getParameterData,
                                self.qcodesDatabase.getParameterInfo)
        # Connect signals
        # To update the status bar
        worker.signals.setStatusBarMessage.connect(self.setStatusBarMessage)
        # To update the progress bar
        worker.signals.updateProgressBar.connect(self.updateProgressBar)
        # If data download failed
        worker.signals.updateDataEmpty.connect(self.updateDataEmpty)
        # When data download is done
        worker.signals.updateDataFull.connect(self.addPlotFromThread)

        # Execute the thread
        self.threadpool.start(worker)



    def updateDataEmpty(self) -> None:
        """
        Method called by LoadDataThread when the data download is done but the
        database is empty.
        We signal the data downloading being done by setting the flag False.
        This will allow the next live plot iteration to try downloading the data
        again.
        """
        
        self._dataDowloadingFlag = False
