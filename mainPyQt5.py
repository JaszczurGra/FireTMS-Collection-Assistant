from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, \
    QMessageBox, QProgressBar, QAction, QLabel, QPushButton, QTabWidget

import maria
from excel import Excel
from firetms import FireTMS
from mail import Mail
from raport_window import Raport
from table import CustomTable


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FireTMS Collection Assitant")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.maria = maria.MariaDataBase('root', '1234', 'database1', 'localhost', 3306, {})
        self.maria.connect()
        self.maria.create_table()

        self.excel = Excel(self)

        self.fire = FireTMS(self)

        self._create_menu_bar()

        self.tables = self.create_tables(layout)

        self._create_progress_bar(layout)

        # self.columnsHeaders = list(c.rstrip('') for c in self.columnsToDatabaseName.keys())
        # self.order_by = [None, 0, None]
        # self.max_line_length_uwagi = 25

        # TODO
        # self.refresh_table()
        # self.main_table.resizeColumnsToContents()
        # header = self.main_table.horizontalHeader()
        # for i, search_bar in enumerate(self.search_bars):
        #     self.main_table.setColumnWidth(i, max(header.sectionSize(i), 100))
        #
        # for i, search_bar in enumerate(self.search_bars):
        #     search_bar.setFixedWidth(header.sectionSize(i) - 8)

        # self.main_table.horizontalHeader().setStretchLastSection(True)

        self.mail = Mail('smtp.poczta.onet.pl', 465, 'julian.mikolajczak@onet.pl', "")

    def closeEvent(self, event):
        reply = QMessageBox(self)
        reply.setWindowTitle("Potwierdź wyjście z programu")
        reply.setText("Na pewno chcesz wyjść z programu?")
        reply.setIcon(QMessageBox.Question)

        tak_button = reply.addButton("Tak", QMessageBox.YesRole)
        nie_button = reply.addButton("Nie", QMessageBox.NoRole)

        reply.exec_()

        if reply.clickedButton() == tak_button:
            self.fire.stop = True
            event.accept()
        else:
            event.ignore()

    def create_tables(self, layout):
        tab_widget = QTabWidget()
        f_layout = QVBoxLayout()
        s_layout = QVBoxLayout()
        t_layout = QVBoxLayout()

        tables = [
            CustomTable(self, {
                'Symbol Klienta': 'klient',
                'Symbol Przewoźnika': 'przewoznik',
                'Numer klienta': 'numer_klienta',
                'Nr ładunku': 'numer',
                'Nr zlecenia': 'zlecenie',
                'Data aktualizacji (Oryginały wysłane)': 'data_aktualizacji_oryginaly_wyslane',
                'Oryginały wysłane': 'oryginaly_wyslane',
                'Oryginały dokumentów': 'oryginaly_dokumentow',
                'Skany dokumentów': 'skany_dokumentow',
                'Wymiana palet': 'wymiana_palet',
                'Kontrolowana temperatura': 'kontrolowana_temperatura',
                'Wydruk z termografu': 'wydruk_z_termografu',
                'Status - dokumenty': 'status_dokumenty',
                'Załadunki': 'zaladunki',
                'Rozładunki': 'rozladunki',
                'Data rozładunku': 'data_rozladunku',
                'Data wysłania maila do Przewoźnika': 'wysylka_maila_dokumnety',
                # 'Wysyłka maila - dokumenty': 'data_wyslania_maila',  # nie bylo
                'Status dokumentów CMR': 'status_dokumnetow_cmr',
                'Uwagi do dokumentów': 'uwagi_do_dokumentow',
                'Faktura sprzedażowa': 'faktura_sprzedazowa',
                'Data płatności faktury': 'data_platonsci_faktury',
                'Status faktury': 'status_faktury',
                'Data wysłania faktury': 'data_wyslania_faktury',
                'Wysyłka faktur': 'wysylka_faktur',
                'Wysyłka dokumentów': 'wysylka_dokumentow',
                'Wymagane originały': 'wymagane_oryginaly',
                'Symbol Przewoźnika ': 'przewoznik',
                'NIP przewoźnika': 'nip_przewoznika',
                'Nr faktury': 'nr_faktury',
                'Data płatności': 'data_platnosci',
                'Status': 'status',
                'Data wysłania maila do Przewoźnika ': 'wysylka_maila_faktury',
                # 'Wysyłka maila - faktury': 'wysylka_maila_faktury',
                'Uwagi do faktur': 'uwagi_do_faktur',
                'Kontrolowana temperatura ': 'kontrolowana_temperatura',
                'Wydruk z termografu ': 'wydruk_z_termografu',
                'Data wysłania maila do Przewoźnika  ': 'wysylka_maila_termograf',
                # 'Wysyłka maila - dokumenty ': 'wysylka_maila_dokumnety',
                'Uwagi do dokumentów ': 'uwagi_do_dokumentow',
                'Spedytor': 'spedytor'

            }, f_layout, 'loads'),
            CustomTable(self, [{
                'Wymiana palet': 'wymiana_palet',
                'Wymiana palet': 'wymiana_palet',
                'Symbol Klienta': 'klient',
                'Nr ładunku': 'numer',
                'Nr klienta': 'numer_klienta',
                'Załadunki': 'zaladunki',
                'Rozładunki': 'rozladunki',
                'Data rozładunku': 'data_rozladunku',
                'Symbol Przewoźnika': 'przewoznik',
                'Nr zlecenia': 'zlecenie'},

                {"Nr kwitu paletowego": "numer_kwitu_paletowego",
                 "Zostawil na zaladunku": "zostawil_na_zaladunku",
                 "Wyjechalo z zaladunku": "wyjechalo_z_zaladunku",
                 "Dostarczyl": "dostarczyl",
                 "Odebral z rozladunku": "odebral_z_rozladunku",
                 "Saldo z przewoźnikiem": "saldo_przewoznik",
                 "Saldo z klientem": "saldo_klient",
                 "Uwagi": "uwagi",
                 "Nr noty obciążeniowej": "nr_noty",
                 "Status noty obciążeniowej": "statu_noty",
                 "Kwota noty obciążeniowej": "kwota_noty",
                 "Waluta noty obciążeniowej": "waluta_noty",
                 "Stali przewoźnicy": "staly_przewoznik",
                 "Data wysłania maila informacyjnego": "data_wyslania_maila_paletowego",
                 "Status rozliczenia": "status_rozliczenia",
                 "Nr faktury klienta": "nr_faktury_kleinta",
                 "Status faktury klienta": "status_faktury_klienta",
                 "Kwota faktury klienta": "kwota_faktury_klienta",
                 "Data wystawienia faktury klienta": "data_wystawienia_faktury_klienta"}
                ], s_layout,  ('loads', 'pallets', 'id', 'id_ladunku'), 1),
            CustomTable(self, {
                'ID (trasy)': 'id',
                'Symbol klienta': 'symbol_klienta',
                'Symbol przewożnika': 'symbol_przewoznika',
                'Opis trasy': '	opis_trasy'
            }, t_layout, 'stali_przewoznicy', 2)

        ]

        f_tab = QWidget()
        s_tab = QWidget()
        t_tab = QWidget()

        f_tab.setLayout(f_layout)
        s_tab.setLayout(s_layout)
        t_tab.setLayout(t_layout)


        # TODO It's possible here to add an icon

        tab_widget.addTab(f_tab, "Windykacja")
        tab_widget.addTab(s_tab, "Palety")
        tab_widget.addTab(t_tab, "Stałe trasy")
        layout.addWidget(tab_widget)

        tab_widget.currentChanged.connect(self.refresh_table)


        return tables

    def create_tab_content(self, tab_name):
        """
        Create the content of a tab.
        """
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel(f"This is the content of {tab_name}.")
        button = QPushButton(f"Button in {tab_name}")

        layout.addWidget(label)
        layout.addWidget(button)

        widget.setLayout(layout)
        return widget

    def _create_progress_bar(self, layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
              QProgressBar {
                  border: 0.5px solid grey;
                  border-radius: 3px;
                  text-align: center;
                  height: 15px
              }

              QProgressBar::chunk {
                  background-color: #4CAF50;  /* Green color for the progress */
              }
          """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

    def _create_menu_bar(self):
        # Creating main menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        import_loads_action = QAction("Importuj ładunki", self)
        import_loads_action.triggered.connect(self.excel.import_loads)
        file_menu.addAction(import_loads_action)

        import_spec_action = QAction("Importuj zasady współpracy", self)
        import_spec_action.triggered.connect(self.excel.import_contractors_specification)
        file_menu.addAction(import_spec_action)
        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Refresh menu
        refresh_menu = menubar.addMenu("Odśwież")
        refresh_day_action = QAction("Odśwież dzisiaj", self)
        refresh_day_action.triggered.connect(self.fire.load_day)
        refresh_menu.addAction(refresh_day_action)

        refresh_week_action = QAction("Odśwież tydzień", self)
        refresh_week_action.triggered.connect(self.fire.load_week)
        refresh_menu.addAction(refresh_week_action)

        refresh_month_action = QAction("Odśwież miesiąc", self)
        refresh_month_action.triggered.connect(self.fire.load_month)
        refresh_menu.addAction(refresh_month_action)

        refresh_date_action = QAction("Odśwież od-do", self)
        refresh_date_action.triggered.connect(self.fire.open_date_window)
        refresh_menu.addAction(refresh_date_action)

        refresh_all_action = QAction("Odśwież wszystko", self)
        refresh_all_action.triggered.connect(self.fire.load_all)
        refresh_menu.addAction(refresh_all_action)

        # Report menu
        report_menu = menubar.addMenu("Raportuj")
        report_missing_thermo_action = QAction("Raportuj brak termografu", self)

        report_missing_thermo_action.triggered.connect(lambda: self.open_raport(0))
        report_menu.addAction(report_missing_thermo_action)

        report_missing_invoice_action = QAction("Raportuj brak faktury zakupowej", self)
        report_missing_invoice_action.triggered.connect(lambda: self.open_raport(1))
        report_menu.addAction(report_missing_invoice_action)

        report_missing_docs_action = QAction("Raportuj brak dokumentów", self)
        report_missing_docs_action.triggered.connect(lambda: self.open_raport(2))
        report_menu.addAction(report_missing_docs_action)

    def open_raport(self, index):
        Raport(self, index)

    # refreshing needed in raport and dtwindow
    def refresh_table(self):
        for table in self.tables:
            table.refresh_table()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
