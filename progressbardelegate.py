# -*- coding: UTF-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QStyledItemDelegate, QStyle

from statmodel import StatModel

ProgressColor = (0xFF0000, 0xFC2700, 0xF75400, 0xF66B00, 0xEEC300,
                 0xE9FF00, 0xD2FF00, 0xBAFF00, 0x76FF00, 0x89FF00, 0x64FF00)


class ProgressBarDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):

        if index.data(BatchModel.RoleTier) == 2:
            super().paint(painter, option, index)
            return

        option.widget.style().drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter)

        painter.save()

        mouseOver = option.state & QStyle.State_MouseOver
        cellSelected = option.state & QStyle.State_Selected

        if mouseOver:
            br = QBrush(QColor(208, 224, 240, 150))
            option.widget.style().drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter)
            painter.fillRect(option.rect, br)

        r = option.rect
        painter.setPen(QColor(Qt.lightGray))

        r.adjust(+1, +1, -3, -2)
        painter.drawRect(r)

        value, total = index.data(BatchModel.RoleProgress)
        progress = 0
        if total != 0:
            progress = value / total

        ci = 0
        if progress != 0:
            ci = int(progress * 10)

        pbr = r.adjusted(+1, +1, 0, 0)

        px = progress * pbr.width()

        painter.fillRect(pbr.adjusted(0, 0, -pbr.width() + px, 0), QBrush(QColor(ProgressColor[ci])))

        f = painter.font()
        f.setPointSize(f.pointSize() * 0.8)
        painter.setFont(f)
        string = f'{value}/{total}'
        fm = painter.fontMetrics()
        trect = fm.boundingRect(string)
        trect.moveTo(r.x() + (r.width() - trect.width()) / 2, r.y() + 1)

        if cellSelected:
            painter.setPen(QColor(Qt.white))
            painter.drawText(trect, 0, string)
            painter.setPen(QColor(Qt.black))
            painter.drawText(trect.adjusted(-1, 0, -1, 0), 0, string)
        else:
            painter.setPen(QColor(Qt.black))
            painter.drawText(trect, 0, string)

        painter.restore()

