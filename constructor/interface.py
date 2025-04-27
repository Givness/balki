from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from structures import *
from grid import GridWidget
from dialogs import DialogManager


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