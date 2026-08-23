# Protocole — algorithmes quantiques RATISS

## Axe initial : Grover à oracle de phase

L’expérience exécute un circuit Grover compact sur trois qubits avec un oracle de phase pour un état marqué. La même construction est évaluée sans bruit puis avec un canal de bruit Aer déclaré. Après chaque itération, elle enregistre la masse de probabilité observée de l’état marqué, la profondeur du circuit et les états du noyau topologique logiciel RATISS.

## Comparaison exacte

| Comparaison | Mesure | Interprétation autorisée |
|---|---|---|
| Idéal vs bruité | Probabilité de l’état marqué dans les counts | Sensibilité de cette simulation au modèle de bruit choisi |
| Itération initiale vs Grover | Gain ou perte de masse sur l’état marqué | Comportement de l’algorithme dans le simulateur |
| Sidecar RATISS | `P_sig`, phase, torsion, cohérence, état protégé | État de la simulation topologique algorithmique, séparé de Grover |

Cette expérience ne présente pas la LCT comme une optimisation quantique établie. Elle vérifie seulement si des signaux RATISS changent en parallèle d’une trajectoire Grover documentée ; le résultat peut être positif, nul ou contraire à l’hypothèse.

## Référence

La fonction `grover_operator` officielle de Qiskit construit l’opérateur de recherche comme oracle de phase et diffusion [1].

[1] [Qiskit — grover_operator](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.grover_operator)
