import datetime
from functools import wraps
from tkinter import messagebox

import mariadb

restartTable = False

import time


def timeit(f):
    @wraps(f)
    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print( 'func:%r args:[%r, %r] took: %2.4f ms' % \
          (f.__name__, args, kw, (te-ts) * 1000))
        return result

    return timed

def add_try(f):
    @wraps(f)
    def wrapTheFunction(*args):
        try:
            func = f(*args)
            args[0].conn.commit()

            return func if func or func == [] else True
        except mariadb.Error as e:
            messagebox.showerror('Error', f"MariaDB error: {e} \n called by function: {f.__name__}")
            return False

    return wrapTheFunction


class MariaDataBase:
    def __init__(self,user,password,name,host,port,  columnsToDatabaseName):
        self.user = user
        self.password = password
        self.databaseName = name
        self.host = host
        self.port = port

        self.conn = None
        self.cursor = None

        self.insideQuerry = ""


    @add_try
    def connect(self):
        self.conn = mariadb.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.databaseName
        )
        self.cursor = self.conn.cursor()

    @add_try
    def create_table(self):
        if not self.conn:
            return  False
        self.cursor = self.conn.cursor()
        if restartTable:
            self.cursor.execute('''DROP TABLE loads''')
            self.cursor.execute('''DROP TABLE pallets''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS loads (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                klient TEXT, przewoznik TEXT, numer_klienta TEXT, numer TEXT, zlecenie TEXT, data_aktualizacji_oryginaly_wyslane TEXT, oryginaly_wyslane BOOL, oryginaly_dokumentow BOOL, skany_dokumentow BOOL , wymiana_palet BOOL, kontrolowana_temperatura BOOL, wydruk_z_termografu BOOL, status_dokumenty TEXT, zaladunki TEXT, rozladunki TEXT, data_rozladunku TEXT, opoznienie_rozladunek TEXT, opoznienie_faktura TEXT, opoznienie_termograf TEXT, data_wyslania_maila TEXT, wysylka_maila_dokumnety TEXT, status_dokumnetow_cmr BOOL, uwagi_do_dokumentow TEXT, faktura_sprzedazowa TEXT, data_platonsci_faktury TEXT, status_faktury TEXT, data_wyslania_faktury TEXT, wysylka_faktur TEXT, wysylka_dokumentow TEXT, wymagane_oryginaly TEXT, nip_przewoznika TEXT, nr_faktury TEXT, data_platnosci TEXT, status TEXT, wysylka_maila_faktury TEXT,wysylka_maila_termograf TEXT, uwagi_do_faktur TEXT, spedytor TEXT, mail TEXT, data_wprowadzenia_do_systemu TEXT
            )
        ''')

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS contractors_specification (
                id INTEGER PRIMARY KEY AUTO_INCREMENT, Symbol TEXT, NIP TEXT, wysylka_faktur TEXT, wysylka_dokumentow TEXT, oryginaly TEXT, UNIQUE(NIP)
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pallets (
                 id INTEGER PRIMARY KEY AUTO_INCREMENT, id_ladunku INT, numer_kwitu_paletowego TEXT, zostawil_na_zaladunku INT, wyjechalo_z_zaladunku INT, dostarczyl INT, odebral_z_rozladunku INT, saldo_przewoznik INT, saldo_klient INT, uwagi TEXT, nr_noty TEXT, statu_noty TEXT, kwota_noty TEXT, waluta_noty TEXT, staly_przewoznik BOOL, data_wyslania_maila_paletowego TEXT, status_rozliczenia TEXT, nr_faktury_kleinta TEXT, status_faktury_klienta TEXT, kwota_faktury_klienta TEXT, data_wystawienia_faktury_klienta TEXT
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS pallets_logs (
                id INTEGER PRIMARY KEY AUTO_INCREMENT, pallets_id INT, operacja TEXT, data TEXT, nr_kwitu TEXT, ilość INT
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS stali_przewoznicy (
                id INTEGER PRIMARY KEY AUTO_INCREMENT, symbol_klienta TEXT, symbol_przewoznika TEXT, opis_trasy TEXT
            )
            '''
        )



        # rzeby populate table do testow do wywalenia pozniej
        if restartTable:
            for i in range(100):
                query = f'''INSERT
                INTO
                pallets(
                    id_ladunku,numer_kwitu_paletowego, zostawil_na_zaladunku, wyjechalo_z_zaladunku, dostarczyl,
                    odebral_z_rozladunku, saldo_przewoznik, saldo_klient, uwagi, nr_noty, statu_noty, kwota_noty,
                    waluta_noty, staly_przewoznik, data_wyslania_maila_paletowego, status_rozliczenia, nr_faktury_kleinta,
                    status_faktury_klienta, kwota_faktury_klienta, data_wystawienia_faktury_klienta
                )
                VALUES(
                     {i},'KW123456', {10*i}, 5, {7*i}, 3, 100, 50, 'Brak uwag', 'NOTA123', 'Oplacona', '500.00', 'PLN', TRUE,
                    '2025-01-15', 'Zrealizowana', 'FV123456', 'Oplacona', '500.00', '2025-01-10'
                )'''
                self.cursor.execute(query)
    @add_try
    def apply_filters(self,filter_conditions='', filter_values='',insideQuerry=None, order_by=None, database='loads'):
        query =insideQuerry + (f" WHERE {' AND '.join(filter_conditions)}" if filter_conditions else '') + (f" ORDER BY {order_by[0]} {'ASC' if order_by[1] == 1 else 'DESC'}" if order_by and order_by[0] and not order_by[1] == 0 else '')
        self.cursor.execute(query, filter_values)

        return self.cursor.fetchall()

    @add_try
    def save_excel_ladunki(self, przewoznik, numer, zaladunki, rozladunki, data_rozladunku, zlecenie,status_dokumentow_cmr):
        try:
            self.cursor.execute('''
                    SELECT COUNT(*) FROM loads WHERE numer = ? AND zlecenie = ?
                ''', (numer, zlecenie))

            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute('''
                    INSERT INTO loads (przewoznik, numer, zlecenie, oryginaly_dokumentow, skany_dokumentow,
                      wymiana_palet, kontrolowana_temperatura, wydruk_z_termografu, status_dokumenty,
                      zaladunki, rozladunki, data_rozladunku,status_dokumnetow_cmr, opoznienie_rozladunek,opoznienie_faktura,opoznienie_termograf,
                      wysylka_maila_dokumnety, uwagi_do_dokumentow,
                      faktura_sprzedazowa, data_platonsci_faktury, status_faktury, data_wyslania_faktury,
                      wysylka_faktur, wysylka_dokumentow, wymagane_oryginaly, nip_przewoznika, nr_faktury,
                      data_platnosci, status, wysylka_maila_faktury,wysylka_maila_termograf, uwagi_do_faktur, spedytor,mail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                ''', (przewoznik, numer, zlecenie, False, False,False,False,False, 'DO WINDYKACJI', zaladunki, rozladunki, data_rozladunku,
                      status_dokumentow_cmr,'','','', '','', '', '', '','', '', '', '','','', '', '', '', '', '', '', ''))
        except:
            self.cursor.execute('''
                UPDATE loads SET przewoznik = ?, zaladunki = ?, rozladunki = ?, data_rozladunku = ? WHERE numer = ? AND zlecenie = ?
            ''', (przewoznik, zaladunki, rozladunki, data_rozladunku, numer, zlecenie))

    @add_try
    def set_date_of_mail_sending(self,column,nr_ladunku,nr_zlecenia):
        self.cursor.execute(f'''SELECT {column}  FROM loads WHERE numer = ? AND zlecenie = ? ''',[nr_ladunku,nr_zlecenia])
        r = self.cursor.fetchone()
        if r and r[0]:
            new_dates = '\n'.join([datetime.datetime.now().strftime("%d-%m-%Y"),r[0]])
        else:
            new_dates = datetime.datetime.now().strftime("%d-%m-%Y")

        self.cursor.execute(f'''
                    UPDATE loads SET 
                        {column} = ?
                    WHERE numer = ? AND zlecenie = ?
                ''', [new_dates,nr_ladunku,nr_zlecenia])

    @add_try
    def update_excel_ladunki_rwp(self, klient, przesylka, numer_klienta, faktura_sprzedazowa):

        self.cursor.execute('''
            SELECT COUNT(*) FROM loads WHERE  numer = ?
        ''', (przesylka, ))

        print(przesylka + " || " + numer_klienta + " || " + faktura_sprzedazowa)

        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute('''
                UPDATE loads SET klient = ?, numer_klienta = ?, faktura_sprzedazowa = ? WHERE numer = ?
            ''', (klient, numer_klienta, faktura_sprzedazowa, przesylka))


    @add_try
    def save_selection_window(self,values):
        if not self.cursor:
            messagebox.showerror("Error", f"Not connected to database")
            return
        self.cursor.execute('''
                    UPDATE loads SET 
                        oryginaly_wyslane = ?,
                        oryginaly_dokumentow = ?,
                        skany_dokumentow = ?,
                        wymiana_palet = ?,
                        kontrolowana_temperatura = ?,
                        wydruk_z_termografu = ?,
                        uwagi_do_dokumentow = ?,
                        uwagi_do_faktur = ?,
                        status_dokumenty = ?
                    WHERE klient = ? AND przewoznik = ? AND numer = ? AND zlecenie = ?
                ''', values)
        self.conn.commit()

    @add_try
    def save_selection_checkboxes(self, values):
        '''5 wartosci checkboxow potem klient przewoznik numer i zlecenie'''
        if not self.cursor:
            messagebox.showerror("Error", f"Not connected to database")
            return
        self.cursor.execute('''
                     UPDATE loads SET 
                         oryginaly_wyslane = ?,
                         oryginaly_dokumentow = ?,
                         skany_dokumentow = ?,
                         wymiana_palet = ?,
                         kontrolowana_temperatura = ?,
                         wydruk_z_termografu = ?,
                         status_dokumenty = ?
                     WHERE klient = ? AND numer = ? AND przewoznik = ?  AND zlecenie = ?
                 ''', values)
        self.conn.commit()

    @add_try
    def save_selection_window_pallets(self, values):
        self.cursor.execute('''
                     UPDATE pallets SET 
                        numer_kwitu_paletowego = ?,
                        zostawil_na_zaladunku = ?,
                        wyjechalo_z_zaladunku = ?,
                        dostarczyl = ?,
                        odebral_z_rozladunku = ?,
                        status_rozliczenia = ?,
                        uwagi = ?,
                     WHERE klient = ? AND przewoznik = ? AND numer = ? AND zlecenie = ?
                 ''', values)
        self.conn.commit()



    @add_try
    def update_contractors(self,val):
        self.cursor.execute('''   
                        UPDATE loads SET 
                            mail = ?,
                            nip_przewoznika = ?
                        WHERE przewoznik = ?
                  ''', val)





    @add_try
    def update_sales_issued(self,val):

        self.cursor.execute('''
                      UPDATE loads SET
                           data_platonsci_faktury = ?,
                           status_faktury = ?,
                           data_wyslania_faktury = ?,
                           faktura_sprzedazowa = ?
                      WHERE numer = ? 
                  ''', val)

    @add_try
    def update_purchase_issued(self, val):

        self.cursor.execute('''
            UPDATE loads SET
                data_platnosci = ?,
                status = ?,
                nr_faktury = ?
            WHERE przewoznik = ? AND zlecenie = ?
        ''', val)


    def generate_inside_quary(self, columnsToDatabaseName):
        if 'SWITCH' in columnsToDatabaseName:
            return
        insideQuerry = ''
        for col in columnsToDatabaseName.keys():
            insideQuerry += columnsToDatabaseName[col] + ","
        return insideQuerry.strip(',')