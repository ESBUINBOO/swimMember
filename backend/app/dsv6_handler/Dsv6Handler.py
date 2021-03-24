import os
import shutil
from collections import defaultdict
import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Dsv6FileHandler:
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

    def get_results_from_file(self, file_to_proceed):  # rename func to analyze_dsv6_file
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

        self.__read_file(file_to_proceed=file_to_proceed)
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

