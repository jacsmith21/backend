import collections
import json
import os
import re

import requests
from bs4 import BeautifulSoup

bases = ['http://www.unb.ca/academics/calendar/undergraduate/{}/frederictonprograms'.format(date) for date in ['current', 'archive/2013-2014']]
bases = [base for base in bases]  # saint-john-coursess

r = requests.get(os.path.join(bases[0], 'bachelorofscienceinsoftwarenegineering.html'))
soup = BeautifulSoup(r.content, 'html5lib')

mcontent = soup.find(id='mcontent')

Tag = collections.namedtuple('Tag', ['attrs', 'text'])


RELATIONSHIPS = ['and', 'or']


class Node:
    def __init__(self, text=None, relationship=False, children=None):
        self.text = text
        self.relationship = relationship
        self.children = children or []

    def __str__(self):
        return self.text or '({})'.format(' '.join([str(child) for child in self.children]))

    def __repr__(self):
        return 'Node(\'{}\')'.format(str(self))

    def __len__(self):
        return len(self.text)


def helper(string, start=0):
    nodes = []
    i = start
    while i < len(string):
        if string[i] == '(':
            parsed, i = _, start = helper(string, i + 1)
            nodes.append(Node(children=parsed))
        elif string[i] == ')':
            nodes.append(Node(string[start:i]))
            return nodes, i + 1
        elif string[i] == ',':
            if string[start:i]:
                nodes.append(Node(string[start:i]))
            start = i = i + 1
        else:
            for relationship in RELATIONSHIPS:
                if i + len(relationship) < len(string) and string[i:i + len(relationship)] == relationship:
                    if string[i - 1] != ' ' or string[i + len(relationship)] != ' ':
                        continue

                    if string[start:i].strip():
                        nodes.append(Node(string[start:i]))

                    relationship = Node(relationship, relationship=True)
                    for j, node in reversed(list(enumerate(nodes[:-1]))):
                        if node.relationship:
                            break
                        nodes.insert(j + 1, relationship)  # insert same relationship
                    nodes.append(relationship)

                    i += len(relationship)
                    start = i

                    break
            else:
                i += 1

    if string[start:].strip():
        nodes.append(Node(string[start:]))

    for i, node in reversed(list(enumerate(nodes[:-1]))):
        if node.relationship:
            break
        nodes.insert(i + 1, Node('and', relationship=True))

    return nodes


def parse(string):
    string = re.split('[a-zA-Z]+:', string, flags=re.IGNORECASE)[0]  # removing all other sentences as they do not usually contain important information
    string = string.rstrip('.')
    string = string.split('.')[0]

    parts = string.split(';')
    if len(parts) > 1:
        for i in range(len(parts) - 1):
            parts[i] = parts[i].strip() + ') and ('
        parts.insert(0, '(')
        parts.append(')')
    string = ''.join(parts)

    nodes = helper(string)
    value = ' '.join([str(node) for node in nodes])
    value = ' '.join(value.split())
    value = re.sub('\(\s*([A-Z0-9 a-z]+)\s*\)', '(\g<1>)', value)
    value = re.sub('([A-Z]{2,5}) ([0-9]{4})', '\g<1>\g<2>', value)
    return value


def split(delimiters, string, maxsplit=0):
    pattern = '|'.join(map(re.escape, delimiters))
    return re.split(pattern, string, maxsplit)


def make_tag(course_name):
    lookup = {
        'CS': 'computer-science',
        'STAT': 'statistics',
        'MATH': 'mathematics',
        'INFO': 'informationsystems',
        'ECE': 'electricalandcomputerengineering',
        'PHYS': 'physics',
        'EE': 'electricalengineering'
    }

    match = re.match('([A-Z]+)([0-9]+)', course_name)
    department, number = match.group(1), match.group(2)

    href = '../frederictoncourses/{}/{}-{}.html'.format(lookup[department], department.lower(), number)
    return Tag({'href': href}, course_name)


data = {}
# Only grab the core courses (there are a lot of other links to courses)
for link in soup.findAll('a', href=re.compile('\.\./frederictoncourses/'))[:41]:
    def add_course(a):
        if a.text in {'ECE2213', 'MATH1053'}:  # {doesn't exist, cant parse prereqs properly}
            return

        for base in bases:
            url = os.path.join(base, a.attrs['href'])
            r = requests.get(url)
            if r.status_code != 404:
                break
        else:
            raise Exception

        # noinspection PyShadowingNames
        soup = BeautifulSoup(r.content, 'html5lib')
        name = soup.find('th', {'abbr': 'Course Code'}).text

        tag = soup.select_one('course_prereq')

        # These courses have their course_coreq is the course_prereq tag which causes issues
        if tag.text and name not in {'ENGG1015', 'PHYS1081', 'CS2253'}:
            prerequisites = re.match('\s*Prerequisites?:\s+(.+)', tag.text).group(1)
        else:
            prerequisites = ''

        recommended = re.findall('recommended\s+([A-Z]{2,5} [0-9]{4})', tag.text, flags=re.IGNORECASE)
        recommended = parse(' and '.join(recommended))

        tag = soup.select_one('course_coreq')
        if tag.text:
            corequisites = re.match('\s*Co-?requisites?:\s+(.+)', tag.text).group(1)
        else:
            corequisites = ''

        prerequisites, corequisites = parse(prerequisites), parse(corequisites)

        course = {
            'name': name,
            'title': soup.find('th', {'abbr': 'Course Dscription'}).text,
            'description': soup.find('course_description').text,
            'prerequisites': prerequisites,
            'corequisites': corequisites,
            'recommended': recommended
        }

        # make sure we remove all whitespace
        for key, val in course.items():
            course[key] = val.strip()

        data[name] = course

        for course_name in re.findall('([A-Z]{2,5}[0-9]{4})', prerequisites + corequisites):
            if course_name not in data:
                print('Recursively adding {}'.format(course_name))
                add_course(make_tag(course_name))

    name = link.text.replace(' ', '')
    if name not in data:
        print('Adding {}'.format(name))
        add_course(link)

with open('data.json', 'w') as fp:
    json.dump(data, fp)
