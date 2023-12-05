import strawberry

from odooghost import stack


@strawberry.type
class Stack:
    name: str
    instance: strawberry.Private[stack.Stack]
