import os
import shutil
from collections import defaultdict
import logging
import sys
from datetime import datetime

from dsv6_data_classes import *
from dsv6_class_mapper import Dsv6ClassMapper

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Dsv6FileHandler(Dsv6ClassMapper):
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
        self.club_names = ["W98 Hannover"]
        self.files_to_proceed = []
        self.file_lines = []
        self.mapped_events = defaultdict(list)
        self.mapped_groups_age = defaultdict(list)
        self.mapped_meeting = defaultdict(list)

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

    def __get_all_files(self):
        self.files_to_proceed = [os.path.join(self.file_dir, f) for f in os.listdir(self.file_dir)
                                 if os.path.isfile(os.path.join(self.file_dir, f)) and f.endswith(".dsv6")]

    def __read_file(self, file_to_proceed):
        with open(file_to_proceed) as f:
            self.file_lines = [i for i in f.read().splitlines() if i != ""]

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
                             "description": " ".join(line_values[7])}
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
                        {event_name: "",
                        places: [{group_age: event_place}],
                        time: ""}
                        ]
                    }
        :return:
        """
        logger.info("get_results_from_file()")
        swimmers_result = defaultdict(list)
        if len(self.file_lines) > 0:
            for line in self.file_lines:
                event_dict = {"places": []}
                line_values = [i.split() for i in line.split(';') if i != '']
                if line_values[0][0] == "VERANSTALTUNG:" or line_values[0][0] == "AUSRICHTER:" or line_values[0][0] == "ABSCHNITT:":
                    self.__map_meeting(line_values=line_values)
                if line_values[0][0] == "WETTKAMPF:":
                    self.__map_events(line_values=line_values)
                if line_values[0][0] == "WERTUNG:":
                    self.__map_group_ages(line_values=line_values)
                if line_values[0][0] == "PNERGEBNIS:":
                    if " ".join(line_values[9]) in self.club_names:
                        swimmer_reg_id = line_values[5]
                        event = self.mapped_events[line_values[0][1]][0]["event"]
                        group_age = self.mapped_groups_age[line_values[2][0]][0]["description"]
                        event_time = str(line_values[11][0])
                        event_place = int(line_values[3][0])
                        if len(swimmers_result[swimmer_reg_id[0]]) > 0:
                            for i in range(0, len(swimmers_result[swimmer_reg_id[0]])):
                                i_values = swimmers_result[swimmer_reg_id[0]][i].values()
                                if event in i_values:
                                    # if we found the already existing part,
                                    # we add the group_age + placing and ending the search
                                    swimmers_result[swimmer_reg_id[0]][i]["places"].append({group_age: event_place})
                                    break
                                elif event not in i_values:
                                    if i + 1 == len(swimmers_result[swimmer_reg_id[0]]):
                                        # if the for-loop comes to and end, but no event was found, we add it
                                        event_dict["event"] = event
                                        event_dict["time"] = event_time
                                        event_dict["places"].append({group_age: event_place})
                                        swimmers_result[swimmer_reg_id[0]].append(event_dict)
                                    else:
                                        continue
                        else:
                            # swimmers_result[swimmer_reg_id[0]] is empty
                            event_dict["event"] = event
                            event_dict["time"] = event_time
                            event_dict["places"].append({group_age: event_place})
                            swimmers_result[swimmer_reg_id[0]].append(event_dict)
        else:
            logger.info("no lines to proceed!")
        # housekeeping
        swimmers_result["meta"].append(self.mapped_meeting)
        self.__reset_mappings()
        # comment in, if you want to move file to files/done
        # self.__move_file_to_done(file_to_proceed=file_to_proceed)
        return swimmers_result

    def __proceed_competition_definition(self):
        logger.info("__proceed_competition_definition()")
        if len(self.file_lines) > 0:
            for line in self.file_lines:
                line_values = [i.split() if i else [] for i in line.split(';')]
                # print(line_values)
                if line_values[0][0] == "VERANSTALTUNG:":
                    mapping = self._Dsv6ClassMapper__veranstaltung_mapper(line=line[15:])
                    dc_veranstaltung = Veranstaltung(**mapping)
                    dc_veranstaltung.zeitmessung = ZeitMessung(mapping["zeitmessung"])
                    print(dc_veranstaltung)
                if line_values[0][0] == "VERANSTALTUNGSORT:":
                    mapping = self._Dsv6ClassMapper__veranstaltungsort_mapper(line=line[19:])
                    dc_veranstaltungsort = VeranstaltungsOrt(**mapping)
                    print(dc_veranstaltungsort)
                if line_values[0][0] == "AUSSCHREIBUNGIMNETZ:":
                    mapping = self._Dsv6ClassMapper__ausschreibung_im_netz_mapper(line=line[21:])
                    if list(mapping.values())[0] == "":
                        print("AusschreibungImNetz ist nicht gefüllt")
                    else:
                        dc_ausschreibung_im_netz = AusschreibungImNetz(**mapping)
                        print(dc_ausschreibung_im_netz)
                if line_values[0][0] == "VERANSTALTER:":
                    mapped_veranstalter = self._Dsv6ClassMapper__veranstalter_mapper(line=line[14:])
                    dc_veranstalter = Veranstalter(**mapped_veranstalter)
                    print(dc_veranstalter)
                elif line_values[0][0] == "AUSRICHTER:":
                    mapped_data = self._Dsv6ClassMapper__ausrichter_mapper(line=line[12:])
                    dc_ausrichter = Ausrichter(**mapped_data)
                    print(dc_ausrichter)
                elif line_values[0][0] == "MELDEADRESSE:":
                    mapped_data = self._Dsv6ClassMapper__meldeadresse_mapper(line=line[14:])
                    dc_meldeadresse = MeldeAdresse(**mapped_data)
                    print(dc_meldeadresse)
                elif line_values[0][0] == "MELDESCHLUSS:":
                    mapped_data = self._Dsv6ClassMapper__meldeschluss_mapper(line=line[14:])
                    print(mapped_data)
                    if self.validate_date(date_text=mapped_data["datum"]) and \
                            self.validate_date_time(date_text=mapped_data["uhrzeit"]):
                        dc_meldeschluss = Meldeschluss(**mapped_data)
                        print(dc_meldeschluss)
                    else:
                        print("invalid date format!")

                elif line_values[0][0] == "ABSCHNITT:":
                    pass

                elif line_values[0][0] == "WETTKAMPF:":
                    pass
                elif line_values[0][0] == "WERTUNG:":
                    pass
                elif line_values[0][0] == "PFLICHTZEIT:":
                    pass
                elif line_values[0][0] == "MELDEGELD:":
                    pass

    def analyse_dsv6_file(self, file_to_proceed):
        self.__choose_function(file_to_proceed=file_to_proceed)


dsv_handler = Dsv6FileHandler()
dsv_handler.update()
dsv_handler.analyse_dsv6_file(file_to_proceed="../files/2018-11-11-Osnabrue-Wk.dsv6")