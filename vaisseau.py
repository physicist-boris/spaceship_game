from vector import Vector
from math import cos, sin, pi


# classe Vaisseau qui implémente un objet dont les attributs correspondent aux caractéristiques du Vaisseau(position, vitesse, angle...)
class Vaisseau:
    def __init__(self, pos, incre_vit, e):
        self.po = pos
        self.vitesse = Vector(0, 0)
        self.angle = 0
        self.increment = incre_vit
        self.energ = e

    def move(self, t):
        # permet au vaisseau de bouger selon un temps t et une vitesse
        self.po += self.vitesse * t

    def acc(self, t):
        # permet au vaisseau d'accélérer en tenant compte du moteur-fusée en secondes de poussée(à chaque secondes de poussée, il diminue)
        if self.energ > 0:
            self.vitesse += Vector(cos((self.angle * pi) / 180), sin((self.angle * pi) / 180)) * self.increment * t
            self.energ -= t
        else:
            pass


# classe Obstacle qui permet de créer un objet qui détecte, si à chaque instant t , il y a collision, et, dans ce cas modifie
# les paramètres de vaisseau(vitesse, position....) sinon dans l'autre cas ne fait rien


class Obstacle:
    def __init__(self, p, v, coeff):
        self.p = p
        self.v = v
        self.coeff = coeff

    def detecter_collision(self, t, veca, vecb):

        delta_q = vecb - veca
        k = self.p + (self.v * t)
        a = ((veca - self.p).produit(delta_q))
        b = ((k - self.p).produit(delta_q))
        if a == 0 and b == 0:
            pass
        elif a != 0 and b == 0:
            pass
        else:
            r = ((veca - self.p).produit(delta_q)) / b
            s = ((veca - self.p).produit(k - self.p)) / b
            if (0 <= r <= 1) and (0 <= s <= 1):
                vecteur_dq = Vector((-delta_q.y), delta_q.x)
                n = vecteur_dq * (1 / vecteur_dq.norme())
                delta_pp = (k - self.p) - (n * (2 * ((k - self.p).scalaire(n))))
                self.p += delta_pp
                self.v = delta_pp * (self.coeff * (self.v.norme() / delta_pp.norme()))
