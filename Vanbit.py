#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import signal
import platform
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import multiprocessing
import subprocess

mizogg = f'''

 Made by Mizogg Version 2.1  © mizogg.co.uk 2018 - 2023      {f"[>] Running with Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"}

'''

class CommandThread(QThread):
    commandOutput = pyqtSignal(str)
    commandFinished = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        self.process = subprocess.Popen(self.command, shell=True)
        self.process.communicate()
        self.commandFinished.emit(self.process.returncode)


class ConsoleWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.consoleOutput = QPlainTextEdit(self)
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setFont(QFont("Courier"))
        self.layout.addWidget(self.consoleOutput)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.consoleOutput.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Change here


    @pyqtSlot(int)
    def update_console_style(self, index):
        if index == 1:
            self.consoleOutput.setStyleSheet("background-color: white; color: purple; font-size: 18px;")
        elif index == 2:
            self.consoleOutput.setStyleSheet("background-color: black; color: green; font-size: 18px;")
        elif index == 3:
            self.consoleOutput.setStyleSheet("background-color: blue; color: white; font-size: 18px;")

    @pyqtSlot(str)
    def append_output(self, output):
        self.consoleOutput.appendPlainText(output)

class KnightRiderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.position = 0
        self.direction = 1
        self.lightWidth = 20
        self.lightHeight = 10
        self.lightSpacing = 10
        self.lightColor = QColor(255, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def startAnimation(self):
        self.timer.start(5)

    def stopAnimation(self):
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(12):
            lightX = self.position + i * (self.lightWidth + self.lightSpacing)
            lightRect = QRect(lightX, 0, self.lightWidth, self.lightHeight)
            painter.setBrush(self.lightColor)
            painter.drawRoundedRect(lightRect, 5, 5)

    def update(self):
        self.position += self.direction
        if self.position <= 0 or self.position >= self.width() - self.lightWidth - self.lightSpacing:
            self.direction *= -1
        self.repaint()


class CommandThreaddisplay(QThread):
    commandOutput = pyqtSignal(str)
    commandFinished = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        if self.command.startswith('python'):
            script = self.command[7:].strip()  # Remove the "python " prefix and leading/trailing spaces
            if script.endswith('.py'):
                self.process = subprocess.Popen(
                    self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                    universal_newlines=True
                )
                for line in self.process.stdout:
                    output = line.strip()
                    self.commandOutput.emit(output)
                self.process.stdout.close()
                self.commandFinished.emit(self.process.wait())
            else:
                try:
                    result = eval(self.command[7:])  # Remove the "python " prefix and evaluate the code
                    self.commandOutput.emit(str(result))
                    self.commandFinished.emit(0)
                except Exception as e:
                    self.commandOutput.emit(str(e))
                    self.commandFinished.emit(1)
        else:
            self.process = subprocess.Popen(
                self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                universal_newlines=True
            )
            for line in self.process.stdout:
                output = line.strip()
                self.commandOutput.emit(output)
            self.process.stdout.close()
            self.commandFinished.emit(self.process.wait())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vanbit GUI @ github.com/Mizogg")
        self.setGeometry(50, 50, 1700, 500)
        self.process = None
        self.commandThread = None
        self.scanning = False
        self.initUI()

    def initUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        cpu_count = multiprocessing.cpu_count()
        self.setStyleSheet(
            """
            QMainWindow {
                background-image: url(mizogg.png);
                background-repeat: no-repeat;
                background-position: top center;
            }
            """
        )
        main_layout = QVBoxLayout()
        # Welcome Label
        welcome_label = QLabel("GUI Crypto Scanner")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: purple;")
        main_layout.addWidget(welcome_label)

        # Line 1 Label
        line1_label = QLabel("Sequence VanBitCrakcenS1 & Random VBCRandom")
        line1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line1_label.setStyleSheet("font-size: 18px; font-weight: bold; color: purple;")
        main_layout.addWidget(line1_label)

        # Line 2 Label
        line2_label = QLabel("The Sequence means that this specific version is geared towards covering ranges, not doing any random mode.\nRandom 100% random within Range")
        line2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line2_label.setStyleSheet("font-size: 14px; color: blue;")
        main_layout.addWidget(line2_label)


        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout(self.centralWidget)

        left_layout = QVBoxLayout()
        self.layout.addLayout(left_layout)
        left_layout.addLayout(main_layout)
        self.threadGroupBox = QGroupBox(self)
        self.threadGroupBox.setTitle("Thread Configuration: Start in Random/Sequence, Stop, or Open in New Window")
        self.threadGroupBox.setStyleSheet("QGroupBox { border: 3px solid green; padding: 15px; }")
        self.threadLayout = QHBoxLayout(self.threadGroupBox)
        self.threadLabel = QLabel("Number of CPUs:", self)
        self.threadLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.threadLayout.addWidget(self.threadLabel)
        self.threadComboBox = QComboBox()
        for i in range(1, cpu_count + 1):
            self.threadComboBox.addItem(str(i))
        self.threadComboBox.setCurrentIndex(2)
        self.threadLayout.addWidget(self.threadComboBox)
        self.randomButton = QPushButton("Random", self)
        self.randomButton.setStyleSheet("color: green;")
        self.randomButton.clicked.connect(self.run_VBCRandom)
        self.threadLayout.addWidget(self.randomButton)
        self.sequenceButton = QPushButton("Sequence", self)
        self.sequenceButton.setStyleSheet("color: blue;")
        self.sequenceButton.clicked.connect(self.run_VanBitCrakcenS1)
        self.threadLayout.addWidget(self.sequenceButton)
        self.stopButton = QPushButton("Stop scanning", self)
        self.stopButton.setStyleSheet("color: red;")
        self.stopButton.clicked.connect(self.stop_exe)
        self.threadLayout.addWidget(self.stopButton)
        self.NEWButton = QPushButton("New window", self)
        self.NEWButton.setStyleSheet("color: orange;")
        self.NEWButton.clicked.connect(self.new_window)
        self.threadLayout.addWidget(self.NEWButton)
        left_layout.addWidget(self.threadGroupBox)

        self.prefixGroupBox = QGroupBox(self)
        self.prefixGroupBox.setTitle("Vanity/Single Address Search Config")
        self.prefixGroupBox.setStyleSheet("QGroupBox { border: 3px solid red; padding: 15px; }")
        prefixLayout = QHBoxLayout(self.prefixGroupBox)
        self.prefixLabel = QLabel("Prefix to search:", self)
        prefixLayout.addWidget(self.prefixLabel)
        self.prefixLineEdit = QLineEdit("13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so", self)
        prefixLayout.addWidget(self.prefixLineEdit)
        self.caseSensitiveCheckBox = QCheckBox("Case Sensitive Search", self)
        prefixLayout.addWidget(self.caseSensitiveCheckBox)
        self.stopCheckBox = QCheckBox("Stop When All Prefixes are Found (Leave blank for Loop)", self)
        prefixLayout.addWidget(self.stopCheckBox)
        left_layout.addWidget(self.prefixGroupBox)

        # Address Configuration
        self.addGroupBox = QGroupBox(self)
        self.addGroupBox.setTitle("Address Configuration: Uncompressed or Both")
        self.addGroupBox.setStyleSheet("QGroupBox { border: 3px solid red; padding: 15px; }")
        self.addressLayout = QHBoxLayout(self.addGroupBox)
        self.uncompressedCheckBox = QCheckBox(
            "Search Uncompressed Addresses (Leave blank for Compressed)", self
        )
        self.addressLayout.addWidget(self.uncompressedCheckBox)
        self.bothAddressesCheckBox = QCheckBox(
            "Search Both Uncompressed or Compressed Addresses (Will not work if Uncompressed Box Tick)", self
        )
        self.addressLayout.addWidget(self.bothAddressesCheckBox)
        left_layout.addWidget(self.addGroupBox)

        # GPU Configuration
        self.gpuGroupBox = QGroupBox(self)
        self.gpuGroupBox.setTitle("GPU Configuration")
        self.gpuGroupBox.setStyleSheet("QGroupBox { border: 3px solid red; padding: 15px; }")
        self.gpuLayout = QHBoxLayout(self.gpuGroupBox)
        self.GPUButton = QPushButton("Check GPU", self.gpuGroupBox)
        self.GPUButton.setStyleSheet("color: blue;")
        self.GPUButton.clicked.connect(self.list_if_gpu)
        self.gpuLayout.addWidget(self.GPUButton)
        self.GPUvsCPUButton = QPushButton("GPU VS CPU", self.gpuGroupBox)
        self.GPUvsCPUButton.setStyleSheet("color: blue;")
        self.GPUvsCPUButton.clicked.connect(self.list_if_gpu)
        self.gpuLayout.addWidget(self.GPUvsCPUButton)
        self.gpuCheckBox = QCheckBox("Enable GPU Calculation (Make sure to Set/fill List of GPU(s) section)", self.gpuGroupBox)
        self.gpuLayout.addWidget(self.gpuCheckBox)
        self.gpuIdLabel = QLabel("List of GPU(s) to use:", self.gpuGroupBox)
        self.gpuLayout.addWidget(self.gpuIdLabel)
        self.gpuIdLineEdit = QLineEdit("0", self.gpuGroupBox)
        self.gpuIdLineEdit.setPlaceholderText('0, 1, 2')
        self.gpuLayout.addWidget(self.gpuIdLineEdit)
        self.gridSizeLabel = QLabel("Grid Size:", self)
        self.gpuLayout.addWidget(self.gridSizeLabel)
        self.gridSize_choice = QComboBox()
        self.gridSize_choice.addItems(['8', '16', '32', '64', '128', '256', '512', '1024'])
        self.gpuLayout.addWidget(self.gridSize_choice)
        left_layout.addWidget(self.gpuGroupBox)

        # File Configuration
        self.outputFileGroupBox = QGroupBox(self)
        self.outputFileGroupBox.setTitle("File Configuration")
        self.outputFileGroupBox.setStyleSheet("QGroupBox { border: 3px solid green; padding: 15px; }")
        outputFileLayout = QHBoxLayout(self.outputFileGroupBox)
        self.outputFileLabel = QLabel("Output File:", self)
        outputFileLayout.addWidget(self.outputFileLabel)
        self.outputFileLineEdit = QLineEdit("found.txt", self)
        self.outputFileLineEdit.setPlaceholderText('Name for your file Found/Winner Results example = found.txt')
        outputFileLayout.addWidget(self.outputFileLineEdit)
        self.inputFileLabel = QLabel("Input File:", self)
        outputFileLayout.addWidget(self.inputFileLabel)
        self.inputFileLineEdit = QLineEdit(self)
        self.inputFileLineEdit.setPlaceholderText('Click browse to find your BTC database')
        outputFileLayout.addWidget(self.inputFileLineEdit)
        self.inputFileButton = QPushButton("Browse", self)
        self.inputFileButton.setStyleSheet("color: green;")
        self.inputFileButton.clicked.connect(self.browse_input_file)
        outputFileLayout.addWidget(self.inputFileButton)
        left_layout.addWidget(self.outputFileGroupBox)

        # Key Space Configuration
        self.keyspaceGroupBox = QGroupBox(self)
        self.keyspaceGroupBox.setTitle("Key Space Configuration")
        self.keyspaceGroupBox.setStyleSheet("QGroupBox { border: 3px solid green; padding: 15px; }")
        keyspaceLayout = QHBoxLayout(self.keyspaceGroupBox)
        self.keyspaceLabel = QLabel("Key Space:", self)
        keyspaceLayout.addWidget(self.keyspaceLabel)
        self.keyspaceLineEdit = QLineEdit("20000000000000000:3ffffffffffffffff", self)
        self.keyspaceLineEdit.setPlaceholderText('Example range for 66 = 20000000000000000:3ffffffffffffffff')
        keyspaceLayout.addWidget(self.keyspaceLineEdit)
        left_layout.addWidget(self.keyspaceGroupBox)

        # Custom Command Input
        self.customGroupBox = QGroupBox(self)
        self.customGroupBox.setTitle("Custom CMD Input")
        self.customGroupBox.setStyleSheet("QGroupBox { border: 3px solid green; padding: 15px; }")
        self.customLayout = QHBoxLayout(self.customGroupBox)
        self.customLabel = QLabel("Custom CMD here:", self)
        self.customLayout.addWidget(self.customLabel)
        self.inputCustomEdit = QLineEdit(self)
        self.inputCustomEdit.setPlaceholderText('VBCRandom -t 4 -o found.txt --keyspace 1:3ffffffffffffffff -i btc.txt')
        self.inputCustomEdit.returnPressed.connect(self.custom_start1)
        self.customLayout.addWidget(self.inputCustomEdit)
        self.customButton = QPushButton("Custom CMD Input", self)
        self.customButton.setStyleSheet("color: green;")
        self.customButton.clicked.connect(self.custom_start)
        self.customLayout.addWidget(self.customButton)
        self.customButton1 = QPushButton("Execute Python Commands", self)
        self.customButton1.setStyleSheet("color: Purple;")
        self.customButton1.clicked.connect(self.custom_start1)
        self.customLayout.addWidget(self.customButton1)
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setStyleSheet("color: red;")
        self.stopButton.clicked.connect(self.stop_exe)
        self.customLayout.addWidget(self.stopButton)
        left_layout.addWidget(self.customGroupBox)
        
        self.knightRiderWidget = KnightRiderWidget(self)
        self.knightRiderWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.knightRiderWidget.setMinimumHeight(20)
        self.knightRiderLayout = QHBoxLayout()
        self.knightRiderLayout.setContentsMargins(0, 15, 0, 0)
        self.knightRiderLayout.addWidget(self.knightRiderWidget)

        self.knightRiderGroupBox = QGroupBox(self)
        self.knightRiderGroupBox.setTitle("Running Process ")
        self.knightRiderGroupBox.setStyleSheet("QGroupBox { border: 3px solid red; padding: 15px; }")
        self.knightRiderGroupBox.setLayout(self.knightRiderLayout)
        mizogg_label = QLabel(mizogg, self)
        mizogg_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        mizogg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.knightRiderGroupBox)
        left_layout.addWidget(mizogg_label)

        # Right Side Layout
        right_layout = QVBoxLayout()
        self.layout.addLayout(right_layout)
        self.colourGroupBox = QGroupBox(self)
        self.colourGroupBox.setStyleSheet("QGroupBox { border: 2px solid purple; padding: 13px; }")
        self.colourWidget = QWidget()
        self.colourLayout = QHBoxLayout(self.colourWidget)
        self.colorlable = QLabel(
            '<html><b><font color="purple" size="2">Pick Console Colour</font></b></html>', self
        )
        self.colorlable.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.colorComboBox = QComboBox(self)
        self.colorComboBox.addItem("Pick Console Colour")
        self.colorComboBox.addItem("Option 1: White Background, Purple Text")
        self.colorComboBox.addItem("Option 2: Black Background, Green Text")
        self.colorComboBox.addItem("Option 3: Blue Background, White Text")
        self.colorComboBox.currentIndexChanged.connect(self.update_console_style)
        self.colourLayout.addWidget(self.colorlable)
        self.colourLayout.addWidget(self.colorComboBox)
        self.colourGroupBox.setLayout(self.colourLayout)
        # Console Window
        self.consoleWindow = ConsoleWindow(self)
        right_layout.addWidget(self.consoleWindow)
        right_layout.addWidget(self.colourGroupBox)

        self.layout.setStretchFactor(left_layout, 2)
        self.layout.setStretchFactor(right_layout, 4)
        # Set the central widget
        self.setCentralWidget(self.centralWidget)


    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Text Files (*.txt);;Binary Files (*.bin);;All Files (*.*)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            file_name = os.path.basename(file_path)
            self.inputFileLineEdit.setText(file_name)
            self.prefixLineEdit.clear()

    def run_VBCRandom(self):
        command = self.construct_command("VBCRandom")
        self.execute_command(command)

    def run_VanBitCrakcenS1(self):
        command = self.construct_command("VanBitCrakcenS1")
        self.execute_command(command)

    def list_if_gpu(self):
        sender = self.sender()

        if sender == self.GPUButton:
            command = "VBCRandom -l"
            self.consoleWindow.append_output(command)
            self.run(command)
        elif sender == self.GPUvsCPUButton:
            message_error = 'GPUvsCPU Test. \n This will cause the program to not responed for 10-20sec While Testing. \n Please wait after closing this screen.'
            self.pop_Result(message_error)
            command = "VBCRandom -check"
            self.consoleWindow.append_output(command)
            self.run(command)
    
    def run(self, command):
        self.process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in self.process.stdout:
            output = line.strip()
            self.consoleWindow.append_output(output)
        self.process.stdout.close()
    
    def custom_start(self):
        command = self.inputCustomEdit.text().strip()
        self.execute_command(command)
        self.consoleWindow.append_output(command)
    
    def custom_start1(self):
        command = self.inputCustomEdit.text().strip()
        self.execute_command1(command)

    def execute_command1(self, command):
        if self.scanning:
            return

        self.scanning = True
        self.knightRiderWidget.startAnimation()

        if self.commandThread and self.commandThread.isRunning():
            self.commandThread.terminate()

        self.consoleWindow.append_output(f"> {command}")
        self.consoleWindow.append_output("")

        self.commandThread = CommandThreaddisplay(command)
        self.commandThread.commandOutput.connect(self.consoleWindow.append_output)
        self.commandThread.commandFinished.connect(self.command_finished)
        self.commandThread.start()

        self.timer.start(100)
        
    def construct_command(self, mode):
        thread_count = int(self.threadComboBox.currentText())
        self.thread_count = thread_count
        command = f"{mode} -t {self.thread_count}"

        if self.caseSensitiveCheckBox.isChecked():
            command += " -c"

        if self.gpuCheckBox.isChecked():
            command += " -gpu"
            gpu_ids = self.gpuIdLineEdit.text().strip()
            command += f" -gpuId {gpu_ids}"
            gpu_grid = self.gridSize_choice.currentText()
            command += f" -g {gpu_grid}"

        if self.stopCheckBox.isChecked():
            command += " -stop"

        if self.uncompressedCheckBox.isChecked():
            command += " -u"

        if self.bothAddressesCheckBox.isChecked():
            command += " -b"

        output_file = self.outputFileLineEdit.text().strip()
        if output_file:
            command += f" -o {output_file}"

        keyspace = self.keyspaceLineEdit.text().strip()
        if keyspace:
            command += f" --keyspace {keyspace}"

        input_file = self.inputFileLineEdit.text().strip()
        if input_file:
            command += f" -i {input_file}"
        else:
            prefix = self.prefixLineEdit.text().strip()
            if prefix:
               command += f" {prefix}"
        self.consoleWindow.append_output(command)
        return command
    
    def stop_exe(self):
        if self.commandThread and self.commandThread.isRunning():
            if platform.system() == "Windows":
                subprocess.Popen(["taskkill", "/F", "/T", "/PID", str(self.commandThread.process.pid)])
            else:
                os.killpg(os.getpgid(self.commandThread.process.pid), signal.SIGTERM)
            
            self.timer.stop()
            self.scanning = False
            self.knightRiderWidget.stopAnimation()
            returncode = 'Closed'
            self.command_finished(returncode)
            
    def pop_Result(self, message_error):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(message_error)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @pyqtSlot()
    def new_window(self):
        python_cmd = f'start cmd /c "{sys.executable}" Vanbit.py'
        subprocess.Popen(python_cmd, shell=True)

    @pyqtSlot()
    def execute_command(self, command):
        if self.scanning:
            return

        self.scanning = True
        self.knightRiderWidget.startAnimation()

        if self.commandThread and self.commandThread.isRunning():
            self.commandThread.terminate()

        self.commandThread = CommandThread(command)
        self.commandThread.commandOutput.connect(self.consoleWindow.append_output)
        self.commandThread.commandFinished.connect(self.command_finished)
        self.commandThread.start()

        self.timer.start(100)
    
    @pyqtSlot(int)
    def command_finished(self, returncode):
        self.timer.stop()
        self.scanning = False
        self.knightRiderWidget.stopAnimation()

        if returncode == 0:
            finish_scan = "Command execution finished successfully"
            self.consoleWindow.append_output(finish_scan)
        elif returncode == 'Closed':
            finish_scan = "Process has been stopped by the user"
            self.consoleWindow.append_output(finish_scan)
        else:
            error_scan = "Command execution failed"
            self.consoleWindow.append_output(error_scan)

    @pyqtSlot(int)
    def update_console_style(self, index):
        self.consoleWindow.update_console_style(index)
        
    def update_gui(self):
        QApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
