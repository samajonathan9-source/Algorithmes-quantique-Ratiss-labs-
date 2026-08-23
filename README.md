# Algorithmes quantique RATISS labs

Ce dépôt lance un circuit Grover de trois qubits avec un oracle de phase, sous simulation Aer idéale et bruitée. Il enregistre à part l’état du noyau `TopologicalQubit` algorithmique RATISS ; ce sidecar n’est ni une porte Grover native, ni une correction d’erreur quantique.

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_ratiss.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src
```

Les résultats observés, y compris une perte de masse sur l’état marqué ou une valeur de persistance nulle, restent dans `artifacts/grover_ratiss.json`.

Voir [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

Les premières métriques calculées sont dans [`docs/RESULTS.md`](docs/RESULTS.md).
