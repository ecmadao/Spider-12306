import re
from datetime import datetime
import json
from colorama import Fore
from .station_name import station_name
from spider import fetch_trains
from prettytable import PrettyTable

URL = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.' \
      'train_date={date}&leftTicketDTO.' \
      'from_station={from_station_key}&leftTicketDTO.to_station={to_station_key}&purpose_codes=ADULT'

TICKETS_TABLE_HEADER = ["车次", "站点", "起止时间", "历时", "商务座", "特等座",
                        "一等座", "二等座", "软卧", "硬卧", "软座", "硬座", "无座"]


def fetch_train_tickets(from_station, to_station, train_type, date=None):
    """get input data and print final result

    :param train_type
    :param from_station
    :param to_station
    :param date
    :return: if data is invalidate then return False
    """
    if date is None:
        date = str(datetime.now()).split(' ')[0]
    else:
        date = validate_date(date)
        if not isinstance(date, str):
            print(make_colorful_font(date['message'], Fore.RED))
            return date['result']
    from_station_key = get_station_key(from_station)
    to_station_key = get_station_key(to_station)

    fetch_url = URL.format(date=date, from_station_key=from_station_key, to_station_key=to_station_key)
    train_tickets = fetch_trains.TrainTickets(fetch_url)
    tickets_result = train_tickets.fetch_tickets()

    # with open('./data/tickets_data.json', encoding="utf-8") as f:
    #     tickets_result = json.loads(f.read())

    if tickets_result['status']:
        print_train_tickets(tickets_result, train_type)
    else:
        print(make_colorful_font(tickets_result['data'], Fore.RED))


def get_station_key(station):
    """convert station to key

    :param station: the station user input
    :return: a validate station key
    """
    upper_stations, lower_stations = station_name()
    if re.findall(u'[a-z]+', station.lower()):
        station_chinese = lower_stations[station.lower()]
        station_key = upper_stations[station_chinese]
        print(station_chinese)
    elif re.findall(u'[\u4e00-\u9fa5]+', station):
        station_key = upper_stations[station]
    else:
        station_key = None
    return station_key


def filter_target_train(train_type):
    """to return a filter function

    :param train_type
    :return: A function to filter target train type
    """
    def target_train(train_obj):
        return train_obj["queryLeftNewDTO"]["station_train_code"][0] == train_type
    return target_train


def print_train_tickets(tickets_result, train_type):
    """make and print a table

    :param tickets_result: fetched result
    :return: None
    """
    t_type = None
    for item in train_type.items():
        t_type, t_type_value = item
        if t_type_value:
            break
        else:
            t_type = None

    if t_type is not None:
        target_train = filter_target_train(t_type)
        tickets_result_data = filter(target_train, tickets_result['data'])
    else:
        tickets_result_data = tickets_result['data']

    tickets_table = PrettyTable(TICKETS_TABLE_HEADER)
    for ticket_dict in tickets_result_data:
        ticket_data = ticket_dict["queryLeftNewDTO"]
        tickets_table_row = [
            ticket_data["station_train_code"],
            '{}\n{}'.format(make_colorful_font(ticket_data["from_station_name"]),
                            make_colorful_font(ticket_data["end_station_name"])),
            '{}\n{}'.format(ticket_data["start_time"], ticket_data["arrive_time"]),
            ticket_data["lishi"], handle_font_color(ticket_data["swz_num"]),
            handle_font_color(ticket_data["tz_num"]), handle_font_color(ticket_data["zy_num"]),
            handle_font_color(ticket_data["ze_num"]), handle_font_color(ticket_data["rw_num"]),
            handle_font_color(ticket_data["yw_num"]), handle_font_color(ticket_data["rz_num"]),
            handle_font_color(ticket_data["yz_num"]), handle_font_color(ticket_data["wz_num"])
        ]
        tickets_table.add_row(tickets_table_row)
        del tickets_table_row
    print(tickets_table)


def make_colorful_font(text, color=Fore.CYAN):
    """make text colorful

    :param text: target text
    :param color: font color, default color is Fore.CYAN
    :return: colored text
    """
    return color + text + Fore.RESET


def handle_font_color(text):
    """A fun to checkout if text should be colorful

    :param text: target text
    :return: colored text
    """
    if text != "--" and text != "无" or text == '有':
        text = make_colorful_font(text, Fore.MAGENTA)
    return text


def validate_date(date):
    """check if the date is validate

    :param date: train start date
    :return: a validate date or return a error message obj
    """
    check_result = re.findall(r'-', date)
    if len(check_result) == 2:
        date_list = date.split('-')
        new_date_list = []
        for i, d in enumerate(date_list):
            if i > 0 and len(d) < 2:
                new_date = '0{}'.format(d)
            else:
                new_date = d
            new_date_list.append(new_date)
        return '-'.join(new_date_list)
    else:
        if len(date) is 8:
            new_date_list = [date[0:4], date[4:6], date[6:8]]
            return '-'.join(new_date_list)
        else:
            return dict([('result', 0),
                         ('message', 'date is invalidate, '
                                     'you should use \'2016-07-18\' or \'20160718\' or \'2016-7-18\'')])
