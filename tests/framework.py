# -*- coding: utf-8 -*-
"""Micro-framework de test, sans dépendance (pytest n'est pas requis)."""
import sys, time, traceback
_T = []
def test(nom):
    def deco(f): _T.append((nom, f)); return f
    return deco
class Echec(AssertionError): pass
def eq(a, b, msg=""):
    if a != b: raise Echec(f"{msg}\n     obtenu   : {a!r}\n     attendu  : {b!r}")
def proche(a, b, tol, msg=""):
    if abs(a - b) > tol:
        raise Echec(f"{msg}\n     obtenu   : {a!r}\n     attendu  : {b!r} ± {tol}"
                    f"\n     écart    : {abs(a-b):.3e}")
def vrai(c, msg=""):
    if not c: raise Echec(msg or "condition fausse")
def lance(titre):
    print("=" * 78); print(titre); print("=" * 78)
    ok = ko = 0; t0 = time.time()
    for nom, f in _T:
        try:
            f(); print(f"  \033[32mOK\033[0m   {nom}"); ok += 1
        except Exception as e:
            print(f"  \033[31mÉCHEC\033[0m {nom}")
            for l in str(e).rstrip().split("\n"): print(f"        {l}")
            if not isinstance(e, AssertionError):
                traceback.print_exc(limit=2)
            ko += 1
    print("-" * 78)
    print(f"  {ok} réussis, {ko} échoués en {time.time()-t0:.1f} s")
    return ko
