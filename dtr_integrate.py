import re
import argparse
import xml.etree.ElementTree as ET
from typing import Type

parser = argparse.ArgumentParser(description='Interpolate correct DocTimeRels in system output.')
parser.add_argument('--sys_out', type=str, help='System output file requiring DocTimeRels')
parser.add_argument('--doc_time_file', type=str, help='Gold annotation file containing the DocTimeRels')

event_rels = [
    'CONTAINS-SUBEVENT',
    'CONTAINS',
    'OVERLAP',
    'BEFORE',
]

# Smallest event relation name is BEFORE
# Use this for chunking
min_prefix_len = 6

class Event:

    def __init__(
            self,
            event_name : str,
            original_begin_offset : int,
            original_end_offset : int,
            doc_time_rel : str = None
    ):
        self.event_name = event_name
        self.original_begin_offset = self.original_begin_offset
        self.original_end_offset = self.original_end_offset
        self.doc_time_rel = self.doc_time_rel

    def __str__(self):
        pass

    def __repr__(self):
        pass
    
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
       pass 

    def __repr__(self):
        pass

def string2event_rel(event_rel : str, events_str: str) -> Type[EventRel]:
    pass

def chunk_event_rel(sysout_line : str):
     

def parenthetic_contents(string, events=None):
    if events is None:
        events = set()
    prefix = 'CONTAINS-SUBEVENT'
    prefix_len = len(prefix)
    if string.startswith(prefix):
        new_str = string[prefix_len:]
        stack = []
        for i, c in enumerate(new_str):
            if c == '(':
                stack.append(i)
            elif c == ')' and stack:
                start = stack.pop()
                if start == 0:
                    events.add(string2event(new_str[start+1:i]))
                    return parenthetic_contents(string[prefix_len+i+1:], events)
    elif len(string) > prefix_len:
        return parenthetic_contents(string[1:], events)
    else:
        return events

def get_events(line):
    # Get the arguments of CONTAINS-SUBEVENT
    raw_events = re.search(r'CONTAINS-SUBEVENT\((.*)\)', line).group(1)
    events_with_indices = [idx_event.strip() for idx_event in raw_events.split(',')]
    
    
def main(sys_out, doc_time_file):
    lines = []
    candidate_lines = []
    event_trigger = 'CONTAINS_SUBEVENT'
    # ex = ('adrenocarninoma', 103, 109)
    event_offset_triples = []
    with open(sys_out, 'r') as events:
        pass
    gold_tree = ET.parse(doc_time_file)

if __name__=='__main__':
    args = parser.parse_args()
    main(args.sys_out, args.doc_time_file)
