from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFontMetrics, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, \
    QHBoxLayout, QSpacerItem, QSizePolicy, QScrollArea, QCheckBox, QDialog, \
    QFormLayout, QLineEdit, QLabel, QTextEdit, QPushButton, QComboBox

from miscellaneous import SpecialCheckbox, CustomSearchField


class CustomTable():
    def __init__(self,parent,columnsToDatabaseName,layout,database=None, tab=0):
        self.parent = parent
        self.maria = parent.maria

        self.columnsToDatabaseNameSplit = None
        self.columnsToDatabaseName = None
        self.inside_querry = self.generate_inside_querry(columnsToDatabaseName,database)

        self.tab = tab
        self.database = database


        self.columnsHeaders = list(c.rstrip('') for c in self.columnsToDatabaseName.keys())
        self.order_by = [None, 0, None]
        self.max_line_length_uwagi = 25


        self.create_all_window_components(layout)
        self.refresh_table()
        self.main_table.resizeColumnsToContents()
        header = self.main_table.horizontalHeader()
        for i, search_bar in enumerate(self.search_bars):
            self.main_table.setColumnWidth(i, max(header.sectionSize(i), 100))

        for i, search_bar in enumerate(self.search_bars):
            search_bar.setFixedWidth(header.sectionSize(i) - 8)

        # self.main_table.horizontalHeader().setStretchLastSection(True)
    def generate_inside_querry(self,cols, db):
        if isinstance(db,str):
            self.columnsToDatabaseName = cols
            return 'SELECT ' + ','.join(cols.values()) + f' FROM {db}'
        else:
            self.columnsToDatabaseNameSplit = cols
            self.columnsToDatabaseName = {**cols[0],**cols[1]}
            return f"SELECT {db[0]}.{f',{db[0]}.'.join(cols[0].values())},{db[1]}.{f',{db[1]}.'.join(cols[1].values())} FROM {db[0]} INNER JOIN {db[1]} ON {db[0]}.{db[2]} = {db[1]}.{db[3]}"

    def create_all_window_components(self, layout):
        # Set up a layout for the search bars
        self.search_bar_container = QWidget()
        self.search_bar_layout = QHBoxLayout()
        self.search_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.search_bar_layout.setSpacing(8)
        spacer = QSpacerItem(4, 5, QSizePolicy.Fixed)
        self.search_bar_layout.addItem(spacer)
        self.search_bars = []

        checkIndexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col.rstrip(' ') in ['Oryginały wysłane', 'Oryginały dokumentów', 'Skany dokumentów', 'Wymiana palet',
                                    'Kontrolowana temperatura', 'Wydruk z termografu', 'Status dokumentów CMR'])]
        dateIndexes = [i for i, col in enumerate(self.columnsHeaders) if str(col).__contains__('Data')]
        for i, c in enumerate(self.columnsHeaders):
            search_bar = CustomSearchField(self.refresh_table, f"Search {c}", 'bool' if i in
                                                                                        checkIndexes else 'status' if c == 'Status - dokumenty' else 'date' if i in dateIndexes else 'text')

            for j, s in enumerate(self.search_bars):
                if list(self.columnsToDatabaseName.values())[i] == list(self.columnsToDatabaseName.values())[j]:
                    s.link(search_bar)
            self.search_bars.append(search_bar)
            self.search_bar_layout.addWidget(search_bar)


        spa = QSpacerItem(4, 1, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.search_bar_layout.addItem(spa)
        # Add the search bar container to the main layout
        self.search_bar_layout.addStretch()

        self.search_bar_container.setLayout(self.search_bar_layout)

        self.main_table = QTableWidget()
        self.main_table.setColumnCount(len(self.columnsHeaders) )  # Set the number of columns to 36
        self.main_table.setRowCount(0)
        self.main_table.setHorizontalHeaderLabels(
            [str(c).rstrip(' ').replace(' ', '\n') for c in self.columnsHeaders])
        # self.main_table.horizontalHeader().setFixedHeight(120)
        self.main_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table cells read-only

        for i, col in enumerate(self.columnsHeaders):
            # header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.main_table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignCenter)

            match self.tab:
                case 0:
                    if col == 'Data aktualizacji (Oryginały wysłane)' or col == 'Oryginały wysłane':
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(144, 45, 212)))
                    elif col == 'Wymiana palet' or i in range(self.columnsHeaders.index('Faktura sprzedażowa'), self.columnsHeaders.index('Wymagane originały') + 1):
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(0, 250, 50)))
                    elif i in range(self.columnsHeaders.index('Kontrolowana temperatura'),self.columnsHeaders.index('Wydruk z termografu') + 1) or i in range(self.columnsHeaders.index('Kontrolowana temperatura '), self.columnsHeaders.index('Uwagi do dokumentów ') + 1):
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(0, 50, 250)))
                    elif i in range(self.columnsHeaders.index('Symbol Przewoźnika '),self.columnsHeaders.index('Uwagi do faktur') + 1):
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(250, 250, 50)))
                    else:
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(200, 200, 200)))
                case 1:
                    if col == 'Status rozliczenia' or i in range(self.columnsHeaders.index('Nr kwitu paletowego'), self.columnsHeaders.index('Uwagi') + 1):
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(230, 220, 120)))
                    elif i in range(self.columnsHeaders.index('Nr noty obciążeniowej'),self.columnsHeaders.index('Waluta noty obciążeniowej') + 1) or i in range(self.columnsHeaders.index('Nr faktury klienta'), self.columnsHeaders.index('Data wystawienia faktury klienta') + 1):
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(120, 120, 200)))
                    elif col == 'Stali przewoźnicy' :
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(200, 120, 120)))
                    else:
                        self.main_table.horizontalHeaderItem(i).setBackground(QBrush(QColor(200, 200, 200)))
                case _:
                    break


        self.main_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_table.horizontalScrollBar().setEnabled(False)
        self.main_table.horizontalScrollBar().setVisible(False)
        self.main_table.verticalScrollBar().setEnabled(False)
        self.main_table.verticalHeader().setVisible(False)
        self.main_table.verticalScrollBar().setVisible(False)

        match self.tab:
            case 0:
                self.main_table.cellDoubleClicked.connect(self.open_selection_window_main)
            case 1:
                self.main_table.cellDoubleClicked.connect(self.open_selection_window_pallets)

        self.main_table.horizontalHeader().sectionClicked.connect(self.on_click_column)

        self.main_table.horizontalHeader().sectionResized.connect(self.on_column_resize)

        self.main_table.setSelectionBehavior(QTableWidget.SelectRows)

        scrollable_layout = QVBoxLayout()
        scrollable_layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)


        scrollable_layout.addWidget(self.search_bar_container, alignment=Qt.AlignTop)
        scrollable_layout.addWidget(self.main_table)

        #bottom spacer
        spa = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        scrollable_layout.addItem(spa)


        container = QWidget()
        container.setLayout(scrollable_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn)  # Always show vertical scrollbar outside the table
        scroll_area.setWidget(container)

        # Set main lay

        layout.addWidget(scroll_area)

    def refresh_table(self, e=0):

        self.main_table.setHorizontalHeaderLabels([str(c).rstrip(' ').replace(' ', '\n') for c in self.columnsHeaders])

        filter_conditions = []
        filter_values = []
        for col, val in zip(self.columnsToDatabaseName.keys(), [search_bar.value() for search_bar in self.search_bars]):
            if val:
                adder = ''
                if self.columnsToDatabaseNameSplit:
                    for i in range(2):
                        if col in self.columnsToDatabaseNameSplit[i]:
                            adder = self.database[i] + '.'

                if isinstance(val, str):
                    filter_conditions.append(f"{adder}{self.columnsToDatabaseName[col]} LIKE ?")
                    filter_values.append(f"%{val}%")
                else:
                    filter_conditions.append(
                        f"STR_TO_DATE(IF(LOCATE('\n', {adder}{self.columnsToDatabaseName[col]}) > 0,SUBSTRING_INDEX({adder}{self.columnsToDatabaseName[col]}, '\n', 1),{adder}{self.columnsToDatabaseName[col]}), '%d-%m-%Y') BETWEEN ? AND ?")
                    filter_values.append(f"{(val[0])}")
                    filter_values.append(f"{(val[1])}")

        data = self.maria.apply_filters(filter_conditions, filter_values, self.inside_querry, self.order_by )
        self.main_table.setRowCount(0)
        self.main_table.setRowCount(len(data))

        colors = {
            'OK': QColor(40, 255, 30),
            'DO WINDYKACJI': QColor(255, 40, 30),
            'SKANY - KLIENT NIE WYMAGA ORYGINAŁÓW': QColor(80, 80, 255),
            "Niezrealizowana":  QColor("red"),
            "Zrealizowana": QColor("green")

        }
        checkIndexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col.rstrip(' ') in ['Oryginały wysłane', 'Oryginały dokumentów', 'Skany dokumentów', 'Wymiana palet',
                                    'Kontrolowana temperatura', 'Wydruk z termografu'])]

        uwagi_daty_indexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col.rstrip(' ') in ['Uwagi do faktur', 'Uwagi do dokumentów', 'Data wysłania maila do Przewoźnika','Uwagi','Data aktualizacj (Oryginały wysłane)'])]
        # error zharkodowana wartosc
        cmr_index = self.columnsHeaders.index('Status dokumentów CMR') if 'Status dokumentów CMR' in self.columnsHeaders else -1
        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                # i = QTableWidgetItem(str(item)).setBackground(QColor(0, 244, 0))
                if col_idx in checkIndexes:
                    checkbox_widget = SpecialCheckbox(row_idx, col_idx, item, self)
                    if len(checkIndexes) ==  1:
                        checkbox_widget.setEnabled(False)
                    self.main_table.setCellWidget(row_idx, col_idx, checkbox_widget)
                elif col_idx == cmr_index:
                    widget = QWidget()
                    checkbox_layout = QHBoxLayout(widget)
                    checkbox = QCheckBox()
                    checkbox.setEnabled(False)
                    checkbox.setChecked(item)
                    checkbox_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                    widget.setLayout(checkbox_layout)
                    self.main_table.setCellWidget(row_idx, col_idx, widget)
                elif 'Status - dokumenty' in self.columnsHeaders and col_idx == self.columnsHeaders.index('Status - dokumenty') and item in colors.keys()  or 'Status rozliczenia' in self.columnsHeaders and col_idx == self.columnsHeaders.index('Status rozliczenia') and item in colors.keys():

                    i = QTableWidgetItem(str(item))
                    i.setBackground(colors[str(item)])
                    self.main_table.setItem(row_idx, col_idx, i)
                elif col_idx in uwagi_daty_indexes:
                    item = str(item)
                    a = QTableWidgetItem(item.split('\n')[0])
                    a.setData(Qt.UserRole, item)
                    a.setToolTip(item)

                    if len(item.split('\n')[0]) > self.max_line_length_uwagi:
                        split = item.split('\n')[0].split(' ')
                        a.setText(item[:self.max_line_length_uwagi] if len(split) == 1 else ' '.join(
                            s if len(' '.join(split[:i + 1])) <= self.max_line_length_uwagi else '' for i, s in
                            enumerate(split)))

                    self.main_table.setItem(row_idx, col_idx, a)
                else:
                    self.main_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))


        if not self.order_by[2] is None and self.order_by[1] != 0:
            item = self.main_table.horizontalHeaderItem(self.order_by[2])
            lines = item.text().split('\n')
            middle = (len(lines) - 1) // 2
            maxLength = max([len(v) for v in lines])
            lines[middle] = ' ' * (maxLength - len(lines[middle]) + 5) + lines[middle] + ' ' * (
                    maxLength - len(lines[middle]) + 4) + ('↑' if self.order_by[1] == 1 else '↓')
            item.setText('\n'.join(lines))
            self.main_table.setHorizontalHeaderItem(self.order_by[2], item)

        self.main_table.setFixedHeight(
            max(self.main_table.rowCount() * self.main_table.rowHeight(0) + self.main_table.horizontalHeader().height(),
                0))

    def on_column_resize(self, index, old_width,width=0):
        if width < 100:
            width = 100
            self.main_table.setColumnWidth(index, 100)
        self.search_bars[index].setFixedWidth(width - (6 if index == len(self.search_bars) -1 else 8))


    def on_click_column(self, ind):
        if ind >= len(self.columnsToDatabaseName): return
        col = list(self.columnsToDatabaseName.values())[ind]
        if self.order_by[0] == col:
            self.order_by[1] = (self.order_by[1] + 1) % 3
        else:
            self.order_by = [col, 1, ind]

        self.refresh_table()

    def open_selection_window_main(self, row, col):
        checkIndexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col.rstrip(' ') in ['Oryginały wysłane','Oryginały dokumentów', 'Skany dokumentów', 'Wymiana palet',
                                    'Kontrolowana temperatura', 'Wydruk z termografu'])]


        labels = ['Symbol Klienta', 'Symbol Przewoźnika', 'Numer klienta', 'Nr ładunku', 'Nr zlecenia',
                  'Oryginały wysłane','Oryginały dokumentów',
                  'Skany dokumentów', 'Wymiana palet', 'Kontrolowana temperatura', 'Wydruk z termografu',
                  'Uwagi do dokumentów', 'Uwagi do faktur']
        # '' if i == 16 else


        values = [self.main_table.item(row, i).data(Qt.UserRole) if column in ['Uwagi do dokumentów', 'Uwagi do faktur']
                    else self.main_table.cellWidget(row, i).checkbox.isChecked() if i in checkIndexes
                    else self.main_table.item(row, i).text() if column in labels else '' for i, column in enumerate(self.columnsHeaders)]


        selection_window = QDialog(self.parent)

        selection_window.setWindowTitle("Edit Load Information")

        selection_layout = QVBoxLayout(selection_window)



        form_layout = QFormLayout()
        checkboxes = []
        uwagi = []
        def _save_selection_window():
            selection_window.close()
            val = [val.isChecked() for i, val in zip(checkIndexes, checkboxes)]
            val.append(uwagi[0].toPlainText())
            val.append(uwagi[1].toPlainText())

            f = 1 if val[0] else (0 if not val[0] else -1)
            g = 1 if val[1] else (0 if not val[1] else -1)
            # error need to be added
            z = 0

            state = 'DO WINDYKACJI'
            if f == 1:
                state = 'OK'
            elif g == 1:
                if z == 0:
                    state = "SKANY - KLIENT NIE WYMAGA ORYGINAŁÓW"
                else:
                    state = "SKANY - ORIGNAŁY"
            val = val + [state] + values[0:2] + values[3:5]

            self.maria.save_selection_window(val)
            self.refresh_table()

        longestLength = 100
        for i in range(5):
            longestLength = max(longestLength, QFontMetrics(QLineEdit().font()).horizontalAdvance( values[i]) + 15)

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            if i >= 5: i+=1
            if i in checkIndexes:
                checkbox = QCheckBox("", checked=values[i])
                form_layout.addRow(label, checkbox)
                checkboxes.append(checkbox)

            elif label_text in ['Uwagi do dokumentów', 'Uwagi do faktur']:
                var = QTextEdit()
                var.setPlainText(values[self.columnsHeaders.index(label_text)])
                var.setReadOnly(False)
                var.setFixedWidth(longestLength)
                var.setFixedHeight(100)
                form_layout.addRow(label, var)
                uwagi.append(var)
            else:
                var = QLineEdit(values[self.columnsHeaders.index(label_text)])
                var.setReadOnly(True)
                var.setFixedWidth(longestLength)
                form_layout.addRow(label, var)



        selection_layout.addLayout(form_layout)

        # Buttons for saving and closing
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(_save_selection_window)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(selection_window.close)
        button_layout.addWidget(close_button)

        selection_layout.addLayout(button_layout)

        selection_window.setLayout(selection_layout)

        selection_window.adjustSize()
        selection_window.setFixedSize(selection_window.size())

        selection_window.exec_()

    def open_selection_window_pallets(self, row, col):
        vals = []
        def _save_selection_window():
            selection_window.close()
            val = [v.text() for v in vals[:-2]] + [vals[-2].currentText()] + [vals[-1].toPlainText()]

            val = val + [values[1],values[2],values[7],values[8]]
            print(val)
            self.maria.save_selection_window_pallets(val)
            self.refresh_table()

        labels = [  'Wymiana palet',
                    'Symbol Klienta',
                    'Nr ładunku',
                    'Nr klienta',
                    'Załadunki',
                    'Rozładunki',
                    'Data rozładunku',
                    'Symbol Przewoźnika',
                    'Nr zlecenia',
                    'Nr kwitu paletowego',
                    'Zostawił na załadunku',
                    'Wyjechało z załadunku',
                    'Dostarczyl',
                    'Odebrał z rozładunku',
                    'Status rozliczenia',
                    'Uwagi']

        editable = [ 'Nr kwitu paletowego',
                    'Zostawił na załadunku',
                    'Wyjechało z załadunku',
                    'Dostarczyl',
                    'Odebrał z rozładunku',
                    ]
        # '' if i == 16 else
        values = [self.main_table.item(row, i).data(Qt.UserRole) if column in ['Uwagi'] else self.main_table.cellWidget(row, i).checkbox.isChecked() if column in ['Wymiana palet']
            else self.main_table.item(row, i).text() if column in labels else '' for i, column in
                  enumerate(self.columnsHeaders)]
        selection_window = QDialog(self.parent)

        selection_window.setWindowTitle("Edit pallet information")

        selection_layout = QVBoxLayout(selection_window)

        form_layout = QFormLayout()

        longestLength = 100

        longestLength = 100
        for i in range(1,10):
            longestLength = max(longestLength, QFontMetrics(QLineEdit().font()).horizontalAdvance(values[i]) + 15)

        for i, label_text in enumerate(labels):
            label = QLabel(label_text)
            if label_text in ['Wymiana palet']:
                checkbox = QCheckBox("", checked=values[i])
                checkbox.setEnabled(False)
                form_layout.addRow(label, checkbox)
            elif label_text in ['Uwagi']:
                var = QTextEdit()
                var.setPlainText(values[self.columnsHeaders.index(label_text)])
                var.setReadOnly(False)
                var.setFixedWidth(longestLength)
                var.setFixedHeight(100)
                form_layout.addRow(label, var)
                vals.append(var)
            elif label_text in 'Status rozliczenia':
                def update_dropdown_color():
                    selected_index = combo_box.currentIndex()  # Get the index of the selected item
                    color = combo_box.model().itemFromIndex(
                        combo_box.model().index(selected_index, 0)).background().color().name()

                    # Apply the color to the dropdown (unfolded state)
                    combo_box.setStyleSheet(f"""
                        QComboBox {{
                            background-color: {color};  /* Set background color of the selected item */
                        }}
                        QComboBox QAbstractItemView {{
                            background-color: transparent;
                        }}
                        QComboBox QAbstractItemView::item:selected {{
                            background-color: {color};  /* Set background color of selected item in dropdown */
                        }}
                    """)

                combo_box = QComboBox()

                curr = 0
                model = QStandardItemModel()
                for j, (text, color) in enumerate([(" ", QColor("gray")),("Niezrealizowana", QColor("red")), ("Zrealizowana", QColor("green"))]):
                    if values[self.columnsHeaders.index('Status rozliczenia')] == text: curr = j
                    item = QStandardItem(text)
                    item.setBackground(color)
                    model.appendRow(item)
                combo_box.setModel(model)
                combo_box.setCurrentIndex(curr)
                combo_box.setFixedWidth(longestLength)
                update_dropdown_color()
                combo_box.currentIndexChanged.connect(update_dropdown_color)

                form_layout.addRow(label, combo_box)
                vals.append(combo_box)
            else:
                # TODO jezeli jest data ustaw pierwsza lub ostatnia tak jak jest  w excelu
                var = QLineEdit(values[self.columnsHeaders.index(label_text)] if label_text in self.columnsHeaders else '')
                var.setReadOnly(label_text not in editable)
                var.setFixedWidth(longestLength)
                form_layout.addRow(label, var)
                if label_text in editable: vals.append(var)

        selection_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(_save_selection_window)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(selection_window.close)
        button_layout.addWidget(close_button)

        selection_layout.addLayout(button_layout)

        selection_window.setLayout(selection_layout)

        selection_window.adjustSize()
        selection_window.setFixedSize(selection_window.size())

        selection_window.exec_()


