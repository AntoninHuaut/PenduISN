class DonneeJeu():
    def __init__(self, mot, erreur):
        self.nbErreur = erreur
        self.motADeviner = mot
        self.lettresHistorique = []

    def ajouterLettre(self, lettre):
        if not lettre in self.lettresHistorique:
            self.lettresHistorique.append(lettre)

    def obtenirMot(self):
        return self.motADeviner

    def obtenirMotProgression(self):
        motProgression = ""

        for lettre in list(self.motADeviner):
            motProgression += lettre if lettre in self.lettresHistorique else "*"

        return motProgression

    def aDevinerMot(self):
        return self.motADeviner == self.obtenirMotProgression()
