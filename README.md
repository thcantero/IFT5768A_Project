<<<<<<< HEAD
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
│
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
=======
# IFT5768A_Project Équipe A-04

## **IFT 6758 - Milestone 1: NHL Data Wrangling and Visualization**

### **Project Overview**
This project is part of the IFT 6758 course at Université de Montréal. In this milestone, we focus on acquiring and exploring NHL play-by-play data using the NHL's public API. The key objectives of this project include:

- **Data Wrangling**: Acquiring raw data from the NHL API and converting it into a usable format.
- **Exploratory Data Analysis**: Cleaning and processing the data for further analysis.
- **Visualization**: Creating both simple and advanced visualizations to gain insights from the data, including shot and goal maps.
- **Blog Post**: Documenting the results in a static blog using Jekyll.

### **Project Structure**

```
/ift6758_project
│
├── /data                # Stores raw and processed data
├── /notebooks           # Jupyter notebooks for data acquisition, exploration, and visualization
├── /src                 # Python source code for data processing and visualization
├── /images              # Images (e.g., rink template) used in visualizations
├── /blog                # Blog post template (Markdown)
├── .gitignore           # Git ignore file to avoid committing large data files
├── README.md            # Project overview and instructions
├── environment.yml      # Conda environment setup file
└── requirements.txt     # Python dependencies
```

### **Setup Instructions**

#### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/ift6758_project.git
cd ift6758_project
```

#### **2. Install Dependencies**

You can install the required packages using either **conda** or **pip**.

- **Using Conda**:
    ```bash
    conda env create -f environment.yml
    conda activate ift6758
    ```

- **Using Pip**:
    ```bash
    pip install -r requirements.txt
    ```

#### **3. Download NHL Data**

To download the NHL play-by-play data, you can run the following script:

```bash
python src/data_acquisition.py
```

The script will download the data for specified NHL seasons and store it in the `/data` folder.

#### **4. Run Jupyter Notebooks**

To explore and visualize the data, launch Jupyter Notebooks:

```bash
jupyter notebook
```

Open the relevant notebooks in the `/notebooks` directory, such as `data_acquisition.ipynb` or `visualization.ipynb`.

#### **5. Generate Visualizations**

After processing the data, you can generate shot maps and other visualizations by running the Python scripts in the `/src` directory or the cells in the Jupyter notebooks.

#### **6. Create Blog Post**

Once all visualizations are generated, the results will be documented in a blog post using the template located in `/blog`. To preview the blog locally, install Jekyll and run:

```bash
jekyll serve
```

### **Key Features**

- **Data Acquisition**: Automated download of NHL play-by-play data for specific seasons.
- **Data Cleaning**: Processing raw data into clean Pandas dataframes.
- **Interactive Visualizations**: Tools like `matplotlib` and `ipywidgets` to explore game data interactively.
- **Shot Maps**: Generate advanced visualizations such as shot and goal maps using the coordinates from the dataset.

### **References**

- [NHL Stats API](https://gitlab.com/dword4/nhlapi)
- [Jekyll Documentation](https://jekyllrb.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### **Team Contributions**

- **Member 1**: Data acquisition and API integration
- **Member 2**: Data cleaning and exploratory analysis
- **Member 3**: Visualization and blog post
>>>>>>> 037983d2aa846db963fdd0a6be7a32af92b6ca43
