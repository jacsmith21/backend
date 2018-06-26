import re
import sys
from collections import deque
from enum import Enum


class Node:
    class Ops(Enum):
        AND = '&'
        OR = '|'

        def __eq__(self, other):
            return other == self.value or super().__eq__(other)

    def __init__(self, value=None, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    @property
    def leaf(self):
        return self.value not in OPS

    def __eq__(self, other):
        return self.value == other or super().__eq__(other)

    def to_dict(self):
        return {
            'value': self.value,
            'left': self.left.to_dict() if self.left is not None else None,
            'right': self.right.to_dict() if self.right is not None else None
        }


OPS = {item.value: item for item in Node.Ops}


def convert_polish_notation(expression):
    if expression is None:
        return None

    output_queue = deque()
    stack = deque()

    for token in expression:
        if token in OPS or token == '(':
            stack.append(token)
        elif token == ')':
            while stack[-1] != '(':
                output_queue.append(stack.pop())
            stack.pop()
        else:
            output_queue.append(token)

    while stack:
        output_queue.append(stack.pop())

    return ''.join(reversed(list(output_queue)))


def make_tree(polish_notation):
    current = next(polish_notation, None)
    if current is None:
        return None
    elif current in OPS:
        return Node(value=current, left=make_tree(polish_notation), right=make_tree(polish_notation))
    else:
        return Node(value=current)


def parse(expression: str):
    """
    Parses an boolean expression into a Tree structure. See here: https://stackoverflow.com/questions/17568067/how-to-parse-a-boolean-expression-and-load-it-into-a-class

    :param expression:
    :return:
    """
    expression = expression.replace(' ', '')

    value_map = {}

    delimiters = list(OPS.keys()) + [')', '(']
    pattern = '|'.join(map(re.escape, delimiters))
    literals = re.split(pattern, expression)
    literals = filter(lambda literal: literal, literals)

    start = 0
    key = 0
    substrings = []
    for literal in literals:
        value_map[str(key)] = literal
        index = expression.index(literal, start)
        substrings.append(expression[start:index]), substrings.append(str(key))
        start, key = index + len(literal), key + 1

    substrings.append(expression[start:])
    expression = ''.join(substrings)

    polish_notation = convert_polish_notation(expression)
    tree = make_tree(iter(polish_notation))

    def replace(node):
        if node is None:
            return
        if node.value not in OPS:
            node.value = value_map[node.value]
        replace(node.left), replace(node.right)

    replace(tree)
    return tree


def main():
    print(parse(sys.argv[1]))


if __name__ == '__main__':
    main()
