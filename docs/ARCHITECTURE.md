# Architecture Grover × RATISS

```mermaid
flowchart LR
  A[Phase oracle for state 111] --> B[Grover operator]
  B --> C[Aer ideal and noisy sampling]
  C --> D[Marked state mass]
  E[Iteration index] --> F[TopologicalQubit algorithmic sidecar]
  F --> G[Phase coherence and P sig]
  B --> I[Fake backend target and coupling map]
  I --> J[Hardware aware transpilation]
  J --> K[Aer fake backend noise model]
  K --> L[Observed counts association]
  G --> M[Reality Flag LCT monitor]
  L --> M
  D --> H[Versioned JSON artifact]
  G --> H
  M --> N[Reality Mode artifact]
```

Le sidecar prend l’index d’itération comme horloge expérimentale, mais il n’est pas injecté dans l’oracle, la diffusion ou la mesure Grover. Cette séparation rend visible une co-évolution de deux objets logiciels sans attribuer automatiquement l’un à l’autre.

La voie Reality Mode ajoute un target et un modèle de bruit provenant d’un faux backend IBM empaqueté. Les counts observés produisent une association classique distincte ; le Reality Flag compare les divergences déclarées sans faire de diagnostic matériel ni modifier le circuit historique.
