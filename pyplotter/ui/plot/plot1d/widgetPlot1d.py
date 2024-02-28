from __future__ import annotations
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from typing import Union, Optional, Tuple, Dict

from .widgetPlot1dui import Ui_Dialog
from ....sources.config import loadConfigCurrent
from ....sources.functions import getCurveColorIndex
from ....sources.pyqtgraph import pg
from ..widgetPlotContainer import WidgetPlotContainer

from .groupBoxStatistics import GroupBoxStatistics
from .groupBoxCalculus import GroupBoxCalculus
from .groupBoxFFT import GroupBoxFFT
from .groupBoxNormalize import GroupBoxNormalize
from .groupBoxFit import GroupBoxFit
from .groupBoxFiltering import GroupBoxFiltering
from .widgetTabCurve import WidgetTabCurve
from .widgetDownsampling import WidgetDownsampling
from .widgetCurveStyle import WidgetCurveStyle


class WidgetPlot1d(QtWidgets.QDialog):
    """
    Class to handle ploting in 1d.
    """

    signalRemovePlotFromRef  = QtCore.pyqtSignal(str, str)
    signal2MainWindowRemoveCurve = QtCore.pyqtSignal(str, str)
    signal2MainWindowClosePlot  = QtCore.pyqtSignal(str)
    signalRemovePlotRef  = QtCore.pyqtSignal(str)

    signalClose1dPlot  = QtCore.pyqtSignal(str)
    signalUpdateCurve  = QtCore.pyqtSignal(str, str, str, np.ndarray, np.ndarray, bool, bool)

    signal2MainWindowAddPlot   = QtCore.pyqtSignal(int, str, str, str, str, str, tuple, str, str, str, str, str, str)

    # To send selected data to interaction group boxes
    signalSendSelectedData = QtCore.pyqtSignal(np.ndarray, str, str, np.ndarray, str, str)

    # Fit interaction
    signalFitUpdate = QtCore.pyqtSignal()
    signalFitClose  = QtCore.pyqtSignal()

    # Filtering interaction
    signalFilteringUpdate  = QtCore.pyqtSignal()
    signalFilteringClose = QtCore.pyqtSignal()

    # Statistics interaction
    signalCheckBoxStatisticsSetChecked = QtCore.pyqtSignal(bool)
    signalStatisticsClosePlot = QtCore.pyqtSignal()
    signalStatisticsUpdate = QtCore.pyqtSignal()


    # FFT interaction
    signalCheckBoxFFTSetChecked = QtCore.pyqtSignal(bool)
    signalFFTUpdate = QtCore.pyqtSignal()
    signalFFTClosePlot = QtCore.pyqtSignal()

    signalCheckBoxFFTnoDCSetChecked = QtCore.pyqtSignal(bool)
    signalFFTNoDcUpdate = QtCore.pyqtSignal()
    signalFFTNoDcClosePlot = QtCore.pyqtSignal()

    signalCheckBoxIFFTSetChecked = QtCore.pyqtSignal(bool)
    signalIFFTUpdate = QtCore.pyqtSignal()
    signalIFFTClosePlot = QtCore.pyqtSignal()


    # Calculus interaction
    signalCheckBoxDifferentiateSetChecked = QtCore.pyqtSignal(bool)
    signalDifferentiateUpdate = QtCore.pyqtSignal()
    signalDifferentiateClosePlot = QtCore.pyqtSignal()

    signalCheckBoxIntegrateSetChecked = QtCore.pyqtSignal(bool)
    signalIntegrateUpdate = QtCore.pyqtSignal()
    signalIntegrateClosePlot = QtCore.pyqtSignal()


    # Normalization interaction
    signalCheckBoxUnwrapSetChecked = QtCore.pyqtSignal(bool)
    signalUnwrapUpdate = QtCore.pyqtSignal()
    signalUnwrapClosePlot = QtCore.pyqtSignal()

    signalCheckBoxRemoveSlopeSetChecked = QtCore.pyqtSignal(bool)
    signalRemoveSlopeUpdate = QtCore.pyqtSignal()
    signalRemoveSlopeClosePlot = QtCore.pyqtSignal()



    def __init__(self, x                  : np.ndarray,
                       y                  : np.ndarray,
                       title              : str,
                       xLabelText         : str,
                       xLabelUnits        : str,
                       yLabelText         : str,
                       yLabelUnits        : str,
                       windowTitle        : str,
                       runId              : int,
                       plotRef            : str,
                       databaseAbsPath    : str,
                       curveId            : str,
                       curveLegend        : str,
                       dateTimeAxis       : bool,
                       dialogX         : Optional[int]=None,
                       dialogY         : Optional[int]=None,
                       dialogWidth     : Optional[int]=None,
                       dialogHeight    : Optional[int]=None) -> None:
        """
        Class handling the plot of 1d data.
        Allow some quick data treatment.
        A plot can be a slice of a 2d plot.

        Parameters
        ----------
        x : np.ndarray
            Data along the x axis, 1d array.
        y : np.ndarray
            Data along the y axis, 1d array.
        title : str
            Plot title.
        xLabelText : str
            Label text along the x axis.
        xLabelUnits : str
            Label units along the x axis.
        yLabelText : str
            Label text along the y axis.
        yLabelUnits : str
            Label units along the y axis.
        windowTitle : str
            Window title.
        runId : int
            Id of the QCoDeS run.
        cleanCheckBox : Callable[[str, str, int, Union[str, list]], None]
            Function called when the window is closed.
        plotRef : str
            Reference of the plot
        addPlot : Callable
            Function from the mainApp used to launched 1d plot and keep plot
            reference updated.
        removePlot : Callable
            Function from the mainApp used to delete 1d plot and keep plot
            reference updated.
        getPlotFromRef : Callable
            Function from the mainApp used to remove 1d plot and keep plot
            reference updated.
        curveId : Optional[str], optional
            Id of the curve being plot, see getCurveId in the mainApp., by default None
        curveLegend : Optional[str], optional
            Label of the curve legend.
            If None, is the same as yLabelText, by default None
        dateTimeAxis : bool, optional
            If yes, the x axis becomes a pyqtgraph DateAxisItem.
            See pyqtgraph doc about DateAxisItem
        """

        # Set parent to None to have "free" qdialog
        super(WidgetPlot1d, self).__init__(None)

        # Build the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.plotWidgetContainer = WidgetPlotContainer(self)


        self._allowClosing = False

        self.config = loadConfigCurrent()

        # Shortcut to access the plot widget and item
        self.plotWidget = self.plotWidgetContainer.plotWidget
        self.plotItem = self.plotWidget.getPlotItem()

        # Allow resize of the plot window
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint|
                            QtCore.Qt.WindowMaximizeButtonHint|
                            QtCore.Qt.WindowCloseButtonHint)

        self.plotType       = '1d'
        self._windowTitle    = windowTitle
        self.runId          = runId
        self.plotRef        = plotRef
        self.databaseAbsPath = databaseAbsPath

        # References of PlotDataItem
        # Structures
        # self.curves = {'curveId' : pg.PlotDataItem}
        self.curves: dict={}

        # Keep track of the sub-interaction plots launched fron that plot
        self.dialogInteraction: Dict[str, dict] = {}

        # References of the infinietLines used to select data for the fit.
        # Structured
        # self.sliceItems = {'a' : pg.InfiniteLine,
        #                    'b' : pg.InfiniteLine}
        self.sliceItems: Dict[str, pg.InfiniteLine] = {}

        # If the xaxis used timestamp, we use a dedicated axisItem
        if dateTimeAxis:
            # This utc offset is unclear to me...
            self.plotItem.setAxisItems({'bottom' : pg.DateAxisItem(utcOffset=0.)})

        # Create legendItem
        self.legendItem = self.plotItem.addLegend()

        # Connect UI
        self.ui.checkBoxLogX.stateChanged.connect(self.checkBoxLogState)
        self.ui.checkBoxLogY.stateChanged.connect(self.checkBoxLogState)
        self.ui.checkBoxSplitYAxis.stateChanged.connect(self.checkBoxSplitYAxisState)
        self.ui.comboBoxXAxis.activated.connect(self.comboBoxXAxisActivated)

        ## Add a widget to handle line style
        self.widgetCurveStyle = WidgetCurveStyle(parent=self.ui.groupBoxDisplay)
        self.widgetCurveStyle.signalCurveStyleChanged.connect(self.curveStyleChanged)

        ## Add a widget to handle downsampling
        self.widgetDownsampling = WidgetDownsampling(parent=self.ui.groupBoxDisplay)
        self.widgetDownsampling.signalDownsamplingChanged.connect(self.downsamplingChanged)

        # Add a radio button for each model of the list
        self.ui.plotDataItemButtonGroup = QtWidgets.QButtonGroup()
        self.ui.radioButtonFitNone = QtWidgets.QRadioButton(self.ui.groupBoxPlotDataItem)
        self.ui.radioButtonFitNone.setEnabled(True)
        self.ui.radioButtonFitNone.setChecked(True)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        self.ui.radioButtonFitNone.setFont(font)
        self.ui.radioButtonFitNone.setText('None')
        self.ui.radioButtonFitNone.curveId = None
        self.ui.radioButtonFitNone.clicked.connect(self.selectPlotDataItem)

        self.ui.verticalLayoutPlotDataItem.addWidget(self.ui.radioButtonFitNone)
        self.ui.plotDataItemButtonGroup.addButton(self.ui.radioButtonFitNone, 0)

        # Order of initialization determine their GUI order
        self.initGroupBoxFFT()
        self.initGroupBoxStatistics()
        self.initGroupBoxCalculus()
        self.initGroupBoxNormalize()
        self.initGroupBoxFit()
        self.initGroupBoxFiltering()
        self.initTabCurve()



        self.setWindowTitle(windowTitle)

        self.plotItem.setTitle(title=title,
                               color=self.config['styles'][self.config['style']]['pyqtgraphTitleTextColor'])

        # To make the GUI faster
        self.plotItem.disableAutoRange()

        # Personalize the GUI
        if self.config['plot1dGrid']:
            self.plotItem.showGrid(x=True, y=True)



        font=QtGui.QFont()
        font.setPixelSize(self.config['tickLabelFontSize'])
        self.plotItem.getAxis('bottom').setTickFont(font)
        self.plotItem.getAxis('left').setTickFont(font)
        self.plotItem.getAxis('bottom').setPen(self.config['styles'][self.config['style']]['pyqtgraphxAxisTicksColor'])
        self.plotItem.getAxis('left').setPen(self.config['styles'][self.config['style']]['pyqtgraphyAxisTicksColor'])
        self.plotItem.getAxis('bottom').setTextPen(self.config['styles'][self.config['style']]['pyqtgraphxAxisTickLabelsColor'])
        self.plotItem.getAxis('left').setTextPen(self.config['styles'][self.config['style']]['pyqtgraphyAxisTickLabelsColor'])

        self.plotItem.setLabel(axis='bottom',
                               text=xLabelText,
                               units=xLabelUnits,
                               **{'color'     : self.config['styles'][self.config['style']]['pyqtgraphxLabelTextColor'],
                                  'font-size' : str(self.config['axisLabelFontSize'])+'pt'})
        self.plotItem.setLabel(axis='left',
                               text=yLabelText,
                               units=yLabelUnits,
                               **{'color'     : self.config['styles'][self.config['style']]['pyqtgraphyLabelTextColor'],
                                      'font-size' : str(self.config['axisLabelFontSize'])+'pt'})

        self.setStyleSheet("background-color: "+str(self.config['styles'][self.config['style']]['dialogBackgroundColor'])+";")
        self.setStyleSheet("color: "+str(self.config['styles'][self.config['style']]['dialogTextColor'])+";")

        self.addPlotDataItem(x                  = x,
                             y                  = y,
                             curveId            = curveId,
                             curveXLabel        = xLabelText,
                             curveXUnits        = xLabelUnits,
                             curveYLabel        = yLabelText,
                             curveYUnits        = yLabelUnits,
                             curveLegend        = curveLegend)

        self.resize(*self.config['dialogWindowSize'])
        self.show()

        # Connect the button to get a screenshot of the plot
        # Done here since we need a reference of the plotWidget
        self.ui.qButtonCopy.clicked.connect(lambda: self.ui.qButtonCopy.clicked_(self.plotWidget))
        # For unknown reason, I have to initialize the text here...
        self.ui.qButtonCopy.setText(self.ui.qButtonCopy._text)

        self.ui.qCheckBoxCrossHair.signalAddCrossHair.connect(self.plotWidget.slotAddCrossHair)

        # AutoRange only after the first data item is added
        # Must be done after the show()
        # Must be called twice (I do not know why)
        self.autoRange()
        self.autoRange()

        # if the dialog size was given (usually meaning a live plot is done)
        if dialogWidth is not None and dialogHeight is not None:
            self.adjustSize()
            frameHeight = self.frameGeometry().height()-self.height()
            frameWidth = self.frameGeometry().width()-self.width()
            self.resize(dialogWidth-frameWidth, dialogHeight-frameHeight)
            self.move(dialogX, dialogY)

    ####################################
    #
    #           init GUI
    #
    ####################################



    def initTabCurve(self) -> None:

        self.ui.widgetTabCurve = WidgetTabCurve(self.ui.tabWidget,
                                                self.plotRef)

        # Events from the groupBox to the plot1d
        self.ui.widgetTabCurve.signalAddPlotDataItem.connect(self.slotAddPlotDataItem)
        self.ui.widgetTabCurve.signalUpdatePlotDataItem.connect(self.slotUpdatePlotDataItem)
        self.ui.widgetTabCurve.signalRemovePlotDataItem.connect(self.slotRemoveCurve)



    def initGroupBoxFFT(self) -> None:

        self.groupBoxFFT = GroupBoxFFT(self.ui.groupBoxCurveInteraction,
                                       self.config,
                                       self.databaseAbsPath,
                                       self.plotItem,
                                       self.plotRef,
                                       self._windowTitle)

        self.signalSendSelectedData.connect(self.groupBoxFFT.slotGetSelectedData)

        self.signalCheckBoxFFTSetChecked.connect(self.groupBoxFFT.slotCheckBoxFFTSetChecked)
        self.signalCheckBoxFFTnoDCSetChecked.connect(self.groupBoxFFT.slotCheckBoxFFTnoDCSetChecked)
        self.signalCheckBoxIFFTSetChecked.connect(self.groupBoxFFT.slotCheckBoxIFFTSetChecked)

        self.signalFFTUpdate.connect(self.groupBoxFFT.slotFFTUpdate)
        self.signalFFTNoDcUpdate.connect(self.groupBoxFFT.slotFFTNoDcUpdate)
        self.signalIFFTUpdate.connect(self.groupBoxFFT.slotIFFTUpdate)

        self.signalFFTClosePlot.connect(self.groupBoxFFT.slotFFTClosePlot)
        self.signalFFTNoDcClosePlot.connect(self.groupBoxFFT.slotFFTNoDcClosePlot)
        self.signalIFFTClosePlot.connect(self.groupBoxFFT.slotIFFTClosePlot)

        self.groupBoxFFT.signalUpdateCurve.connect(self.signalUpdateCurve)
        self.groupBoxFFT.signal2MainWindowAddPlot.connect(self.signal2MainWindowAddPlot)
        self.groupBoxFFT.signalClose1dPlot.connect(self.signalClose1dPlot)
        self.ui.verticalLayout_2.addWidget(self.groupBoxFFT)



    def initGroupBoxStatistics(self) -> None:

        self.groupBoxStatistics = GroupBoxStatistics(self.ui.groupBoxCurveInteraction,
                                                     self.config,
                                                     self.databaseAbsPath,
                                                     self.plotItem,
                                                     self.plotRef,
                                                     self._windowTitle)
        self.signalSendSelectedData.connect(self.groupBoxStatistics.slotGetSelectedData)
        self.signalCheckBoxStatisticsSetChecked.connect(self.groupBoxStatistics.slotCheckBoxStatisticsSetChecked)
        self.signalStatisticsUpdate.connect(self.groupBoxStatistics.slotUpdate)
        self.signalStatisticsClosePlot.connect(self.groupBoxStatistics.slotClosePlot)

        self.groupBoxStatistics.signalUpdateCurve.connect(self.signalUpdateCurve)
        self.groupBoxStatistics.signal2MainWindowAddPlot.connect(self.signal2MainWindowAddPlot)
        self.groupBoxStatistics.signalClose1dPlot.connect(self.signalClose1dPlot)
        self.ui.verticalLayout_2.addWidget(self.groupBoxStatistics)



    def initGroupBoxCalculus(self) -> None:



        self.groupBoxCalculus = GroupBoxCalculus(self.ui.groupBoxCurveInteraction,
                                                 self.config,
                                                 self.databaseAbsPath,
                                                 self.plotItem,
                                                 self.plotRef,
                                                 self._windowTitle)
        self.signalSendSelectedData.connect(self.groupBoxCalculus.slotGetSelectedData)

        self.signalCheckBoxDifferentiateSetChecked.connect(self.groupBoxCalculus.slotCheckBoxDifferentiateSetChecked)
        self.signalCheckBoxIntegrateSetChecked.connect(self.groupBoxCalculus.slotCheckBoxIntegrateSetChecked)
        self.signalDifferentiateUpdate.connect(self.groupBoxCalculus.slotDifferentiateUpdate)
        self.signalDifferentiateClosePlot.connect(self.groupBoxCalculus.slotDifferentiateClosePlot)
        self.signalIntegrateUpdate.connect(self.groupBoxCalculus.slotIntegrateUpdate)
        self.signalIntegrateClosePlot.connect(self.groupBoxCalculus.slotIntegrateClosePlot)

        self.groupBoxCalculus.signalUpdateCurve.connect(self.signalUpdateCurve)
        self.groupBoxCalculus.signal2MainWindowAddPlot.connect(self.signal2MainWindowAddPlot)
        self.groupBoxCalculus.signalClose1dPlot.connect(self.signalClose1dPlot)
        self.ui.verticalLayout_2.addWidget(self.groupBoxCalculus)



    def initGroupBoxNormalize(self) -> None:



        self.groupBoxNormalize = GroupBoxNormalize(self.ui.groupBoxCurveInteraction,
                                                  self.config,
                                                  self.databaseAbsPath,
                                                  self.plotItem,
                                                  self.plotRef,
                                                  self._windowTitle)
        self.signalSendSelectedData.connect(self.groupBoxNormalize.slotGetSelectedData)

        self.signalCheckBoxUnwrapSetChecked.connect(self.groupBoxNormalize.slotCheckBoxUnwrapSetChecked)
        self.signalUnwrapUpdate.connect(self.groupBoxNormalize.slotUnwrapUpdate)
        self.signalUnwrapClosePlot.connect(self.groupBoxNormalize.slotUnwrapClosePlot)

        self.signalCheckBoxRemoveSlopeSetChecked.connect(self.groupBoxNormalize.slotCheckBoxRemoveSlopeSetChecked)
        self.signalRemoveSlopeUpdate.connect(self.groupBoxNormalize.slotRemoveSlopeUpdate)
        self.signalRemoveSlopeClosePlot.connect(self.groupBoxNormalize.slotRemoveSlopeClosePlot)

        self.groupBoxNormalize.signalUpdateCurve.connect(self.signalUpdateCurve)
        self.groupBoxNormalize.signal2MainWindowAddPlot.connect(self.signal2MainWindowAddPlot)
        self.groupBoxNormalize.signalClose1dPlot.connect(self.signalClose1dPlot)
        self.ui.verticalLayout_2.addWidget(self.groupBoxNormalize)



    def initGroupBoxFit(self) -> None:
        """
        Method called at the initialization of the GUI.
        Make a list of radioButton reflected the available list of fitmodel.
        By default all radioButton are disabled and user should chose a plotDataItem
        to make them available.
        """

        self.groupBoxFit  = GroupBoxFit(self.ui.groupBoxCurveInteraction,
                                        self.plotRef,
                                        self.plotItem)

        # Events from the groupBox to the plot1d
        self.groupBoxFit.signalAddPlotDataItem.connect(self.slotAddPlotDataItem)
        self.groupBoxFit.signalUpdatePlotDataItem.connect(self.slotUpdatePlotDataItem)
        self.groupBoxFit.signalRemovePlotDataItem.connect(self.slotRemoveCurve)

        # Events from the plot1d to the groupBox
        self.signalSendSelectedData.connect(self.groupBoxFit.slotGetSelectedData)
        self.signalFitUpdate.connect(self.groupBoxFit.slotFitUpdate)
        self.signalFitClose.connect(self.groupBoxFit.slotFitClose)

        # Add GUI
        self.ui.verticalLayout_2.addWidget(self.groupBoxFit)



    def initGroupBoxFiltering(self) -> None:
        """
        Method called at the initialization of the GUI.
        Make a list of radioButton reflected the available list of fitmodel.
        By default all radioButton are disabled and user should chose a plotDataItem
        to make them available.
        """

        self.groupBoxFiltering  = GroupBoxFiltering(self.ui.groupBoxCurveInteraction,
                                                    self.plotRef,
                                                    self.plotItem)

        # Events from the groupBox to the plot1d
        self.groupBoxFiltering.signalAddPlotDataItem.connect(self.slotAddPlotDataItem)
        self.groupBoxFiltering.signalUpdatePlotDataItem.connect(self.slotUpdatePlotDataItem)
        self.groupBoxFiltering.signalRemovePlotDataItem.connect(self.slotRemoveCurve)

        # Events from the plot1d to the groupBox
        self.signalSendSelectedData.connect(self.groupBoxFiltering.slotGetSelectedData)
        self.signalFilteringUpdate.connect(self.groupBoxFiltering.slotFilteringUpdate)
        self.signalFilteringClose.connect(self.groupBoxFiltering.slotFilteringClose)

        # Add GUI
        self.ui.verticalLayout_2.addWidget(self.groupBoxFiltering)




    ####################################
    #
    #           Method to close, clean stuff
    #
    ####################################



    def closeEvent(self, evnt: QtGui.QCloseEvent) -> None:

        # # We catch the close event and ignore it
        if not self._allowClosing:
            evnt.ignore()

        for curveId, interaction in self.dialogInteraction.items():
            if curveId in list(self.curves.keys()):
                interaction['dialog'].close()

        # All the closing procedure of the plot is handle in the MainWindow
        self.signalClose1dPlot.emit(self.plotRef)



    ####################################
    #
    #           Method related to the plotDataItem
    #
    ####################################



    def updateListXAxis(self) -> None:

        self.ui.comboBoxXAxis.clear()

        for curve in self.curves.values():
            if self.ui.comboBoxXAxis.findText(curve.curveXLabel)==-1:
                self.ui.comboBoxXAxis.addItem(curve.curveXLabel)
            if self.ui.comboBoxXAxis.findText(curve.curveYLabel)==-1:
                self.ui.comboBoxXAxis.addItem(curve.curveYLabel)

        self.ui.comboBoxXAxis.setCurrentIndex(self.ui.comboBoxXAxis.findText(self.plotItem.getAxis('bottom').labelText))



    def comboBoxXAxisActivated(self, autoRange: bool=False) -> None:
        """
        Method to change the xAxis along which the plotDataItem are plotted.
        """

        # The change of x axis is enable only if there is no fit or filtering
        # being done
        if self.ui.comboBoxXAxis.isEnabled():
            # Get a curve containing the data to update the plot
            # Either in its x or y axis
            for curve in self.curves.values():
                # During liveplot, dataset may be None for the first iteration
                if curve._dataset is not None:
                    if curve.curveXLabel==self.ui.comboBoxXAxis.currentText():
                        newXData  = curve.x
                        newXLabel = curve.curveXLabel
                        newXUnits = curve.curveXUnits
                        break
                    if curve.curveYLabel==self.ui.comboBoxXAxis.currentText():
                        newXData  = curve.y
                        newXLabel = curve.curveYLabel
                        newXUnits = curve.curveYUnits
                        break

            # We update the curve
            for curve in self.curves.values():
                # During liveplot, dataset may be None for the first iteration
                if curve._dataset is not None:
                    # During liveplot, [:len(newXData)] handles update of the y axis
                    curve.setData(x=newXData[:len(curve.y)],
                                  y=curve.y[:len(newXData)])

            # We update the x label
            self.plotItem.setLabel(axis ='bottom',
                                   text =newXLabel,
                                   units=newXUnits)

        if autoRange:
            self.autoRange()



    ####################################
    #
    #           Method related to display
    #
    ####################################



    def updatePlotProperty(self, prop: str,
                                 value: str) -> None:

        if prop=='plotTitle':
            self.plotItem.setTitle(title=value)



    ####################################
    #
    #           Method related to the plotDataItem
    #
    ####################################



    def getNotHiddenCurves(self) -> dict:
        """
        Obtain the dict of not hidden curves
        """

        curvesNotHidden = {}
        for curveId, plotDataItem in self.curves.items():
            if not plotDataItem.hidden:
                curvesNotHidden[curveId] = plotDataItem

        return curvesNotHidden



    def autoRange(self) -> None:
        """
        Autorange the plotItem based on the unHide plotDataItem.
        """

        curvesNotHidden = self.getNotHiddenCurves()

        xRange = [1e99, -1e99]
        yRange = [1e99, -1e99]

        for curveId, plotDataItem in curvesNotHidden.items():

            xRangeTemp = plotDataItem.dataBounds(0)
            yRangeTemp = plotDataItem.dataBounds(1)

            if xRangeTemp[0] is not None and xRangeTemp[1] is not None and yRangeTemp[0] is not None and yRangeTemp[1] is not None:

                if xRangeTemp[0]<xRange[0]:
                    xRange[0] = xRangeTemp[0]
                if yRangeTemp[0]<yRange[0]:
                    yRange[0] = yRangeTemp[0]

                if xRangeTemp[1]>xRange[1]:
                    xRange[1] = xRangeTemp[1]
                if yRangeTemp[1]>yRange[1]:
                    yRange[1] = yRangeTemp[1]

        self.plotItem.setRange(xRange=xRange, yRange=yRange)



    ####################################
    #
    #           Method to add, update, remove items
    #
    ####################################



    def getLineColor(self, onlyOnePoint: bool) -> Tuple[int,
                                                        QtGui.QPen,
                                                        Optional[str],
                                                        QtGui.QPen,
                                                        QtGui.QBrush]:
        """
        Return a pyqtgraph mKpen with the color of the next curve following
        the colors in config files
        """

        colorIndex = getCurveColorIndex([curve.colorIndex for curve in self.curves.values()],
                                        self.config)
        linePen = pg.mkPen(color=self.config['plot1dColors'][colorIndex],
                           width=self.config['plotDataItemWidth'])
        symbolBrush = pg.mkBrush(color=self.config['plot1dColors'][colorIndex])
        symbolPen = pg.mkPen(color='black',
                             width=self.config['plotDataItemWidth'])

        # If the user changed the default curveStyle
        if hasattr(self, 'curveStyle'):
            # If symbol are needed
            if self.curveStyle in (' o', 'o-'):
                symbol = self.config['plot1dSymbol'][colorIndex]
            else:
                symbol = None
        else:
            symbol = None

        # If there is only one data point, we override user choice and draw a
        # symbol, otherwise the point is not visible.
        if onlyOnePoint:
            symbol = self.config['plot1dSymbol'][colorIndex]

        return colorIndex, linePen, symbol, symbolPen, symbolBrush



    def updatePlotDataItem(self, x                  : np.ndarray,
                                 y                  : np.ndarray,
                                 curveId            : str,
                                 curveLegend        : str,
                                 autoRange          : bool,
                                 interactionUpdateAll: bool) -> None:
        """
        Method called by a plot2d when use drag a sliceLine.
        Updating an existing plotDataItem and the plot legendItem

        Parameters
        ----------
        x : np.ndarray
            x data.
        y : np.ndarray
            y data.
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        curveLegend : str
            Legend label of the curve.
        autoRange : bool
            If the view should perform an autorange after updating the data.
            Can be slow for heavy data array.
        """

        # Set option if plotting histogram
        # stepMode: Optional[str] = None
        # if histogram:
        #     stepMode = 'center'

        self.curves[curveId].setData(x=x,
                                     y=y)


        self.curves[curveId].x = x
        self.curves[curveId].y = y
        self.curves[curveId].curveLegend = curveLegend

        self.updateLegend()

        # If a curve selection has been done, we update the selected data
        curveIdSelection = self.ui.plotDataItemButtonGroup.checkedButton().curveId
        if curveIdSelection is not None:
            self.updateSelectedData()
            self.updatePlotDataItemStyle(curveIdSelection)

        # we update interaction
        if interactionUpdateAll:
            self.interactionUpdateAll()

        # we update the axis
        # The autorange is done there
        self.comboBoxXAxisActivated(autoRange)



    def addPlotDataItem(self, x                 : np.ndarray,
                              y                 : np.ndarray,
                              curveId           : str,
                              curveXLabel       : str,
                              curveXUnits       : str,
                              curveYLabel       : str,
                              curveYUnits       : str,
                              curveLegend       : str,
                              showInLegend      : bool=True,
                              hidden            : bool=False) -> None:
        """
        Method adding a plotDataItem to the plotItem.

        Parameters
        ----------
        x : np.ndarray
            x data.
        y : np.ndarray
            y data.
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        curveYLabel: str
            y label of the curve.
        curveYUnits: str
            y units of the curve.
        curveLegend : str
            Legend label of the curve.
        showInLegend : bool
            If the plotDataLegend should be shown in the legend.
            Default True.
        hidden : bool
            If the plotDataItem is hidden.
            Default False.
        """

        # Get the dataPlotItem color
        colorIndex, linePen, symbol, symbolPen, symbolBrush = self.getLineColor(len(x)==1)

        # Create plotDataItem and save its reference
        self.curves[curveId] = self.plotItem.plot(x,
                                                  y,
                                                  pen=linePen,
                                                  symbol=symbol,
                                                  symbolPen=symbolPen,
                                                  symbolBrush=symbolBrush,
                                                  useCache=True, # Improve performance
                                                  autoDownsample=True, # Improve performance
                                                #   clipToView = True, # Improve performance
                                                  )

        # Create usefull attribute
        self.curves[curveId].x                  = x
        self.curves[curveId].y                  = y
        self.curves[curveId].colorIndex         = colorIndex
        self.curves[curveId].curveXLabel        = curveXLabel
        self.curves[curveId].curveXUnits        = curveXUnits
        self.curves[curveId].curveYLabel        = curveYLabel
        self.curves[curveId].curveYUnits        = curveYUnits
        self.curves[curveId].curveLegend        = curveLegend
        self.curves[curveId].showInLegend       = showInLegend
        self.curves[curveId].hidden             = hidden
        self.curves[curveId].pen                = linePen

        self.updateListDataPlotItem(curveId)
        self.updateListXAxis()



    def removePlotDataItem(self, curveId: str) -> None:
        """
        Remove a PlotDataItem identified via its "curveId".

        Parameters
        ----------
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        """

        # If no curve will be displayed, we close the QDialog
        if len(self.curves)==1:
            self.close()
        else:
            # Remove the curve
            self.plotItem.removeItem(self.curves[curveId])
            del(self.curves[curveId])

            self.updateListDataPlotItem(curveId)
            self.updateListXAxis()



    def updateyLabel(self) -> None:
        """
        Update the ylabel of the plotItem
        There are 4 cases depending of the number of dataPlotItem:
            1. If there is 1: the displayed ylabel is the data ylabel.
            2. If there are more than 1 with the same unit: the unit is displayed.
            3. If there are more than 1 with different unit: the unit "a.u" displayed.
            4. If there is 2 and one is the selection curve: we change nothing.
            5. If all curves are hidden, we display "None".
        """

        # Obtain the list of not hidden plotDataItem
        curvesNotHidden = self.getNotHiddenCurves()


        # If there are two curves and one is the selection one, we change nothing
        if len(curvesNotHidden)==2 and any(['selection' in curveId for curveId in curvesNotHidden.keys()]):
            pass
        # If there are three curves and one is the selection one and the other a fit, we change nothing
        elif (len(curvesNotHidden)==3
              and any(['selection' in curveId for curveId in curvesNotHidden.keys()])
              and any(['fit' in curveId for curveId in curvesNotHidden.keys()])):
            pass
        # If there is more than one plotDataItem
        # We check of the share the same unit
        elif len(curvesNotHidden)>1 and len(set(curve.curveYUnits for curve in curvesNotHidden.values()))==1:
            self.plotItem.setLabel(axis ='left',
                                    text ='',
                                    units=curvesNotHidden[list(curvesNotHidden.keys())[0]].curveYUnits)
        # We check of the share the same label
        elif len(set(curve.curveYLabel for curve in curvesNotHidden.values()))>1:
            self.plotItem.setLabel(axis ='left',
                                    text ='',
                                    units='a.u')
        # If there is only one plotDataItem or if the plotDataItems share the same label
        elif len(curvesNotHidden)==1:
            self.plotItem.setLabel(axis ='left',
                                    text =curvesNotHidden[list(curvesNotHidden.keys())[0]].curveYLabel,
                                    units=curvesNotHidden[list(curvesNotHidden.keys())[0]].curveYUnits)
        else:
            self.plotItem.setLabel(axis ='left',
                                    text ='None',
                                    units='')



    def updateLegend(self) -> None:
        """
        Update the legendItem of the plotItem.
        Only plotDataItem with showInLegend==True and hidden==False are shown
        To do so, we
        1. Clear the legendItem.
        2. Browse plotDataItem and add then to the freshly cleared legendItem.
        """

        self.legendItem.clear()

        # We do not add items in the legend when there is only one curve
        # except when the 1d plot is linked to a 2d plot
        if len(self.curves)==1:
            for curve in self.curves.values():
                if curve.showInLegend and not curve.hidden:
                    self.legendItem.addItem(curve, curve.curveLegend)
        elif len(self.curves) > 1:
            for curve in self.curves.values():
                if curve.showInLegend and not curve.hidden:
                    self.legendItem.addItem(curve, curve.curveLegend)



    def updateListDataPlotItem(self, curveId: str) -> None:
        """
        Method called when a plotDataItem is added or removed to the plotItem.
        Add a radioButton to allow the user to select the plotDataItem.
        Add a checkBox to allow the user to hide the plotDataItem.

        Parameters
        ----------
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        """

        if len(self.curves)==2:
            self.ui.checkBoxSplitYAxis.setEnabled(True)
        else:
            self.ui.checkBoxSplitYAxis.setEnabled(False)

        # Update list of plotDataItem only if the plotDataItem is not a fit
        if ('fit' not in curveId and
            'filtering' not in curveId and
            'selection' not in curveId):
            # Add a radioButton to allow the user to select the plotDataItem.
            # If there is already a button with curveId, we remove it
            createButton = True
            for radioButton in self.ui.plotDataItemButtonGroup.buttons():
                if radioButton.curveId==curveId:
                    self.ui.plotDataItemButtonGroup.removeButton(radioButton)
                    radioButton.setParent(None)
                    createButton = False
            # Otherwise, we create it
            if createButton:
                radioButton = QtWidgets.QRadioButton(self.curves[curveId].curveYLabel)
                radioButton.curveId = curveId
                self.ui.plotDataItemButtonGroup.addButton(radioButton, len(self.ui.plotDataItemButtonGroup.buttons()))
                radioButton.clicked.connect(self.selectPlotDataItem)
                self.ui.verticalLayoutPlotDataItem.addWidget(radioButton)

            # Add a checkBox to allow the user to hide the plotDataItem.
            # If there is already a button with curveId, we remove it
            createButton = True
            for i in range(self.ui.verticalLayoutHide.count()):
                if self.ui.verticalLayoutHide.itemAt(i) is not None:
                    checkBox = self.ui.verticalLayoutHide.itemAt(i).widget()
                    if checkBox.curveId==curveId:
                        self.ui.verticalLayoutHide.removeWidget(checkBox)
                        checkBox.setParent(None)
                        createButton = False
            # Otherwise, we create it
            if createButton:
                checkBox = QtWidgets.QCheckBox(self.curves[curveId].curveYLabel)
                checkBox.curveId = curveId
                checkBox.stateChanged.connect(lambda : self.hidePlotDataItem(checkBox))

                checkBox.setChecked(self.curves[curveId].hidden)
                self.ui.verticalLayoutHide.addWidget(checkBox)

        # We update displayed information
        self.updateLegend()
        self.updateyLabel()



    ####################################
    #
    #           Method to related to display
    #
    ####################################



    def checkBoxLogState(self, b: QtWidgets.QCheckBox) -> None:
        """
        Method called when user click on the log checkBoxes.
        Modify the scale, linear or logarithmic, of the plotItem following
        which checkbox are checked.
        """

        # If split y axis enable
        if hasattr(self, 'curveRight'):
            plotItems = [self.plotItem, self.curveRight]
        else:
            plotItems = [self.plotItem]

        if self.ui.checkBoxLogX.isChecked():
            if self.ui.checkBoxLogY.isChecked():
                [item.setLogMode(True, True) for item in plotItems]
            else:
                [item.setLogMode(True, False) for item in plotItems]
        else:
            if self.ui.checkBoxLogY.isChecked():
                [item.setLogMode(False, True) for item in plotItems]
            else:
                [item.setLogMode(False, False) for item in plotItems]

        if hasattr(self, 'curveRight'):
            self.vbRight.autoRange()



    @QtCore.pyqtSlot(str)
    def curveStyleChanged(self, curveStyle: str) -> None:
        """
        Called from widgetCurveStyle when user click on the comboBox.
        Used to changed the curveStyle of the displayed curves.
        """

        # Save the current curveStyle
        self.curveStyle = curveStyle

        # CurveStyle: symbol + line
        if curveStyle=='o-':

            for i, (key, curve) in enumerate(list(self.curves.items())):
                if key != 'fit':
                    curve.setSymbol(self.config['plot1dSymbol'][i%len(self.config['plot1dSymbol'])])
                    curve.setPen(curve.pen)

                    # If split y axis enable
                    if hasattr(self, 'curveRight'):
                        self.curveRight.setSymbol(self.config['plot1dSymbol'][i%len(self.config['plot1dSymbol'])])
                        self.curveRight.setPen(self.curveRight.pen)
        # CurveStyle: symbol
        elif curveStyle==' o':

            for i, (key, curve) in enumerate(list(self.curves.items())):
                if key != 'fit':
                    curve.setSymbol(self.config['plot1dSymbol'][i%len(self.config['plot1dSymbol'])])
                    curve.setPen(pg.mkPen(None))

                    # If split y axis enable
                    if hasattr(self, 'curveRight'):
                        self.curveRight.setSymbol(self.config['plot1dSymbol'][i%len(self.config['plot1dSymbol'])])
                        self.curveRight.setPen(pg.mkPen(None))
        # CurveStyle: line
        else:
            for i, (key, curve) in enumerate(list(self.curves.items())):
                if key != 'fit':
                    curve.setSymbol(None)
                    curve.setPen(curve.pen)

            # If split y axis enable
            if hasattr(self, 'curveRight'):
                self.curveRight.setSymbol(None)
                self.curveRight.setPen(self.curveRight.pen)



    def splitAutoBtnClicked(self) -> None:
        """
        Method used to overwrite the standard "autoBtnClicked" of the PlotItem.
        Simply allow, in the split mode view (see checkBoxSplitYAxisState), to
        autorange the two viewbox at the same time.
        """
        if self.plotItem.autoBtn.mode == 'auto':
            self.vbRight.setYRange(self.vbRight.addedItems[0].yData.min(), self.vbRight.addedItems[0].yData.max())
            self.vbRight.setXRange(self.vbRight.addedItems[0].xData.min(), self.vbRight.addedItems[0].xData.max())
            self.plotItem.enableAutoRange()
            self.plotItem.autoBtn.hide()
        else:
            self.plotItem.disableAutoRange()



    def checkBoxSplitYAxisState(self, b: QtWidgets.QCheckBox) -> None:
        """
        Method called when user click on the Symbol checkBox.
        Put symbols on all plotDataItem except fit model.
        """

        # Only work for two plotDataItem
        if len(self.curves)==2:

            # Get the curveId for the curve linked to the left and right axis.
            leftCurveId  = list(self.curves.keys())[0]
            rightCurveId = list(self.curves.keys())[1]

            if self.ui.checkBoxSplitYAxis.isChecked():

                self.ui.groupBoxCurveInteraction.setEnabled(False)

                # Create an empty plotDataItem which will contain the right curve
                self.curveRight = pg.PlotDataItem(pen=self.curves[rightCurveId].pen)

                # Create and set links for a second viewbox which will contains the right curve
                self.vbRight = pg.ViewBox()
                self.vbRight.setXLink(self.plotItem)
                self.plotItem.scene().addItem(self.vbRight)
                self.plotItem.showAxis('right')
                self.plotItem.getAxis('right').linkToView(self.vbRight)

                # Remove the plotDataItem which will be on the second viewbox
                self.plotItem.removeItem(self.curves[rightCurveId])

                # Remove the legendItem, now obsolete with the right axis
                self.legendItem.clear()

                # Display the correct information on each axis about their curve
                self.plotItem.setLabel(axis='left',
                                    text=self.curves[leftCurveId].curveYLabel,
                                    units=self.curves[leftCurveId].curveYUnits,
                                    **{'color'     : self.config['styles'][self.config['style']]['pyqtgraphyLabelTextColor'],
                                        'font-size' : str(self.config['axisLabelFontSize'])+'pt'})
                self.plotItem.setLabel(axis='right',
                                    text=self.curves[rightCurveId].curveYLabel,
                                    units=self.curves[rightCurveId].curveYUnits,
                                    **{'color'     : self.config['styles'][self.config['style']]['pyqtgraphyLabelTextColor'],
                                        'font-size' : str(self.config['axisLabelFontSize'])+'pt'})

                # Add the plotDataItem in the right viewbox
                self.vbRight.addItem(self.curveRight)
                self.curveRight.setData(self.curves[rightCurveId].xData, self.curves[rightCurveId].yData)
                self.vbRight.setYRange(self.curves[rightCurveId].yData.min(), self.curves[rightCurveId].yData.max())

                # Sorcery to me, found here:
                # https://stackoverflow.com/questions/29473757/pyqtgraph-multiple-y-axis-on-left-side
                # If that's not here, the views are incorrect
                def updateViews():
                    self.vbRight.setGeometry(self.plotItem.getViewBox().sceneBoundingRect())
                    self.vbRight.linkedViewChanged(self.plotItem.getViewBox(), self.vbRight.XAxis)
                updateViews()
                self.plotItem.getViewBox().sigResized.connect(updateViews)

                # We overwrite the autoRange button to make it work with
                # both axis
                self.plotItem.autoBtn.clicked.disconnect(self.plotItem.autoBtnClicked)
                self.plotItem.autoBtn.clicked.connect(self.splitAutoBtnClicked)
            else:

                self.ui.groupBoxCurveInteraction.setEnabled(True)

                # Restore the autoRange button original method
                self.plotItem.autoBtn.clicked.disconnect(self.splitAutoBtnClicked)
                self.plotItem.autoBtn.clicked.connect(self.plotItem.autoBtnClicked)

                # Remove the right viewbox and other stuff done for the right axis
                self.plotItem.hideAxis('right')
                self.plotItem.scene().removeItem(self.vbRight)
                self.plotItem.getViewBox().sigResized.disconnect()
                del(self.vbRight)
                del(self.curveRight)

                # Put back the left view box as it was before the split
                self.plotItem.addItem(self.curves[rightCurveId])

                self.updateLegend()
                self.updateyLabel()



    def hidePlotDataItem(self, cb : QtWidgets.QCheckBox) -> None:

        curveId      = cb.curveId
        plotDataItem = self.curves[curveId]

        # We get the interaction radioBox having the same curveId
        radioBox = [i for i in [self.ui.verticalLayoutPlotDataItem.itemAt(i).widget() for i in range(self.ui.verticalLayoutPlotDataItem.count())] if i.curveId==curveId][0]

        if cb.isChecked():

            # if checkBox.isChecked():
            plotDataItem.setAlpha(0, False)
            plotDataItem.hidden = True

            # When the curve is hidden, we do not allow interaction with it
            radioBox.setEnabled(False)
        else:
            # If the curve was previously hidden
            if plotDataItem.hidden:
                plotDataItem.hidden = False
                plotDataItem.setAlpha(1, False)

                radioBox.setEnabled(True)

        # Update the display
        self.updateyLabel()
        self.updateLegend()
        self.autoRange()



    @QtCore.pyqtSlot(int)
    def downsamplingChanged(self, downsamplingValue: int) -> None:
        """
        Called from widgetDownsampling when user click on the spinBox.
        Used to changed the downSampling of the displayed curves.

        Args:
            downsamplingValue: Factor of the downsampling
        """

        # We update all the curve with the new downsampling
        for curve in self.curves.values():
            curve.setDownsampling(downsamplingValue)



    ####################################
    #
    #           Method to related to interaction
    #
    ####################################



    def interactionCurveClose(self, curveId: str) -> None:
        """
        Called from MainWindow when sub-interaction plot is closed.
        Uncheck their associated checkBox
        """

        if 'fftnodc' in curveId:
            self.signalCheckBoxFFTnoDCSetChecked.emit(False)
        elif 'ifft' in curveId:
            self.signalCheckBoxIFFTSetChecked.emit(False)
        elif 'fft' in curveId:
            self.signalCheckBoxFFTSetChecked.emit(False)
        elif 'unwrap' in curveId:
            self.signalCheckBoxUnwrapSetChecked.emit(False)
        elif 'unslop' in curveId:
            self.signalCheckBoxRemoveSlopeSetChecked.emit(False)
        elif 'derivative' in curveId:
            self.signalCheckBoxDifferentiateSetChecked.emit(False)
        elif 'primitive' in curveId:
            self.signalCheckBoxIntegrateSetChecked.emit(False)
        elif 'histogram' in curveId:
            self.signalCheckBoxStatisticsSetChecked.emit(False)



    ####################################
    #
    #           Method to related to data selection
    #
    ####################################



    def updateSelectedData(self) -> None:
        """
        Get the x and y data of the curve specified by its curve id troncated
        between the infiniteLines "a" and "b".
        It does not matter if a<b or a>b.

        Parameters
        ----------
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        """
        curveId = self.ui.plotDataItemButtonGroup.checkedButton().curveId

        if curveId is not None:
            a = self.sliceItems['a'].value()
            b = self.sliceItems['b'].value()

            n = np.abs(self.curves[curveId].xData-a).argmin()
            m = np.abs(self.curves[curveId].xData-b).argmin()

            # +1 to take into account the last selection point
            if n<m:
                x: np.ndarray = self.curves[curveId].xData[n:m+1]
                y: np.ndarray = self.curves[curveId].yData[n:m+1]
            else:
                x = self.curves[curveId].xData[m:n+1]
                y = self.curves[curveId].yData[m:n+1]


            # If we are dealing with histogram data
            if len(x)==len(y)+1:
                x = x[:-2]+(x[1]-x[0])/2

            self.selectedX, self.selectedY = x, y

            self.signalSendSelectedData.emit(self.selectedX,
                                             self.selectedXLabel,
                                             self.selectedXUnits,
                                             self.selectedY,
                                             self.selectedYLabel,
                                             self.selectedYUnits)



    def selectionInifiniteLineChangeFinished(self, lineItem: pg.InfiniteLine,
                                                   curveId: str) -> None:
        """
        Method call when user release a dragged selection line.
        Update the selected data and if a model is already being active, update
        the model as well.

        Parameters
        ----------
        lineItem : pg.InfiniteLine
            Pyqtgraph infiniteLine being dragged.
        curveId : str
            Id of the curve.
            See getCurveId from MainApp
        """

        # Update data used for the fit
        self.updateSelectedData()

        # Update the style of the display plotDataItem
        self.updatePlotDataItemStyle(curveId)

        # we update interaction
        self.interactionUpdateAll()

        # We overide a pyqtgraph attribute when user drag an infiniteLine
        lineItem.mouseHovering  = False



    def selectionInifiniteLineDragged(self, lineItem: pg.InfiniteLine) -> None:
        """
        Method call when an user is dragging a selection line.

        Parameters
        ----------
        lineItem : pg.InfiniteLine
            Pyqtgraph infiniteLine being dragged.
        """

        # We overide a pyqtgraph attribute when user drag an infiniteLine
        lineItem.mouseHovering  = True



    def updateSelectionInifiteLine(self, curveId: Union[str, None]) -> None:
        """
        Method call by selectPlotDataItem.
        Handle the creation or deletion of two infiniteLine items used to select
        data.
        The infiniteLine item  events are connected as follow:
            sigPositionChangeFinished -> selectionInifiniteLineChangeFinished
            sigDragged -> selectionInifiniteLineDragged

        Parameters
        ----------
        curveId : str
            Id of the curve.
            If None, we delete the infinite lines
            See getCurveId from MainApp
        """

        # If we want to remove the selection infinite line
        if curveId is None:
            if 'a' in self.sliceItems.keys():
                self.plotItem.removeItem(self.sliceItems['a'])
            if 'b' in self.sliceItems.keys():
                self.plotItem.removeItem(self.sliceItems['b'])
        else:
            pen = pg.mkPen(color=self.config['styles'][self.config['style']]['plot1dSelectionLineColor'],
                           width=3,
                           style=QtCore.Qt.SolidLine)
            hoverPen = pg.mkPen(color=self.config['styles'][self.config['style']]['plot1dSelectionLineColor'],
                                width=3,
                                style=QtCore.Qt.DashLine)

            angle = 90.
            pos = self.curves[curveId].xData[0]

            t = pg.InfiniteLine(angle=angle, movable=True, pen=pen, hoverPen=hoverPen)
            t.setPos(pos)

            self.plotItem.addItem(t)
            self.sliceItems['a'] = t
            t.sigPositionChangeFinished.connect(lambda: self.selectionInifiniteLineChangeFinished(lineItem=t, curveId=curveId))
            t.sigDragged.connect(lambda: self.selectionInifiniteLineDragged(lineItem=t))

            pos = self.curves[curveId].xData[-1]

            t = pg.InfiniteLine(angle=angle, movable=True, pen=pen, hoverPen=hoverPen)
            t.setPos(pos)

            self.plotItem.addItem(t)
            self.sliceItems['b'] = t
            t.sigPositionChangeFinished.connect(lambda: self.selectionInifiniteLineChangeFinished(lineItem=t, curveId=curveId))
            t.sigDragged.connect(lambda: self.selectionInifiniteLineDragged(lineItem=t))



    def updatePlotDataItemStyle(self, curveId: Union[str, None]) -> None:
        """
        Modify the style of a plotDataItem.
        Use to indicate which plotDataItem is currently selected

        Parameters
        ----------
        curveId : str
            Id of the curve.
            If None, put back the default plotDataItem style.
            See getCurveId from MainApp
        """

        if curveId is not None:
            if curveId+'-selection' not in self.curves.keys():
                # Create new style
                Pen = pg.mkPen(color=self.config['plot1dColorsComplementary'][self.curves[curveId].colorIndex],
                               style=QtCore.Qt.SolidLine ,
                               width=self.config['plotDataItemWidth'])

                self.addPlotDataItem(x            = self.selectedX,
                                     y            = self.selectedY,
                                     curveId      = curveId+'-selection',
                                     curveXLabel  = self.curves[curveId].curveXLabel,
                                     curveXUnits  = self.curves[curveId].curveXUnits,
                                     curveYLabel  = self.curves[curveId].curveYLabel,
                                     curveYUnits  = self.curves[curveId].curveYUnits,
                                     curveLegend  = 'Selection',
                                     showInLegend = True)

                # Apply new style
                self.curves[curveId+'-selection'].setPen(Pen)
            else:
                # Update the curve
                self.curves[curveId+'-selection'].setData(x=self.selectedX,
                                                          y=self.selectedY)
        else:
            # Remove the curve
            curveIdToBeRemoved = None
            for curveId in self.curves.keys():
                if '-selection' in curveId:
                    curveIdToBeRemoved = curveId
                    break
            if curveIdToBeRemoved is not None:
                self.removePlotDataItem(curveIdToBeRemoved)



    def selectPlotDataItem(self) -> None:
        """
        Method called when user clicks on a radioButton of the list of
        plotDataItem.
        The method will put the curve data in memory and display which
        plotDataItem is currently selected.
        If the use clicked on the None button, we delete the selected data and
        all subsequent object created with it.
        Called the following method:
            updateSelectionInifiteLine
            updatePlotDataItemStyle
            enableWhenPlotDataItemSelected
        """
        radioButton = self.ui.plotDataItemButtonGroup.checkedButton()

        # When user click None, we unselect everything
        if radioButton.curveId is None:

            checkBoxes = (self.ui.verticalLayoutHide.itemAt(i).widget() for i in range(self.ui.verticalLayoutHide.count()))
            for checkBox in checkBoxes:
                checkBox.setEnabled(True)

            self.interactionCloseAll()

            # Remove the selection Infinite Line
            self.updateSelectionInifiteLine(None)

            # Remove the selected curve
            self.updatePlotDataItemStyle(None)

            # Disable interaction using selected data
            self.enableWhenPlotDataItemSelected(False)

        else:

            checkBoxes = (self.ui.verticalLayoutHide.itemAt(i).widget() for i in range(self.ui.verticalLayoutHide.count()))
            for checkBox in checkBoxes:
                if checkBox.curveId==radioButton.curveId:
                    checkBox.setEnabled(False)

            self.selectedYLabel :str = self.curves[radioButton.curveId].curveYLabel
            self.selectedXLabel :str = self.curves[radioButton.curveId].curveXLabel
            self.selectedYUnits :str = self.curves[radioButton.curveId].curveYUnits
            self.selectedXUnits :str = self.curves[radioButton.curveId].curveXUnits

            # The addSliceItem method has be launched before the update
            self.updateSelectionInifiteLine(radioButton.curveId)

            # Update data used for the fit
            self.updateSelectedData()

            # Update the style of the display plotDataItem
            self.updatePlotDataItemStyle(radioButton.curveId)

            # Enable interaction using selected data
            self.enableWhenPlotDataItemSelected(True)



    def enableWhenPlotDataItemSelected(self, enable: bool) -> None:
        """
        Method called when user clicks on a radioButton of the list of
        plotDataItem.
        Make enable or disable the radioButton of models.

        Parameters
        ----------
        enable : bool
            Enable or not the GUI to interact with the selected curve.
        """

        self.groupBoxFFT.setEnabled(enable)
        self.groupBoxCalculus.setEnabled(enable)
        self.groupBoxStatistics.setEnabled(enable)
        self.groupBoxFiltering.setEnabled(enable)
        self.groupBoxFit.setEnabled(enable)
        self.groupBoxNormalize.setEnabled(enable)

        # The change of x-axis is enable only when no interaction is done
        self.ui.comboBoxXAxis.setEnabled(not enable)



    def interactionCloseAll(self) -> None:

        self.signalFilteringClose.emit()
        self.signalFitClose.emit()
        self.signalFFTClosePlot.emit()
        self.signalFFTNoDcClosePlot.emit()
        self.signalIFFTClosePlot.emit()
        self.signalDifferentiateClosePlot.emit()
        self.signalIntegrateClosePlot.emit()
        self.signalUnwrapClosePlot.emit()
        self.signalRemoveSlopeClosePlot.emit()
        self.signalStatisticsClosePlot.emit()



    def interactionUpdateAll(self) -> None:

        self.signalFilteringUpdate.emit()
        self.signalFitUpdate.emit()
        self.signalFFTUpdate.emit()
        self.signalFFTNoDcUpdate.emit()
        self.signalIFFTUpdate.emit()
        self.signalDifferentiateUpdate.emit()
        self.signalIntegrateUpdate.emit()
        self.signalUnwrapUpdate.emit()
        self.signalRemoveSlopeUpdate.emit()
        self.signalStatisticsUpdate.emit()



    ####################################
    #
    #           Slot from other widgets
    #
    ####################################



    @QtCore.pyqtSlot(str, str)
    def slotRemoveCurve(self, plotRef: str,
                              curveId: str) -> None:
        """
        If user remove a curve.
        The signal is propagated to all plot.
        We check if that concerns that instance and if yes effectivelty remove
        a curve.
        """
        if plotRef==self.plotRef:
            if curveId in self.curves.keys():
                self.removePlotDataItem(curveId)



    ####################################
    #
    #           Slot for fit and filtering interaction
    #
    ####################################



    QtCore.pyqtSlot(np.ndarray, np.ndarray, str, str, str, str, str, str, bool, bool)
    def slotAddPlotDataItem(self, x                 : np.ndarray,
                                  y                 : np.ndarray,
                                  curveId           : str,
                                  curveXLabel       : str,
                                  curveXUnits       : str,
                                  curveYLabel       : str,
                                  curveYUnits       : str,
                                  curveLegend       : str,
                                  showInLegend      : bool,
                                  hidden            : bool) -> None:

        self.addPlotDataItem(x=x,
                             y=y,
                             curveId=curveId,
                             curveXLabel=curveXLabel,
                             curveXUnits=curveXUnits,
                             curveYLabel=curveYLabel,
                             curveYUnits=curveYUnits,
                             curveLegend=curveLegend,
                             showInLegend=showInLegend,
                             hidden=hidden)



    @QtCore.pyqtSlot(np.ndarray, np.ndarray, str, str, bool, bool)
    def slotUpdatePlotDataItem(self, x           : np.ndarray,
                                     y           : np.ndarray,
                                     curveId     : str,
                                     curveLegend : str,
                                     autoRange   : bool,
                                     interactionUpdateAll: bool) -> None:

        self.updatePlotDataItem(x=x,
                                y=y,
                                curveId=curveId,
                                curveLegend=curveLegend,
                                autoRange=autoRange,
                                interactionUpdateAll=interactionUpdateAll)



    @QtCore.pyqtSlot(str)
    def closeInteractionDialog(self, interaction: str) -> None:

        # We close the plot
        if 'fit' in self.curves.keys():
            self.removePlotDataItem(interaction)

        # We reset the comboBox without triggering event
        self.dialogInteraction[interaction]['comboBox'].blockSignals(True)
        self.dialogInteraction[interaction]['comboBox'].setCurrentIndex(0)
        self.dialogInteraction[interaction]['comboBox'].blockSignals(False)

        # Allow to uncheck button without triggering event
        # self.dialogInteraction[interaction]['button'].setCheckable(False)
        # self.dialogInteraction[interaction]['button'].setCheckable(True)

        # Delete its associated reference
        del(self.dialogInteraction[interaction])



    @QtCore.pyqtSlot(np.ndarray, np.ndarray, str, str)
    def updateInteractionCurve(self, x                  : np.ndarray,
                                     y                  : np.ndarray,
                                     curveId            : str,
                                     curveLegend        : Optional[str]=None) -> None:

        self.curves[curveId].setData(x=x, y=y)
        self.curves[curveId].curveLegend = curveLegend
        self.updateLegend()