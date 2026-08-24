# Audit visuel — Grover Reality Mode

La figure `grover-reality-mode.png` affiche la masse observée de `|111⟩` dans le modèle local hardware-aware en regard du circuit idéal. Les deux courbes sont lisibles et la baisse de masse aux itérations 1 et 2 est directement issue de l’artefact exécuté.

Le panneau inférieur montre la divergence LCT calculée pour le seuil nominal et le scénario de sensibilité. Les seuils `0.15` et `0.02` sont visibles ; depuis la correction du sidecar, les points des itérations 1 et 2 dépassent ces deux seuils et sont identifiés par des marqueurs Reality Flag. Cette figure n’est pas une détection d’anomalie sur QPU réel : elle visualise un modèle Aer local basé sur un snapshot de faux backend IBM.
