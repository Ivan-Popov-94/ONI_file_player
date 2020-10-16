#!/usr/bin/env python

import os
import sys

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle,
                             QVBoxLayout, QGridLayout, QAction, QDialog,
                             QMainWindow, QWidget, QSpacerItem, QFrame)
from PyQt5.QtGui import QIcon
import ffms2
from oni2avi import oni_converter

# from progress_bar import ProgressBar as pb


# class ProgressBar(QDialog, pb):
#     def __init__(self, fn=None):
#         QDialog.__init__(self)
#         self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
#         self.setupUi(self, fn)

# def progress_bar(self, fn):
#     progress_bar_inst = ProgressBar(fn)
#     progress_bar_inst.show()
#     progress_bar_inst.exec()


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("ONI Player")
        self.setWindowIcon(QIcon('images/play.png'))
        self.vsource = None

        class MediaPlayer(QMediaPlayer):
            def __init__(self, parent=None, flags=QMediaPlayer.VideoSurface):
                super(MediaPlayer, self).__init__(parent)
                self.parent = parent

            def frame_step(self, direction):
                frames = list(map(round, self.parent.vsource.track.timecodes))
                if 0 < self.position() < max(frames):
                    dif = [abs(self.position() - x) for x in frames]
                    self.setPosition(frames[dif.index(min(dif)) + direction])


        self.colorMediaPlayer = MediaPlayer(parent=self)
        self.depthMediaPlayer = MediaPlayer(parent=self)

        self.colorVideoWidget = QVideoWidget()
        self.depthVideoWidget = QVideoWidget()

        # spacers for control panel
        self.leftSpacerItem = QSpacerItem(10, 10,
                                          QSizePolicy.Expanding,
                                          QSizePolicy.Minimum)
        self.rightSpacerItem = QSpacerItem(10, 10,
                                           QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)

        # buttom for control panel
        self.backButton = QPushButton()
        self.backButton.setEnabled(False)
        self.backButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backButton.clicked.connect(lambda: self.prev_next_frame(-1))
        self.backButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)
        self.playButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.forwardButton = QPushButton()
        self.forwardButton.setEnabled(False)
        self.forwardButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forwardButton.clicked.connect(lambda: self.prev_next_frame(1))
        self.forwardButton.setSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)
        self.colorLabel = QLabel('Color stream')
        self.depthLabel = QLabel('Depth stream')
        self.hframe = QFrame(self)
        self.hframe.setFrameShape(QFrame.HLine)
        self.hframe.setFrameShadow(QFrame.Raised)
        # self.hframe.setLineWidth(1)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)  # png!!!
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.addSpacerItem(self.leftSpacerItem)
        controlLayout.addWidget(self.backButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.forwardButton)
        controlLayout.addSpacerItem(self.rightSpacerItem)

        self.videoLayout = QGridLayout()
        self.videoLayout.setSpacing(10)
        self.videoLayout.addWidget(self.colorLabel, 0, 0, Qt.AlignCenter)
        self.videoLayout.addWidget(self.depthLabel, 0, 1, Qt.AlignCenter)
        self.videoLayout.addWidget(self.colorVideoWidget, 1, 0)
        self.videoLayout.addWidget(self.depthVideoWidget, 1, 1)

        layout = QVBoxLayout()
        layout.addLayout(self.videoLayout)
        layout.addWidget(self.positionSlider)
        layout.addLayout(controlLayout)
        layout.addWidget(self.hframe)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.colorMediaPlayer.setVideoOutput(self.colorVideoWidget)
        self.colorMediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.colorMediaPlayer.positionChanged.connect(self.positionChanged)
        self.colorMediaPlayer.durationChanged.connect(self.durationChanged)
        self.colorMediaPlayer.error.connect(self.handleError)

        self.depthMediaPlayer.setVideoOutput(self.depthVideoWidget)
        self.depthMediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.depthMediaPlayer.positionChanged.connect(self.positionChanged)
        self.depthMediaPlayer.durationChanged.connect(self.durationChanged)
        self.depthMediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open oni file", '',
                                                  '*.oni', QDir.homePath())
        self.errorLabel.setText("Processing of ONI file. Please wait.")
        path_to_color_avi = os.path.join(os.getcwd(), 'color.avi')
        path_to_depth_avi = os.path.join(os.getcwd(), 'depth.avi')
        if fileName != '':
            print(self.errorLabel.text())
            oni_converter(fileName)
            if os.path.isfile('color.avi') and os.path.isfile('depth.avi'):
                self.errorLabel.setText("ONI file has been processed successfully.")
            self.colorMediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(path_to_color_avi)))
            self.depthMediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(path_to_depth_avi)))
            self.playButton.setEnabled(True)
            self.vsource = ffms2.VideoSource('color.avi')

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.colorMediaPlayer.state() == QMediaPlayer.PlayingState:
            self.colorMediaPlayer.pause()
            self.depthMediaPlayer.pause()
        else:
            self.errorLabel.setText('')
            self.colorMediaPlayer.play()
            self.depthMediaPlayer.play()

    def prev_next_frame(self, direction):
        if self.colorMediaPlayer.state() == QMediaPlayer.PausedState:
            self.colorMediaPlayer.frame_step(direction)
            self.depthMediaPlayer.frame_step(direction)

    def mediaStateChanged(self, state):
        if self.colorMediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
            self.backButton.setEnabled(False)
            self.forwardButton.setEnabled(False)
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            self.backButton.setEnabled(True)
            self.forwardButton.setEnabled(True)

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.colorMediaPlayer.setPosition(position)
        self.depthMediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: "
                                + self.colorMediaPlayer.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(960, 540)
    player.show()
    if os.path.isfile('color.avi'):
        os.remove('color.avi')
    if os.path.isfile('depth.avi'):
        os.remove('depth.avi')
    sys.exit(app.exec_())


