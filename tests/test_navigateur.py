# -*- coding: utf-8 -*-
"""
Test de bout en bout : l'application s'ouvre-t-elle sans erreur et les cinq
onglets se rendent-ils ? Ignoré silencieusement si Playwright n'est pas installé
(pip install playwright && playwright install chromium).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from framework import test, eq, vrai, lance
APP = "file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
                                               "eurodreams_v6.html"))
try:
    from playwright.sync_api import sync_playwright
    DISPO = True
except ImportError:
    DISPO = False

def _session(actions):
    """Ouvre l'application, exécute `actions(page)`, renvoie les erreurs JS."""
    errs = []
    with sync_playwright() as pw:
        exe = "/opt/pw-browsers/chromium"
        nav = pw.chromium.launch(executable_path=exe if os.path.exists(exe) else None)
        pg = nav.new_page(viewport={"width": 430, "height": 900})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(APP)
        actions(pg)
        nav.close()
    return errs

@test("les 5 onglets se rendent sans une seule erreur JavaScript")
def _():
    if not DISPO: print("        (ignoré : playwright absent)"); return
    def actions(pg):
        for t in ("bank", "data", "cag", "pop", "gen"):
            pg.click(f'button[data-t="{t}"]'); pg.wait_for_timeout(400)
            vrai(pg.eval_on_selector(f"#tab-{t}", "e=>!e.classList.contains('hide')"),
                 f"l'onglet {t} ne s'affiche pas")
    eq(_session(actions), [])

@test("le générateur refuse plus de 6 grilles disjointes et le dit")
def _():
    if not DISPO: print("        (ignoré : playwright absent)"); return
    vu = {}
    def actions(pg):
        pg.fill("#nGrilles", "12"); pg.select_option("#strat", "disj")
        pg.click("#go"); pg.wait_for_timeout(500)
        vu["t"] = pg.inner_text("#out")
    eq(_session(actions), [])
    vrai("Impossible" in vu["t"], "aucun avertissement affiché")

@test("la bankroll charge l'historique et signale les tirages en régime Boost")
def _():
    if not DISPO: print("        (ignoré : playwright absent)"); return
    vu = {}
    def actions(pg):
        pg.click('button[data-t="bank"]'); pg.wait_for_timeout(300)
        pg.click("#bDemo"); pg.wait_for_timeout(1500)
        vu["k"] = pg.inner_text("#bKpi"); vu["d"] = pg.input_value("#bDate")
    eq(_session(actions), [])
    vrai("33 tirage(s) en régime Boost" in vu["k"], "le Boost n'est pas compté")
    vrai("+24,76 €" in vu["k"], "le bonus d'espérance du Boost a changé")
    vrai(vu["d"] and vu["d"][0] == "2", "la date par défaut n'est pas renseignée")

@test("la saisie refuse une ligne vide et un gain négatif")
def _():
    if not DISPO: print("        (ignoré : playwright absent)"); return
    vu = {}
    def actions(pg):
        pg.click('button[data-t="bank"]'); pg.wait_for_timeout(300)
        pg.fill("#bK", "0"); pg.select_option("#bJ", "0")
        pg.click("#bAdd"); pg.wait_for_timeout(300)
        vu["vide"] = pg.inner_text("#bMsg")
        pg.fill("#bK", "4"); pg.select_option("#bJ", "1"); pg.fill("#bGain", "-5")
        pg.click("#bAdd"); pg.wait_for_timeout(300)
        vu["neg"] = pg.inner_text("#bMsg")
    eq(_session(actions), [])
    vrai("Rien à enregistrer" in vu["vide"], "ligne vide acceptée")
    vrai("ne peut pas être négatif" in vu["neg"], "gain négatif accepté")

if __name__ == "__main__":
    sys.exit(lance("TESTS — APPLICATION DANS UN NAVIGATEUR"))
