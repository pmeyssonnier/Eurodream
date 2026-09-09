# -*- coding: utf-8 -*-
"""Lance toute la suite. Code de sortie = nombre de tests échoués."""
import importlib, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import framework
MODULES = [("test_probabilites", "COMBINATOIRE EURODREAMS"),
           ("test_joker_pmf",    "LOI DU GAIN JOKER+"),
           ("test_donnees",      "DONNÉES OFFICIELLES"),
           ("test_application",  "COHÉRENCE APPLICATION / SCRIPTS"),
           ("test_navigateur",   "APPLICATION DANS UN NAVIGATEUR")]
total = 0
for mod, titre in MODULES:
    framework._T.clear()
    importlib.import_module(mod)
    total += framework.lance(titre)
    print()
print("=" * 78)
print("  SUITE COMPLÈTE : " + ("TOUT PASSE" if total == 0 else f"{total} ÉCHEC(S)"))
print("=" * 78)
sys.exit(min(total, 125))
