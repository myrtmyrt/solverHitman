# IA02 - Projet

Afin de garantir une certaine qualité de code dans nos programmes, nous avons utilisé un outil de lint (black). 


## Préliminaires

La taille de la carte est de m lignes*n colonnes.
On a comme variables le nombre d’invités et le nombre de gardes. 
Personne ne bouge sauf Hitman.

### Les différents objets et personnes du jeu
Il s’agit d’un jeu séquentiel à un joueur. Les objets pouvant se situer sur la carte sont les suivants :
* Hitman
* Un/des garde(s)
* Un/des civil(s)
* Un costume
* Une corde
* Un/des mur(s)


### Les différentes actions possibles
Seul Hitman peut se déplace et effectuer différentes actions : 
* Avancer d'une case 
* Se tourner dans le sens des aiguilles d'une montre
* Se tourner dans le sens contraire des aiguilles d'une montre
* Prendre le costume
* Mettre le costume
* Prendre l'arme
* Neutraliser un garde
* Neutraliser un civil
* Tuer la cible

### Les contraintes du jeu
* Une case ne peut contenir qu’une seule personne (hormis Hitman), un seul objet, être vide ou être un mur.
* Hitman peut se déplacer sur une case adjacente si elle n’est pas un mur, ni occupée par un garde. 
* Il existe un unique costume sur toute la carte
* Il existe une unique arme sur toute la carte 
*Une personne regarde dans une direction (N/S/E/O) sauf la cible.

Les contraintes qui s'appliquent à la phase 1 et donc à la modélisation SAT sont les suivantes :

Une case ne peut contenir qu’une seule personne (hormis Hitman), un seul objet, être vide ou être un mur.
* Il existe un unique costume sur toute la carte
* Il existe une unique arme sur toute la carte 
* Une personne regarde dans une direction (N/S/E/O) sauf la cible.

Recherche à l'aide de la logique propositionnelle}

Représentation du problème}
Les contraintes du jeu sont représentées par des conjonction de clauses afin d'avoir un fichier .cnf exécutable sur le solveur gophersat.

### Les variables
D'après les contraintes et la description du jeu, il nous faut 2 variables guard et civil, représentant les personnes, ainsi que leur orientation (N,S,E,W). On obtient alors 4 variables pour chaque type de personne la représentant avec son orientation.
On a de plus la variable empty et wall, ainsi que les objets, suit et piano\_wire.

## Forces et faiblesses de notre projet
Les forces de notre projet sont les suivantes :
* Nous avons pu implémenter quatre algorithmes de recherche différents, ce qui nous a permis de comparer les résultats obtenus et de choisir le meilleur.
Bien-sûr, c'est le A* qui a donné les meilleurs résultats, mais nous avons pu voir que le DFS et le BFS donnaient aussi, mais avec un temps d'exécution plus long et un score plus élevé.

|         | Map facile | Map moyenne |Map difficile |
|:-------:|:---------:|:-----------:|:------------:|
|   DFS   |  Ligne 1  |   Ligne 1   |   Ligne 1    |
|   DPS   |  Ligne 2  |   Ligne 2   |   Ligne 2    |
| Glouton |  Ligne 3  |   Ligne 3   |   Ligne 3    |
|  Astar  |           |             |              |

## Comment fonctionne notre projet
La modélisation STRIPS est disponible en pdf dans le dossier en dehors de ce README.


Dans la phase 2 de Hitman, le héros peut effectuer des actions qui modifient l’état du jeu, on peut donc représenter une partie de jeu comme une suite d’états successifs, et un plan de jeu comme une suite d’actions
successives.
Cette relation entre les actions et les états fait évidemment penser à un graphe, dans lequel les noeuds sont les états et l’arête entre les noeuds S1 et S2 est l’action A qui permet de passer d’un état à l’autre. En considérant qu’il existe un état initial, on peut même
représenter l’ensemble des états possibles après n actions par un arbre de taille n + 1.
Nous pouvons donc résoudre le problème en utilisant une méthode de parcours d’arbre (informée ou non informée), comme le parcours en profondeur, le parcours en largeur ou l’algorithme A\*.

### Choix d'implémentation et structure de données
Nous avons donc implémenté des algorithmes de parcours d’arbre en python, en stockant un état de jeu dans une variable et en créant un ensemble de fonctions permettant de trouver les états successeurs d’un état donné par une liste d’actions données.
Nous avons utilisé les types hashables (donc non mutables) de python afin de pouvoir stocker les états dans un dictionnaire, pour reconstituer le chemin à la fin de la recherche.
## Comment faire fonctionner notre projet

