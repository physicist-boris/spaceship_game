from glo1901 import Chrono
from vaisseau import Vaisseau
from vaisseau import Obstacle
from Mission import Mission
from vector import Vector
import polytri
import pyglet.gl
from pyglet.window import key

import json
import argparse
from glo1901 import ClientReseau

parser = argparse.ArgumentParser(description="Jeu des tortues de l'espace.")
parser.add_argument("--serveur", metavar="adresse", help="Adresse du serveur (default: python.gel.ulaval.ca)")
parser.add_argument("--port", metavar="numéro", help="Numéro de port du serveur (default: 31415)", type=int)
group = parser.add_mutually_exclusive_group()
group.add_argument("--créer", metavar=("n", "fichier"), nargs=2,
                   help="Créer une partie de n joueurs dont la mission est spécifiée dans fichier (default: (1, "
                        "'mission.json'))")
group.add_argument("--joindre", metavar="pseudo", help="Pseudonyme de la partie à joindre (default: None)")
group.add_argument("--lister",
                   help="Afficher la liste des pseudonymes des parties en attente de joueurs (default: False)",
                   action='store_true')
parser.add_argument("joueur", help="Pseudonyme du joueur")

args = parser.parse_args()


# fonction jouer() qui génère l'univers et toute la dynamique du jeu à l'aide du nombre de joueurs(n) et des
# paramètres de missions(carte)
def jouer(n, carte):
    missionss = Mission((carte[0][0], carte[0][1]), (carte[1][0], carte[1][1]), carte[2], carte[3], carte[4], carte[5],
                        carte[6])
    vaisseau = Vaisseau(Vector(missionss.jx, missionss.jy), missionss.vitax, missionss.energie)

    window = pyglet.window.Window(700, 700)
    kitten = pyglet.image.load('pilote.png')
    kitten.anchor_x = kitten.width // 2
    kitten.anchor_y = kitten.height // 2
    poten = pyglet.sprite.Sprite(kitten, x=missionss.jx, y=missionss.jy)
    croix = pyglet.image.load('trou35.png')
    croix.anchor_x = croix.width // 2
    croix.anchor_y = croix.height // 2
    croixx = pyglet.sprite.Sprite(croix, x=missionss.fx, y=missionss.fy)
    fond = pyglet.image.load('fond.jpg')
    fonds = pyglet.sprite.Sprite(fond, x=0, y=0)
    liste_joueurs = []
    for i in range(0, n - 1):  # boucle qui génère une liste avec les sprites des différents joueurs
        beta = pyglet.image.load('pilote2.png')
        beta.anchor_x = beta.width // 2
        beta.anchor_y = beta.height // 2
        liste_joueurs.append(pyglet.sprite.Sprite(beta, x=missionss.jx, y=missionss.jy))
    keys = key.KeyStateHandler()
    window.push_handlers(keys)
    delta_r = Chrono(autostart=True)  # création du chrono

    @window.event
    def on_draw():
        window.clear()
        fonds.draw()
        for vecteurs in range(0, len(missionss.listpol)):
            vertex = missionss.listpol[vecteurs]
            for i in polytri.triangulate(vertex):
                pyglet.graphics.draw(3, pyglet.gl.GL_POLYGON,
                                     ('v2i', (i[0][0], i[0][1], i[1][0], i[1][1], i[2][0], i[2][1])),
                                     ('c3B', (255, 0, 0, 0, 255, 0, 0, 0, 255)))
        croixx.draw()
        poten.draw()
        for autres_joueurs in liste_joueurs:
            autres_joueurs.draw()  # affiche les différents sprites des joueurs à l'écran
        croixx.draw()
        if delta_r.get() > 0.025:
            # ok, le délai minimum est respecté,
            # rapporter l'état puis mettre à zéro le chrono
            états = client.rapporter((vaisseau.po.x, vaisseau.po.y), (vaisseau.vitesse.x, vaisseau.vitesse.y),
                                     vaisseau.angle)

            if états is not None:
                fin_jeu = états.copy()
                fin_jeu.pop('gagnant')
                for pseudo in états.keys():
                    if états[pseudo] is None:
                        continue
                    score_label = pyglet.text.Label(text=pseudo, x=états[pseudo][0][0], y=états[pseudo][0][1])
                    score_label.draw()
                fin_jeu.pop(client.pseudonyme)
                b = 0
                # Si la méthode "rapporter" renvoie un dictionnaire avec les positions et les angles des joueurs,
                # on génère une boucle, et on itère sur chaque clé pour pouvoir associer ces coordonnées aux
                # coordonnées des sprites des joueurs
                for adversaire in fin_jeu.values():
                    if adversaire is None:
                        continue
                    liste_joueurs[b].x, liste_joueurs[b].y = adversaire[0][0], adversaire[0][1]
                    liste_joueurs[b].rotation = adversaire[2]
                    b += 1
                if états['gagnant'] is not None:
                    a = "Le gagnant est: "
                    a += "{}, ".format(états["gagnant"])
                    print(a)  # affiche le ou les gagnants
                    exit()  # quitte le jeu
            delta_r.reset()  # mettre à zéro le chrono

    def update(dt):

        if keys[key.LEFT]:
            vaisseau.angle -= missionss.ang * dt
        if keys[key.RIGHT]:
            vaisseau.angle += missionss.ang * dt
        if keys[key.UP]:
            vaisseau.acc(dt)

        vaisseau.move(dt)
        # détecte si il y a collision avec les 4 bords de la fenêtre
        obstacle = Obstacle(vaisseau.po, vaisseau.vitesse, missionss.elas)
        obstacle.detecter_collision(dt, Vector(700, 0), Vector(700, 700))
        obstacle.detecter_collision(dt, Vector(0, 0), Vector(0, 700))
        obstacle.detecter_collision(dt, Vector(0, 700), Vector(700, 700))
        obstacle.detecter_collision(dt, Vector(0, 0), Vector(700, 0))
        # détecte si il y a collision avec les différents obstacles du jeu
        for i in range(0, len(missionss.listpol)):
            for j in range(0, len(missionss.listpol[i])):
                if j == (len(missionss.listpol[i]) - 1):
                    obstacle.detecter_collision(dt, Vector(missionss.listpol[i][j][0], missionss.listpol[i][j][1]),
                                                Vector(missionss.listpol[i][0][0], missionss.listpol[i][0][1]))
                else:
                    obstacle.detecter_collision(dt, Vector(missionss.listpol[i][j][0], missionss.listpol[i][j][1]),
                                                Vector(missionss.listpol[i][j + 1][0], missionss.listpol[i][j + 1][1]))
        vaisseau.po.x, vaisseau.po.y = obstacle.p.x, obstacle.p.y
        vaisseau.vitesse.x, vaisseau.vitesse.y = obstacle.v.x, obstacle.v.y
        # associe les positions et angles de l'objet vaisseau au sprite du joueur
        poten.x, poten.y = vaisseau.po.x, vaisseau.po.y
        poten.rotation = vaisseau.angle

    pyglet.clock.schedule_interval(update, 1 / 60)
    pyglet.app.run()


client = ClientReseau(args.joueur, "python.gel.ulaval.ca", 31415)  # créé une connexion au serveur

if args.créer:
    with open(args.créer[1], 'r') as fich:
        chaîne = fich.read()
        liste = json.loads(chaîne)  # transforme le fichier json avec les paramètres de la mission sous forme de liste
    client.creer(int(args.créer[0]), (
        (liste[0][0], liste[0][1]), (liste[1][0], liste[1][1]), liste[2], liste[3], liste[4], liste[5],
        liste[6]))  # créé la partie
    jouer(int(args.créer[0]), liste)  # ouvre l'univers et la dynamique du jeu
elif args.joindre:
    parties = client.joindre(args.joindre)  # join la partie
    jouer(len(parties["joueurs"]), parties["mission"])  # ouvre l'univers et la dynamique du jeu
elif args.lister:
    partie = client.lister()
    print(partie)  # affiche les parties disponibles
