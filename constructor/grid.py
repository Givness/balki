from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QTransform
from PyQt6.QtCore import Qt, QPointF, QPoint
from structures import *
import math

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
        bounds = self.calculate_bounds(center)
        spacing, sub_spacing = self.calculate_spacing()

        self.draw_grid(painter, center, bounds, spacing, sub_spacing)
        self.draw_axes(painter, center)
        self.draw_labels(painter, center, bounds, spacing)
        self.draw_beams(painter, center)
        self.draw_forces_and_torques(painter, center)
        self.draw_nodes(painter, center)

    def calculate_bounds(self, center):
        left = -(center.x()) / self.scale
        right = (self.width() - center.x()) / self.scale
        top = -(center.y()) / self.scale
        bottom = (self.height() - center.y()) / self.scale
        return left, right, top, bottom

    def calculate_spacing(self):
        steps = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
        sub_steps = 4
        for step in steps:
            if step * self.scale >= 60:
                return step, step / sub_steps
        return 1.0, 0.2

    def draw_grid(self, painter, center, bounds, spacing, sub_spacing):
        left, right, top, bottom = bounds

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

    def draw_axes(self, painter, center):
        axis_pen = QPen(Qt.GlobalColor.black)
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)

        if -self.coord_limit <= 0 <= self.coord_limit:
            painter.drawLine(int(center.x()), 0, int(center.x()), self.height())
            painter.drawLine(0, int(center.y()), self.width(), int(center.y()))

    def draw_labels(self, painter, center, bounds, spacing):
        left, right, top, bottom = bounds
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", 9))

        x = int(left // spacing) * spacing
        while x <= right:
            if -self.coord_limit <= x <= self.coord_limit:
                px = center.x() + x * self.scale
                if 0 < px < self.width():
                    self.draw_text(painter, int(px), 6, str(int(x) if spacing >= 1 else f"{x:.2f}"))
                    self.draw_text(painter, int(px), self.height() - 6, str(int(x) if spacing >= 1 else f"{x:.2f}"))
            x += spacing

        y = int(top // spacing) * spacing
        while y <= bottom:
            if -self.coord_limit <= y <= self.coord_limit:
                py = center.y() + y * self.scale
                if 0 < py < self.height():
                    self.draw_text(painter, 6, int(py), str(int(-y) if spacing >= 1 else f"{-y:.2f}"))
                    self.draw_text(painter, self.width() - 6, int(py), str(int(-y) if spacing >= 1 else f"{-y:.2f}"))
            y += spacing

    def draw_text(self, painter, x, y, text):
        metrics = painter.fontMetrics()
        text_rect = metrics.tightBoundingRect(text)
        text_rect.adjust(-1, -1, 1, 1)
        text_rect.moveCenter(QPoint(x, y))

        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(text_rect)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def draw_beams(self, painter, center):
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

            count += 1

    def draw_forces_and_torques(self, painter, center):
        for segment in self.beam.get_segments():
            x1 = center.x() + segment.node1.x * self.scale
            y1 = center.y() - segment.node1.y * self.scale
            x2 = center.x() + segment.node2.x * self.scale
            y2 = center.y() - segment.node2.y * self.scale

            for force in segment.forces:
                self.draw_force(painter, x1, y1, x2, y2, segment.length, force)
            for torque in segment.torques:
                self.draw_torque(painter, x1, y1, x2, y2, segment.length, torque)

    def draw_force(self, painter, x1, y1, x2, y2, length, force):
        x = x1 + force.node1_dist * (x2 - x1) / length
        y = y1 + force.node1_dist * (y2 - y1) / length

        size_y = int(2 * self.scale)
        size_y = 35 if size_y > 35 else size_y
        size_x = size_y * 2

        painter.save()
        painter.translate(x, y)
        painter.rotate(-force.angle)
        painter.drawPixmap(-size_x, -size_y // 2, size_x, size_y, QPixmap("images\\arrow.svg"))
        painter.restore()

        text = f'{force.value} Н'
        self.draw_annotation(painter, x, y, size_x, force.angle, text)

    def draw_torque(self, painter, x1, y1, x2, y2, length, torque):
        x = x1 + torque.node1_dist * (x2 - x1) / length
        y = y1 + torque.node1_dist * (y2 - y1) / length

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
        self.draw_annotation(painter, x, y, size, 0, text)

    def draw_annotation(self, painter, x, y, size, angle, text):
        metrics = painter.fontMetrics()
        text_rect = metrics.tightBoundingRect(text)
        text_x = int(x - size * math.cos(math.radians(angle)))
        text_y = int(y + size * math.sin(math.radians(angle)))
        text_rect.moveTopLeft(QPoint(text_x, text_y))
        text_rect.adjust(-1, -1, 1, 1)

        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(text_rect)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def draw_nodes(self, painter, center):
        node_radius = 2
        count = 1
        self.node_mapping = {}
        for node in self.beam.get_nodes():
            self.node_mapping[count] = node

            x = center.x() + node.x * self.scale
            y = center.y() - node.y * self.scale

            if node.support:
                size = int(2 * self.scale)
                size = 35 if size > 35 else size
                painter.save()
                painter.translate(x, y)
                painter.rotate(-node.support.angle)

                match node.support.support_type:
                    case Support.Type.FIXED: image = QPixmap("images\\support0.svg")
                    case Support.Type.PINNED: image = QPixmap("images\\support1.svg")
                    case Support.Type.ROLLER: image = QPixmap("images\\support2.svg")
                painter.drawPixmap(-size // 2, -size // 2 + 12, size, size, image)
                painter.restore()

            node_brush = QColor(0, 0, 255, 127)
            node_text_pen = Qt.GlobalColor.blue
            if node.hinge:
                size = int(2 * self.scale)
                size = 35 if size > 35 else size
                painter.drawPixmap(int(x - size // 2), int(y - size // 2), size, size, QPixmap("images\\hinge.svg"))
                node_text_pen = Qt.GlobalColor.red
                node_brush = QColor(255, 0, 0, 127)

            painter.setBrush(node_brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), node_radius * 2, node_radius * 2)

            text = str(count)
            metrics = painter.fontMetrics()
            text_rect = metrics.tightBoundingRect(text)
            text_rect.moveCenter(QPoint(int(x), int(y - metrics.height() / 2 - node_radius - 1)))
            text_rect.adjust(-1, -1, 0, 1)

            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(text_rect)

            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(node_text_pen)
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