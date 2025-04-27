from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QMessageBox
)
from structures import *

def smart_str(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

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