# PyQt5 Video player
#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QGridLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QSpacerItem
from PyQt5.QtGui import QIcon
import sys


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("ONI Player")

        self.colorMediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.depthMediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        colorVideoWidget = QVideoWidget()
        depthVideoWidget = QVideoWidget()

        # spacers for control panel
        self.leftSpacerItem = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.rightSpacerItem  = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.backButton = QPushButton()
        self.backButton.setEnabled(False)
        self.backButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backButton.clicked.connect(self.previous_frame)
        self.backButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.next_frame)
        self.playButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.forwardButton = QPushButton()
        self.forwardButton.setEnabled(False)
        self.forwardButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forwardButton.clicked.connect(self.play)
        self.forwardButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        self.colorLabel = QLabel('Color stream')
        self.depthLabel = QLabel('Depth stream')

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
        #fileMenu.addAction(newAction)
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

        videoLayout = QGridLayout()
        videoLayout.setSpacing(10)
        videoLayout.addWidget(self.colorLabel, 0, 0, Qt.AlignCenter)
        videoLayout.addWidget(self.depthLabel, 0, 1, Qt.AlignCenter)
        videoLayout.addWidget(colorVideoWidget, 1, 0)
        videoLayout.addWidget(depthVideoWidget, 1, 1)


        layout = QVBoxLayout()
        layout.addLayout(videoLayout)
        layout.addWidget(self.positionSlider)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.colorMediaPlayer.setVideoOutput(colorVideoWidget)
        self.colorMediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.colorMediaPlayer.positionChanged.connect(self.positionChanged)
        self.colorMediaPlayer.durationChanged.connect(self.durationChanged)
        self.colorMediaPlayer.error.connect(self.handleError)

        self.depthMediaPlayer.setVideoOutput(depthVideoWidget)
        self.depthMediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.depthMediaPlayer.positionChanged.connect(self.positionChanged)
        self.depthMediaPlayer.durationChanged.connect(self.durationChanged)
        self.depthMediaPlayer.error.connect(self.handleError)

    def one_frame_step(cur_pos, direction):
        pass

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.colorMediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.depthMediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.colorMediaPlayer.state() == QMediaPlayer.PlayingState:
            self.colorMediaPlayer.pause()
            self.depthMediaPlayer.pause()
        else:
            self.colorMediaPlayer.play()
            self.depthMediaPlayer.play()

    def previous_frame(self):

        if self.colorMediaPlayer.state() == QMediaPlayer.PausedState:
            self.colorMediaPlayer.pause()
            self.depthMediaPlayer.pause()


    def mediaStateChanged(self, state):
        if self.colorMediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.colorMediaPlayer.setPosition(position)
        self.depthMediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.colorMediaPlayer.errorString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(960, 540)
    player.show()
    sys.exit(app.exec_())