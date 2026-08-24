# Grover Reality Mode — contrat local hardware-aware

## Portée

Cette expérience est une **simulation locale Aer** utilisant `FakeSherbrooke` de Qiskit IBM Runtime comme source empaquetée de target, de carte de couplage et de propriétés de calibration. Elle ne contacte pas IBM Quantum, ne soumet pas un circuit au matériel et ne présente pas le snapshot comme une calibration en direct. [1]

Le circuit logique reste le Grover trois qubits déjà versionné. Il est transpilé avec l’allocation physique déclarée `[0, 14, 26]`, puis exécuté dans Aer avec le modèle de bruit local construit depuis le faux backend. Un terme dépolarisant CX additionnel de `0.01` est inclus dans le profil et conservé dans `hidden_ground_truth` jusqu’après le calcul du moniteur.

## Le Reality Flag

Le moniteur ne reconstruit pas une matrice densité matérielle. Il observe les counts, la masse de l’état marqué et un sidecar algorithmique bruité par la dégradation mesurée. Sa divergence est :

```text
mass_gap = abs(ideal_marked_mass - observed_marked_mass)
psig_gap = abs(expected_sidecar_P_sig - observed_sidecar_P_sig)
lct_divergence = (mass_gap × psig_gap) / abs(expected_sidecar_P_sig × expected_sidecar_coherence)
```

Le flag est levé seulement quand cette valeur strictement calculée dépasse le seuil fourni au scénario. L’association provenant des counts conserve son propre `P_sig`; dans l’exécution actuelle il vaut `0.0` à chaque itération, et aucune valeur logique ne le remplace.

| Profil | Seuil LCT | Flags observés | Lecture autorisée |
|---|---:|---|---|
| Nominal | 0.15 | Itérations 1 et 2 | Depuis la correction du sidecar (moteur PR #1), la divergence calculée (`0.169988`, `0.526472`) franchit ce seuil. |
| Sensibilité | 0.02 | Itérations 1 et 2 | Le même franchissement est conservé sous ce seuil plus bas. |

Le flag ne déclare pas une anomalie réelle, une dérive IBM ou une correction d’erreur. Il marque une différence dans la simulation locale et indique la frontière d’itération où elle a été observée.

## Reproduction

```bash
PYTHONPATH=/chemin/vers/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src /chemin/vers/ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode.json

PYTHONPATH=/chemin/vers/ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src /chemin/vers/ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode_sensitivity.json \
  --reality-flag-lct-threshold 0.02
```

## Références

[1] [Qiskit IBM Runtime — fake provider](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/fake-provider)
