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
