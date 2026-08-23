# Résultats observés — Grover et sidecar RATISS

La première exécution locale a utilisé Qiskit Aer, seed `42`, un bruit dépolarisant CX de `0.02` et `512` tirs par étape. L’artefact complet est [`artifacts/grover_ratiss.json`](../artifacts/grover_ratiss.json).

| Itération Grover | Profondeur | Masse marquée idéale `111` | Masse marquée bruitée `111` | P sig logique RATISS | Cohérence logicielle |
|---:|---:|---:|---:|---:|---:|
| 0 | 2 | 0.117188 | 0.107422 | 1.214413 | 1.00 |
| 1 | 10 | 0.769531 | 0.669922 | 0.763344 | 0.98 |
| 2 | 18 | 0.962891 | 0.677734 | 0.768691 | 0.96 |

Le circuit idéal augmente la masse de l’état marqué à deux itérations dans cette construction. La version bruitée montre une masse plus faible à ces mêmes étapes. Le sidecar RATISS est exposé en parallèle et demeure marqué `protected=true` selon sa règle algorithmique ; cette sortie ne constitue pas une preuve que la LCT améliore Grover ou corrige son bruit.

> Le résultat est une simulation locale. Il ne correspond pas à une exécution QPU et ne transforme pas le sidecar topologique en composant physique.

## Reproduction

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_ratiss.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_ratiss.json --shots 512
```

## Référence

[1] [Qiskit — grover_operator](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.grover_operator)
