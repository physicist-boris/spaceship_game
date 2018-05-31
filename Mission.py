class Mission:
    def __init__(self , j, f,  O, E, a, angle, c ):
        self.jx = j[0]
        self.jy = j[1]
        self.fx = f[0]
        self.fy = f[1]
        self.listpol = O
        self.energie  = E
        self.vitax = a
        self.ang = angle
        self.elas = c

#classe Mission, dont les attributs de l'instance correspondent aux paramètres de la Mission

