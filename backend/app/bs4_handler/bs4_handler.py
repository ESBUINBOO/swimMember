from bs4 import BeautifulSoup
from lxml import etree
from collections import defaultdict

skipping_th = ["<th>Strecke</th>", "<th>Zeit</th>", "<th>Punkte</th>", "<th>Details</th>", "<th>Stadt</th>", "<th>Monat</th>"]


def chunks(lst, n):
    n = max(1, n)
    return list((lst[i:i+n] for i in range(0, len(lst), n)))


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def change_list_item(lst, old_item):
    for idx, item in enumerate(lst):
        if old_item in item:
            item = find_between(s=item, first="<td>", last="</td>")
            lst[idx] = item
    return lst


def extract_infos(raw_html):
    #soup = BeautifulSoup(open("test.html"), 'html.parser')
    soup = BeautifulSoup(raw_html, 'html.parser')
    trs = list(soup.find_all("tr"))[5:]
    return trs


def beautify_results(raw_html):
    results_dict = defaultdict(list)
    raw_results = extract_infos(raw_html=raw_html)
    course = "sc"
    tmp_list = []
    for items in raw_results:
        tmp_dict = {}
        new_content = [i for i in items.contents if i != "\n"]
        if str(new_content[0]) in skipping_th:
            continue
        if str(new_content[0]) in tmp_list:
            course = "lc"
        # key = find_between(s=str(new_content[0]), first="<td>", last="</td>")
        tmp_dict[find_between(s=str(new_content[0]), first="<td>", last="</td>")] = {"time": find_between(s=str(new_content[1]), first="<td>", last="</td>"),
                                    "location": find_between(s=str(new_content[2]), first="<td>", last="</td>"),
                                    "date": find_between(s=str(new_content[3]), first="<td>", last="</td>")}
        results_dict[course].append(tmp_dict)
        tmp_list.append(str(new_content[0]))
    return results_dict.items()
