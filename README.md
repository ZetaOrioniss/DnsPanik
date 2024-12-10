Installation des dépendances:

	pip install -r requirements.txt


Énumération de sous-domaines :

    Recherche et identifie les sous-domaines d'un domaine cible à l'aide d'une liste de mots (wordlist).
    Vérifie si les sous-domaines sont actifs (répondent à une requête DNS).
    Enregistre les résultats dans une base de données SQLite.

Énumération des répertoires :

    Recherche et identifie les répertoires disponibles sur un site web cible via des requêtes HTTP.
    Utilise une wordlist pour tester les noms de répertoires courants.
    Enregistre les répertoires valides dans une base de données SQLite.

Stockage des résultats :

    Les données des domaines, sous-domaines et répertoires sont sauvegardées dans une base de données SQLite locale (default.db) pour consultation ou réutilisation future.

Options de ligne de commande :

    --sub : Lance l'énumération des sous-domaines.
    --dir : Lance l'énumération des répertoires.
    --verbose : Mode verbeux pour afficher des détails supplémentaires pendant l'exécution.
    --delete : Supprime la base de données existante.
    -h ou --help : Affiche un guide d'utilisation détaillé.
