from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QTransform
from PyQt6.QtCore import Qt, QPointF, QPoint
from structures import *

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
                painter.drawPixmap(-size_x, -size_y // 2, size_x, size_y, QPixmap("images\\arrow.svg"))
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
                    painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("images\\circlearrow.svg").transformed(QTransform().scale(-1, 1)))
                else:
                    painter.drawPixmap(-size // 2, -size // 2, size, size, QPixmap("images\\circlearrow.svg"))
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
                    case Support.Type.FIXED: image = QPixmap("images\\support0.svg")
                    case Support.Type.PINNED: image = QPixmap("images\\support1.svg")
                    case Support.Type.ROLLER: image = QPixmap("images\\support2.svg")
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