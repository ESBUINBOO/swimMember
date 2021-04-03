from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Union
import pydantic


@dataclass
class Bahnlaenge(str, Enum):
    kuba = "25"
    laba = "50"
    fw = "FW"
    alle_bahnlaengen = "AL"


@dataclass
class ZeitMessung(str, Enum):
    handzeit = "HANDZEIT"
    automatisch = "AUTOMATISCH"
    halb_automatisch = "HALBAUTOMATISCH"

@dataclass
class Technik(str, Enum):
    freistil = "F"
    ruecken = "R"
    brust = "B"
    schmetterling = "S"
    lagen = "L"
    beliebig = "X"


@dataclass
class Ausuebung(str, Enum):
    ganze_lage = "GL"
    beine = "BE"
    arme = "AR"
    start = "ST"
    wende = "WE"
    gleituebung = "GB"
    beliebig = "X"


@dataclass
class Geschlecht(str, Enum):
    maennlich = "M"
    weiblich = "W"
    mixed = "X"


@dataclass
class ZuordnungBestenliste(str, Enum):
    schwimmen_masters = "MS"
    freiwasser = "FW"
    kindgerechter_wk = "KG"
    anderes = "XX"


@dataclass
class Wettkampfart(str, Enum):
    vorlauf = "V"
    zwischen_lauf = "Z"
    finale = "F"
    entscheidung = "E"


@dataclass
class Wertungsklasse(str, Enum):
    jahrgang = "JG"
    altersklasse = "AK"


@dataclass
class MeldegeldTyp(str, Enum):
    pauschale = "Meldegeldpauschale"
    einzel = "Einzelmeldegeld"
    staffel = "Staffelmeldegeld"
    wk = "Wkmeldegeld"
    mannschaft = "Mannschaftsmeldegeld"


@dataclass
class Address(pydantic.BaseModel):
    """
    required fields:
    """
    __slots__ = ["strasse", "plz", "ort", "land"]
    strasse: str
    plz: str
    ort: str
    land: str

    # @pydantic.validator('strasse', pre=True, always=True, check_fields=False)
    # def strasse(cls, v):
    #     return v or ""
    #
    # @pydantic.validator('plz', pre=True, always=True, check_fields=False)
    # def plz(cls, v):
    #     return v or ""
    #
    # @pydantic.validator('ort', pre=True, always=True, check_fields=False)
    # def ort(cls, v):
    #     return v or ""
    #
    # @pydantic.validator('land', pre=True, always=True, check_fields=False)
    # def land(cls, v):
    #     return v or ""


@dataclass
class Contact(pydantic.BaseModel):
    """
    required fields: email
    """
    __slots__ = ["telefon", "fax", "email"]
    telefon: Optional[str]
    fax: Optional[str]
    email: str

    # @pydantic.validator('telefon', pre=True, always=False, check_fields=False)
    # def telefon(cls, v):
    #     return v or ""
    #
    # @pydantic.validator('fax', pre=True, always=False, check_fields=False)
    # def fax(cls, v):
    #     return v or ""
    #
    # @pydantic.validator('email', pre=True, always=False, check_fields=False)
    # def email(cls, v):
    #     return v or ""


@dataclass
class Format:
    """
        required fields: listart, verson
    """
    __slots__ = ["listart", "version"]
    listart: str
    version: int


@dataclass
class Erzeuger:
    """
        required fields: software, version, kontakt
    """
    __slots__ = ["software", "version", "kontakt"]
    software: str
    version: str
    kontakt: str


@dataclass
class Veranstaltung:
    """
    required fields: veranstaltungs_beschreibung, veranstaltungs_ort, bahnlaenge, zeitmessung
    """
    __slots__ = ["veranstaltungs_beschreibung", "veranstaltungs_ort", "bahnlaenge", "zeitmessung"]
    veranstaltungs_beschreibung: str
    veranstaltungs_ort: str
    bahnlaenge: Bahnlaenge
    zeitmessung: ZeitMessung


@dataclass
class VeranstaltungsOrt:
    """
    required fields: name_schwimmhalle, ort, land
    """
    #__slots__ = ["strasse", "plz", "ort", "land", "telefon", "fax", "email"]
    name_schwimmhalle: str
    contact: Contact
    address: Address


@dataclass
class Abschnitt:
    __slots__ = ["abschnitts_nummer", "abschnitts_datum", "einlass",
                 "kampfrichtersitzung", "anfangszeit", "relative_angaben"]
    abschnitts_nummer: int
    abschnitts_datum: str
    einlass: str
    kampfrichtersitzung: str
    anfangszeit: str
    relative_angaben: str


@dataclass
class AusschreibungImNetz:
    """
    required fields:
    """
    __slots__ = ["internet_adresse"]
    internet_adresse: str


@dataclass
class Veranstalter:
    """
    required_fields: name_veranstalter
    """
    __slots__ = ["name_veranstalter"]
    name_veranstalter: str


@dataclass
class Ausrichter:
    __slots__ = ["name_ausrichter", "name_kontakt", "address", "contact"]
    name_ausrichter: str
    name_kontakt: str
    address: Address
    contact: Contact


@dataclass
class MeldeAdresse:
    """
    required fields: name_meldeadresse, email
    """
    __slots__ = ["name_meldeadresse", "address", "contact"]
    name_meldeadresse: str
    address: Address
    contact: Contact


@dataclass
class Meldeschluss:
    """
    required fields: datum, uhrzeit
    """
    datum: str
    uhrzeit: str


@dataclass
class Bankverbindung:
    """
    required fields: iban, bic
    """
    __slots__ = ["name_bank", "iban", "bic"]
    name_bank: str
    iban: str
    bic: str


@dataclass
class Besonderes:
    """
    required fields: anmerkungen
    """
    __slots__ = ["anmerkungen"]
    anmerkungen: str


@dataclass
class Nachweis:
    """
    required fields: nachweis_von, bahnlaenge
    """
    __slots__ = ["nachweis_von", "nachweis_bis", "bahnlaenge"]
    nachweis_von: str
    nachweis_bis: str
    bahnlaenge: Bahnlaenge


@dataclass
class Wettkampf:
    """
    required fields:
    """
    __slots__ = ["wettkampf_nr", "wettkampf_art", "abschnitts_nr", "anzahl_starter", "einzelstrecke",
                 "technik", "ausuebung", "geschlecht", "zuordnung_bestenliste",
                 "quali_wettkampfnr", "quali_wettkampfart"]
    wettkampf_nr: int
    wettkampf_art: str
    abschnitts_nr: int
    anzahl_starter: int
    einzelstrecke: int
    technik: Technik
    ausuebung: Ausuebung
    geschlecht: Geschlecht
    zuordnung_bestenliste: ZuordnungBestenliste
    quali_wettkampfnr: int
    quali_wettkampfart: Wettkampfart


@dataclass
class Wertung:
    """
    required fields:
    """
    __slots__ = ["wettkampf_nr", "wettkampf_art", "wertungs_id", "wertungs_klasse", "min_jg", "max_jg", "geschlecht",
                 "wertungs_name"]
    wettkampf_nr: int
    wettkampf_art: Wettkampfart
    wertungs_id: int
    wertungs_klasse: Wertungsklasse
    min_jg: int
    max_jg: int
    geschlecht: Geschlecht
    wertungs_name: str


@dataclass
class Pflichtzeit:
    """
    required fields
    """
    __slots__ = ["wettkampf_nr", "wettkampf_art", "wertungs_klasse", "min_jg", "max_jg", "pflichtzeit", "geschlecht"]
    wettkampf_nr: int
    wettkampf_art: Wettkampfart
    wertungs_klasse: Wertungsklasse
    min_jg: int
    max_jg: int
    pflichtzeit: str
    geschlecht: Geschlecht


@dataclass
class Meldegeld:
    """
    required fields: meldegeld_typ, betrag
    """
    __slots__ = ["meldegeld_typ", "betrag", "wettkampf_nr"]
    meldegeld_typ: MeldegeldTyp
    betrag: float
    wettkampf_nr: int


@dataclass
class Verein:
    """
    required fields: bezeichnung, kennzahl, landes_schwimmverband, fina_nationen_kuerzel
    """
    __slots__ = ["bezeichnung", "kennzahl", "landes_schwimmverband", "fina_nationen_kuerzel"]
    bezeichnung: str
    kennzahl: int
    landes_schwimmverband: int
    fina_nationen_kuerzel: str


# @dataclass
# class Ansprechpartner(Address, Contact):
#     """
#     required fields: name, email
#     """
#     name: str


@dataclass
class KampfrichterGruppe(str, Enum):
    wk_richter = "WKR"
    auswerter = "AUS"
    schiedsrichter = "SCH"
    sprecher = "SPR"


@dataclass
class KariPosition(str, Enum):
    starter = "STA"
    auswerter = "AUS"
    zielrichter_obmann = "ZRO"
    zielrichter = "ZR"
    zeitnehmer_obmann = "ZNO"
    zeitnehmer = "ZN"
    reserve_zeitnehmer = "RZN"
    schwimmrichter = "SR"
    wenderichter_obmann = "WRO"
    wenderichter = "WR"
    protokoll_fuehrer = "PKF"
    schiedsrichter = "SCH"
    sprecher = "SPR"
    sonstiges = "ZBV"


@dataclass
class KariMeldung:
    __slots__ = ["nr_kampfrichter", "name", "kampfrichter_gruppe"]
    nr_kampfrichter: int
    name: str
    kampfrichter_gruppe: KampfrichterGruppe


@dataclass
class KariAbschnitt:
    __slots__ = ["nr_kampfrichter", "abschnitts_nummer", "einsatzwunsch"]
    nr_kampfrichter: int
    abschnitts_nummer: int
    einsatzwunsch: KariPosition


@dataclass
class Trainer:
    """
    required fields: trainer_id, trainer_name
    """
    __slots__ = ["trainer_id", "trainer_name"]
    trainer_id: int
    trainer_name: str


@dataclass
class PNMeldung:
    """
    required fields: name, dsv_id, schwimmer_id, geschlecht
    """
    __slots__ = ["name", "dsv_id", "schwimmer_id", "geschlecht", "trainer_id"]
    name: str
    dsv_id: int
    schwimmer_id: int
    geschlecht: Geschlecht
    trainer_id: int


@dataclass
class StartPN:
    """
    required fields: schwimmer_id, wk_nummer
    """
    __slots__ = ["schwimmer_id", "wk_nummer", "meldezeit"]
    schwimmer_id: int
    wk_nummer: int
    meldezeit: str


@dataclass
class STMeldung:
    """
    required fields: staffel_nr, staffel_id, wertungsklasse, min_jg
    """
    __slots__ = ["staffel_nr", "staffel_id", "wertungsklasse", "min_jg", "max_jg", "staffel_name"]
    staffel_nr: int
    staffel_id: int
    wertungsklasse: Wertungsklasse
    min_jg: int
    max_jg: int
    staffel_name: str


@dataclass
class StartST:
    """
    required fields: staffel_id, wk_nummer
    """
    __slots__ = ["staffel_id", "wk_nummer", "meldezeit"]
    staffel_id: int
    wk_nummer: int
    meldezeit: str


@dataclass
class StaffelPerson:
    """
    required fields: staffel_id, wk_nr, schwimmer_id, schwimmer_start_position
    """
    __slots__ = ["staffel_id", "wk_nr", "schwimmer_id", "schwimmer_start_position"]
    staffel_id: int
    wk_nr: int
    schwimmer_id: int
    schwimmer_start_position: int


@dataclass
class Kampfgericht:
    """
    required fields: abschnitts_nr, position, kari_name, kari_verein
    """
    __slots__ = ["abschnitts_nr", "position", "kari_name", "kari_verein"]
    abschnitts_nr: int
    position: KariPosition
    kari_name: str
    kari_verein: str


@dataclass
class Person:
    """
    required fields: name, dsv_id, schwimemr_id, geschlecht
    """
    __slots__ = ["name", "dsv_id", "schwimemr_id", "geschlecht", "altersklasse"]
    name: str
    dsv_id: int
    schwimmer_id: int
    geschlecht: Geschlecht
    jahrgang: int
    altersklasse: int


@dataclass
class GrundDerNichtWertung(str, Enum):
    disqualifikation = "DS"
    nicht_angetreten = "NA"
    abmeldung = "AB"
    aufgegeben = "AU"
    zeitueberschreitung = "ZU"


@dataclass
class ReaktionsArt(str, Enum):
    start_vor_startsignal = "-"
    start_nach_startsignal = "+"


@dataclass
class ENM:
    norm_erreicht = "E"
    enm_faellig = "F"
    norm_nicht_erreicht_nachweisbar = "N"



@dataclass
class PersonenErgebnis:
    """
    required fields: schwimmer_id, wettkampf_nr, wk_art, wertungs_id, platz, endzeit
    """
    __slots__ = ["schwimmer_id", "wettkampf_nr", "wk_art", "wertungs_id", "platz",
                 "endzeit", "grund_der_nicht_wertung", "disq_bemerkung", "enm"]
    schwimmer_id: int
    wettkampf_nr: int
    wk_art: Wettkampfart
    wertungs_id: int
    platz: int
    endzeit: str
    grund_der_nicht_wertung: GrundDerNichtWertung
    disq_bemerkung: str
    enm: ENM


@dataclass
class PNZwischenZeit:
    """
    required fields: schwimmer_id, wk_nr, wk_art, distanz, zwischen_zeit
    """
    __slots__ = ["schwimmer_id", "wk_nr", "wk_art", "distanz", "zwischen_zeit"]
    schwimmer_id: int
    wk_nr: int
    wk_art: Wettkampfart
    distanz: int
    zwischen_zeit: str


@dataclass
class PNReaktion:
    """
    required fields: schwimmer_id, wk_nr, wk_art, reaktion_zeit
    """
    __slots__ = ["schwimmer_id", "wk_nr", "wk_art", "reaktion_art", "reaktion_zeit"]
    schwimmer_id: int
    wk_nr: int
    wk_art: Wettkampfart
    reaktion_art: ReaktionsArt
    reaktion_zeit: str


@dataclass
class Staffel:
    """
    required fields: staffel_nr, staffel_id, wertungsklasse, min_jg
    """
    __slots__ = ["staffel_nr", "staffel_id", "wertungsklasse", "min_jg", "max_jg"]
    staffel_nr: int
    staffel_id: int
    wertungsklasse: Wertungsklasse
    min_jg: int
    max_jg: int


@dataclass
class StaffelPerson:
    """
    required fields: staffel_id, wk_nr, wk_art, name, dsv_id, schwimmer_start_position, geschlecht, jahrgang
    """
    __slots__ = ["staffel_id", "wk_nr", "wk_art", "name", "dsv_id",
                 "schwimmer_start_position", "geschlecht", "jahrgang"]
    staffel_id: int
    wk_nr: int
    wk_art: Wettkampfart
    name: str
    dsv_id: int
    schwimmer_start_position: int
    geschlecht: Geschlecht
    jahrgang: int
    altersklasse: int


@dataclass
class StaffelErgebnis:
    """
    required fields: staffel_id, wk_nr, wk_art, wertungs_id, platz, endzeit
    """
    __slots__ = ["staffel_id", "wk_nr", "wk_art", "wertungs_id", "platz", "endzeit", "grund_nicht_wertung",
                 "dsq_schwimmer_start_position", "dsq_bemerkung", "enm"]
    staffel_id: int
    wk_nr: int
    wk_art: Wettkampfart
    wertungs_id: int
    platz: int
    endzeit: str
    grund_nicht_wertung: GrundDerNichtWertung
    dsq_schwimmer_start_position: int
    dsq_bemerkung: str
    enm: ENM


@dataclass
class STZwischenzeit:
    """
    required fields: staffel_id, wk_nr, wk_art, schwimmer_start_position, distanz, zwischenzeit
    """
    __slots__ = ["staffel_id", "wk_nr", "wk_art", "schwimmer_start_position", "distanz", "zwischenzeit"]
    staffel_id: int
    wk_nr: int
    wk_art: Wettkampfart
    schwimmer_start_position: int
    distanz: int
    zwischenzeit: int


@dataclass
class STAbloese:
    """
    required fields: staffel_id, wk_nr, wk_art, schwimmer_start_position, reaktion_art, reaktion_zeit
    """
    __slots__ = ["staffel_id", "wk_nr", "wk_art", "schwimmer_start_position", "reaktion_art", "reaktion_zeit"]
    staffel_id: int
    wk_nr: int
    wk_art: Wettkampfart
    schwimmer_start_position: int
    reaktion_art: ReaktionsArt
    reaktion_zeit: str


@dataclass
class PNErgebnis:
    """
    required fields: wk_nr, wk_art, wertungs_id, platz, name, dsv_id, schwimmer_id,
    geschlecht, jahrgang, verein, vereinskennzahl, endzeit
    """
    __slots__ = ["wk_nr", "wk_art", "wertungs_id", "platz", "grund_nicht_wertung", "name", "dsv_id", "schwimmer_id",
    "geschlecht", "jahrgang", "altersklasse", "verein", "vereinskennzahl", "endzeit", "dsq_bemerkung", "enm"]
    wk_nr: int
    wk_art: Wettkampfart
    wertungs_id: int
    paltz: int
    grund_nicht_wertung: GrundDerNichtWertung
    name: str
    dsv_id: int
    schwimmer_id: int
    geschlecht: Geschlecht
    jahrgang: int
    altersklasse: int
    verein: str
    vereinskennzahl: int
    endzeit: str
    dsq_bemerkung: str
    enm: ENM