import re
import argparse
import xml.etree.ElementTree as ET
from typing import Type

parser = argparse.ArgumentParser(description='Interpolate correct DocTimeRels in system output.')
parser.add_argument('--sys_out', type=str, help='System output file requiring DocTimeRels')

event_rels = [
    'CONTAINS-SUBEVENT',
    'CONTAINS',
    'OVERLAP',
    'BEFORE',
]

class Event:
    def __init__(
            self,
            event_name : str,
            event_type : int,
            begin_offset : int,
            end_offset : int,
            event_tag : str,
            doc_time_rel : str = None
    ):
        self.event_name = event_name
        self.event_type = event_type
        self.begin_offset = begin_offset
        self.end_offset = end_offset
        self.event_tag = event_tag
        self.doc_time_rel = doc_time_rel

    def __str__(self):
        main_body = f'type={self.event_type}!{self.begin_offset}-{self.end_offset}!{self.event_tag}'
        if self.doc_time_rel:
            return f'{self.event_name}({main_body}; doctimerel={self.doc_time_rel})'
        else:
            return f'{self.event_name}({main_body})'
    
class EventRel:
    def __init__(
            self,
            rel_name : str,
            event_1 : Type[Event],
            event_2 : Type[Event]
    ):
       self.rel_name = rel_name
       self.event_1 = event_1
       self.event_2 = event_2

    def __str__(self):
        return f'{self.rel_name}({str(self.event_1)}, {str(self.event_2)})' 

def string2event(event_str: str):
    if event_str[-1] != ')':
        event_str += ')'
    event_ls = re.split('\(|\)', event_str)[:-1]
    raw_type, raw_offsets, raw_tag = event_ls[1].split('!')
    event_name = event_ls[0]
    event_type = int(raw_type.split('=')[1])
    begin_offset, end_offset = [int(offset) for offset in raw_offsets.split('-')]
    event_tag = raw_tag
    return Event(event_name, event_type, begin_offset, end_offset, event_tag)

def extract_events(events_str: str):
    return [string2event(event.strip()) for event in events_str[1:-1].split('),')]
    
def extract_event_rel(sysout_line : str):
    event_rel = begin_offset = end_offset = remainder = None
    for rel in event_rels:
        rel_split = re.split(rel, sysout_line)
        if len(rel_split) > 1:
             event_rel = rel
             begin_offset = len(rel_split[0])
             remainder = rel_split[1]
             break
    if remainder:
        stack = []
        for i, c in enumerate(remainder):
            if c == '(':
                stack.append(i)
            elif c == ')' and stack:
                start = stack.pop()
                if start == 0:
                   end_offset = begin_offset + len(event_rel) + i + 1
                   event_1, event_2 = extract_events(remainder[:i + 1])
                   return (EventRel(event_rel, event_1, event_2), begin_offset, end_offset)

def event_span(event : Type[Event]):
    return f'{event.begin_offset},{event.end_offset}'
               
def extract_eventrel_with_doctimerel(line, xml_tree):
    event_rel, begin_offset, end_offset = extract_event_rel(line)
    doctimerel_dict = {}
    event_1_span = event_span(event_rel.event_1)
    event_2_span = event_span(event_rel.event_2)
    for entity in xml_tree.iter('entity'):
        span = entity.find('span').text
        if span == event_1_span:
            doctimerel = entity.find('properties').find('DocTimeRel')
            if doctimerel is not None:
                doctimerel_dict['event_1'] = doctimerel.text
        if span == event_2_span:
            doctimerel = entity.find('properties').find('DocTimeRel')
            if doctimerel is not None:
                doctimerel_dict['event_2'] = doctimerel.text
        if len(doctimerel_dict) > 1:
            break
    if 'event_1' in doctimerel_dict:
        event_rel.event_1.doc_time_rel = doctimerel_dict['event_1']
    if 'event_2' in doctimerel_dict:
        event_rel.event_2.doc_time_rel = doctimerel_dict['event_2']
    return event_rel, begin_offset, end_offset
    
def main(sys_out):
    current_gold_xml = None
    outfile_name = 'DocTimeRel_' + sys_out.split('/')[-1]
    with open(sys_out, 'r') as infile, open(outfile_name, 'w') as outfile:
        for line in infile:
            if line.startswith('Doc id'):
                outfile.write(line)
                outfile.write('\n')
                filename = line.split(':')[-1].strip()
                current_gold_xml = ET.parse(filename).getroot()
            else:
                event_rel, begin, end = extract_eventrel_with_doctimerel(line, current_gold_xml)
                out_line = line[:begin] + str(event_rel) + line[end:]
                outfile.write(out_line)
                outfile.write('\n')
                
if __name__=='__main__':
    args = parser.parse_args()
    main(args.sys_out)
