import pandas as pd
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread, QCoreApplication
class Excel:
    def __init__(self, parent):
        self.parent = parent
        self.data_frame = []
        pass

    def import_loads(self):
        file_path = QFileDialog.getOpenFileName(self.parent, "Excel z ładunkami", "", "Xls (*.xls)")[0]
        if not file_path:
            return
        try:
            self.data_frame = pd.read_excel(file_path)
            # Remove unnamed columns
            self.data_frame = self.data_frame.loc[:, ~self.data_frame.columns.str.contains('^Unnamed')]
            self.save_loads_to_database()
            self.update_loads_to_database_rwp()
            QMessageBox.information(self.parent, "Success", "Data imported and saved to the database successfully.")
            self.parent.refresh_table()  # Refresh the view after import
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to import file:\n{e}")

    def save_loads_to_database(self):
        for index, row in self.data_frame.iterrows():
            zlecenie = row['Zlecenie wystawione'] if 'Zlecenie wystawione' in self.data_frame.columns and pd.notna(
                row['Zlecenie wystawione']) else ''
            if not zlecenie or not zlecenie.split('/')[0] == 'Z':
                continue
            status = row['Status'] if 'Status' in self.data_frame.columns and pd.notna(row['Status']) else ''

            if not (status == 'Zafakturowane' or status == "Zakończone"):
                continue
            przewoznik = row['Przewoźnik'] if 'Przewoźnik' in self.data_frame.columns and pd.notna(
                row['Przewoźnik']) else ''
            numer = row['Nr ładunku klienta'] if 'Nr ładunku klienta' in self.data_frame.columns and pd.notna(row['Nr ładunku klienta']) else ''
            zaladunki = row['Załadunki'] if 'Załadunki' in self.data_frame.columns and pd.notna(row['Załadunki']) else ''
            rozladunki = row['Rozładunki'] if 'Rozładunki' in self.data_frame.columns and pd.notna(row['Rozładunki']) else ''
            data_rozladunku_match = re.search(r"\((\d{2}.\d{2}.\d{4})\)$", rozladunki)
            data_rozladunku = data_rozladunku_match.group(1).replace('.','-') if data_rozladunku_match else None
            staus_dokumentow_cmr = 'CMR' in str(row['Dokumenty']) if 'Dokumenty' in self.data_frame.columns and pd.notna(row['Dokumenty']) else False
            self.parent.maria.save_excel_ladunki(przewoznik, numer, zaladunki, rozladunki, data_rozladunku, zlecenie,staus_dokumentow_cmr)

        print("OK! Loads saved!")

    def update_loads_to_database_rwp(self):

        for index, row in self.data_frame.iterrows():
            # Tylko wiersze od RWZ
            RWZ = row['Zlecenie wystawione'] if 'Zlecenie wystawione' in self.data_frame.columns and pd.notna(row['Zlecenie wystawione']) else ''
            if not RWZ or not RWZ.split('/')[0] == 'RWZ':
                continue
            klient = row['Klient'] if 'Klient' in self.data_frame.columns and pd.notna(row['Klient']) else ''
            przesylka = row['Numer'] if 'Numer' in self.data_frame.columns and pd.notna(row['Numer']) else ''
            numer_klienta = row['Nr ładunku klienta'] if 'Nr ładunku klienta' in self.data_frame.columns and pd.notna(row['Nr ładunku klienta']) else ''
            faktura_sprzedazowa = row['Faktura sprzedażowa'] if 'Faktura sprzedażowa' in self.data_frame.columns and pd.notna(row['Faktura sprzedażowa']) else ''

            self.parent.maria.update_excel_ladunki_rwp(klient, przesylka, numer_klienta, faktura_sprzedazowa)
        print("OK! Loads updated!")

    def import_contractors_specification(self):
        file_path = QFileDialog.getOpenFileName(self.parent, "Excel z zasadami współpracy", "", "Xlsx (*.xlsx)")[0]
        if not file_path:
            return

        try:
            self.data_frame = pd.read_excel(file_path)
            # Remove unnamed columns
            self.data_frame = self.data_frame.loc[:, ~self.data_frame.columns.str.contains('^Unnamed')]
            self.save_contractors_specification()
            self.parent.refresh_table()  # Refresh the view after import
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Wystąpił problem z importem zasad współpracy:\n{e}")

    def save_contractors_specification(self):
        cursor = self.parent.maria.conn.cursor()
        for index, row in self.data_frame.iterrows():
            Symbol = row['Symbol klienta'] if 'Symbol klienta' in self.data_frame.columns and pd.notna(row['Symbol klienta']) else ''
            NIP = row['NIP'] if 'NIP' in self.data_frame.columns and pd.notna(row['NIP']) else ''
            wysylka_faktur = row['Wysyłka faktur'] if 'Wysyłka faktur' in self.data_frame.columns and pd.notna(
                row['Wysyłka faktur']) else ''
            wysylka_dokumentow = row[
                'Wysyłka dokumentów'] if 'Wysyłka dokumentów' in self.data_frame.columns and pd.notna(
                row['Wysyłka dokumentów']) else ''
            oryginaly = row['Oryginały'] if 'Oryginały' in self.data_frame.columns and pd.notna(
                row['Oryginały']) else ''

            # Debug: wyświetlenie wartości przed wstawieniem
            print(
                f"Przetwarzanie wiersza {index}: NIP={NIP}, Wysyłka faktur={wysylka_faktur}, Wysyłka dokumentów={wysylka_dokumentow}, Oryginały={oryginaly}")
            cursor.execute(
                '''
                SELECT COUNT(*) FROM contractors_specification WHERE NIP = ? AND wysylka_faktur = ? AND wysylka_dokumentow = ? AND oryginaly = ?
                ''', (NIP, wysylka_faktur, wysylka_dokumentow, oryginaly))

            if cursor.fetchone()[0] == 0:
                try:
                    cursor.execute(
                        '''
                        INSERT INTO contractors_specification (Symbol ,NIP, wysylka_faktur, wysylka_dokumentow, oryginaly)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (Symbol, NIP, wysylka_faktur, wysylka_dokumentow, oryginaly))
                except:
                    QMessageBox.critical(self.parent, "Error", f"Brak połączenia z bazą danych")
                    continue

        self.parent.maria.conn.commit()
        QMessageBox.information(self.parent, "Success", "Import zakończony")

