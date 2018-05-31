from math import sqrt


#classe vecteur qui implémente un objet vecteur avec les caractéristiques des opérations vectorielles
class Vector:
    def __init__(self, a, b):
        self.x = a
        self.y = b

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, d):
        return Vector(d * self.x, d * self.y)

    def produit(self, other):
        return (self.x * other.y) - (self.y * other.x)

    def norme(self):
        return sqrt(self.x**2 + self.y**2)

    def scalaire(self, other):
        return (self.x*other.x) + (self.y*other.y)



