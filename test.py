import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class CWidget(QWidget):

    def __init__(self):
        super().__init__()
        # for PyQt embedding
        self.fig = plt.Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        self.timeInterval = 0.1

        self.x = np.arange(0, 2*np.pi, self.timeInterval)
        self.y = np.sin(self.x)


        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)

        self.setLayout(vbox)
        self.setGeometry(0,0,800,400)


        self.ax = self.fig.add_subplot(1,1,1)

        self.line, = self.ax.plot(self.x, self.y)


        self.ani = animation.FuncAnimation(self.fig, self.animate, init_func=self.initPlot, interval=100, blit=False, save_count=50)
        self.canvas.draw()

        self.show()

    def initPlot(self):
        self.line.set_ydata([np.nan]*len(self.x))
        return self.line,

    def animate(self, i):
        self.line.set_ydata(np.sin(self.x + i * self.timeInterval))
        return self.line,

    def closeEvent(self, e):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())
