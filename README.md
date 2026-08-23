# Algorithmes quantique RATISS labs

# Algorithmes quantiques RATISS Labs

> **Banc d’expériences de circuits quantiques** — Grover sous simulation Aer, comparaison idéal/bruité et lecture séparée d’un sidecar topologique RATISS.

| Type de projet | Objet quantique | Objet RATISS | Produit de recherche |
|---|---|---|---|
| Algorithme quantique reproductible | Recherche Grover, oracle de phase pour `|111⟩` | `TopologicalQubit` algorithmique | Counts, masse de l’état marqué, phase, cohérence et `P_sig` logique |

Ce laboratoire vérifie concrètement une trajectoire simple : un oracle de phase et la diffusion Grover amplifient l’état marqué dans le simulateur idéal ; un canal de bruit déclaré modifie la distribution. Le côté RATISS ne remplace pas Grover : il produit un **second flux de variables topologiques logicielles**, explicitement séparé de l’algorithme quantique.

> Aucune ligne de ce dépôt ne prétend que la LCT optimise Grover, corrige le bruit ou décrit un qubit topologique matériel. Le sidecar est une simulation algorithmique versionnée.

## Visuels issus de l’artefact exécuté

![Masse de l’état marqué Grover](docs/assets/grover-marked-mass.png)

La courbe vert menthe représente les counts Aer idéaux ; la courbe corail vient du même circuit sous bruit CX dépolarisant `p=0.02`. La masse observée de `|111⟩` atteint `0.962891` à l’itération 2 dans l’idéal et `0.677734` sous ce bruit déclaré.

![Cohérence et P sig du sidecar RATISS](docs/assets/grover-ratiss-sidecar.png)

Cette figure ne représente pas une propriété calculée à partir de l’état Grover seul. Elle suit le sidecar `TopologicalQubit` à l’horloge des itérations. Son `P_sig` oscille librement selon ses transformations ; il n’est pas fixé pour suivre la masse Grover.

## Reality Mode Grover : faux backend local et Reality Flag

![Masse observée et divergence LCT Reality Mode](docs/assets/grover-reality-mode.png)

Le Reality Mode ajoute un second protocole, séparé de l’expérience historique : Qiskit transpile Grover vers le *target* et la topologie de couplage empaquetés par `FakeSherbrooke`, puis Aer utilise le modèle de bruit local dérivé de ce faux backend. Aucun job QPU n’est soumis. L’allocation physique déclarée est `[0, 14, 26]` ; la profondeur compilée passe de `4` à `330` puis `533` aux itérations 0, 1 et 2. Le transpileur n’a exporté aucun `swap` explicite dans cette exécution, mais a tout de même décomposé le circuit dans le jeu de portes de la cible.

![Coût de transpilation hardware-aware](docs/assets/grover-hardware-aware.png)

Le moniteur reçoit les counts observés, construit une association de counts RATISS séparée, puis compare la masse marquée et les sidecars idéal/observé. Son **Reality Flag** est une condition LCT déclarée, pas un diagnostic d’un QPU réel. Avec le seuil nominal `0.15`, aucune itération ne déclenche le flag. Un scénario de sensibilité séparé, à seuil `0.02`, le déclenche à l’itération 2 lorsque la divergence calculée vaut `0.0436962248`.

| Itération | Masse idéale | Masse observée fake backend | Profondeur compilée | Divergence LCT nominale | P sig association counts |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.117188 | 0.121094 | 4 | 0.000000 | 0.0 |
| 1 | 0.769531 | 0.339844 | 330 | 0.015701 | 0.0 |
| 2 | 0.962891 | 0.298828 | 533 | 0.043697 | 0.0 |

## Architecture

```mermaid
flowchart LR
  A[Phase oracle for 111] --> B[Grover operator]
  B --> C[Aer sampling]
  C --> D[Marked state mass]
  E[Iteration clock] --> F[RATISS logical sidecar]
  F --> G[Phase coherence and P sig]
  B --> I[Fake backend target and noise model]
  I --> J[Hardware aware transpilation]
  J --> K[Observed counts association]
  G --> L[Reality Flag LCT]
  K --> L
  D --> H[JSON artifact]
  G --> H
  L --> M[Reality Mode artifact]
```

L’architecture détaillée est dans [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). La séparation des branches de calcul est une contrainte centrale : les résultats Grover et RATISS sont enregistrés dans le même artefact, mais ne sont jamais convertis l’un dans l’autre.

## Résultats calculés

| Itération | Masse `|111⟩` idéale | Masse `|111⟩` bruitée | `P_sig` logique RATISS | Cohérence logique |
|---:|---:|---:|---:|---:|
| 0 | 0.117188 | 0.107422 | 1.214413 | 1.00 |
| 1 | 0.769531 | 0.669922 | 0.763344 | 0.98 |
| 2 | 0.962891 | 0.677734 | 0.768691 | 0.96 |

Ces valeurs viennent de [`artifacts/grover_ratiss.json`](artifacts/grover_ratiss.json), avec seed `42` et `512` tirs. Elles peuvent changer lorsque la configuration, le seed, le bruit, l’oracle ou le nombre de tirs changent ; le dépôt conserve la configuration avec les sorties.

## Exécution locale

```bash
git clone https://github.com/evinajonathan13-max/Algorithmes-quantique-Ratiss-labs-.git
git clone https://github.com/evinajonathan13-max/ratiss-topological-decoherence-engine.git
cd Algorithmes-quantique-Ratiss-labs-
python3 -m pip install -e .

PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_ratiss.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_ratiss.json --shots 512

PYTHONPATH=../ratiss-topological-decoherence-engine/src \
python3 scripts/run_grover_reality_mode.py \
  --engine-src ../ratiss-topological-decoherence-engine/src \
  --output artifacts/grover_reality_mode.json --shots 512
```

## Tests

```bash
PYTHONPATH=../ratiss-topological-decoherence-engine/src python3 -m pytest -q
python3 scripts/generate_docs_figures.py
```

Les tests vérifient que le circuit construit reste à trois qubits avec trois mesures et que la masse marquée est dérivée des counts fournis, non d’une constante attendue.

## Documentation du laboratoire

| Document | Ce qu’il apporte |
|---|---|
| [`PROTOCOL.md`](docs/PROTOCOL.md) | Construction de l’oracle et comparaisons autorisées |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Séparation Grover / sidecar RATISS |
| [`RESULTS.md`](docs/RESULTS.md) | Observations exactes de la première exécution |
| [`VISUAL_AUDIT.md`](docs/VISUAL_AUDIT.md) | Validation de lecture des graphiques |
| [`REALITY_MODE.md`](docs/REALITY_MODE.md) | Contrat du faux backend, Reality Flag et scénarios de seuil |
| [`REALITY_MODE_VISUAL_AUDIT.md`](docs/REALITY_MODE_VISUAL_AUDIT.md) | Vérification des nouveaux graphiques Reality Mode |

Distribué sous [licence MIT](LICENSE).
