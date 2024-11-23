import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from sklearn.calibration import calibration_curve, CalibrationDisplay
import matplotlib.ticker as ticker

def tracer_ROC(y_val, pred_probs):
    """
    Trace une courbe ROC pour les valeurs réelles (y_val) et les probabilités prédites, et calcule l'AUC.
    """
    probs_isgoal = pred_probs[:, 1]
    fpr, tpr, _ = roc_curve(y_val, probs_isgoal)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    lw = 2
    plt.plot(
        fpr,
        tpr,
        color="darkorange",
        lw=lw,
        label="Courbe ROC (aire = %0.2f)" % roc_auc,
    )
    # Inclure une ligne de base d'un classificateur aléatoire (50% de chance)
    plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Taux de faux positifs", fontsize=16)
    plt.ylabel("Taux de vrais positifs", fontsize=16)
    plt.title('Courbes ROC', fontsize=16)
    plt.legend(loc="lower right")

    ax = plt.gca()
    ax.grid()
    ax.set_facecolor('0.95')
    plt.tight_layout()
    plt.savefig('roc_curve.png')
    plt.show()

def calculer_percentile(pred_probs, y_val):
    """
    Calcule les percentiles des probabilités prédites et les combine avec les valeurs réelles.
    """
    # Création d'un DataFrame pour les probabilités de tir
    df_probs = pd.DataFrame(pred_probs)
    df_probs = df_probs.rename(columns={0: "Probabilité_non_but", 1: "Probabilité_but"})
    
    # Combinaison des probabilités et de la colonne 'isGoal'
    df_probs = pd.concat([df_probs["Probabilité_but"].reset_index(drop=True), y_val["isGoal"].reset_index(drop=True)], axis=1)
    
    # Calcul des percentiles et ajout dans le DataFrame
    valeurs_percentile = df_probs['Probabilité_but'].rank(pct=True)
    df_probs['Percentile'] = valeurs_percentile * 100
    df_percentile = df_probs.copy()
    
    return df_percentile

def taux_buts(df_percentile):
    """
    Calcule le taux de buts dans chaque intervalle de percentiles.
    """
    liste_taux = []
    largeur_bin = 5
    i = 0
    liste_i = []

    while i < (100 - largeur_bin + 1):  # 95 est la borne inférieure du dernier intervalle
        liste_i.append(i)
        
        # Délimitation des intervalles
        borne_inf = i
        borne_sup = i + largeur_bin
        
        # Lignes correspondant aux percentiles de l'intervalle
        lignes_bin = df_percentile[(df_percentile['Percentile'] >= borne_inf) & (df_percentile['Percentile'] < borne_sup)]
        
        # Calcul du taux de buts
        buts = lignes_bin['isGoal'].value_counts()[1]
        tirs = len(lignes_bin)  # Nombre total de tirs dans l'intervalle
        taux = (buts / tirs) * 100  # Taux en pourcentage
        
        liste_taux.append(taux)
        i += largeur_bin
    
    # Création d'un DataFrame avec les taux de buts
    df_taux_buts = pd.DataFrame(list(zip(liste_taux, liste_i)), columns=['Taux', 'Percentile'])
    
    return df_taux_buts

def tracer_taux_buts(df_taux_buts):
    """
    Trace le taux de buts en fonction des percentiles.
    """
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    ax.grid()
    ax.set_facecolor('0.95')
    x = df_taux_buts['Percentile']
    y = df_taux_buts['Taux']
    plt.plot(x, y)
    ax.set_ylim([0, 100])
    ax.set_xlim([0, 100])
    ax.invert_xaxis()
    ticks_majeurs = np.arange(0, 110, 10)
    ax.set_xticks(ticks_majeurs)
    ax.set_yticks(ticks_majeurs)
    plt.xlabel('Percentile du modèle de probabilité de tir', fontsize=16)
    plt.title('Taux de buts', fontsize=16)
    plt.ylabel('Buts / (Tirs + Buts)%', fontsize=16)
    plt.savefig('goal_rate_plot.png')
    plt.show()

def tracer_taux_buts_cumules(df_percentile):
    """
    Trace les taux cumulatifs de buts en fonction des percentiles.
    """
    plt.figure(figsize=(8, 6))
    df_seulement_but = df_percentile[df_percentile['isGoal'] == 1]
    ax = sns.ecdfplot(data=df_seulement_but, x=100 - df_seulement_but.Percentile)
    ax = plt.gca()
    ax.grid()
    ax.set_facecolor('0.95')
    plt.yticks(np.arange(0, 1.05, 0.1))
    plt.xticks(np.arange(0, 100 * 1.01, 10))
    xvals = ax.get_xticks()
    ax.set_xticklabels(100 - xvals.astype(np.int32), fontsize=16)
    yvals = ax.get_yticks()
    ax.set_yticklabels(['{:,.0%}'.format(y) for y in yvals], fontsize=16)
    ax.set_xlabel('Percentile du modèle de probabilité de tir', fontsize=16)
    ax.set_ylabel('Proportion', fontsize=16)
    ax.set_title(f"% Cumulatif des buts", fontsize=16)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.savefig('cumulative_goal_rate.png')
    ax.legend(['Régression Logistique'])
    plt.show()

def tracer_courbe_calibration(y_val, pred_probs):
    """
    Trace une courbe de calibration pour évaluer les prédictions du modèle.
    """
    plt.figure(figsize=(8, 6))
    ax = CalibrationDisplay.from_predictions(y_val['isGoal'], pred_probs[:, 1], n_bins=50)
    ax = plt.gca()
    ax.grid()
    ax.set_facecolor('0.95')
    ax.set_title(f"Courbe de Calibration", fontsize=16)
    plt.ylabel('Fraction de positifs', fontsize=16)
    plt.xlabel('Probabilité prédite moyenne', fontsize=16)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
    plt.savefig('calibration_curve.png')
    plt.show()