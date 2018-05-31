#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Ce fichier contient les définitions des classes ClientReseau et Chrono, utiles
à la réalisation du jeu «Perdu dans l'espace!».
'''
__auteur__ = "Marc Parizeau"
__date__ = "2017-09-04"

import json, socket, time


class ClientReseau(object):
    """Client réseau du jeu «Perdu dans l'espace!».

    :param pseudonyme: pseudonyme de votre vaisseau.
    :param serveur: adresse ou nom de l'hôte du serveur de jeu.
    :param port: port du serveur de jeu.
    """
    def __init__(self, pseudonyme, serveur, port):
        self.pseudonyme = pseudonyme
        self.serveur = serveur
        self.port = port
        self.socket = socket.create_connection((self.serveur, self.port))
        self.tampon = ""

    def creer(self, n, mission):
        """Communique avec le serveur de jeu pour créer une partie.

        :param n: nombre de joueurs désirés (min: 1)
        :param mission: tuple des paramètres de la mission.

        :returns: un dictionnaire contenant une clé 'joueurs' à laquelle
        est associée un tuple de pseudonymes de joueur.
        """
        requete = {"requête" : "créer",
                   "pseudonyme" : self.pseudonyme,
                   "joueurs" : n,
                   "mission" : mission}

        self.__envoyer(requete)
        return self.__recevoir_sync()


    def lister(self):
        """Demande au serveur la liste des parties en attente de joueurs.

        :returns: dictionnaire contenant où les clés sont les pseudonymes des
        créateurs des parties en attente et les valeurs le nombre de places
        disponibles.
        """
        requete = {"requête" : "lister"}

        self.__envoyer(requete)
        return self.__recevoir_sync()


    def joindre(self, hote):
        """Indique au serveur que l'on désire joindre la partie crée par hote.

        :param hote: pseudonyme de l'hôte de la partie à joindre.

        :returns: dictionnaire contenant les clés:
            - 'joueurs' : la liste de noms de joueurs membres de la partie;
            - 'mission' : tuple des paramètres de la mission.
        """
        requete = {"requête" : "joindre",
                   "partie" : hote,
                   "pseudonyme" : self.pseudonyme}

        self.__envoyer(requete)
        return self.__recevoir_sync()

    def rapporter(self, position, vitesse, orientation):
        """Rapporte au serveur l'état de notre vaisseau.

        :param position: sequence de deux nombres correspondant à la position
        :param vitesse: sequence de deux nombres correspondant à la vitesse
        :param orientation: scalaire représentant l'orientation du vaisseau

        :returns: dictionnaire contenant les clés:
            - 'gagnant': pseudonyme du gagnant si la partie est terminée;
              `None` autrement;
            - '<pseudo1>': dernier état connu du vaisseau du joueur <pseudo1>;
            - ...
        La fonction peut aussi retourner None si aucune réponse n'a été obtenue
        à temps du serveur de jeu.
        """
        requete = {"requête" : "rapporter",
                   "état" : (position, vitesse, orientation)}

        self.__envoyer(requete)
        return self.__recevoir_async()

    def __envoyer(self, requete):
        """Envoie une requête au serveur de jeu sous la forme d'une chaîne
        de caractères JSON.
        """
        self.socket.sendall(bytes(json.dumps(requete), "utf-8"))

    def __recevoir(self):
        """Reçoit du serveur de jeu une chaîne de caractères et retourne
        un dictionnaire ou None si aucune réponse valide n'a été reçue.
        """
        self.tampon += str(self.socket.recv(4096), "utf-8")
        fin = self.tampon.rfind("}")
        debut = self.tampon[:fin].rfind("{")

        if debut < 0 or fin < 0:
            return None

        try:
            reponse = json.loads(self.tampon[debut:fin+1])
        except ValueError:
            raise ValueError("Le serveur nous a répondu un message "
                             "incompréhensible: '{}'".format(self.tampon))
        else:
            self.tampon = self.tampon[fin+1:]

        if "erreur" in reponse:
            raise Exception(reponse["erreur"])
        return reponse

    def __recevoir_sync(self):
        """Reçoit un message complet de façon synchrone, c'est-à-dire qu'on
        attend qu'un dictionnaire complet ait pu être décodé avant de quitter
        la fonction.
        """
        ret = None
        while ret is None:
            ret = self.__recevoir()
        return ret

    def __recevoir_async(self):
        """Reçoit un message du serveur de jeu façon asynchrone. Si le
        serveur ne renvoit rien, la fonction retourne simplement None.
        """
        self.socket.setblocking(0)
        try:
            reponse = self.__recevoir()
        except socket.error:
            reponse = None
        self.socket.setblocking(1)
        return reponse


class Chrono:
    '''Chronograph class.'''

    def __init__(self, autostart=False):
        '''Initialize counter to zero; if autostart true, start counting.'''
        self.time = 0
        if autostart:
            self.last = time.perf_counter()
        else:
            self.last = None

    def get(self):
        '''Get elapsed time since start; return 0 if not started.'''
        current = time.perf_counter()
        if self.last:
            self.time += current - self.last
            self.last = current
        return self.time

    def reset(self, autostop=False):
        '''Reset counter to zero; if autostop false, keep counting.'''
        self.time = 0
        if autostop:
            self.last = None
        elif self.last:
            self.last = time.perf_counter()

    def start(self):
        '''Start chronograph; does nothing if not already stoped.'''
        if not self.last:
            self.last = time.perf_counter()
        return self

    def stop(self):
        '''Stop chronograph; does nothing if already stopped.'''
        if self.last:
            self.time += time.perf_counter() - self.last
            self.last = None

def testloop(chrono):
    x = None
    while x != 'quit':
        x = input()
        if x == 'start':
            chrono.start()
        elif x == 'stop':
            chrono.stop()
        elif x == 'reset':
            chrono.reset()
        elif x == 'get':
            chrono.get()

        print('chrono={} sec'.format(chrono.get()))

if __name__ == '__main__':
    chrono = Chrono()
    testloop(chrono)
