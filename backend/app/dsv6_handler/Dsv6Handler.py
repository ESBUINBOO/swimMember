import os
import shutil
from collections import defaultdict
from dataclasses import asdict
import logging
import re
import sys
from datetime import datetime

from .dsv6_data_classes import *
from .dsv6_class_mapper import Dsv6DefinitionClassMapper, Dsv6ResultClassMapper

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Dsv6FileHandler(Dsv6DefinitionClassMapper, Dsv6ResultClassMapper):
    """
    # todo: der Handler soll auch Meldedateien erstellen können!
    This class handles DSV6-Files. If you want to proceed files you call the var "files_to_proceed", but you need to
    copy the list. Otherwise its a call-by-reference. The list will be manipulated while runtime. So you need to
    do something like this: for dsv_file in dsv_handler.files_to_proceed.copy()
    before you proceed files, you need to run the update() method, to get all unprocessed files from dir "files"
    Example:
        dsv_handler = Dsv6FileHandler()
        dsv_handler.update()
        for dsv_file in dsv_handler.files_to_proceed.copy():
            print("processing dsv_file {}".format(dsv_file))
            results = dsv_handler.get_results_from_file(file_to_proceed=dsv_file)
            for k, v in results.items():
                print(k, v)
    """
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.file_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files'))
        self.file_done_dir = os.path.join(self.file_dir, "done")
        self.club_names = ["W98 Hannover"]  # todo: this must be in config
        self.return_def = ["meeting_definition", "meeting_results"]
        self.files_to_proceed = []
        self.file_lines = []
        self.mapped_events = defaultdict(list)
        self.mapped_verein = defaultdict(list)
        self.mapped_groups_age = defaultdict(list)
        self.mapped_meeting = {}
        self.mapped_swimmer_ids = {}
        self.tmp_pnzwischenzeit = {}

    def update(self):
        self.__get_all_files()

    @staticmethod
    def validate_date_time(date_text):
        try:
            datetime.strptime(date_text, '%H:%M')
            return True
        except ValueError as err:
            print("Incorrect data format, should be H:M. Error: {}".format(err))
            return False

    @staticmethod
    def validate_date(date_text):
        try:
            datetime.strptime(date_text, '%d.%m.%Y')
            return True
        except ValueError as err:
            print("Incorrect data format, should be HH.MM. Error: {}".format(err))

    @staticmethod
    def add_blank(line):
        patter = "([a-zA-Z].:\S)"
        x = re.search(patter, line)
        if x:
            index = x.string.index(":") + 1
            new_line = x.string[:index] + " " + x.string[index:]
            return new_line
        return line

    def __get_all_files(self):
        self.files_to_proceed = [os.path.join(self.file_dir, f) for f in os.listdir(self.file_dir)
                                 if os.path.isfile(os.path.join(self.file_dir, f)) and f.endswith(".dsv6")]

    def __read_file(self, file_to_proceed):
        # some dsv6 software add a blank after class name, some doesnt
        with open(file_to_proceed) as f:
            self.file_lines = [self.add_blank(line=i) for i in f.read().splitlines() if i != ""]

    def __move_file_to_done(self, file_to_proceed):
        if not os.path.exists(self.file_done_dir):
            logger.info("{} doesnt exists, so I will create it".format(self.file_done_dir))
            os.mkdir(self.file_done_dir)
        shutil.move(src=file_to_proceed, dst=self.file_done_dir)
        self.files_to_proceed.remove(file_to_proceed)

    def __map_meeting(self, line_values):
        if line_values[0][0] == "VERANSTALTUNG:":
            self.mapped_meeting = {"meeting_name": " ".join(line_values[0][1:]),
                                   "date": [],
                                   "location": line_values[1][0],
                                   "course": line_values[2][0],
                                   "timing": line_values[3][0],
                                   "sections": []}
        elif line_values[0][0] == "AUSRICHTER:":
            self.mapped_meeting.update({"organizer": {"club": " ".join(line_values[0][1:]),
                                                      "contact": " ".join(line_values[1][0:]),
                                                      "email": line_values[7][0]}})
        elif line_values[0][0] == "ABSCHNITT:":
            mapped_sections = {line_values[0][1]: line_values[1][0] + " " + line_values[2][0]}
            date = line_values[1][0]
            if date not in self.mapped_meeting["date"]:
                self.mapped_meeting["date"].append(date)
            self.mapped_meeting["sections"].append(mapped_sections)

    def __map_events(self, line_values):
        mapped_event = {"competition_type": line_values[1][0],
                        "section": line_values[2][0],
                        "number_of_starters": line_values[3][0],
                        "event": line_values[4][0] + line_values[5][0],
                        "gender": line_values[7][0]}
        self.mapped_events[line_values[0][1]].append(mapped_event)

    def __map_group_ages(self, line_values):
        mapped_group_ages = {"from_to_group_ages": [int(line_values[4][0]), int(line_values[5][0])],
                             "gender": line_values[6][0],
                             "description": " ".join(line_values[6])}
        self.mapped_groups_age[line_values[2][0]].append(mapped_group_ages)

    def __reset_mappings(self):
        self.mapped_meeting = defaultdict(list)
        self.mapped_groups_age = defaultdict(list)
        self.mapped_events = defaultdict(list)
        self.file_lines = []

    def __get_format(self, file_to_proceed):
        """
        check if file is a meeting definition or a meeting result list
        """
        self.__read_file(file_to_proceed=file_to_proceed)
        if len(self.file_lines) > 0:
            for line in self.file_lines:
                line_values = [i.split() for i in line.split(';') if i != '']
                if line_values[0][0] == "FORMAT:":
                    return line_values[0][1]
        else:
            logger.info("no lines to proceed!")

    def __choose_function(self, file_to_proceed):
        file_type = self.__get_format(file_to_proceed=file_to_proceed)
        if file_type == "Wettkampfdefinitionsliste":
            # its a competition definition list
            return self.__proceed_competition_definition()
        elif file_type == "Wettkampfergebnisliste":
            # its a competition result list
            return self.__proceed_competition_result()

    def __proceed_competition_result(self):
        """
        data structur:
                    {dsv_id: [
                                {
                                    event_name: [{_wk_art_: {wertung: event_place, time: _time_}}]
                                }
                            ]
                    }
        :return:
        """
        # todo refactor the mapper funcs to the proper methods (Veranstaltung, Wettkampf, Wertung)
        logger.info("__proceed_competition_result()")
        swimmers_result = defaultdict(list)
        if len(self.file_lines) > 0:
            for line in self.file_lines:
                event_dict = defaultdict(list)
                line_values = [i.split() for i in line.split(';') if i != '']
                if line_values[0][0] == "VERANSTALTUNG:":
                    self.mapped_meeting = self._Dsv6BaseClassMapper__veranstaltung_mapper(line=line[15:])
                if line_values[0][0] == "WETTKAMPF:":
                    mapped_wettkampf = self._Dsv6BaseClassMapper__wettkampf_mapper(line=line[11:])
                    self.mapped_events[mapped_wettkampf["wettkampf_nr"]].append(
                        {"wettkampf_art": mapped_wettkampf["wettkampf_art"],
                         "abschnitt": mapped_wettkampf["abschnitts_nr"],
                         "anzahl_starter": mapped_wettkampf["anzahl_starter"],
                         "event": mapped_wettkampf["einzelstrecke"] + mapped_wettkampf["technik"],
                         "geschlecht": mapped_wettkampf["geschlecht"]})
                if line_values[0][0] == "WERTUNG:":
                    mapped_wertung = self._Dsv6BaseClassMapper__wertung_mapper(line=line[9:])
                    self.mapped_groups_age[mapped_wertung["wertungs_id"]].append(
                        {"from_to_group_ages": [mapped_wertung["min_jg"], mapped_wertung["max_jg"]],
                         "gender": mapped_wertung["geschlecht"],
                         "description": mapped_wertung["wertungs_name"]})

                if line_values[0][0] == "PNERGEBNIS:":
                    if " ".join(line_values[9]) in self.club_names:
                        mapped_pnergebnis = self._Dsv6ResultClassMapper__pnergebnis_mapper(line=line[12:])
                        swimmer_reg_id = mapped_pnergebnis["dsv_id"]
                        self.mapped_swimmer_ids[mapped_pnergebnis["schwimmer_id"]] = swimmer_reg_id
                        competition_type = mapped_pnergebnis["wk_art"]
                        event = self.mapped_events[mapped_pnergebnis["wk_nr"]][0]["event"]
                        group_age = self.mapped_groups_age[mapped_pnergebnis["wertungs_id"]][0]["description"]
                        event_time = mapped_pnergebnis["endzeit"]
                        event_place = int(mapped_pnergebnis["platz"])
                        event_dict[event].append({competition_type: {group_age: event_place, "time": event_time}})
                        if len(swimmers_result[swimmer_reg_id]) > 0:
                            for i in range(0, len(swimmers_result[swimmer_reg_id])):
                                i_values = swimmers_result[swimmer_reg_id][i].keys()
                                if event in i_values:
                                    # if we found the already existing part,
                                    # we add the group_age + placing and ending the search
                                    if competition_type in swimmers_result[swimmer_reg_id][i][event][0]:
                                        swimmers_result[swimmer_reg_id][i][event][0][competition_type].update(
                                            event_dict[event][0][competition_type])
                                    else:
                                        swimmers_result[swimmer_reg_id][i][event].append(
                                            event_dict[event][0])
                                    break
                                elif event not in i_values:
                                    if i + 1 == len(swimmers_result[swimmer_reg_id]):
                                        # if the for-loop comes to and end, but no event was found, we add it
                                        swimmers_result[swimmer_reg_id].append(event_dict)
                                    else:
                                        continue
                        else:
                            swimmers_result[swimmer_reg_id].append(event_dict)
                if line_values[0][0] == "PNZWISCHENZEIT:":
                    mapped_data = self._Dsv6DefinitionClassMapper__pnzwischenzeit_mapper(line=line[15:])
                    swimmer_id = mapped_data["schwimmer_id"]
                    if swimmer_id in self.mapped_swimmer_ids.keys():
                        swimmer_reg_id = self.mapped_swimmer_ids[swimmer_id]
                        competition_type = mapped_data["wk_art"]
                        event = mapped_data["wk_nr"]
                        for events in swimmers_result[swimmer_reg_id]:
                            if event == events["wk_nr"]:
                                if swimmers_result[swimmer_reg_id][event]["Zwischenzeit"]:
                                    swimmers_result[swimmer_reg_id][event]["Zwischenzeit"].append(mapped_data)
                                else:
                                    swimmers_result[swimmer_reg_id][event]["Zwischenzeit"] = [mapped_data]
                    else:
                        self.tmp_pnzwischenzeit[swimmer_id] = mapped_data
            # proceed the tmp_pnzwischenzeit
            for _swimmer_id, pn_zwischenzeit in self.tmp_pnzwischenzeit.items():
                logger.debug(pn_zwischenzeit)
                if _swimmer_id in self.mapped_swimmer_ids.keys():
                    swimmer_reg_id = self.mapped_swimmer_ids[_swimmer_id]
                    event_name = self.mapped_events[pn_zwischenzeit["wk_nr"]][0]["event"]
                    logger.debug("event_name: {}".format(event_name))
                    wk_art = pn_zwischenzeit["wk_art"]


        else:
            logger.info("no lines to proceed!")
        # housekeeping
        swimmers_result["meta"].append(self.mapped_meeting)
        self.__reset_mappings()
        # comment in, if you want to move file to files/done
        # self.__move_file_to_done(file_to_proceed=file_to_proceed)
        return {self.return_def[1]: swimmers_result}

    def __proceed_competition_definition(self):
        # todo: we dont need to transform to data class, because the values should be correct
        logger.info("__proceed_competition_definition()")
        sections = []
        events = []
        group_ages = []
        mandatory_times = []
        meeting_definition = {}
        if len(self.file_lines) > 0:
            for line in self.file_lines:
                line_values = [i.split() if i else [] for i in line.split(';')]
                if line_values[0][0] == "VERANSTALTUNG:":
                    mapping = self._Dsv6BaseClassMapper__veranstaltung_mapper(line=line[15:])
                    meeting_definition["Veranstaltung"] = mapping
                if line_values[0][0] == "VERANSTALTUNGSORT:":
                    mapping = self._Dsv6DefinitionClassMapper__veranstaltungsort_mapper(line=line[19:])
                    meeting_definition["Veranstaltungsort"] = mapping
                if line_values[0][0] == "AUSSCHREIBUNGIMNETZ:":
                    mapping = self._Dsv6DefinitionClassMapper__ausschreibung_im_netz_mapper(line=line[21:])
                    if list(mapping.values())[0] == "":
                        print("AusschreibungImNetz ist nicht gefüllt")
                    else:
                        meeting_definition["AusschreibungImNetz"] = mapping
                if line_values[0][0] == "VERANSTALTER:":
                    mapped_veranstalter = self._Dsv6DefinitionClassMapper__veranstalter_mapper(line=line[14:])
                    meeting_definition["Veranstalter"] = mapped_veranstalter
                elif line_values[0][0] == "AUSRICHTER:":
                    mapped_data = self._Dsv6DefinitionClassMapper__ausrichter_mapper(line=line[12:])
                    meeting_definition["Ausrichter"] = mapped_data
                elif line_values[0][0] == "MELDEADRESSE:":
                    mapped_data = self._Dsv6DefinitionClassMapper__meldeadresse_mapper(line=line[14:])
                    meeting_definition["Meldeadresse"] = mapped_data
                elif line_values[0][0] == "MELDESCHLUSS:":
                    mapped_data = self._Dsv6DefinitionClassMapper__meldeschluss_mapper(line=line[14:])
                    if self.validate_date(date_text=mapped_data["datum"]) and \
                            self.validate_date_time(date_text=mapped_data["uhrzeit"]):
                        meeting_definition["Meldeschluss"] = mapped_data
                    else:
                        logger.error("invalid date format!")
                        # todo: should it break here?
                elif line_values[0][0] == "BANKVERBINDUNG:":
                    mapped_data = self._Dsv6DefinitionClassMapper__bankverbindung_mapper(line=line[16:])
                    meeting_definition["Bankverbindung"] = mapped_data
                elif line_values[0][0] == "BESONDERES:":
                    mapped_data = self._Dsv6DefinitionClassMapper__besonderes_mapper(line=line[12:])
                    meeting_definition["Besonderes"] = mapped_data
                elif line_values[0][0] == "NACHWEIS:":
                    mapped_data = self._Dsv6DefinitionClassMapper__nachweis_mapper(line=line[10:])
                    if self.validate_date(date_text=mapped_data["nachweis_von"]) \
                        and self.validate_date(date_text=mapped_data["nachweis_bis"]):
                        meeting_definition["Nachweis"] = mapped_data
                    else:
                        logger.error("invalid date format!")
                        # todo: should it break here?
                elif line_values[0][0] == "ABSCHNITT:":
                    mapped_data = self._Dsv6DefinitionClassMapper__abschnitt_mapper(line=line[11:])
                    if self.validate_date(date_text=mapped_data["abschnitts_datum"]) and \
                            self.validate_date_time(date_text=mapped_data["einlass"]) and \
                            self.validate_date_time(date_text=mapped_data["kampfrichtersitzung"]) and \
                            self.validate_date_time(date_text=mapped_data["anfangszeit"]):
                        sections.append(mapped_data)
                    else:
                        logger.error("invalid date format!")
                        # todo: should it break here?
                elif line_values[0][0] == "WETTKAMPF:":
                    mapped_data = self._Dsv6BaseClassMapper__wettkampf_mapper(line=line[11:])
                    events.append(mapped_data)
                elif line_values[0][0] == "WERTUNG:":
                    mapped_data = self._Dsv6BaseClassMapper__wertung_mapper(line=line[9:])
                    if mapped_data["geschlecht"] == "":
                        for wk in events:
                            if wk.wettkampf_nr == mapped_data["wettkampf_nr"]:
                                mapped_data["geschlecht"] = wk.geschlecht
                                break
                    group_ages.append(mapped_data)
                elif line_values[0][0] == "PFLICHTZEIT:":
                    mapped_data = self._Dsv6DefinitionClassMapper__pflichtzeit_mapper(line=line[13:])
                    mandatory_times.append(mapped_data)
                elif line_values[0][0] == "MELDEGELD:":
                    pass
        meeting_definition["Abschnitte"] = sections
        meeting_definition["Wettkaempfe"] = events
        meeting_definition["Wertungen"] = group_ages
        meeting_definition["Pflichtzeiten"] = mandatory_times
        return {self.return_def[0]: meeting_definition}

    def analyze_dsv6_file_type(self, file_to_proceed):
        """
        this method takes a dsv6 file and checks, which format it has und chooses the correct proceed method. It
        returns a dict like {"format_name": data}
        Where data is a set of data classes
        :params: file_to_proceed: path to the dsv6-file
        :returns: dict with format name and data
        :return_type dict
        """
        return self.__choose_function(file_to_proceed=file_to_proceed)
