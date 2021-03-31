import pandas as pd
from dsv6_data_classes import *


class Dsv6ClassMapper:
    def __init__(self):
        pass

    @staticmethod
    def __address_mapper(data):
        return pd.DataFrame(columns=["strasse", "plz", "ort", "land"],
                            data=data).to_dict('records')[0]

    @staticmethod
    def __contact_mapper(data):
        return pd.DataFrame(columns=["telefon", "fax", "email"],
                            data=data).to_dict('records')[0]

    @staticmethod
    def __format_mapper(line_values):
        format_map = {}
        for i in range(0, len(line_values) - 1):
            if i == 0:
                format_map["listart"] = line_values[0][1]
            if i == 1:
                format_map["version"] = line_values[1][0]
        return format_map

    def __erzeuger_mapper(self):
        pass

    @staticmethod
    def __veranstaltung_mapper(line):
        base = pd.DataFrame(columns=["veranstaltungs_beschreibung", "veranstaltungs_ort", "bahnlaenge", "zeitmessung"],
                            data=[line.split(';')[:4]]).to_dict('records')[0]
        return base

    def __veranstaltungsort_mapper(self, line):
        base = pd.DataFrame(columns=["name_schwimmhalle"],
                            data=[line.split(';')[0:1]]).to_dict('records')[0]
        address = self.__address_mapper(data=[line.split(';')[1:5]])
        contact = self.__contact_mapper(data=[line.split(';')[5:8]])
        base["address"], base["contact"] = address, contact
        return base

    def __ausschreibung_im_netz_mapper(self, line):
        base = pd.DataFrame(columns=["internet_adresse"],
                            data=[line.split(';')[0:1]]).to_dict('records')[0]
        return base

    @staticmethod
    def __veranstalter_mapper(line):
        base = pd.DataFrame(columns=["name_veranstalter"],
                            data=[line.split(';')[0:1]]).to_dict('records')[0]
        return base

    def __ausrichter_mapper(self, line):
        base = pd.DataFrame(columns=["name_ausrichter", "name_kontakt"],
                            data=[line.split(';')[0:2]]).to_dict('records')[0]
        address = self.__address_mapper(data=[line.split(';')[2:6]])
        contact = self.__contact_mapper(data=[line.split(';')[6:9]])
        base["address"], base["contact"] = address, contact
        return base

    def __meldeadresse_mapper(self, line):
        base = pd.DataFrame(columns=["name_meldeadresse"],
                            data=[line.split(';')[0:1]]).to_dict('records')[0]
        address = self.__address_mapper(data=[line.split(';')[1:5]])
        contact = self.__contact_mapper(data=[line.split(';')[5:8]])
        base["address"], base["contact"] = address, contact
        return base

    def __meldeschluss_mapper(self, line):
        base = pd.DataFrame(columns=["datum", "uhrzeit"],
                            data=[line.split(';')[0:2]]).to_dict('records')[0]
        return base

    def __bankverbindung_mapper(self):
        pass

    def __besonderes_mapper(self):
        pass

    def __nachweis_mapper(self):
        pass

    def __abschnitt_mapper(self):
        pass

    def __wettkampf_mapper(self):
        pass

    def __wertung_mapper(self):
        pass

    def __pflichtzeit_mapper(self):
        pass

    def __meldegeld_mapper(self):
        pass

    def __verein_mapper(self):
        pass

    def __ansprechpartner_mapper(self):
        pass

    def __karimeldung_mapper(self):
        pass

    def __kariabschnitt_mapper(self):
        pass

    def __trainer_mapper(self):
        pass

    def __pnmeldung_mapper(self):
        pass

    def __startpn_mapper(self):
        pass

    def __stmeldung_mapper(self):
        pass

    def __startst_mapper(self):
        pass

    def __staffelperson_mapper(self):
        pass

    def __kampfgericht_mapper(self):
        pass

    def __person_mapper(self):
        pass

    def __personenrgebnis_mapper(self):
        pass

    def __pnzwischenzeit_mapper(self):
        pass

    def __pnreaktion_mapper(self):
        pass

    def __staffel_mapper(self):
        pass

    def __staffelergebnis_mapper(self):
        pass

    def __stzwischenzeit_mapper(self):
        pass

    def __stabloese_mapper(self):
        pass

    def __pnergebnis_mapper(self):
        pass

    def __stergebnis_mapper(self):
        pass
