
from datetime import datetime, timedelta
import requests
from PyQt5.QtCore import Qt, QTimer, QThread, QCoreApplication, QDateTime,QDate
from PyQt5.QtWidgets import *
class FireTMS:
    def __init__(self, parent):
        self.parent = parent
        self.pageSize = 100
        self.stop = False

    def load_day(self):
        self.load_from_to(datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"))

    def load_week(self):
        self.load_from_to((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                          datetime.now().strftime("%Y-%m-%d"))

    def load_month(self):
        self.load_from_to((datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"))

    def load_all(self):
        self.load_from_to("2010-01-01", datetime.now().strftime("%Y-%m-%d"))

    def load_from_date_window(self, f, t):
        # if self.dateWindow:
        #     self.dateWindow.destroy()
        self.load_from_to(f, t)


    def load_contractors(self):
        print('Loading contractors from fireTMS')

        headers = {
            "apiKey": "10915582-924a-4fce-b049-8c49175106c4|N/B+yeBIo2tP26DklLbhdA=="
        }

        params = {
            "asc": True,
            "page": 1,
            "pageSize": self.pageSize,
        }
        contractors = []
        stop = False
        while not stop:

            response_contractors = requests.get("https://app.firetms.com/api/contractors/", headers=headers,
                                                params=params)
            params['page'] = params['page'] + 1

            if response_contractors.status_code == 200:
                # Successfully received a response
                js = response_contractors.json()
                if js['totalItems'] < self.pageSize:
                    stop = True
                    continue
                for item in response_contractors.json()['items']:
                    contractors.append(item)

                QCoreApplication.processEvents()

            elif response_contractors.status_code == 401:
                stop = True
                print('unathorized contractors')
                QMessageBox.critical(self.parent, "Error", "Unauthorized: Check your API key.")
                return
            else:
                stop = True
                print('other error')
                QMessageBox.critical(self.parent, "Error",
                                     f"Error {response_contractors.status_code}: {response_contractors.text}")
                return
            if self.stop: return




        for contractor in contractors:
            print(contractor)
            if not contractor['name']: continue

            mail = '-'
            if contractor['contactPersons']:
                for person in contractor['contactPersons']:
                    if person['email']:
                        # so that first email is assigned if no emails are with adm
                        if mail == '-' :
                            mail = person['email']
                        if (person['firstName'] and 'adm' in person['firstName'].lower()
                                or person['lastName'] and 'adm' in person['lastName'].lower()
                                or 'adm' in person['email'].lower()):
                            mail = person['email']
                            break
            val = [
                mail,
                contractor['normalizedVatEuId'] if contractor['normalizedVatEuId'] else contractor['normalizedTaxId'] if contractor['normalizedTaxId'] else '-',
                contractor['name']
            ]
            val = [v.lstrip(' ').rstrip(' ') for v in val]
            print(f"Contractor info: {val}")
            if not self.parent.maria.update_contractors(val):
                return


    def load_sales_issued(self, f, t):

        def _reformat_date_user(d):
            d.replace(',', '-')
            if len(d.split('-')[0]) == 4:
                date = QDate.fromString(d, "yyyy-MM-dd")
                d = date.toString("dd-MM-yyyy")
            return d

        headers = {
            "apiKey": "10915582-924a-4fce-b049-8c49175106c4|N/B+yeBIo2tP26DklLbhdA=="
        }

        params = {
            "asc": True,
            "page": 1,
            "pageSize": self.pageSize,
            "sortBy": "id",
            "dateOfIssueFrom": f,
            "dateOfIssueTo": t,
        }

        items = []
        maxPage = 2
        while params['page'] <= maxPage:

            response_faktura = requests.get("https://app.firetms.com/api/invoices/sales/issued/", headers=headers, params=params)

            if response_faktura.status_code == 200:
                # Successfully received a response
                js = response_faktura.json()
                # print(response.json())
                maxPage = js['maxPageNumber']

                for item in response_faktura.json()['items']:
                    items.append(item)
                if maxPage != 0:
                    self.parent.progress_bar.setMaximum(maxPage)
                    self.parent.progress_bar.setValue(params['page'])
                else:
                    self.parent.progress_bar.setMaximum(100)
                    self.parent.progress_bar.setValue(100)
                QCoreApplication.processEvents()
                params['page'] = params['page'] +1


            elif response_faktura.status_code == 401:
                QMessageBox.critical(self.parent, "Error",  "Unauthorized: Check your API key.")
                return
            else:
                QMessageBox.critical(self.parent, "Error",  f"Error {response_faktura.status_code}: {response_faktura.text}")
                return

            if self.stop: return


        for item in items:
            for i in range(len(item['items'])):
                try:

                    val = [

                        _reformat_date_user( str(item['calculatedPaymentTerm']).split('T')[0] if item['calculatedPaymentTerm'] else ''),
                        #status platnosci faktury
                        item['status'],

                        # data wyslania faktury
                        _reformat_date_user(item['correspondenceData'][ 'postingDate'] if item['correspondenceData'] and item['correspondenceData'][ 'postingDate'] else ''),

                        # numer faktury
                        item['documentNumber'] if item['documentNumber'] else '',

                        # sql numer ladunku
                        item['items'][i]['transportServiceData']['clientOrderDocNumber']
                    ]
                    val = [v.lstrip(' ').rstrip(' ') for v in val]
                    print(f"Invoices sales isued info: {val}")
                    # cursor = self.parent.maria.conn.cursor()

                    #error czy tylko po numerze
                    if not self.parent.maria.update_sales_issued(val):
                        return
                except:
                    continue


    def load_purchase_issued(self, f, t):

        def _reformat_date_user(d):
            d.replace(',', '-')
            if len(d.split('-')[0]) == 4:
                date = QDate.fromString(d, "yyyy-MM-dd")
                d = date.toString("dd-MM-yyyy")
            return d

        headers = {
            "apiKey": "10915582-924a-4fce-b049-8c49175106c4|N/B+yeBIo2tP26DklLbhdA=="
        }

        params = {
            "asc": True,
            "page": 1,
            "pageSize": 20,
            "sortBy": "id",
            "dateOfIssueFrom": f,
            "dateOfIssueTo": t,
        }

        items = []
        maxPage = 2
        while params['page'] <= maxPage:

            response_faktura = requests.get("https://app.firetms.com/api/invoices/purchase/issued/", headers=headers, params=params)

            if response_faktura.status_code == 200:
                # Successfully received a response
                js = response_faktura.json()
                # print(js)
                maxPage = js['maxPageNumber']

                for item in response_faktura.json()['items']:
                    items.append(item)
                if maxPage != 0:
                    self.parent.progress_bar.setMaximum(maxPage)
                    self.parent.progress_bar.setValue(params['page'])
                else:
                    self.parent.progress_bar.setMaximum(100)
                    self.parent.progress_bar.setValue(100)
                QCoreApplication.processEvents()
                params['page'] = params['page'] +1


            elif response_faktura.status_code == 401:
                QMessageBox.critical(self.parent, "Error",  "Unauthorized: Check your API key.")
                return
            else:
                QMessageBox.critical(self.parent, "Error",  f"Error {response_faktura.status_code}: {response_faktura.text}")
                return

            if self.stop: return

        for item in items:
            try:
                val = [
                    #Data płatności
                    _reformat_date_user( str(item['calculatedPaymentTerm']).split('T')[0] if item['calculatedPaymentTerm'] else ''),
                    #status platnosci faktury
                    item['status'],

                    # numer faktury
                    item['documentNumber'],

                    # seller numer nip
                    #item['seller']['taxId']['normalizedTaxId'] if item['seller']['vatEuId'] else item['seller']['vatEuId']['normalizedValue'],
                    item['seller']['companyName'],

                    # sql numer zlecenia
                    item['relatedOrderNumber']
                ]

                val = [v.lstrip(' ').rstrip(' ') for v in val]
                print(f"Invoices purchase issued info: {val}")
                if not self.parent.maria.update_purchase_issued(val):
                    return
            except:
                continue


    def load_from_to(self, f, t):

        def _check_date_issue(d):
            d.replace(',', '-')
            if len(d.split('-')[0]) < 4:
                date = QDate.fromString(d, "dd-MM-yyyy")
                d = date.toString("yyyy-MM-dd")
            return d

        print(f == QDateEdit)
        f = _check_date_issue(f)
        t = _check_date_issue(t)
        print(f'loading data from {f} to {t}')

        #error wylaczone contractors

        self.parent.progress_bar.setValue(0)
        self.parent.progress_bar.show()

        print('Downloading contractors')
        self.load_contractors()
        self.parent.refresh_table()
        print('Completed! Successfully load contractors!')
        print('Downloading Invoices Sales')
        self.load_sales_issued(f, t)
        self.parent.refresh_table()
        print('Completed! Successfully load Invoices Sales!')
        print('Loading invoices purchase')
        self.load_purchase_issued(f, t)
        self.parent.refresh_table()
        print('Completed! Successfully load Invoices Purchase!')
        print('OK! All downloads has completed!')
        QMessageBox.information(self.parent, "Zakończono", "Pomyślnie załadowano dane z API FireTMS")
        self.parent.progress_bar.hide()
        # correspondenceStatus

    def open_date_window(self):
        # Create a QDialog instance

        dialog = QDialog()
        dialog.setWindowTitle("Wprowadź daty odświeżenia")

        layout = QFormLayout()



        # Creating fields for dates
        dialog.start_date = QDateEdit(calendarPopup=True)
        dialog.start_date.setDate(QDate(2015,1,1))
        dialog.start_date.setDisplayFormat('dd-MM-yyyy')

        layout.addRow(QLabel("Od:"), dialog.start_date)

        dialog.end_date = QDateEdit(calendarPopup=True)
        dialog.end_date.setDateTime(QDateTime.currentDateTime())
        dialog.end_date.setDisplayFormat('dd-MM-yyyy')
        layout.addRow(QLabel("Do:"), dialog.end_date)

        # Creating buttons
        dialog.fetch_button = QPushButton("Pobierz")
        dialog.fetch_button.clicked.connect(dialog.close)
        dialog.fetch_button.clicked.connect(
            lambda: self.load_from_to(dialog.start_date.text(), dialog.end_date.text()))
        layout.addRow(dialog.fetch_button)

        dialog.close_button = QPushButton("Zamknij")
        dialog.close_button.clicked.connect(dialog.close)
        layout.addRow(dialog.close_button)

        dialog.setLayout(layout)
        dialog.exec_()  # Show the dialog as a modal window

