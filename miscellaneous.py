from PyQt5.QtCore import QCoreApplication, Qt, QDate
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QVBoxLayout, QLineEdit, QComboBox, QDateEdit, QPushButton


# noinspection PyUnresolvedReferences,PyArgumentList
class SpecialCheckbox(QWidget):
    def __init__(self, row, column, val, parent):
        super().__init__()
        self.parent: CustomSearchField = parent
        self.row = row
        self.skip = False
        checkbox_layout = QHBoxLayout(self)
        checkbox = QCheckBox("", checked=(val if val is not None else False))
        checkbox.stateChanged.connect(
            lambda: self.checkbox_swapped(row, column, self.checkbox.isChecked(), self.skip))
        checkbox_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
        self.setLayout(checkbox_layout)
        self.checkbox = checkbox


    # only implemented for main table and hardcoded indexes
    def checkbox_swapped(self, row, col, val, skip):
        if skip: return
        rows = list(dict.fromkeys([idx.row() for idx in self.parent.main_table.selectedIndexes()]))

        if row not in rows:
            self.save_row_checkboxes(row, col)
        else:
            for r in rows:
                if not r == row:
                    self.parent.main_table.cellWidget(r, col).skip = True
                    self.parent.main_table.cellWidget(r, col).checkbox.setChecked(val)
                    self.parent.main_table.cellWidget(r, col).skip = False
                self.save_row_checkboxes(r, col)

        # error w terori nie trzeba refreshowac
        self.parent.refresh_table()

    def save_row_checkboxes(self, rowId=-1, col=-1):
        if rowId == -1 or col == -1: return

        val = []

        for i in range(6, 12):
            val.append(self.parent.main_table.cellWidget(rowId, i).checkbox.isChecked())

        if col == 31:  val[3] = self.parent.main_table.cellWidget(rowId, col).checkbox.isChecked()
        if col == 32:  val[4] = self.parent.main_table.cellWidget(rowId, col).checkbox.isChecked()
        f = 1 if val[1] else (0 if not val[1] else -1)
        g = 1 if val[2] else (0 if not val[2] else -1)
        # error need to be added
        z = 0

        state = 'DO WINDYKACJI'
        if f == 1:
            state = 'OK'
        elif g == 1:
            if z == 0:
                state = "SKANY - KLIENT NIE WYMAGA ORYGINAŁÓW"
            else:
                state = "SKANY - ORGINAŁY"
        val.append(state)
        val.append(self.parent.main_table.item(rowId, 0).text())
        val.append(self.parent.main_table.item(rowId, 1).text())
        val.append(self.parent.main_table.item(rowId, 3).text())
        val.append(self.parent.main_table.item(rowId, 4).text())

        print(val)
        self.parent.maria.save_selection_checkboxes(val)




# noinspection PyUnresolvedReferences,PyArgumentList
class CustomSearchField(QWidget):
    def __init__(self, function, emptyText, type):
        super().__init__()
        self.type = type
        self.linked = []
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom)
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget = None
        if type == 'text':
            search_bar = QLineEdit()
            search_bar.setPlaceholderText(emptyText)
            search_bar.textChanged.connect(function)
            search_bar.textChanged.connect(self.update_linked)
            layout.addWidget(search_bar)
            self.widget = search_bar
        elif type == 'bool':
            combobox = QComboBox()
            combobox.addItem('')
            combobox.addItem('Tak')
            combobox.addItem('Nie')
            combobox.currentTextChanged.connect(self.update_linked)
            combobox.currentTextChanged.connect(function)
            layout.addWidget(combobox)
            self.widget = combobox
        elif type == 'status':
            combobox = QComboBox()
            combobox.addItem('')
            combobox.addItem('DO WINDYKACJI')
            combobox.addItem('OK')
            combobox.addItem('SKANY - KLIENT NIE WYMAGA ORYGINAŁÓW')
            combobox.currentTextChanged.connect(function)
            combobox.currentTextChanged.connect(self.update_linked)
            layout.addWidget(combobox)
            self.widget = combobox

        elif type == 'date':
            def _on_user_data_set_start():
                if self.widget[1].isHidden():
                    self.widget[1].setDate(self.widget[0].date())
                    self.widget[1].show()

                if self.widget[1].date() < self.widget[0].date():
                    self.widget[1].setDate(self.widget[0].date())
                QCoreApplication.processEvents()
                function()

            def _selecting_date(placeholder):
                placeholder.hide()
                self.widget[0].blockSignals(True)
                self.widget[0].setDate(QDate.currentDate())
                self.widget[0].blockSignals(False)

                self.widget[0].show()
                self.widget[0].setFocus()
                self.widget[2].show()
                function()

            def _cancel_date(placeholder):
                self.widget[0].hide()
                self.widget[1].hide()
                self.widget[2].hide()
                placeholder.show()

            placeholder_edit = QLineEdit()
            placeholder_edit.setPlaceholderText("Select a date...")
            placeholder_edit.setReadOnly(True)
            placeholder_edit.setFrame(False)
            placeholder_edit.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder_edit)
            placeholder_edit.mousePressEvent = lambda e: _selecting_date(placeholder_edit)

            start_date = QDateEdit(calendarPopup=True)
            start_date.clear()
            start_date.userDateChanged.connect(lambda: _on_user_data_set_start())
            start_date.setDisplayFormat('dd-MM-yyyy')
            start_date.hide()
            layout.addWidget(start_date)

            end_date = QDateEdit(calendarPopup=True)
            end_date.setDisplayFormat('dd-MM-yyyy')
            end_date.setDate(QDate())
            end_date.userDateChanged.connect(lambda: _on_user_data_set_start())

            end_date.hide()
            layout.addWidget(end_date)

            cancel_button = QPushButton('Anuluj')
            cancel_button.hide()
            cancel_button.clicked.connect(lambda: _cancel_date(placeholder_edit))
            cancel_button.clicked.connect(function)
            layout.addWidget(cancel_button)

            self.widget = [start_date, end_date, cancel_button]

        self.setLayout(layout)

    def link(self, obj, first=True):
        self.linked.append(obj)
        if first:
            obj.link(self, False)

    def update_linked(self):
        for o in self.linked:
            o.blockSignals(True)
            o.set(self.value())
            o.blockSignals(False)

    def value(self):
        if self.widget is None:
            print('Zle ustawiony typ widgetu w CustomeSearchField')
            return ''
        if self.type == 'text':
            return self.widget.text()
        elif self.type == 'bool':
            v = self.widget.currentText()
            return '1' if v == 'Tak' else '0' if v == 'Nie' else ''
        elif self.type == 'status':
            return self.widget.currentText()
        elif self.type == 'date':
            return '' if self.widget[0].isHidden() else self.widget[0].date().toString('dd-MM-yyyy') if self.widget[
                                                                                                            1].isHidden() or \
                                                                                                        self.widget[
                                                                                                            1].date() == \
                                                                                                        self.widget[
                                                                                                            0].date() else [
                self.widget[0].date().toString('yyyy-MM-dd'), self.widget[1].date().toString('yyyy-MM-dd')]
        return ''

    def set(self, val):
        if self.widget is None:
            print('Zle ustawiony typ widgetu w CustomSearchField')
            return ''
        if self.type == 'bool' or self.type == 'status':
            self.widget.setCurrentText('Tak' if val == '1' else 'Nie' if val == '0' else '')
        elif self.type == 'text':
            self.widget.setText(val)
        elif self.type == 'date':
            print('date setting not implemented yet')
