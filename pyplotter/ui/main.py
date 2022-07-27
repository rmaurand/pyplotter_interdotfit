# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\scripts\pyplotter\pyplotter\ui\main.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 612)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setContentsMargins(4, 0, 4, 4)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, 6, -1, 1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.TopHorizontalLayout = QtWidgets.QHBoxLayout()
        self.TopHorizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.TopHorizontalLayout.setSpacing(0)
        self.TopHorizontalLayout.setObjectName("TopHorizontalLayout")
        self.groupBoxDataExplorer = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxDataExplorer.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBoxDataExplorer.setFont(font)
        self.groupBoxDataExplorer.setObjectName("groupBoxDataExplorer")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.groupBoxDataExplorer)
        self.verticalLayout_12.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_12.setSpacing(4)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.pushButtonOpenFolder = QtWidgets.QPushButton(self.groupBoxDataExplorer)
        self.pushButtonOpenFolder.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButtonOpenFolder.setMaximumSize(QtCore.QSize(80, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.pushButtonOpenFolder.setFont(font)
        self.pushButtonOpenFolder.setObjectName("pushButtonOpenFolder")
        self.verticalLayout_12.addWidget(self.pushButtonOpenFolder)
        self.labelPath = QtWidgets.QHBoxLayout()
        self.labelPath.setObjectName("labelPath")
        self.verticalLayout_12.addLayout(self.labelPath)
        self.TopHorizontalLayout.addWidget(self.groupBoxDataExplorer)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.TopHorizontalLayout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.TopHorizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget_2 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.labelFolder = QtWidgets.QLabel(self.layoutWidget_2)
        self.labelFolder.setMinimumSize(QtCore.QSize(0, 20))
        self.labelFolder.setMaximumSize(QtCore.QSize(16777215, 20))
        self.labelFolder.setObjectName("labelFolder")
        self.verticalLayout_5.addWidget(self.labelFolder)
        self.tableWidgetFolder = QtWidgets.QTableWidget(self.layoutWidget_2)
        self.tableWidgetFolder.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidgetFolder.setFont(font)
        self.tableWidgetFolder.setStyleSheet("")
        self.tableWidgetFolder.setLineWidth(0)
        self.tableWidgetFolder.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.tableWidgetFolder.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidgetFolder.setAlternatingRowColors(True)
        self.tableWidgetFolder.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetFolder.setShowGrid(False)
        self.tableWidgetFolder.setObjectName("tableWidgetFolder")
        self.tableWidgetFolder.setColumnCount(2)
        self.tableWidgetFolder.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetFolder.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidgetFolder.setHorizontalHeaderItem(1, item)
        self.tableWidgetFolder.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidgetFolder.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidgetFolder.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetFolder.verticalHeader().setVisible(False)
        self.verticalLayout_5.addWidget(self.tableWidgetFolder)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelRun = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.labelRun.setMinimumSize(QtCore.QSize(1, 20))
        self.labelRun.setMaximumSize(QtCore.QSize(150, 20))
        self.labelRun.setObjectName("labelRun")
        self.horizontalLayout_2.addWidget(self.labelRun)
        self.labelCurrentRun = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.labelCurrentRun.setMinimumSize(QtCore.QSize(0, 20))
        self.labelCurrentRun.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelCurrentRun.setFont(font)
        self.labelCurrentRun.setText("")
        self.labelCurrentRun.setObjectName("labelCurrentRun")
        self.horizontalLayout_2.addWidget(self.labelCurrentRun)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.tableWidgetParameters = QtWidgets.QTableWidget(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidgetParameters.setFont(font)
        self.tableWidgetParameters.setLineWidth(0)
        self.tableWidgetParameters.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidgetParameters.setAlternatingRowColors(True)
        self.tableWidgetParameters.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetParameters.setShowGrid(False)
        self.tableWidgetParameters.setObjectName("tableWidgetParameters")
        self.tableWidgetParameters.setColumnCount(6)
        self.tableWidgetParameters.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetParameters.setHorizontalHeaderItem(5, item)
        self.tableWidgetParameters.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetParameters.verticalHeader().setVisible(False)
        self.verticalLayout_6.addWidget(self.tableWidgetParameters)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelMetadata = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.labelMetadata.setMinimumSize(QtCore.QSize(0, 20))
        self.labelMetadata.setMaximumSize(QtCore.QSize(140, 20))
        self.labelMetadata.setObjectName("labelMetadata")
        self.horizontalLayout_3.addWidget(self.labelMetadata)
        self.labelCurrentMetadata = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.labelCurrentMetadata.setMinimumSize(QtCore.QSize(0, 20))
        self.labelCurrentMetadata.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelCurrentMetadata.setFont(font)
        self.labelCurrentMetadata.setText("")
        self.labelCurrentMetadata.setObjectName("labelCurrentMetadata")
        self.horizontalLayout_3.addWidget(self.labelCurrentMetadata)
        self.labelFilter = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.labelFilter.setEnabled(False)
        self.labelFilter.setMinimumSize(QtCore.QSize(0, 20))
        self.labelFilter.setMaximumSize(QtCore.QSize(40, 20))
        self.labelFilter.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelFilter.setObjectName("labelFilter")
        self.horizontalLayout_3.addWidget(self.labelFilter)
        self.snapshotLineEditFilter = SnapshotQLineEdit(self.verticalLayoutWidget_2)
        self.snapshotLineEditFilter.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.snapshotLineEditFilter.sizePolicy().hasHeightForWidth())
        self.snapshotLineEditFilter.setSizePolicy(sizePolicy)
        self.snapshotLineEditFilter.setMinimumSize(QtCore.QSize(0, 20))
        self.snapshotLineEditFilter.setMaximumSize(QtCore.QSize(150, 20))
        font = QtGui.QFont()
        font.setItalic(True)
        self.snapshotLineEditFilter.setFont(font)
        self.snapshotLineEditFilter.setText("")
        self.snapshotLineEditFilter.setObjectName("snapshotLineEditFilter")
        self.horizontalLayout_3.addWidget(self.snapshotLineEditFilter)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.snapShotTreeView = SnapshotViewTree(self.verticalLayoutWidget_2)
        self.snapShotTreeView.setObjectName("snapShotTreeView")
        self.verticalLayout_7.addWidget(self.snapShotTreeView)
        self.layoutWidget_3 = QtWidgets.QWidget(self.splitter_2)
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.layoutWidget_3)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelDataBase = QtWidgets.QLabel(self.layoutWidget_3)
        self.labelDataBase.setMaximumSize(QtCore.QSize(110, 16777215))
        self.labelDataBase.setObjectName("labelDataBase")
        self.horizontalLayout.addWidget(self.labelDataBase)
        self.labelCurrentDataBase = QtWidgets.QLabel(self.layoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.labelCurrentDataBase.setFont(font)
        self.labelCurrentDataBase.setStyleSheet("color: green;")
        self.labelCurrentDataBase.setText("")
        self.labelCurrentDataBase.setObjectName("labelCurrentDataBase")
        self.horizontalLayout.addWidget(self.labelCurrentDataBase)
        self.checkBoxHidden = QtWidgets.QCheckBox(self.layoutWidget_3)
        self.checkBoxHidden.setEnabled(False)
        self.checkBoxHidden.setMaximumSize(QtCore.QSize(90, 16777215))
        self.checkBoxHidden.setObjectName("checkBoxHidden")
        self.horizontalLayout.addWidget(self.checkBoxHidden)
        self.verticalLayout_11.addLayout(self.horizontalLayout)
        self.tableWidgetDataBase = QTableWidgetKey(self.layoutWidget_3)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tableWidgetDataBase.setFont(font)
        self.tableWidgetDataBase.setLineWidth(0)
        self.tableWidgetDataBase.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.tableWidgetDataBase.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidgetDataBase.setAlternatingRowColors(True)
        self.tableWidgetDataBase.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidgetDataBase.setShowGrid(False)
        self.tableWidgetDataBase.setColumnCount(8)
        self.tableWidgetDataBase.setObjectName("tableWidgetDataBase")
        self.tableWidgetDataBase.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetDataBase.setHorizontalHeaderItem(7, item)
        self.tableWidgetDataBase.horizontalHeader().setDefaultSectionSize(80)
        self.tableWidgetDataBase.horizontalHeader().setMinimumSectionSize(32)
        self.tableWidgetDataBase.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetDataBase.verticalHeader().setVisible(False)
        self.verticalLayout_11.addWidget(self.tableWidgetDataBase)
        self.verticalLayout_4.addWidget(self.splitter_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setMinimumSize(QtCore.QSize(0, 30))
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1024, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuConfig = QtWidgets.QMenu(self.menuBar)
        self.menuConfig.setObjectName("menuConfig")
        self.menustyle = QtWidgets.QMenu(self.menuConfig)
        self.menustyle.setObjectName("menustyle")
        self.menuplot = QtWidgets.QMenu(self.menuConfig)
        self.menuplot.setObjectName("menuplot")
        self.menuLiveplot = QtWidgets.QMenu(self.menuBar)
        self.menuLiveplot.setObjectName("menuLiveplot")
        MainWindow.setMenuBar(self.menuBar)
        self.actionqb = QtWidgets.QAction(MainWindow)
        self.actionqb.setCheckable(True)
        self.actionqb.setChecked(False)
        self.actionqb.setEnabled(True)
        self.actionqb.setObjectName("actionqb")
        self.actionqdark = QtWidgets.QAction(MainWindow)
        self.actionqdark.setCheckable(True)
        self.actionqdark.setChecked(False)
        self.actionqdark.setObjectName("actionqdark")
        self.actionwhite = QtWidgets.QAction(MainWindow)
        self.actionwhite.setCheckable(True)
        self.actionwhite.setObjectName("actionwhite")
        self.actionDefaultPath = QtWidgets.QAction(MainWindow)
        self.actionDefaultPath.setObjectName("actionDefaultPath")
        self.actionAxisLabelColor = QtWidgets.QAction(MainWindow)
        self.actionAxisLabelColor.setObjectName("actionAxisLabelColor")
        self.actionAxisTickLabelsColor = QtWidgets.QAction(MainWindow)
        self.actionAxisTickLabelsColor.setObjectName("actionAxisTickLabelsColor")
        self.actionTitleColor = QtWidgets.QAction(MainWindow)
        self.actionTitleColor.setObjectName("actionTitleColor")
        self.actionAxisTicksColor = QtWidgets.QAction(MainWindow)
        self.actionAxisTicksColor.setObjectName("actionAxisTicksColor")
        self.actionFontsize = QtWidgets.QAction(MainWindow)
        self.actionFontsize.setObjectName("actionFontsize")
        self.actionColormap = QtWidgets.QAction(MainWindow)
        self.actionColormap.setObjectName("actionColormap")
        self.actionqt_material = QtWidgets.QAction(MainWindow)
        self.actionqt_material.setObjectName("actionqt_material")
        self.actionSelectDatabase = QtWidgets.QAction(MainWindow)
        self.actionSelectDatabase.setObjectName("actionSelectDatabase")
        self.actionOpenliveplot = QtWidgets.QAction(MainWindow)
        self.actionOpenliveplot.setObjectName("actionOpenliveplot")
        self.menustyle.addAction(self.actionqb)
        self.menustyle.addAction(self.actionqdark)
        self.menustyle.addAction(self.actionwhite)
        self.menuplot.addAction(self.actionAxisLabelColor)
        self.menuplot.addAction(self.actionAxisTickLabelsColor)
        self.menuplot.addAction(self.actionTitleColor)
        self.menuplot.addAction(self.actionAxisTicksColor)
        self.menuplot.addAction(self.actionFontsize)
        self.menuplot.addAction(self.actionColormap)
        self.menuConfig.addAction(self.menustyle.menuAction())
        self.menuConfig.addAction(self.actionDefaultPath)
        self.menuConfig.addAction(self.menuplot.menuAction())
        self.menuLiveplot.addAction(self.actionOpenliveplot)
        self.menuBar.addAction(self.menuConfig.menuAction())
        self.menuBar.addAction(self.menuLiveplot.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pyplotter"))
        self.groupBoxDataExplorer.setTitle(_translate("MainWindow", "Data explorer"))
        self.pushButtonOpenFolder.setText(_translate("MainWindow", "Open folder"))
        self.labelFolder.setText(_translate("MainWindow", "Browse folder:"))
        self.tableWidgetFolder.setSortingEnabled(True)
        item = self.tableWidgetFolder.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "item"))
        item = self.tableWidgetFolder.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "size"))
        self.labelRun.setText(_translate("MainWindow", "Browse parameters run:"))
        self.tableWidgetParameters.setSortingEnabled(True)
        item = self.tableWidgetParameters.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "run id"))
        item = self.tableWidgetParameters.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "experiment name"))
        item = self.tableWidgetParameters.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "plotted"))
        item = self.tableWidgetParameters.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "axis"))
        item = self.tableWidgetParameters.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "unit"))
        item = self.tableWidgetParameters.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "swept parameters"))
        self.labelMetadata.setText(_translate("MainWindow", "Browse metadata run:"))
        self.labelFilter.setText(_translate("MainWindow", "Filter:"))
        self.labelDataBase.setText(_translate("MainWindow", "Browse database:"))
        self.checkBoxHidden.setText(_translate("MainWindow", "Show hidden"))
        self.tableWidgetDataBase.setSortingEnabled(True)
        item = self.tableWidgetDataBase.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "run id"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "dim"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "experiment"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "sample"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "run name"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "started"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "completed"))
        item = self.tableWidgetDataBase.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "records"))
        self.menuConfig.setTitle(_translate("MainWindow", "Config"))
        self.menustyle.setTitle(_translate("MainWindow", "style"))
        self.menuplot.setTitle(_translate("MainWindow", "plot"))
        self.menuLiveplot.setTitle(_translate("MainWindow", "Liveplot"))
        self.actionqb.setText(_translate("MainWindow", "qb"))
        self.actionqdark.setText(_translate("MainWindow", "qdark"))
        self.actionwhite.setText(_translate("MainWindow", "white"))
        self.actionDefaultPath.setText(_translate("MainWindow", "Select default folder"))
        self.actionAxisLabelColor.setText(_translate("MainWindow", "Axis label color"))
        self.actionAxisTickLabelsColor.setText(_translate("MainWindow", "Axis tick labels color"))
        self.actionTitleColor.setText(_translate("MainWindow", "Title color"))
        self.actionAxisTicksColor.setText(_translate("MainWindow", "Axis ticks color"))
        self.actionFontsize.setText(_translate("MainWindow", "Font-size"))
        self.actionColormap.setText(_translate("MainWindow", "colormap"))
        self.actionqt_material.setText(_translate("MainWindow", "qt-material"))
        self.actionSelectDatabase.setText(_translate("MainWindow", "Select database"))
        self.actionOpenliveplot.setText(_translate("MainWindow", "Open liveplot"))
from ..ui.qtable_widget_key import QTableWidgetKey
from ..ui.snapshot_q_line_edit import SnapshotQLineEdit
from ..ui.snapshot_view_tree import SnapshotViewTree
