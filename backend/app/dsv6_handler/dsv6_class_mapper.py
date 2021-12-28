import pandas as pd
from .dsv6_data_classes import Verein, Pflichtzeit, Ansprechpartner, Address, Contact, Veranstalter, \
    Veranstaltung, Bahnlaenge, ZeitMessung, VeranstaltungsOrt, MeldeAdresse, Meldeschluss, Meldegeld, MeldegeldTyp, \
    KariMeldung, KariAbschnitt, KariPosition, Kampfgericht, KampfrichterGruppe, Technik, Ausrichter, Ausuebung, \
    AusschreibungImNetz, Bankverbindung, Besonderes, Nachweis, Abschnitt, Trainer, Wettkampf, Wertung, Wertungsklasse, \
    PNMeldung, PNReaktion, PNErgebnis, PNZwischenZeit, STMeldung, STZwischenzeit, STAbloese, StaffelErgebnis, \
    Staffel, StaffelPerson, StartPN, StartST, Person, PersonenErgebnis, Wettkampfart, GrundDerNichtWertung, \
    Geschlecht, ENM
from dataclasses import asdict


class Dsv6BaseClassMapper:
    def __init__(self):
        pass

    def __erzeuger_mapper(self):
        pass

    @staticmethod
    def __format_mapper(line_values):
        format_map = {}
        for i in range(0, len(line_values) - 1):
            if i == 0:
                format_map["listart"] = line_values[0][1]
            if i == 1:
                format_map["version"] = line_values[1][0]
        return format_map

    @staticmethod
    def __address_mapper(data):
        base = pd.DataFrame(columns=["strasse", "plz", "ort", "land"],
                            data=data).to_dict('records')[0]
        return asdict(Address(**base))

    @staticmethod
    def __contact_mapper(data):
        base = pd.DataFrame(columns=["telefon", "fax", "email"],
                            data=data).to_dict('records')[0]
        return asdict(Contact(**base))

    @staticmethod
    def __veranstaltung_mapper(line):
        base = pd.DataFrame(columns=["veranstaltungs_beschreibung", "veranstaltungs_ort"],
                            data=[line.split(';')[:2]]).to_dict('records')[0]
        bahnlaenge = pd.DataFrame(columns=["bahnlaenge"], data=[line.split(';')[2:3]]).to_dict('records')[0]
        bahnlaenge_obj = Bahnlaenge(bahnlaenge["bahnlaenge"])
        zeitmessung = pd.DataFrame(columns=["zeitmessung"], data=[line.split(';')[3:4]]).to_dict('records')[0]
        zeitmessung_obj = ZeitMessung(zeitmessung["zeitmessung"])
        return asdict(Veranstaltung(bahnlaenge=bahnlaenge_obj.value, zeitmessung=zeitmessung_obj.value,
                                    veranstaltungs_beschreibung=base["veranstaltungs_beschreibung"],
                                    veranstaltungs_ort=base["veranstaltungs_ort"]))

    def __wettkampf_mapper(self, line):
        base = pd.DataFrame(columns=Wettkampf.__slots__,
                            data=[line.split(';')[:len(Wettkampf.__slots__)]]).to_dict('records')[0]
        return asdict(Wettkampf(**base))

    def __wertung_mapper(self, line):
        base = pd.DataFrame(columns=Wertung.__slots__,
                            data=[line.split(';')[:len(Wertung.__slots__)]]).to_dict('records')[0]
        return asdict(Wertung(**base))


class Dsv6DefinitionClassMapper(Dsv6BaseClassMapper):
    def __init__(self):
        super().__init__()

    def __veranstaltungsort_mapper(self, line):
        base = pd.DataFrame(columns=VeranstaltungsOrt.__slots__,
                            data=[line.split(';')[0:len(VeranstaltungsOrt.__slots__)]]).to_dict('records')[0]
        return asdict(VeranstaltungsOrt(**base))

    def __ausschreibung_im_netz_mapper(self, line):
        base = pd.DataFrame(columns=AusschreibungImNetz.__slots__,
                            data=[line.split(';')[0:len(AusschreibungImNetz.__slots__)]]).to_dict('records')[0]
        return asdict(AusschreibungImNetz(**base))

    @staticmethod
    def __veranstalter_mapper(line):
        base = pd.DataFrame(columns=Veranstalter.__slots__,
                            data=[line.split(';')[0:len(Veranstalter.__slots__)]]).to_dict('records')[0]
        return asdict(Veranstalter(**base))

    def __ausrichter_mapper(self, line):
        base = pd.DataFrame(columns=Ausrichter.__slots__,
                            data=[line.split(';')[0:len(Ausrichter.__slots__)]]).to_dict('records')[0]
        return asdict(Ausrichter(**base))

    def __meldeadresse_mapper(self, line):
        base = pd.DataFrame(columns=MeldeAdresse.__slots__,
                            data=[line.split(';')[0:len(MeldeAdresse.__slots__)]]).to_dict('records')[0]
        return asdict(MeldeAdresse(**base))

    def __meldeschluss_mapper(self, line):
        base = pd.DataFrame(columns=Meldeschluss.__slots__,
                            data=[line.split(';')[0:len(Meldeschluss.__slots__)]]).to_dict('records')[0]
        return asdict(Meldeschluss(**base))

    def __bankverbindung_mapper(self, line):
        base = pd.DataFrame(columns=Bankverbindung.__slots__,
                            data=[line.split(';')[0:len(Bankverbindung.__slots__)]]).to_dict('records')[0]
        return asdict(Bankverbindung(**base))

    def __besonderes_mapper(self, line):
        base = pd.DataFrame(columns=Besonderes.__slots__,
                            data=[line.split(';')[0:len(Besonderes.__slots__)]]).to_dict('records')[0]
        return asdict(Besonderes(**base))

    def __nachweis_mapper(self, line):
        base = pd.DataFrame(columns=Nachweis.__slots__,
                            data=[line.split(';')[0:len(Nachweis.__slots__)]]).to_dict('records')[0]
        return asdict(Nachweis(**base))

    def __abschnitt_mapper(self, line):
        base = pd.DataFrame(columns=Abschnitt.__slots__,
                            data=[line.split(';')[0:len(Abschnitt.__slots__)]]).to_dict('records')[0]
        return asdict(Abschnitt(**base))

    def __pflichtzeit_mapper(self, line):
        base = pd.DataFrame(columns=Pflichtzeit.__slots__,
                            data=[line.split(';')[:len(Pflichtzeit.__slots__)]]).to_dict('records')[0]
        return asdict(Pflichtzeit(**base))

    def __meldegeld_mapper(self, line):
        base = pd.DataFrame(columns=Meldegeld.__slots__,
                            data=[line.split(';')[:len(Meldegeld.__slots__)]]).to_dict('records')[0]
        meldegeld_typ = MeldegeldTyp(base["meldegeld_typ"])
        return asdict(Meldegeld(meldegeld_typ=meldegeld_typ.value,
                                betrag=base["betrag"],
                                wettkampf_nr=base["wettkampf_nr"]))

    def __verein_mapper(self, line):
        base = pd.DataFrame(columns=Verein.__slots__,
                            data=[line.split(';')[0:len(Verein.__slots__)]]).to_dict('records')[0]
        return asdict(Verein(**base))

    def __ansprechpartner_mapper(self, line):
        base = pd.DataFrame(columns=Ansprechpartner.__slots__,
                            data=[line.split(';')[0:len(Ansprechpartner.__slots__)]]).to_dict('records')[0]
        return asdict(Ansprechpartner(**base))

    def __karimeldung_mapper(self, line):
        base = pd.DataFrame(columns=KariMeldung.__slots__,
                            data=[line.split(';')[0:len(KariMeldung.__slots__)]]).to_dict('records')[0]
        return asdict(KariMeldung(**base))

    def __kariabschnitt_mapper(self, line):
        base = pd.DataFrame(columns=KariAbschnitt.__slots__,
                            data=[line.split(';')[0:len(KariAbschnitt.__slots__)]]).to_dict('records')[0]
        return asdict(KariAbschnitt(**base))

    def __trainer_mapper(self, line):
        base = pd.DataFrame(columns=Trainer.__slots__,
                            data=[line.split(';')[0:len(Trainer.__slots__)]]).to_dict('records')[0]
        return asdict(Trainer(**base))

    def __pnmeldung_mapper(self, line):
        base = pd.DataFrame(columns=PNMeldung.__slots__,
                            data=[line.split(';')[0:len(PNMeldung.__slots__)]]).to_dict('records')[0]
        return asdict(PNMeldung(**base))

    def __startpn_mapper(self, line):
        base = pd.DataFrame(columns=StartPN.__slots__,
                            data=[line.split(';')[0:len(StartPN.__slots__)]]).to_dict('records')[0]
        return asdict(StartPN(**base))

    def __stmeldung_mapper(self, line):
        base = pd.DataFrame(columns=STMeldung.__slots__,
                            data=[line.split(';')[0:len(STMeldung.__slots__)]]).to_dict('records')[0]
        return asdict(STMeldung(**base))

    def __startst_mapper(self, line):
        base = pd.DataFrame(columns=StartST.__slots__,
                            data=[line.split(';')[0:len(StartST.__slots__)]]).to_dict('records')[0]
        return asdict(StartST(**base))

    def __staffelperson_mapper(self, line):
        base = pd.DataFrame(columns=StaffelPerson.__slots__,
                            data=[line.split(';')[0:len(StaffelPerson.__slots__)]]).to_dict('records')[0]
        return asdict(StaffelPerson(**base))

    def __kampfgericht_mapper(self, line):
        base = pd.DataFrame(columns=Kampfgericht.__slots__,
                            data=[line.split(';')[0:len(Kampfgericht.__slots__)]]).to_dict('records')[0]
        return asdict(Kampfgericht(**base))

    def __person_mapper(self, line):
        base = pd.DataFrame(columns=Person.__slots__,
                            data=[line.split(';')[0:len(Person.__slots__)]]).to_dict('records')[0]
        return asdict(Person(**base))

    def __personenrgebnis_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=PersonenErgebnis.__slots__,
                            data=[line.split(';')[0:len(PersonenErgebnis.__slots__)]]).to_dict('records')[0]
        return asdict(PersonenErgebnis(**base))

    def __pnzwischenzeit_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=PNZwischenZeit.__slots__,
                            data=[line.split(';')[0:len(PNZwischenZeit.__slots__)]]).to_dict('records')[0]
        return asdict(PNZwischenZeit(**base))

    def __pnreaktion_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=PNReaktion.__slots__,
                            data=[line.split(';')[0:len(PNReaktion.__slots__)]]).to_dict('records')[0]
        return asdict(PNReaktion(**base))

    def __staffel_mapper(self, line):
        base = pd.DataFrame(columns=Staffel.__slots__,
                            data=[line.split(';')[0:len(Staffel.__slots__)]]).to_dict('records')[0]
        return asdict(Staffel(**base))

    def __staffelergebnis_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=StaffelErgebnis.__slots__,
                            data=[line.split(';')[0:len(StaffelErgebnis.__slots__)]]).to_dict('records')[0]
        return asdict(StaffelErgebnis(**base))

    def __stzwischenzeit_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=STZwischenzeit.__slots__,
                            data=[line.split(';')[0:len(STZwischenzeit.__slots__)]]).to_dict('records')[0]
        return asdict(STZwischenzeit(**base))

    def __stabloese_mapper(self, line):
        # todo: maybe should be in Dsv6ResultClassMapper
        base = pd.DataFrame(columns=STAbloese.__slots__,
                            data=[line.split(';')[0:len(STAbloese.__slots__)]]).to_dict('records')[0]
        return asdict(STAbloese(**base))

    def __pnergebnis_mapper(self, line):
        base = pd.DataFrame(columns=PNErgebnis.__slots__,
                            data=[line.split(';')[0:len(PNErgebnis.__slots__)]]).to_dict('records')[0]
        return asdict(PNErgebnis(**base))


class Dsv6ResultClassMapper(Dsv6BaseClassMapper):
    def __init__(self):
        super().__init__()

    def __pnergebnis_mapper(self, line):
        base = pd.DataFrame(columns=PNErgebnis.__slots__,
                            data=[line.split(';')[0:len(PNErgebnis.__slots__)]]).to_dict('records')[0]
        wk_art = Wettkampfart(base["wk_art"])
        geschlecht = Geschlecht(base["geschlecht"])
        grund_nicht_wertung = GrundDerNichtWertung(base["grund_nicht_wertung"])
        enm = ENM(base["enm"])
        base["wk_art"] = wk_art.value
        base["geschlecht"] = geschlecht.value
        base["grund_nicht_wertung"] = grund_nicht_wertung.value
        base["enm"] = enm.value
        return asdict(PNErgebnis(**base))

