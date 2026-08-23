# Résultats observés — Grover et sidecar RATISS

La première exécution locale a utilisé Qiskit Aer, seed `42`, un bruit dépolarisant CX de `0.02` et `512` tirs par étape. L’artefact complet est [`artifacts/grover_ratiss.json`](../artifacts/grover_ratiss.json).

| Itération Grover | Profondeur | Masse marquée idéale `111` | Masse marquée bruitée `111` | P sig logique RATISS | Cohérence logicielle |
|---:|---:|---:|---:|---:|---:|
| 0 | 2 | 0.117188 | 0.107422 | 1.214413 | 1.00 |
| 1 | 10 | 0.769531 | 0.669922 | 0.763344 | 0.98 |
| 2 | 18 | 0.962891 | 0.677734 | 0.768691 | 0.96 |

Le circuit idéal augmente la masse de l’état marqué à deux itérations dans cette construction. La version bruitée montre une masse plus faible à ces mêmes étapes. Le sidecar RATISS est exposé en parallèle et demeure marqué `protected=true` selon sa règle algorithmique ; cette sortie ne constitue pas une preuve que la LCT améliore Grover ou corrige son bruit.

> Le résultat est une simulation locale. Il ne correspond pas à une exécution QPU et ne transforme pas le sidecar topologique en composant physique.

## Grover Reality Mode : transpilation et divergence déclarées

Le fichier [`artifacts/grover_reality_mode.json`](../artifacts/grover_reality_mode.json) utilise un snapshot local de `FakeSherbrooke` pour transpiler le même circuit Grover vers une topologie et un modèle de bruit empaquetés. L’allocation déclarée `[0, 14, 26]` entraîne une forte augmentation de profondeur après décomposition, même si aucun `swap` explicite n’est exporté par le transpileur dans cette exécution.

| Itération | Masse idéale | Masse observée | Profondeur compilée | Taille compilée | Divergence LCT | Reality Flag nominal |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 0.117188 | 0.121094 | 4 | 12 | 0.000000 | Non |
| 1 | 0.769531 | 0.339844 | 330 | 770 | 0.015701 | Non |
| 2 | 0.962891 | 0.298828 | 533 | 1102 | 0.043696 | Non |

Le `P_sig` de l’association de counts est `0.0` aux trois étapes et reste inchangé. Il ne devient pas le `P_sig` du sidecar. Avec un seuil nominal de `0.15`, aucune divergence ne déclenche le Reality Flag. Le scénario séparé [`grover_reality_mode_sensitivity.json`](../artifacts/grover_reality_mode_sensitivity.json), dont le seul seuil passe à `0.02`, déclenche le flag à l’itération 2. Cette sortie mesure une condition de simulation locale, non une anomalie sur matériel IBM.

## Reproduction

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_ratiss.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_ratiss.json --shots 512

PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode.json
```

## Référence

[1] [Qiskit — grover_operator](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.grover_operator)

[2] [Qiskit IBM Runtime — fake provider](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/fake-provider)
