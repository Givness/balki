import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtSvgWidgets import QSvgWidget
from structures import *

def random_color():
    return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class CoordinatePlane(QFrame):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.setStyleSheet("background-color: white;")
        self.scale_factor = 1
        self.lines = []
        self.point_numbers = {}
        self.squares = []
        self.next_segment_number = 1
        self.next_point_number = 1
        self.nodes = []
        self.beam_segments = []

    def change_scale(self, factor):
        self.scale_factor *= factor
        self.scale_factor = max(0.5, min(2.0, self.scale_factor))
        self.update()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            width, height = self.width(), self.height()
            center_x, center_y = width // 2, height // 2
            step = int(40 * self.scale_factor)
            grid_pen = QPen(Qt.GlobalColor.lightGray)
            grid_pen.setWidth(1)
            painter.setPen(grid_pen)

            for x in range(center_x % step, width, step):
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 5, center_y + 15, f"{(x - center_x) // step}")
            for x in range(center_x % step, -1, -step):
                painter.drawLine(x, 0, x, height)
                painter.drawText(x + 5, center_y + 15, f"{(x - center_x) // step}")

            for y in range(center_y % step, height, step):
                painter.drawLine(0, y, width, y)
                painter.drawText(center_x + 5, y - 5, f"{(center_y - y) // step}")
            for y in range(center_y % step, -1, -step):
                painter.drawLine(0, y, width, y)
                painter.drawText(center_x + 5, y - 5, f"{(center_y - y) // step}")

            axis_pen = QPen(Qt.GlobalColor.black)
            axis_pen.setWidth(2)
            painter.setPen(axis_pen)

            painter.drawLine(center_x, 0, center_x, height)
            painter.drawLine(0, center_y, width, center_y)

            for i, line in enumerate(self.lines, start=1):
                x1, y1, x2, y2, color = line
                x1_pixel = center_x + int(x1 * 40 * self.scale_factor)
                y1_pixel = center_y - int(y1 * 40 * self.scale_factor)
                x2_pixel = center_x + int(x2 * 40 * self.scale_factor)
                y2_pixel = center_y - int(y2 * 40 * self.scale_factor)
                line_pen = QPen(color)
                line_pen.setWidth(2)
                painter.setPen(line_pen)
                painter.drawLine(x1_pixel, y1_pixel, x2_pixel, y2_pixel)
                painter.setBrush(color)
                painter.drawText(x1_pixel + (x2_pixel - x1_pixel) // 2 - 5, y1_pixel + (y2_pixel - y1_pixel) // 2 - 5, str(i))
                painter.drawEllipse(x1_pixel - 4, y1_pixel - 4, 8, 8)
                painter.drawEllipse(x2_pixel - 4, y2_pixel - 4, 8, 8)
                painter.setPen(Qt.GlobalColor.black)
                for (x, y), num in self.point_numbers.items():
                    x_pixel = center_x + int(x * 40 * self.scale_factor)
                    y_pixel = center_y - int(y * 40 * self.scale_factor)
                    painter.drawText(x_pixel + 5, y_pixel - 5, str(num))

            for x, y, color, angle in self.squares:
                x_pixel = center_x + int(x * 40 * self.scale_factor)
                y_pixel = center_y - int(y * 40 * self.scale_factor)
                size = int(30 * self.scale_factor)
                painter.setBrush(color)
                painter.setPen(Qt.GlobalColor.black)
                painter.save()
                painter.translate(x_pixel, y_pixel)
                painter.rotate(-angle + 90)
                painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("support.svg"))
                painter.restore()
        except Exception as e:
            print(f"Error in paintEvent: {e}")

    def draw_line(self, x1, y1, x2, y2):
        try:
            color = random_color()
            self.next_segment_number += 1
            self.lines.append((x1, y1, x2, y2, color))
            for x, y in [(x1, y1), (x2, y2)]:
                if (x, y) not in self.point_numbers:
                    self.point_numbers[(x, y)] = self.next_point_number
                    self.next_point_number += 1
                    self.nodes.append(Node(x, y))

            self.beam_segments.append(BeamSegment(self.nodes[self.point_numbers[(x1, y1)] - 1], self.nodes[self.point_numbers[(x2, y2)] - 1]))
            self.update()
        except Exception as e:
            print(f"Error in draw_line: {e}")

    def add_square(self, point_number, angle):
        for (x, y), num in self.point_numbers.items():
            if num == point_number:
                self.squares.append((x, y, random_color(), angle))
                self.update()
                break

    def save_as_image(self, file_path):
        pixmap = self.grab()
        pixmap.save(file_path, "JPG")

    def draw_vector(self, x1, y1, x2, y2):
        color = random_color()
        self.lines.append((x1, y1, x2, y2, color))
        arrow_size = 0.2
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return
        dx, dy = dx / length, dy / length
        left_x = x2 - dx * 0.3 + dy * arrow_size
        left_y = y2 - dy * 0.3 - dx * arrow_size
        right_x = x2 - dx * 0.3 - dy * arrow_size
        right_y = y2 - dy * 0.3 + dx * arrow_size
        self.lines.append((left_x, left_y, x2, y2, color))
        self.lines.append((right_x, right_y, x2, y2, color))
        self.update()

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Введите координаты")
        self.setFixedSize(300, 120)
        layout = QFormLayout(self)
        self.x1_input = QLineEdit(self)
        self.y1_input = QLineEdit(self)
        self.x2_input = QLineEdit(self)
        self.y2_input = QLineEdit(self)
        layout.addRow("X1:", self.x1_input)
        layout.addRow("Y1:", self.y1_input)
        layout.addRow("X2:", self.x2_input)
        layout.addRow("Y2:", self.y2_input)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_coordinates(self):
        return (
            float(self.x1_input.text()), float(self.y1_input.text()),
            float(self.x2_input.text()), float(self.y2_input.text())
        )

class VectorInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Введите координаты вектора")
        self.setFixedSize(250, 150)

        layout = QFormLayout(self)

        self.segment_number = QLineEdit(self)
        self.value = QLineEdit(self)
        self.angle = QLineEdit(self)
        self.offset= QLineEdit(self)

        layout.addRow("Сегмент:", self.segment_number)
        layout.addRow("Значение:", self.value)
        layout.addRow("Угол:", self.angle)
        layout.addRow("Отступ:", self.offset)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_coordinates(self):
        segment_number = int(self.segment_number.text())
        value = float(self.value.text())
        angle = float(self.angle.text())
        offset = float(self.offset.text())
        return segment_number, value, angle, offset

class SquareInputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление квадрата")
        self.setFixedSize(250, 180)

        layout = QFormLayout(self)

        self.point_input = QLineEdit(self)
        self.angle_input = QLineEdit(self)
        self.v_force_input = QLineEdit(self)
        self.h_force_input = QLineEdit(self)

        layout.addRow("Номер точки:", self.point_input)
        layout.addRow("Угол (градусы):", self.angle_input)
        layout.addRow("Вертикальная реакция:", self.v_force_input)
        layout.addRow("Горизонтальная реакция:", self.h_force_input)


        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def get_data(self):
        point_number = int(self.point_input.text())
        angle = float(self.angle_input.text())
        v_force = float(self.v_force_input.text())
        h_force = float(self.h_force_input.text())
        return point_number, angle, v_force, h_force

class AnswerDialog(QDialog):
    def __init__(self, text):
        super().__init__()
        self.setWindowTitle("Ответ")
        self.setFixedSize(250, 180)

        layout = QFormLayout(self)
        self.message = QLabel(text)
        layout.addRow(self.message)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализатор")
        self.setGeometry(100, 100, 800, 500)

        main_layout = QHBoxLayout(self)

        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        label = QLabel("Меню")
        button1 = QPushButton("Создание балки")
        button2 = QPushButton("Создание опоры")
        vector_button = QPushButton("Создание вектора")
        solve_button = QPushButton("Вычислить")
        
        button1.clicked.connect(self.on_button1_click)
        button2.clicked.connect(self.on_button2_click)
        vector_button.clicked.connect(self.on_vector_button_click)
        solve_button.clicked.connect(self.on_solve_button_click)

        menu_layout.addWidget(label)
        menu_layout.addWidget(button1)
        menu_layout.addWidget(button2)
        menu_layout.addWidget(vector_button)
        menu_layout.addWidget(solve_button)
        zoom_in_button = QPushButton("Увеличить +")
        zoom_out_button = QPushButton("Уменьшить -")

        zoom_in_button.clicked.connect(lambda: self.plane.change_scale(1.2))
        zoom_out_button.clicked.connect(lambda: self.plane.change_scale(0.8))

        menu_layout.addWidget(zoom_in_button)
        menu_layout.addWidget(zoom_out_button)

        menu_layout.addStretch()

        self.plane = CoordinatePlane()

        main_layout.addLayout(menu_layout, 1)
        main_layout.addWidget(self.plane, 3)

        self.setLayout(main_layout)

        save_button = QPushButton("Сохранить изображение")
        save_button.clicked.connect(self.save_image)
        menu_layout.addWidget(save_button)

    def on_button1_click(self):
        dialog = InputDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            x1, y1, x2, y2 = dialog.get_coordinates()
            self.plane.draw_line(x1, y1, x2, y2)

    def on_button2_click(self):
        dialog = SquareInputDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            point_number, angle, v_force, h_force = dialog.get_data()
            if point_number < self.plane.next_point_number:
                self.plane.nodes[point_number - 1].add_support(Support(angle, v_force, h_force, 0))
                self.plane.add_square(point_number, angle)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "JPEG Files (*.jpg);;All Files (*)")
        if file_path:
            self.plane.save_as_image(file_path)

    def on_vector_button_click(self):
        dialog = VectorInputDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            segment_number, value, angle, offset = dialog.get_coordinates()
            s = self.plane.beam_segments[segment_number - 1]
            x1 = (s.node1.x + offset * (s.node2.x - s.node1.x) / s.length)
            y1 = (s.node1.y + offset * (s.node2.y - s.node1.y) / s.length)
            x2 = x1 + np.cos(np.deg2rad(angle)) * 2
            y2 = y1 + np.sin(np.deg2rad(angle)) * 2
            s.forces.append(Force(value, angle, offset))
            self.plane.draw_vector(x2, y2, x1, y1)

    def on_solve_button_click(self):
        self.plane.beam = Beam(self.plane.beam_segments)
        print(self.plane.beam.solve())
        dialog = AnswerDialog(self.plane.beam.solve())
        dialog.exec()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())