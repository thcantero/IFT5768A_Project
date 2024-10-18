# IFT5768A_Projet Équipe A-04

**Étape 1 : Traitement et Visualisation des Données NHL**

Aperçu du Projet
Dans cette étape, nous nous concentrons sur l’acquisition et l’exploration des données de jeu en direct de la NHL en utilisant l'API publique de la NHL. Les principaux objectifs de ce projet incluent:

1. **Traitement des données:** Acquisition des données brutes de l'API de la NHL et conversion en un format utilisable.
2. **Nettoyage des données** Pour une analyse ultérieure.
3. **Debbogeur interactif:** Offre une exploration approfondie de tous les évéenments par saison donnée.
4. **Visualisation:** Création de visualisations simples et avancées pour obtenir des informations à partir des données, y compris des cartes de tirs et de buts.
5. **Article de Blog:** Documentation des résultats dans un blog statique en utilisant Jekyll.


### Structure de projet
/ift6758_projet  
├── /data                # Stocke les données brutes et traitées  
├── /notebooks           # Notebooks Jupyter pour l'acquisition, l'exploration et la visualisation des données  
├── /src                 # Code source Python pour le traitement et la visualisation des données  
├── /images              # Tous les images utilisées dans les visualisations et tous les visualisations  
├── README.md            # Aperçu du projet et instructions  
├── environment.yml      # Fichier de configuration de l'environnement Conda  
└── requirements.txt     # Dépendances Python  

### Instructions d’Installation
1. Cloner le Dépôt
```bash
Copy code
git clone https://github.com/votre-utilisateur/ift6758_projet.git
cd ift6758_projet
```

2. Installer les Dépendances
Vous pouvez installer les packages requis en utilisant soit conda, soit pip.

Utiliser Conda :
```
bash
Copy code
conda env create -f environment.yml
conda activate ift6758
```
Utiliser Pip :

```
bash
Copy code
pip install -r requirements.txt
```

3. Télécharger les Données NHL
Pour télécharger les données de jeu en direct de la NHL, vous pouvez exécuter le script suivant :
```
bash
Copy code
python src/data_acquisition.py
```
Le script téléchargera les données pour les saisons NHL spécifiées et les stockera dans le dossier /data.

4. Lancer les Notebooks Jupyter
Pour explorer et visualiser les données, lancez les Notebooks Jupyter :
```
bash
Copy code
jupyter notebook
```
