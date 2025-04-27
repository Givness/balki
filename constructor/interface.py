from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from structures import *
import sys

def smart_str(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class GridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.scale = 40.0
        self.min_scale = 1.0
        self.max_scale = 1000.0
        self.offset = QPointF(0, 0)
        self.last_mouse_pos = None
        self.coord_limit = 10000
        self.margin = 40
        self.beam = Beam()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        center = QPointF(self.width() / 2, self.height() / 2) + self.offset

        left = -(center.x()) / self.scale
        right = (self.width() - center.x()) / self.scale
        top = -(center.y()) / self.scale
        bottom = (self.height() - center.y()) / self.scale

        # Адаптивный шаг
        steps = [0.01, 0.02, 0.05,
                 0.1, 0.2, 0.5,
                 1, 2, 5,
                 10, 20, 50,
                 100, 200, 500, 1000]
        sub_steps = 4
        spacing = 1.0
        sub_spacing = 0.2
        for step in steps:
            if step * self.scale >= 60:
                spacing = step
                sub_spacing = step / sub_steps
                break

        # Дополнительная сетка
        sub_grid_pen = QPen(QColor(220, 220, 220))
        sub_grid_pen.setWidth(0)
        painter.setPen(sub_grid_pen)

        x = int(left // sub_spacing) * sub_spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                painter.drawLine(int(px), 0, int(px), self.height())
            x += sub_spacing

        y = int(top // sub_spacing) * sub_spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                painter.drawLine(0, int(py), self.width(), int(py))
            y += sub_spacing

        # Основная сетка
        grid_pen = QPen(Qt.GlobalColor.lightGray)
        grid_pen.setWidth(2)
        painter.setPen(grid_pen)

        x = int(left // spacing) * spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                painter.drawLine(int(px), 0, int(px), self.height())
            x += spacing

        y = int(top // spacing) * spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                painter.drawLine(0, int(py), self.width(), int(py))
            y += spacing

        # Оси
        axis_pen = QPen(Qt.GlobalColor.black)
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)

        if -self.coord_limit <= 0 <= self.coord_limit:
            painter.drawLine(int(center.x()), 0, int(center.x()), self.height())
            painter.drawLine(0, int(center.y()), self.width(), int(center.y()))

        # Подписи
        painter.setPen(Qt.GlobalColor.black)
        font = QFont("Arial", 9)
        painter.setFont(font)

        # Подписи по X
        x = int(left // spacing) * spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                if 0 < px < self.width():
                    text = str(int(x) if spacing >= 1 else f"{x:.2f}")
                    
                    # Фон текста
                    metrics = painter.fontMetrics()
                    text_rect = metrics.tightBoundingRect(text)
                    text_rect.adjust(-1, -1, 1, 1)

                    painter.setBrush(Qt.GlobalColor.white)
                    painter.setPen(Qt.PenStyle.NoPen)

                    text_rect.moveCenter(QPoint(int(px), 6))
                    painter.drawRect(text_rect)

                    text_rect.moveCenter(QPoint(int(px), self.height() - 6))
                    painter.drawRect(text_rect)

                    #Тексты
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(Qt.GlobalColor.black)

                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

                    text_rect.moveCenter(QPoint(int(px), 6))
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            x += spacing

        # Подписи по Y
        y = int(top // spacing) * spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                if 0 < py < self.height():
                    text = str(int(-y) if spacing >= 1 else f"{-y:.2f}")

                    # Фон текста
                    metrics = painter.fontMetrics()
                    text_rect = metrics.tightBoundingRect(text)
                    text_rect.adjust(-1, -1, 1, 1)

                    painter.setBrush(Qt.GlobalColor.white)
                    painter.setPen(Qt.PenStyle.NoPen)

                    text_rect.moveCenter(QPoint(6, int(py)))
                    painter.drawRect(text_rect)

                    text_rect.moveCenter(QPoint(self.width() - 6, int(py)))
                    painter.drawRect(text_rect)

                    # Тексты
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(Qt.GlobalColor.black)

                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

                    text_rect.moveCenter(QPoint(6, int(py)))
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            y += spacing

        # Балки
        count = 1
        self.segment_mapping = {}
        for segment in self.beam.get_segments():
            self.segment_mapping[count] = segment

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            x1 = center.x() + segment.node1.x * self.scale
            y1 = center.y() - segment.node1.y * self.scale
            x2 = center.x() + segment.node2.x * self.scale
            y2 = center.y() - segment.node2.y * self.scale
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Силы
            for force in segment.forces:
                x = x1 + force.node1_dist * (x2 - x1) / segment.length
                y = y1 + force.node1_dist * (y2 - y1) / segment.length

                size_y = int(2 * self.scale)
                size_y = 35 if size_y > 35 else size_y
                size_x = size_y * 2

                painter.save()
                painter.translate(x, y)
                painter.rotate(-force.angle)
                painter.drawPixmap(-size_x, -size_y // 2, size_x, size_y, QPixmap("arrow.svg"))
                painter.restore()

                text = f'{force.value} Н'
            
                metrics = painter.fontMetrics()
                text_rect = metrics.tightBoundingRect(text)
                text_x = int(x - size_x * math.cos(math.radians(force.angle)))
                text_y = int(y + size_x * math.sin(math.radians(force.angle)))
                text_rect.moveTopLeft(QPoint(text_x, text_y))
                text_rect.adjust(-1, -1, 1, 1)

                painter.setBrush(Qt.GlobalColor.white)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(text_rect)
                    
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            # Моменты
            for torque in segment.torques:
                x = x1 + torque.node1_dist * (x2 - x1) / segment.length
                y = y1 + torque.node1_dist * (y2 - y1) / segment.length

                size = int(2 * self.scale)
                size = 35 if size > 35 else size

                painter.save()
                painter.translate(x, y)
                if torque.value < 0:
                    painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("circlearrow.svg").transformed(QTransform().scale(-1, 1)))
                else:
                    painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("circlearrow.svg"))
                painter.restore()

                text = f'{torque.value} Нм'
            
                metrics = painter.fontMetrics()
                text_rect = metrics.tightBoundingRect(text)
                text_x = int(x + size // 2)
                text_y = int(y - size // 2)
                text_rect.moveTopLeft(QPoint(text_x, text_y))
                text_rect.adjust(-1, -1, 1, 1)

                painter.setBrush(Qt.GlobalColor.white)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(text_rect)
                    
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

            # Номера балок
            text = str(count)
            
            metrics = painter.fontMetrics()
            text_rect = metrics.tightBoundingRect(text)
            rect_x = int((x1 + x2) / 2) if y1 == y2 else int((x1 + x2) / 2 - text_rect.width() - 1)
            rect_y = int((y1 + y2) / 2) if x1 == x2 else int((y1 + y2) / 2 - text_rect.height() - 1)
            text_rect.moveCenter(QPoint(rect_x, rect_y))
            text_rect.adjust(-1, -1, 1, 1)

            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(text_rect)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
            count += 1

        # Узлы
        node_radius = 2  # Радиус узлов
        count = 1
        self.node_mapping = {}
        for node in self.beam.get_nodes():
            self.node_mapping[count] = node

            x = center.x() + node.x * self.scale
            y = center.y() - node.y * self.scale

            # Опора
            if node.support:
                size = int(2 * self.scale)
                size = 35 if size > 35 else size
                painter.save()
                painter.translate(x, y)
                painter.rotate(-node.support.angle)
                                
                image = None
                match node.support.get_type:
                    case Support.Type.FIXED: image = QPixmap("support0.svg")
                    case Support.Type.PINNED: image = QPixmap("support1.svg")
                    case Support.Type.ROLLER: image = QPixmap("support2.svg")
                painter.drawPixmap(-size // 2, -size // 2 + 12, size, size, image)
                painter.restore()

            # Узел
            painter.setBrush(QColor(0, 0, 255, 127))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), node_radius * 2, node_radius * 2)

            # Номера узлов
            text = str(count)
            
            metrics = painter.fontMetrics()
            text_rect = metrics.tightBoundingRect(text)
            text_rect.moveCenter(QPoint(int(x), int(y - metrics.height() / 2 - node_radius - 1)))
            text_rect.adjust(-1, -1, 0, 1)

            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(text_rect)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(Qt.GlobalColor.blue)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
            count += 1

    def resetOffset(self):
        self.offset = QPointF(0, 0)
        self.update()

    def wheelEvent(self, event):
        zoom_in_factor = 1.1
        zoom_out_factor = 0.9

        old_scale = self.scale
        if event.angleDelta().y() > 0:
            self.scale *= zoom_in_factor
        else:
            self.scale *= zoom_out_factor

        self.scale = max(self.min_scale, min(self.max_scale, self.scale))

        mouse_pos = event.position()
        center = QPointF(self.width() / 2, self.height() / 2)
        mouse_delta = mouse_pos - center - self.offset
        self.offset -= mouse_delta * (self.scale / old_scale - 1)

        self.clamp_offset()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.position()
            self.clamp_offset()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    def clamp_offset(self):
        half_w = self.width() / 2
        half_h = self.height() / 2

        max_offset_x = self.coord_limit * self.scale - half_w
        max_offset_y = self.coord_limit * self.scale - half_h

        self.offset.setX(max(-max_offset_x, min(max_offset_x, self.offset.x())))
        self.offset.setY(max(-max_offset_y, min(max_offset_y, self.offset.y())))


class BeamSegmentDialog(QDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить сегмент балки")

        self.inputs = [QLineEdit() for _ in range(4)]
        labels = ["X1:", "Y1:", "X2:", "Y2:"]
        layout = QVBoxLayout()

        for label, input_field in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(input_field)
            layout.addLayout(row)

        if default_values:
            for field, value in zip(self.inputs, default_values):
                field.setText(smart_str(value))

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)
        self._data = None

    def validate_and_accept(self):
        try:
            values = [float(field.text()) for field in self.inputs]
            self._data = values
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

    def get_data(self):
        return self._data


class SupportDialog(QDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить опору")

        self.inputs = [QLineEdit(), QComboBox(), QLineEdit()]
        self.inputs[1].addItems(["Жёсткая заделка", "Шарнирно-неподвижная", "Шарнирно-подвижная"])
        labels = ["Номер узла:", "Тип опоры:", "Угол:"]

        layout = QVBoxLayout()

        for label, input_field in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(input_field)
            layout.addLayout(row)

        if default_values:
            self.inputs[0].setText(smart_str(default_values[0]))
            self.inputs[1].setCurrentIndex(default_values[1])
            self.inputs[2].setText(smart_str(default_values[2]))

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)
        self._data = None

    def validate_and_accept(self):
        try:
            node_number = int(self.inputs[0].text())
            support_type = self.inputs[1].currentIndex()
            angle = float(self.inputs[2].text())
            self._data = (node_number, support_type, angle)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

    def get_data(self):
        return self._data


class ForceDialog(QDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить силу")

        self.inputs = [QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(), QCheckBox(), QLineEdit()]
        labels = ["Номер балки:", "Отступ:", "Значение:", "Угол:", "Распределённая:", "Длина"]
        layout = QVBoxLayout()

        for label, input_field in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(input_field)
            layout.addLayout(row)

        self.inputs[4].stateChanged.connect(self.toggle_length_field)
        self.toggle_length_field()

        if default_values:
            self.inputs[0].setText(smart_str(default_values[0]))
            self.inputs[1].setText(smart_str(default_values[1]))
            self.inputs[2].setText(smart_str(default_values[2]))
            self.inputs[3].setText(smart_str(default_values[3]))
            if default_values[4] != 1:
                self.inputs[4].setChecked(True)
                self.inputs[5].setText(smart_str(default_values[4]))
            else:
                self.inputs[4].setChecked(False)

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)
        self._data = None

    def toggle_length_field(self):
        if self.inputs[4].isChecked():
            self.inputs[5].setEnabled(True)
        else:
            self.inputs[5].setEnabled(False)

    def validate_and_accept(self):
        try:
            segment_number = int(self.inputs[0].text())
            offset = float(self.inputs[1].text())
            value = float(self.inputs[2].text())
            angle = float(self.inputs[3].text())
            length = float(self.inputs[5].text()) if self.inputs[4].isChecked() else 1

            self._data = (segment_number, offset, value, angle, length)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

    def get_data(self):
        return self._data


class TorqueDialog(QDialog):
    def __init__(self, parent=None, default_values=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить момент")

        self.inputs = [QLineEdit(), QLineEdit(), QLineEdit()]
        labels = ["Номер балки:", "Отступ:", "Значение:"]
        layout = QVBoxLayout()

        for label, input_field in zip(labels, self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(input_field)
            layout.addLayout(row)

        if default_values:
            for field, value in zip(self.inputs, default_values):
                field.setText(smart_str(value))

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.validate_and_accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)
        self._data = None

    def validate_and_accept(self):
        try:
            segment_number = int(self.inputs[0].text())
            offset = float(self.inputs[1].text())
            value = float(self.inputs[2].text())

            self._data = (segment_number, offset, value)
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Ошибка!", str(IncorrectInputError("Введены некорректные данные!")))

    def get_data(self):
        return self._data
    

class SolveDialog(QDialog):
    def __init__(self, answers: dict[str: float], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить момент")

        self.inputs = [QLineEdit() for _ in answers]
        labels = ["Ответ:" for _ in answers]
        layout = QVBoxLayout()

        for answer, input in zip(answers.items(), self.inputs):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{answer[0]}:"))
            row.addWidget(input)
            input.setReadOnly(True)
            input.setText(str(answer[1]))
            layout.addLayout(row)

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(self.accept)
        layout.addWidget(button_ok)

        self.setLayout(layout)


class DialogManager:
    def __init__(self, grid_widget):
        self.grid_widget = grid_widget

    def open_segment_dialog(self):
        default_data = None
        while True:
            dialog = BeamSegmentDialog(None, default_data)
            if not dialog.exec():
                break
            try:
                x1, y1, x2, y2 = dialog.get_data()
                node1 = Node(x1, y1)
                node2 = Node(x2, y2)
                self.grid_widget.beam.add_segment(BeamSegment(node1, node2))
                self.grid_widget.update()
                break
            except Exception as e:
                QMessageBox.critical(None, "Ошибка!", str(e))
                default_data = dialog.get_data()

    def open_support_dialog(self):
        default_data = None
        while True:
            dialog = SupportDialog(None, default_data)
            if not dialog.exec():
                break
            try:
                node_number, support_type_index, angle = dialog.get_data()
                if node_number < 1 or node_number not in self.grid_widget.node_mapping:
                    raise NonExistentError(f"Узел {node_number} не существует!")
                ufx = support_type_index != Support.Type.ROLLER.value
                ut = support_type_index == Support.Type.FIXED.value
                self.grid_widget.node_mapping[node_number].add_support(Support(angle, 0, 0, 0, ufx, True, ut))
                self.grid_widget.update()
                break
            except Exception as e:
                QMessageBox.critical(None, "Ошибка!", str(e))
                default_data = dialog.get_data()

    def open_force_dialog(self):
        default_data = None
        while True:
            dialog = ForceDialog(None, default_data)
            if not dialog.exec():
                break
            try:
                segment_number, offset, value, angle, length = dialog.get_data()
                if segment_number not in self.grid_widget.segment_mapping:
                    raise NonExistentError(f"Сегмент балки {segment_number} не существует!")
                force = Force(value, angle, offset, length, False)
                self.grid_widget.segment_mapping[segment_number].add_force(force)
                self.grid_widget.update()
                break
            except Exception as e:
                QMessageBox.critical(None, "Ошибка!", str(e))
                default_data = dialog.get_data()

    def open_torque_dialog(self):
        default_data = None
        while True:
            dialog = TorqueDialog(None, default_data)
            if not dialog.exec():
                break
            try:
                segment_number, offset, value = dialog.get_data()
                if segment_number not in self.grid_widget.segment_mapping:
                    raise NonExistentError(f"Сегмент балки {segment_number} не существует!")
                torque = Torque(value, offset, False)
                self.grid_widget.segment_mapping[segment_number].add_torque(torque)
                self.grid_widget.update()
                break
            except Exception as e:
                QMessageBox.critical(None, "Ошибка!", str(e))
                default_data = dialog.get_data()

    def open_solve_dialog(self):
        solve = {}
        try:
            solve = self.grid_widget.beam.solve()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка!", str(e))
            return

        dialog = QDialog()
        dialog.setWindowTitle("Результаты расчёта")
        layout = QVBoxLayout()

        for key, value in solve.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            result_field = QLineEdit(str(value))
            result_field.setReadOnly(True)
            row.addWidget(result_field)
            layout.addLayout(row)

        button_ok = QPushButton("ОК")
        button_ok.clicked.connect(dialog.accept)
        layout.addWidget(button_ok)

        dialog.setLayout(layout)
        dialog.exec()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.grid_widget = GridWidget()
        self.dialogs = DialogManager(self.grid_widget)

        left_layout = QVBoxLayout()

        add_segment_button = QPushButton("Добавить сегмент балки")
        add_segment_button.clicked.connect(self.dialogs.open_segment_dialog)
        left_layout.addWidget(add_segment_button)

        add_support_button = QPushButton("Добавить опору")
        add_support_button.clicked.connect(self.dialogs.open_support_dialog)
        left_layout.addWidget(add_support_button)

        add_force_button = QPushButton("Добавить силу")
        add_force_button.clicked.connect(self.dialogs.open_force_dialog)
        left_layout.addWidget(add_force_button)

        add_torque_button = QPushButton("Добавить момент")
        add_torque_button.clicked.connect(self.dialogs.open_torque_dialog)
        left_layout.addWidget(add_torque_button)

        solve_button = QPushButton("Посчитать")
        solve_button.clicked.connect(self.dialogs.open_solve_dialog)
        left_layout.addWidget(solve_button)

        reset_offset_button = QPushButton("Вернуться к началу координат")
        reset_offset_button.clicked.connect(self.grid_widget.resetOffset)
        left_layout.addWidget(reset_offset_button)

        clear_button = QPushButton("Очистить поле")
        clear_button.clicked.connect(self.clear_button_message)
        left_layout.addWidget(clear_button)

        save_button = QPushButton("Сохранить балку")
        save_button.clicked.connect(self.save_beam)
        left_layout.addWidget(save_button)

        load_button = QPushButton("Загрузить балку")
        load_button.clicked.connect(self.load_beam)
        left_layout.addWidget(load_button)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(200)

        layout.addWidget(left_widget)
        layout.addWidget(self.grid_widget)
        self.setLayout(layout)

    def save_beam(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить балку",
            "",
            "Файлы балки (*.bm);;Все файлы (*)"
        )
        if filename:
            if not filename.endswith(".bm"):
                filename += ".bm"
            try:
                self.grid_widget.beam.save_to_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", str(e))

    def load_beam(self):
        if len(self.grid_widget.beam.graph.nodes) > 0:
            box = QMessageBox(self)
            box.setWindowTitle("Подтверждение загрузки")
            box.setText("Вы хотите загрузить другую балку? Текущая балка будет удалена.")
            button_yes = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
            button_no = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            box.exec()

            if box.clickedButton() != button_yes:
                return  # Пользователь отказался

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить балку",
            "",
            "Файлы балки (*.bm);;Все файлы (*)"
        )
        if not filename:
            return  # Пользователь отменил выбор файла

        try:
            self.clear_field()
            self.grid_widget.beam = Beam.load_from_file(filename)
            self.grid_widget.update()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def clear_button_message(self):
        box = QMessageBox(self)
        box.setWindowTitle("Подтверждение очистки")
        box.setText("Вы уверены, что хотите очистить поле?")
        button_yes = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        button_no = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        box.exec()

        if box.clickedButton() == button_yes:
            self.clear_field()

    def clear_field(self):
        for cls in [Force, Torque, Support, Node, BeamSegment, Beam]:
            cls._next_id = 1
            cls._used_ids.clear()

        self.grid_widget.beam = Beam()
        self.grid_widget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.setWindowTitle("Определение реакций опор")
    window.show()
    sys.exit(app.exec())
