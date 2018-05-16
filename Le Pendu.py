from tkinter import *
from tkinter import simpledialog, messagebox
from tkinter.messagebox import *
from assets import Options
from assets import DonneeJeu
import random
import copy

# Url
from urllib.request import urlopen
import webbrowser
from threading import Thread

# Musique
from pydub import AudioSegment
from pydub.playback import play
import _thread

def lettrePlusFrequente():
    lettreTri = []
    options.frequences = []
    options.frequencesTemp_NonNul = []
    totalNbLetMot = 0
    
    for i in range(len(options.lettreOrdre)):
        for j in range(len(motsTemp)):
            nbLetMot = motsTemp[j].count(options.lettreOrdre[i])
            totalNbLetMot += nbLetMot
        
        options.frequences.append(totalNbLetMot)
        totalNbLetMot = 0
        
    for k in range(len(options.lettreOrdre)):
        if options.frequences[k] != 0:
            lettreTri.append(options.lettreOrdre[k])
            options.frequencesTemp_NonNul.append(options.frequences[k])
            
    options.lettreOrdre = copy.copy(lettreTri)
    options.frequences = copy.copy(options.frequencesTemp_NonNul)
    return options.frequences.index(max(options.frequences))

def gerer_Dem(etatTemp):
    global options
    options.etatDem = etatTemp

    if etatTemp:
        lance_Demonstration()
        dem.entryconfig(0, state=DISABLED)
        dem.entryconfig(1, state=NORMAL)
    else:
        dem.entryconfig(1, state=DISABLED)
        dem.entryconfig(0, state=NORMAL)

def lance_Demonstration():
    global hypotheses, motsTemp
    longInconnue = len(donnee.motADeviner)
    options.frequences = []
    if not options.triMots:
        hypotheses = [mot for mot in mots if len(mot) == longInconnue]
        motsTemp = copy.copy(hypotheses)
        options.triMots = True

    else:
        if len(hypotheses) == 1:
            entree_Valeur.set(hypotheses[0])
            verifPendu()
        else:
            hypotheses = copy.copy(motsTemp)
            posLettreListe = lettrePlusFrequente()

            entree_Valeur.set(options.lettreOrdre[posLettreListe])
            del options.lettreOrdre[posLettreListe]
            verifPendu()

    if options.etatDem:
        root.update()
        root.after(350, lance_Demonstration)

def obtenirMots():
    with open("assets/mots.txt", 'r') as fichier:
        return [ligne.replace("\n", "") for ligne in fichier]

def obtenirMotAleatoire():
    return mots[random.randint(0, len(mots) - 1)]

def ouvrirURL(dansThread):
    if not dansThread:
        # 'dansThread' permet d'éviter le léger gèlement quand les requetes URL sont exécutés en créant un Thread
        t = Thread(target=ouvrirURL, args=(True,))
        t.start()
    else:
        url = "https://fr.wikipedia.org/wiki/" + options.dernierMot
    
        try:
            urlopen(url)
            webbrowser.open(url)
        except:
            showinfo("Information", "Le dernier mot '" + options.dernierMot + "', n'est pas disponible sur Wikipédia")

def modifOptions_Vie(i):
    if i == -1:
        i = simpledialog.askinteger("Nombre de vie", "Entrez un nombre entre 1 et 999", parent=root, minvalue=1, maxvalue=999)
        
        # Si l'utilisateur ferme la fenetre sans rentrer de valeur
        if i is None:
            return

    modifAffichage_Vie(i)
    options.nbVie = i
    redemarrer(True)

def modifOptions_difficulte(i):
    if i == -1:
        showinfo("Information", "Facile: La première lettre est donnée\n\nNormal: Mode de jeu de base\n\nHardcore: Les vies ne vous sont pas redonnées à chaque nouveau mot")
        return

    options.difficulte = i
    difficulteMAJ(i)
    redemarrer(True)

def modifAffichage_Vie(i):
    pendu_Cadre.itemconfigure(vieText, text=("" if i < 10 else "  " if i < 100 else "    ") + "×" + str(i) + " ") # Espace rajouté entre 10 et 999 vies pour parer un problème d'affichage

def modifLettresEntrees():
    lettres_Utilisees = str(donnee.lettresHistorique)[1:-1].replace("'", "")
    lettres_Valeur.set("Lettre(s) entrée(s):  " + ("Aucune" if lettres_Utilisees == "" else lettres_Utilisees))

def modifPenduImage(erreur):
    tempImg = PhotoImage(file='assets/img/' + str(int(erreur / (options.nbVie / 10))) + '.png')
    pendu_Label.configure(image=tempImg)
    pendu_Label.image = tempImg

def motADevinerMAJ(text):
    mot_Valeur.set("Mot à deviner: " + text)

def scoreMAJ(i):
    score_Valeur.set("Score: " + str(i))

def difficulteMAJ(i):
    difficulte_Valeur.set("Facile      " if i == 0 else "Normal    " if i == 1 else "Hardcore")

def redemarrer(renitialiser):
    global donnee

    options.lettreOrdre = ['e','a','s','i','n','t','r','l','u','o','d','c','p','m','v','g','f','b','q','h', 'k', 'x','j','y','z','w']
    options.triMots = False

    if options.etatDem:
        resultat = messagebox.askyesno("Démonstration", "Continuer la démonstration ?")

        if not resultat:
            gerer_Dem(False)

    if renitialiser:
        options.score = 0

    options.dernierMot = donnee.obtenirMot()
    donnee = DonneeJeu.DonneeJeu(obtenirMotAleatoire(), (donnee.nbErreur if donnee.nbErreur < options.nbVie else 0) if options.difficulte == 2 else 0)
    motADevinerMAJ(donnee.obtenirMotProgression())
    scoreMAJ(options.score)
    modifAffichage_Vie(options.nbVie - donnee.nbErreur)
    modifPenduImage(0)
    modifLettresEntrees()

    if options.difficulte == 0:
        entree_Valeur.set(donnee.motADeviner[0])
        verifPendu()

#La fonction clavier renvoie un argument, *event permet de le rendre facultative pour l'utiliser avec le bouton valider (l'argument  du claviern est inutilisé)
def verifPendu(*enter):
    global motsTemp
    valeur = entree_Champ.get().lower()
    entree_Valeur.set("")

    if valeur == "" or not valeur.isalpha():
        showinfo("Information", "Veuillez insérer une lettre ou un mot !")
        return

    erreur = False
    # C'est un mot
    if len(valeur) != 1:
        if donnee.motADeviner == valeur:
            donnee.lettresHistorique = list(valeur)
        else:
            erreur = True

    # C'est une lettre
    else:
        donnee.ajouterLettre(valeur)
        
        if options.etatDem and valeur in donnee.motADeviner:
            for i in range(len(motsTemp)):
                if donnee.motADeviner.count(valeur) != motsTemp[i].count(valeur):
                    hypotheses.remove(motsTemp[i])
                    
            motsTemp = copy.copy(hypotheses)
            
        if valeur not in donnee.obtenirMot():
            erreur = True

    if erreur:
        donnee.nbErreur += 1
        modifAffichage_Vie(options.nbVie - donnee.nbErreur)
        modifPenduImage(donnee.nbErreur)

    modifLettresEntrees()
    motADevinerMAJ(donnee.obtenirMotProgression())

    if donnee.aDevinerMot():
        showinfo("Gagné !", "Vous avez gagné avec " + str(options.nbVie - donnee.nbErreur) + " vie(s)")
        options.score += 1
        redemarrer(False)

    if options.nbVie - donnee.nbErreur <= 0:
        _thread.start_new_thread(play, (gameOver_Son,))
        showinfo("Perdu !", "Le mot était: " + donnee.obtenirMot())
        redemarrer(True)

gameOver_Son = AudioSegment.from_wav("assets/perdu.wav")

mots = obtenirMots()
donnee = DonneeJeu.DonneeJeu(obtenirMotAleatoire(), 0)
options = Options.Options()

root = Tk()
root.tk_setPalette('white')
root.title("Le Pendu")
root.bind('<Return>', verifPendu)
root.resizable(0,0)

# Menu - Sous-Menu - Configuration
menuPrincipal = Menu(root)
fichier = Menu(menuPrincipal, tearoff=0)
vie = Menu(fichier, tearoff=0)
difficulte = Menu(fichier, tearoff=0)
dem = Menu(fichier,tearoff=0)

menuPrincipal.add_cascade(label="Options", menu=fichier)
fichier.add_cascade(label="Difficulté", menu=difficulte)
fichier.add_cascade(label="Nombre de Vie", menu=vie)
fichier.add_cascade(label="Démonstration", menu=dem)
fichier.add_command(label="Quitter", command=root.destroy)

vie.add_command(label= "Personnalisé", command=lambda:modifOptions_Vie(-1))
vie.add_command(label= "3 Vies", command=lambda:modifOptions_Vie(3))
vie.add_command(label= "5 Vies", command=lambda:modifOptions_Vie(5))
vie.add_command(label= "10 Vies", command=lambda:modifOptions_Vie(10))

difficulte.add_command(label= "Information", command=lambda:modifOptions_difficulte(-1))
difficulte.add_command(label= "Facile", command=lambda:modifOptions_difficulte(0))
difficulte.add_command(label= "Normal", command=lambda:modifOptions_difficulte(1))
difficulte.add_command(label= "Hardcore", command=lambda:modifOptions_difficulte(2))

dem.add_command(label="Lancer démonstration",command=lambda:gerer_Dem(True))
dem.add_command(label="Arrêter démonstration",command=lambda:gerer_Dem(False))
dem.entryconfig(1,state=DISABLED)

root.config(menu=menuPrincipal)

titre = Label(root, text='Le Pendu', fg='#ff0000', font=("Ubuntu", 25))
titre.pack()
# =====

pendu_Cadre = Canvas(root, width=600, height=300, bg='white')

# Affichage "Vie"
img = PhotoImage(file='assets/img/coeur.png')
pendu_Cadre.create_image(10 + 64/2, 64/2, image=img)

vieText = pendu_Cadre.create_text(110, 30, text="×5 ", font=("Arial", 30))
# =====

# Affichage Score
score_Valeur = StringVar()
scoreMAJ(0)
score_Label = Label(pendu_Cadre, textvariable=score_Valeur, font=("Arial", 25))
pendu_Cadre.create_window(67, 100, window=score_Label)
# =====

#  Affichage Difficulté
difficulte_Valeur = StringVar()
difficulteMAJ(1)
difficulte_Label = Label(pendu_Cadre, textvariable=difficulte_Valeur, font=("Arial", 25))
pendu_Cadre.create_window(72, 150, window=difficulte_Label)
# =====

# Affichage Pendu
pendu_Label = Label(pendu_Cadre, image=PhotoImage(file='assets/img/0.png'))
pendu_Cadre.create_window(175 + 450/2, 250/2, window=pendu_Label)
# =====

pendu_Cadre.pack()

# Partie inférieure
entree_Cadre = Frame(root, highlightthickness=0, width=600, height=200, bg='#d9dbdd')
entree_Cadre.pack(fill='both')

lettres_Valeur = StringVar()
modifLettresEntrees()
lettres = Label(entree_Cadre, textvariable=lettres_Valeur, bg='#d9dbdd', font=("Arial", 12))
lettres.pack()

infos = Label(entree_Cadre, text='Entrez une lettre ou le mot', bg='#d9dbdd', font=("Arial", 15))
infos.pack()

mot_Valeur = StringVar()
motADevinerMAJ(donnee.obtenirMotProgression())
mot = Label(entree_Cadre, textvariable=mot_Valeur, bg='#d9dbdd', font=("Arial", 15))
mot.pack()

entree_Valeur = StringVar()
entree_Champ = Entry(entree_Cadre, bg="#d9dbdd", textvariable=entree_Valeur, width=30, font=("Arial", 15), justify='center')
entree_Champ.focus_set()
entree_Champ.pack(side=LEFT, padx=30, ipadx=50, pady=10)

valider = Button(entree_Cadre, text ='Valider', command=verifPendu, font=("Arial", 15))
valider.pack(side=LEFT)

wikipedia = Button(entree_Cadre, text ='?', command=lambda:ouvrirURL(False), font=("Arial", 15))
wikipedia.pack(side=LEFT)
# =====

root.mainloop()
