from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QScrollArea, QWidget, QSpacerItem, QSizePolicy, QVBoxLayout, \
    QTableWidget, QDialog, QMessageBox, QProgressBar, QLabel, QTableWidgetItem, QCheckBox

from miscellaneous import CustomSearchField

send_mail = True
min_column_width = 100


class Raport:
    def __init__(self, parent, index=0):
        self.index = index
        self.parent = parent
        self.max_line_length_uwagi = 30
        self.sortBy = [
            'Wydruk z termografu',
            'None',
            'Oryginały dokumentów'
        ][self.index]

        self.title = ["Raportuj brak termografu", "Raportuj brak faktury zakupowej", "Raportuj brak dokumentów"][
            self.index]

        self.column_of_date_mail = [
            'wysylka_maila_termograf',
            'wysylka_maila_faktury',
            'wysylka_maila_dokumnety'
        ][self.index]

        self.columnsToDatabaseName = [{
            'Symbol Klienta': 'klient',
            'Symbol Przewoźnika': 'przewoznik',
            'NIP Przewoźnika': 'nip_przewoznika',

            'Wydruk z termografu': 'wydruk_z_termografu',

            'Nr ładunku': 'numer',
            'Nr zlecenia': 'zlecenie',

            'Uwagi do dokumentów': 'uwagi_do_dokumentow',
            'Data wysłania maila': 'wysylka_maila_termograf',
            'Mail kontaktowy': 'mail'

        },
            {
                'Symbol Klienta': 'klient',
                'Symbol Przewoźnika': 'przewoznik',
                'Nr ładunku': 'numer',
                'Nr zlecenia': 'zlecenie',

                'NIP Przewoźnika': 'nip_przewoznika',
                'Nr faktury': 'nr_faktury',
                'Data płatności faktury': 'data_platnosci',
                'Status faktury': 'status',
                'Data rozładunku': 'data_rozladunku',

                'Uwagi do faktur': 'uwagi_do_faktur',
                'Data wysłania maila': 'wysylka_maila_faktury',
                'Mail kontaktowy': 'mail'

            },
            {
                # BRAK DOKUMENTOW

                'Symbol Klienta': 'klient',
                'Symbol Przewoźnika': 'przewoznik',
                'NIP Przewoźnika': 'nip_przewoznika',
                'Nr ładunku': 'numer',
                'Nr zlecenia': 'zlecenie',

                'Faktura sprzedażowa': 'faktura_sprzedazowa',

                'Status faktury': 'status_faktury',
                'Data wysłania faktury': 'data_wyslania_faktury',
                'Wysyłka faktur': 'wysylka_faktur',
                'Wysyłka dokumentów': 'wysylka_dokumentow',
                'Wymagane oryginały': 'wymagane_oryginaly',

                'Data wysłania maila': 'wysylka_maila_dokumnety',
                'Mail kontaktowy': 'mail'

            }
        ][self.index]

        self.columnsHeaders = list(c.rstrip(' ') for c in self.columnsToDatabaseName.keys())

        self.insideQuerry = ','.join(list(self.columnsToDatabaseName.values()))

        # 0 none 1 asc 2 des
        self.order_by = [None, 0, None]

        self.finished_setup = False

        self.raport_window = QDialog(parent)
        self.raport_window.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.raport_window.resize(800, 600)
        self.raport_window.setWindowTitle(self.title)
        raport_layout = QVBoxLayout(self.raport_window)
        search_bar_container = QWidget()
        search_bar_layout = QHBoxLayout()
        search_bar_layout.setContentsMargins(0, 0, 0, 0)
        search_bar_layout.setSpacing(8)
        spacer = QSpacerItem(4, 0, QSizePolicy.Fixed)
        search_bar_layout.addItem(spacer)

        self.search_bars = []

        self.checkIndexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col in ['Oryginały dokumentów', 'Skany dokumentów', 'Wymiana palet',
                        'Kontrolowana temperatura', 'Wydruk z termografu', 'Status dokumentów CMR'])]
        self.uwagi_daty_indexes = [i for i, col in enumerate(self.columnsHeaders) if (
                col.rstrip(' ') in ['Uwagi do faktur', 'Uwagi do dokumentów',
                                    'Data wysłania maila'])]

        dateIndexes = [i for i, col in enumerate(self.columnsHeaders) if str(col).__contains__('Data')]
        for i, c in enumerate(self.columnsHeaders):
            search_bar = CustomSearchField(self.refresh_table, f"Search {c}", 'bool' if i in
                                                                                        self.checkIndexes else 'status' if c == 'Status - dokumenty' else 'date' if i in dateIndexes else 'text')

            if c == self.sortBy:
                search_bar.set('Nie')

            self.search_bars.append(search_bar)
            search_bar_layout.addWidget(search_bar, alignment=Qt.AlignLeft)

        spacer = QSpacerItem(4, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        search_bar_layout.addItem(spacer)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_bar_layout.addItem(spacer)
        # Add the search bar container to the main layout
        search_bar_container.setLayout(search_bar_layout)

        self.table = QTableWidget()

        self.table.setColumnCount(len(self.columnsHeaders))  # Set the number of columns to 36
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(
            [str(c).rstrip(' ').replace(' ', '\n') for c in self.columnsHeaders])
        # self.table.horizontalHeader().setFixedHeight(120)

        # self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table cells read-only
        color = [QColor(0, 50, 250), QColor(250, 250, 50), QColor(0, 250, 50)][self.index]

        for i, col in enumerate(self.columnsHeaders):
            self.table.horizontalHeaderItem(i).setBackground(QBrush(color))
            #  self.table.horizontalHeaderItem(i).setBackground(QBrush(QColor(200, 200, 200)))

        self.table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalScrollBar().setEnabled(False)
        self.table.horizontalScrollBar().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalScrollBar().setVisible(False)
        self.table.verticalScrollBar().setEnabled(False)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().sectionClicked.connect(self.on_click_column)
        # self.raport_window.resize.connect(lambda: self.check_width())
        scrollable_layout = QVBoxLayout()
        scrollable_layout.addWidget(search_bar_container, alignment=Qt.AlignTop)
        scrollable_layout.addWidget(self.table, alignment=Qt.AlignTop)

        # bottom spacer
        spa = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        scrollable_layout.addItem(spa)

        container = QWidget()
        container.setLayout(scrollable_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)

        raport_layout.addWidget(scroll_area)

        # Buttons for saving and closing
        button_layout = QHBoxLayout()
        save_button = QPushButton("Wyślij maile")
        save_button.clicked.connect(self.send)
        button_layout.addWidget(save_button)

        close_button = QPushButton("Zamknij")
        close_button.clicked.connect(self.raport_window.close)
        button_layout.addWidget(close_button)

        raport_layout.addLayout(button_layout)
        self.raport_window.setLayout(raport_layout)

        self.raport_window.finished.connect(parent.refresh_table)

        self.finished_setup = True

        self.refresh_table()
        # self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()

        full_width = 10
        header = self.table.horizontalHeader()
        for i, search_bar in enumerate(self.search_bars):
            self.table.setColumnWidth(i, max(self.table.columnWidth(i), 100))
            full_width += header.sectionSize(i)
        self.raport_window.resize(full_width, self.raport_window.height())
        for i, search_bar in enumerate(self.search_bars):
            search_bar.setFixedWidth(header.sectionSize(i) - 8)

        self.table.horizontalHeader().sectionResized.connect(self.on_column_resize)


        self.raport_window.exec_()

    def check_width(self, event=0):
        full_width = 56
        header = self.table.horizontalHeader()
        for i, search_bar in enumerate(self.search_bars):
            self.table.setColumnWidth(i, max(self.table.columnWidth(i), 100))
            full_width += header.sectionSize(i)
        if full_width < self.raport_window.width():
            self.raport_window.resize(full_width, self.raport_window.height())

    def on_column_resize(self, index, old_width, width=0):
        if width < 100:
            width = 100
            self.table.setColumnWidth(index, 100)
        self.search_bars[index].setFixedWidth(width - (6 if index == len(self.search_bars) - 1 else 8))
        # if old_width > width:
        #     self.check_width()

    def on_click_column(self, ind):
        col = list(self.columnsToDatabaseName.values())[ind]
        if self.order_by[0] == col:
            self.order_by[1] = (self.order_by[1] + 1) % 3
        else:
            self.order_by = [col, 1, ind]
        self.refresh_table()

    def send_verified(self, verification_window, rows, progressbar):
        progressbar.show()
        QCoreApplication.processEvents()

        sent_mails = []
        symbol = self.columnsHeaders.index('Symbol Przewoźnika')
        nip_index = self.columnsHeaders.index('NIP Przewoźnika')
        mail_index = self.columnsHeaders.index('Mail kontaktowy')

        nr_ladunku_index = self.columnsHeaders.index('Nr ładunku')
        nr_zlecenia_index = self.columnsHeaders.index('Nr zlecenia')

        for r in rows:
            mail = self.table.item(r, mail_index).text()
            nip = self.table.item(r, nip_index).text()
            nr_ladunku = self.table.item(r, nr_ladunku_index).text()
            nr_zlecenia = self.table.item(r, nr_zlecenia_index).text()

            mail_polish = [
                (f'{nr_zlecenia} – Prośba o przesłanie wydruku z termografu',
                 f'''Szanowni Państwo,

    Zwracamy się z prośbą o możliwie najszybsze przesłanie oryginału lub skanu wydruku z termografu dotyczącego realizowanego przez Państwa zlecenia o numerze {nr_zlecenia}. Dokument prosimy przesłać w odpowiedzi na tę wiadomość, nie zmieniając jej tytułu bądź przesłać pocztą tradycyjną na adres:

Lynx Cargo Sp. z o.o.
ul. 1 Maja 191
25-646 Kielce

Z poważaniem 
Dział administracji Lynx Cargo
Tel. +48 784 116 461
Mail: temp@lynx-cargo.com
             '''),
                (f'{nr_zlecenia} – Prośba o przesłanie skanu faktury',
                 f'''Szanowni Państwo,

    Zwracamy się z prośbą o możliwie najszybsze przesłanie skanu faktury dotyczącej realizowanego przez Państwa zlecenia o numerze {nr_zlecenia}. Dokument prosimy przesłać w odpowiedzi na tę wiadomość, nie zmieniając jej tytułu.

    Przypominamy, że zgodnie z warunkami zlecenia termin płatności liczony jest od daty przesłania oryginałów faktury i dokumentów pocztą tradycyjną na adres naszej siedziby:

Lynx Cargo Sp. z o.o.
ul. 1 Maja 191
25-646 Kielce

Z poważaniem
Dział administracji Lynx Cargo
Tel. +48 784 116 461
Mail: adm@lynx-cargo.com '''),
                (f'{nr_zlecenia} – Prośba o przesłanie dokumentów transportowych ',
                 f'''Szanowni Państwo,

    Zwracamy się z prośbą o możliwie najszybsze przesłanie oryginałów dokumentów transportowych dotyczących realizowanego przez Państwa zlecenia o numerze {nr_zlecenia}. Dokumenty prosimy o przesłanie pocztą tradycyjną na adres podany w zleceniu, tj.

Lynx Cargo Sp. z o.o.
ul. 1 Maja 191
25-646 Kielce

Z poważaniem 
Dział administracji Lynx Cargo
Tel. +48 784 116 461
Mail: adm@lynx-cargo.com
            ''')][self.index]
            mail_english = [
                (f'{nr_zlecenia} – Thermoregister printout request ',
                 f'''Dear Business Partner, 

    We would like to ask you to send as soon as possible an original or a scan of the thermoregister printout relating to your order numer {nr_zlecenia}. Please send the document in reply to this message without changing the title or send it by post to: 

Lynx Cargo Sp. z o.o. 
1 Maja Street 191 
25-646 Kielce 
Poland

Sincerely 
Lynx Cargo Administration Department 
Tel. +48 784 116 461 
Mail: temp@lynx-cargo.com '''),
                (f'{nr_zlecenia} - Invoice scan request ',
                 f'''Dear Business Partner, 

    We would like to ask you to send us as soon as possible a scan of the invoice concerning the order number {nr_zlecenia}, which you have carried out. Please send the document in response to this message without changing the title.

    We would like to remind you that, in accordance with the terms of the order, the payment term counts from the date of sending the original invoice and documents by post to the address of our registered office: 

Lynx Cargo Sp. z o.o. 
1 Maja Street 191 
25-646 Kielce 
Poland

Sincerely 
Lynx Cargo Administration Department 
Tel. +48 784 116 461 
Mail: adm@lynx-cargo.com 
            '''),
                (f'{nr_zlecenia} – Transport documents request ',
                 f'''Dear Business Partner, 

    We would like to ask you to send us as soon as possible the original transport documents relating to your order number {nr_zlecenia}. Please send the documents by post to the address given in the order, which is:

Lynx Cargo Sp. z o.o. 
1 Maja Street 191 
25-646 Kielce
Poland

Sincerely 
Lynx Cargo Administration Department 
Tel. +48 784 116 461 
Mail: adm@lynx-cargo.com 
''')
            ][self.index]

            if not mail or not mail.__contains__('@'):
                continue

            if not self.parent.mail.send_mail(mail_polish if nip.__contains__('PL') else mail_english,
                                              mail if send_mail else 'losowy@w.w',
                                              ['temp@lynx-cargo.com', 'adm@lynx-cargo.com',
                                               'adm@lynx-cargo.com'][self.index]):
                msg_box = QMessageBox(self.raport_window)
                msg_box.setWindowTitle("Error")
                msg_box.setText(
                    f"Nie udało się wysłać maila do {mail}, bład serwera wysyłającego")
                msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg_box.exec_()
            else:
                sent_mails.append(mail)
                self.parent.maria.set_date_of_mail_sending(self.column_of_date_mail, nr_ladunku, nr_zlecenia)
            progressbar.setValue(progressbar.value() + 1)
            QCoreApplication.processEvents()

        self.refresh_table()

    def refresh_table(self):
        if not self.finished_setup: return
        self.table.setHorizontalHeaderLabels(
            [str(c).rstrip(' ').replace(' ', '\n') for c in self.columnsHeaders])
        filter_conditions = []
        filter_values = []
        for col, val in zip(self.columnsToDatabaseName.keys(),
                            [search_bar.value() for search_bar in self.search_bars]):
            if val:
                if isinstance(val, str):
                    filter_conditions.append(f"{self.columnsToDatabaseName[col]} LIKE ?")
                    filter_values.append(f"%{val}%")
                else:
                    filter_conditions.append(
                        f"STR_TO_DATE(IF(LOCATE('\n', {self.columnsToDatabaseName[col]}) > 0,SUBSTRING_INDEX({self.columnsToDatabaseName[col]}, '\n', 1),{self.columnsToDatabaseName[col]}), '%d-%m-%Y') BETWEEN ? AND ?")
                    filter_values.append(f"{(val[0])}")
                    filter_values.append(f"{(val[1])}")

        data = self.parent.maria.apply_filters(filter_conditions, filter_values, self.insideQuerry, self.order_by)
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        colors = {
            'OK': QColor(40, 255, 30),
            'DO WINDYKACJI': QColor(255, 40, 30),
            'SKANY - KLIENT NIE WYMAGA ORYGINAŁÓW': QColor(80, 80, 255)
        }

        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                if col_idx in self.checkIndexes:
                    widget = QWidget()
                    checkbox_layout = QHBoxLayout()
                    checkbox_widget = QCheckBox()
                    checkbox_layout.addWidget(checkbox_widget, alignment=Qt.AlignCenter)
                    widget.setLayout(checkbox_layout)
                    checkbox_widget.setChecked(item)
                    checkbox_widget.setEnabled(False)
                    self.table.setCellWidget(row_idx, col_idx, widget)
                elif 'Status - dokumenty' in self.columnsHeaders and col_idx == self.columnsHeaders.index(
                        'Status - dokumenty') and item in colors.keys():
                    i = QTableWidgetItem(str(item))
                    i.setBackground(colors[str(item)])
                    self.table.setItem(row_idx, col_idx, i)
                elif col_idx in self.uwagi_daty_indexes:
                    item = str(item)
                    a = QTableWidgetItem(item.split('\n')[0])
                    a.setData(Qt.UserRole, item)
                    a.setToolTip(item)
                    if len(item.split('\n')[0]) > self.max_line_length_uwagi:
                        split = item.split('\n')[0].split(' ')
                        a.setText(item[:self.max_line_length_uwagi] if len(split) == 1 else ' '.join(
                            s if len(' '.join(split[:i + 1])) <= self.max_line_length_uwagi else '' for i, s in
                            enumerate(split)))

                    self.table.setItem(row_idx, col_idx, a)
                else:
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

        if not self.order_by[2] is None and self.order_by[1] != 0:
            item = self.table.horizontalHeaderItem(self.order_by[2])
            lines = item.text().split('\n')
            middle = (len(lines) - 1) // 2
            maxLength = max([len(v) for v in lines])
            lines[middle] = ' ' * (maxLength - len(lines[middle]) + 5) + lines[middle] + ' ' * (
                    maxLength - len(lines[middle]) + 4) + ('↑' if self.order_by[1] == 1 else '↓')
            item.setText('\n'.join(lines))
            self.table.setHorizontalHeaderItem(self.order_by[2], item)

        self.table.setFixedHeight(
            max(self.table.rowCount() * self.table.rowHeight(0) + self.table.horizontalHeader().height(), 0))

    def send(self):
        rows = list(dict.fromkeys([idx.row() for idx in self.table.selectedIndexes()]))

        if not 'NIP Przewoźnika' in self.columnsHeaders:
            print('No Nip in the table')
            return
        if not 'Mail kontaktowy' in self.columnsHeaders:
            print('No mail in the table')
            return

        if not 'Nr ładunku' in self.columnsHeaders:
            print('No nr ladunku in the table')
            return
        if not 'Nr zlecenia' in self.columnsHeaders:
            print('No nr zlecenia in the table')
            return
        if not 'Mail kontaktowy' in self.columnsHeaders:
            print('No mail in the table')

        symbol = self.columnsHeaders.index('Symbol Przewoźnika')
        mail_index = self.columnsHeaders.index('Mail kontaktowy')

        not_existing_mails = []
        mails = []
        for r in rows:
            mail = self.table.item(r, mail_index).text()
            if not mail or not mail.__contains__('@'):
                not_existing_mails.append(self.table.item(r, symbol).text())
            else:
                mails.append([self.table.item(r, symbol).text(), mail])

        verification_window = QDialog(self.raport_window)
        verification_window.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        verification_window.setWindowTitle("Wysłać maile?")
        verification_layout = QVBoxLayout(verification_window)

        if len(mails) > 0:
            mailText = QLabel()
            mailText.setText(
                'Maile zostaną wysłane do: \n\n' + ',\n'.join((m[0] + ': ' + m[1]) for m in mails) + '\n')
            verification_layout.addWidget(mailText)

        if len(mails) > 0 and len(not_existing_mails) > 0:  verification_layout.addItem(
            QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        if len(not_existing_mails) > 0:
            notMailText = QLabel()
            notMailText.setText(
                'Maile nie zostaną wysłane do z powodu braku danych w bazie danych: \n\n' + ',\n'.join(
                    list(set(not_existing_mails))) + '\n')
            verification_layout.addWidget(notMailText)

        progress = QProgressBar()
        progress.setValue(0)
        progress.setMaximum(len(mails))
        progress.setStyleSheet("""
            QProgressBar {
                border: 0.5px solid grey;
                border-radius: 3px;
                text-align: center;
                height: 10px
            }
    
            QProgressBar::chunk {
                background-color: #4CAF50;  /* Green color for the progress */
            }
        """)
        verification_layout.addWidget(progress)
        progress.hide()

        button_layout = QHBoxLayout()

        save_button = QPushButton("Wyślij")
        save_button.clicked.connect(lambda: self.send_verified(verification_window, rows, progress))
        # error czy odrazu zamykac czy po tym jak wysle
        save_button.clicked.connect(verification_window.close)

        if len(not_existing_mails) > 0 and len(mails) == 0:
            save_button.setEnabled(False)

        button_layout.addWidget(save_button)

        close_button = QPushButton("Anuluj")
        close_button.clicked.connect(verification_window.close)
        button_layout.addWidget(close_button)

        verification_layout.addLayout(button_layout)

        verification_window.setLayout(verification_layout)

        verification_window.exec_()
