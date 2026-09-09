# -*- coding: utf-8 -*-
"""
EuroDreams - AUDIT 4/4 : le test chi2 d'uniformite des numeros est-il bien
calibre ? (tirage SANS remise de 6 numeros parmi 40 -> ce n'est PAS un
multinomial : les comptages sont negativement correles.)
"""
import numpy as np
from scipy import stats

N, K, T = 40, 6, 297          # 40 numeros, 6 tires, 297 tirages
p, E = K/N, T*K/N
print(f"{T} tirages, effectif attendu par numero E = {E}")

# --- 1. Esperance THEORIQUE de la statistique sous H0 -------------------
# O_i ~ Binomiale(T, p) (marginalement, car les tirages sont i.i.d.)
# Var(O_i) = T p (1-p)  ->  E[chi2] = sum Var/E = N * T p (1-p) / (T p) = N (1-p)
print(f"E[chi2] sous H0 (exact) = N(1-p) = {N*(1-p):.2f}")
print(f"E[chi2] si on suppose (a tort) un multinomial a 40 cases = ddl = {N-1}")
print("-> la statistique est structurellement PLUS PETITE que ce que suppose chi2_39.\n")

# --- 2. Loi nulle par simulation exacte --------------------------------
rng = np.random.default_rng(1234)
B = 200_000
stat = np.empty(B); maxc = np.empty(B, dtype=np.int32)
for b in range(B):
    # T tirages sans remise de 6 parmi 40, vectorise par argpartition
    idx = np.argpartition(rng.random((T, N)), K, axis=1)[:, :K]
    cnt = np.bincount(idx.ravel(), minlength=N)
    stat[b] = ((cnt - E)**2 / E).sum()
    maxc[b] = cnt.max()

OBS = 39.6
print(f"Loi nulle simulee ({B:,} rep.) :".replace(",", " "))
print(f"  moyenne = {stat.mean():.2f}  (theorie {N*(1-p):.2f})   ecart-type = {stat.std():.2f}")
print(f"  quantiles 5/50/95/99 % = {np.quantile(stat,[.05,.5,.95,.99]).round(2)}")
print(f"\n  p-value CORRECTE  pour chi2_obs = {OBS} : {(stat >= OBS).mean():.4f}")
print(f"  p-value NAIVE  (chi2 a 39 ddl)        : {1-stats.chi2.cdf(OBS, N-1):.4f}  <-- valeur annoncee 0,44")
print(f"  ecart : le test naif est CONSERVATEUR, il surestime la p-value de "
      f"~{(1-stats.chi2.cdf(OBS,N-1)) - (stat>=OBS).mean():.3f}")
print(f"  seuil de rejet a 5 % : correct = {np.quantile(stat,.95):.2f} | naif = {stats.chi2.ppf(.95,N-1):.2f}")

# --- 3. Puissance : que faudrait-il pour detecter un biais ? -----------
print("\n--- Puissance du test sur 297 tirages ---")
print("  Correction v6 : le poids w passe a l'echantillonnage sans remise ne donne")
print("  PAS un ratio de frequence egal a w. Le script tabulait donc la puissance")
print("  contre une alternative qui n'etait pas celle annoncee. On CALIBRE : pour")
print("  chaque ratio cible, on cherche le poids qui produit ce ratio, mesure sur")
print("  200 000 tirages simules.")
seuil = np.quantile(stat, .95)
def tire(w, m):
    """m tirages de K numeros sans remise, poids w (course exponentielle)."""
    return np.argpartition(rng.exponential(size=(m, N)) / w, K, axis=1)[:, :K]
def ratio_realise(poids, m=200000):
    w = np.ones(N); w[0] = poids; w /= w.sum()
    f = np.bincount(tire(w, m).ravel(), minlength=N)[0] / m
    return f / (K / N)
def calibre(cible):
    lo, hi = 1.0, 4.0
    for _ in range(18):
        mid = (lo + hi) / 2
        if ratio_realise(mid) < cible: lo = mid
        else: hi = mid
    return (lo + hi) / 2
for cible in (1.05, 1.10, 1.20, 1.50):
    poids = calibre(cible)
    w = np.ones(N); w[0] = poids; w /= w.sum()
    hit = 0
    for b in range(4000):
        cnt = np.bincount(tire(w, T).ravel(), minlength=N)
        hit += (((cnt - E) ** 2 / E).sum() >= seuil)
    print(f"  numero {cible:.2f}x plus frequent (poids calibre {poids:.3f}, "
          f"ratio verifie {ratio_realise(poids):.3f}) -> puissance = {hit/4000:.1%}")
print("  -> sur 297 tirages le test ne detecte qu'un biais ENORME.")
print("     'p = 0,44 donc pas de signal' est un abus : c'est 'pas de signal DETECTABLE'.")

# --- 4. Frequence maximale observee ------------------------------------
print(f"\n--- Statistique du maximum (max de frequence observe = 58) ---")
print(f"  loi nulle du max : moyenne {maxc.mean():.2f}, quantiles 50/90/95 % "
      f"= {np.quantile(maxc,[.5,.9,.95]).round(1)}")
print(f"  P(max >= 58) = {(maxc >= 58).mean():.4f}")
print(f"  P(max <= 58) = {(maxc <= 58).mean():.4f}   <-- a comparer au '59 %' annonce")
