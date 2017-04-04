from PySide import QtGui, QtCore
from .common import SourceEditorDialog
import sources


class SourcesListDock(QtGui.QDockWidget):

    def __init__(self, sandbox, *args, **kwargs):
        QtGui.QDockWidget.__init__(self, 'Sources', *args, **kwargs)
        self.sandbox = sandbox

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        sources = SourcesList(sandbox)
        sources_add_menu = SourcesAddButton(sandbox)

        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)
        self.widget.layout().addWidget(sources)
        self.widget.layout().addWidget(sources_add_menu)

        self.setWidget(self.widget)


class SourcesAddButton(QtGui.QToolButton):

    class SourcesAddMenu(QtGui.QMenu):

        def __init__(self, sandbox, *args, **kwargs):
            QtGui.QMenu.__init__(self, *args, **kwargs)
            self.sandbox = sandbox

            def addSource(source):
                self.sandbox.addSource(source)

            for src in sources.__sources__:
                self.addAction(
                    '%s' % src.__represents__,
                    lambda: addSource(src.getRepresentedSource(sandbox)))

    def __init__(self, sandbox, parent=None):
        QtGui.QToolButton.__init__(self, parent)

        menu = self.SourcesAddMenu(sandbox, self, 'Availables sources')

        self.setText('Add Source')
        self.setMenu(menu)

        self.setIcon(self.style().standardPixmap(
                     QtGui.QStyle.SP_FileDialogDetailedView))
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)


class SourcesList(QtGui.QListView):

    class SourceItemDelegate(QtGui.QStyledItemDelegate):

        def paint(self, painter, option, index):
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)

            style = QtGui.QApplication.style() if options.widget is None\
                else options.widget.style()

            doc = QtGui.QTextDocument()
            doc.setHtml(options.text)

            options.text = ""
            style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

            ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

            textRect = style.subElementRect(
                QtGui.QStyle.SE_ItemViewItemText, options, options.widget)
            painter.save()
            painter.translate(textRect.topLeft())
            painter.setClipRect(textRect.translated(-textRect.topLeft()))
            doc.documentLayout().draw(painter, ctx)

            painter.restore()

        def sizeHint(self, option, index):
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)

            doc = QtGui.QTextDocument()
            doc.setHtml(options.text)
            doc.setTextWidth(options.rect.width())
            return QtCore.QSize(doc.idealWidth(), doc.size().height())

    class SourceContextMenu(QtGui.QMenu):

        def __init__(self, sandbox, idx, *args, **kwargs):
            QtGui.QMenu.__init__(self, *args, **kwargs)
            self.sandbox = sandbox
            self.idx = idx

            def removeSource():
                self.sandbox.sources.removeSource(self.idx)

            def editSource():
                editing_dialog = self.sandbox.sources.data(
                    self.idx, SourceEditorDialog)
                editing_dialog.show()


            print self.style().standardPixmap(
                    QtGui.QStyle.SP_DialogCloseButton)
            self.addAction(
                self.style().standardPixmap(
                    QtGui.QStyle.SP_DialogCloseButton),
                'Edit', editSource)
            self.addAction(
                self.style().standardPixmap(
                    QtGui.QStyle.SP_DialogCloseButton),
                'Remove', removeSource)

    def __init__(self, sandbox, *args, **kwargs):
        QtGui.QListView.__init__(self, *args, **kwargs)
        self.sandbox = sandbox
        self.setModel(sandbox.sources)
        self.setItemDelegate(self.SourceItemDelegate())
        self.setAlternatingRowColors(True)
        sandbox.sources.setSelectionModel(self.selectionModel())

    def edit(self, idx, trigger, event):
        if trigger == QtGui.QAbstractItemView.EditTrigger.DoubleClicked or\
          trigger == QtGui.QAbstractItemView.EditTrigger.SelectedClicked:
            editing_dialog = idx.data(SourceEditorDialog)
            editing_dialog.show()
        return False

    @QtCore.Slot()
    def contextMenuEvent(self, event):
        idx = self.indexAt(event.pos())
        menu = self.SourceContextMenu(self.sandbox, idx, self)
        menu.popup(event.globalPos())
