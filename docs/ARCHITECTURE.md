# Architecture Grover × RATISS

```mermaid
flowchart LR
  A[Phase oracle for state 111] --> B[Grover operator]
  B --> C[Aer ideal and noisy sampling]
  C --> D[Marked state mass]
  E[Iteration index] --> F[TopologicalQubit algorithmic sidecar]
  F --> G[Phase coherence and P sig]
  D --> H[Versioned JSON artifact]
  G --> H
```

Le sidecar prend l’index d’itération comme horloge expérimentale, mais il n’est pas injecté dans l’oracle, la diffusion ou la mesure Grover. Cette séparation rend visible une co-évolution de deux objets logiciels sans attribuer automatiquement l’un à l’autre.
