import sys
from collections import deque
from enum import Enum

import utils


class Node:
    class Ops(Enum):
        AND = '&', 'and'
        OR = '|', 'or'

        def __eq__(self, other):
            if super().__eq__(other):
                return True

            for alias in self.value:
                if other == alias:
                    return True

            return False

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

    def __repr__(self):
        return 'Node({}, left={}, right={})'.format(self.value, self.leaf, self.right)


OPS = set()
for op in Node.Ops:
    for al in op.value:
        OPS.add(al)


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

    return list(reversed(list(output_queue)))


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
    if not expression:
        return Node('')

    expression = utils.split(['and', 'or', '&', '|', '(', ')'], expression, keep=True)
    polish_notation = convert_polish_notation(expression)
    tree = make_tree(iter(polish_notation))
    return tree


def main():
    print(parse(sys.argv[1]))


if __name__ == '__main__':
    main()
