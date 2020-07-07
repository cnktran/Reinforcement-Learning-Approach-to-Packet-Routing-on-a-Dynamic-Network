from wallet import *


class person(object):
    def __init__(self, age):
        self._age = age


p1 = person(10)

w1 = wallet("blue")
m1 = mo.money("500")
print(p1._age)
print(w1._color)
print(m1._amount)
