# DORA: The TALN Corpus Explorer
## ou
## Découverte et Exploration des Articles TALN

Le script Python **DORA** est conçu pour exploiter le Corpus TALN, une collection d'articles provenant des conférences TALN et RÉCITAL, couvrant la période de 1997 à 2019. Le corpus comprend 1602 articles scientifiques en français, totalisant 5,8 millions de mots, présentés au format Text Encoding Initiative (TEI).


## Fonctionnalités principales

1. **Livret des résumés :** Le script permet d'extraire et d'afficher les informations clés sur les articles, telles que le titre, l'année de publication, les résumés, et les mots-clés. L'utilisateur peut filtrer les articles par année, mots-clés, et choisir le format de sortie entre la console, le texte ou un fichier PDF.

2. **Évolution par année d'un terme donné :** L'utilisateur peut visualiser graphiquement ou tabulairement l'évolution de la fréquence d'un terme spécifique à travers les années du corpus.

3. **Catégorisation non supervisée des articles (Clustering) :** Le script effectue une catégorisation non supervisée des articles en utilisant l'algorithme k-means pour regrouper les articles similaires. Les résultats sont présentés dans un nuage de points avec des annotations.

4. **Taux de citation d'un auteur :** L'utilisateur peut spécifier un auteur, et le script comptera le nombre de citations de cet auteur dans l'ensemble du corpus.

5. **Taux de citation de tous les auteurs :** Le script fournit une analyse statistique du nombre de citations pour tous les auteurs présents dans le corpus. L'utilisateur peut choisir l'ordre de tri et le nombre d'auteurs à afficher.



## Prérequis

Avant d'utiliser le script, assurez-vous d'avoir les bibliothèques Python requises installées. Vous pouvez les installer en utilisant la commande suivante :

```bash
pip install xml.etree.ElementTree fpdf collections tabulate numpy matplotlib scikit-learn nltk mplcursors
```

## Utilisation

Le script peut être utilisé de deux manières :

### 1. Utilisation directe (sans menu)
Vous pouvez utiliser directement le script en créant une instance de la classe TALN et en appelant ses méthodes. Voici un exemple :


```python
# Exemple d'utilisation directe
tei_parser = TALN("corpus_taln_v1.tei.xml", filtre_annee="2014", filtre_mots_cles=["machine learning", "nlp"], format_sortie="pdf", langue="en")

# Charger le contenu XML du fichier
tei_parser.load_xml()

# Itérer à travers les éléments TEI et imprimer/exporter les informations d'article en fonction des conditions
tei_parser.livret_de_resumes()

# Calculer et imprimer la fréquence du terme par année
tei_parser.imprimer_frequence_terme_par_annee(terme="tal", sortie="graphique")

# Regrouper les articles et afficher le nuage de points avec les noms d'articles
tei_parser.cluster_articles(num_clusters=5, article_names=article_names)

# Compter les citations pour un auteur spécifique
tei_parser.compter_citations_pour_author(author_name="Tanguy")

# Compter les citations pour tous les auteurs et afficher les principaux auteurs
tei_parser.count_all_authors(order='desc', top_n=10)
```

### 2. Menu interactif
Le script inclut un menu interactif qui permet aux utilisateurs de choisir différentes options. Pour utiliser le menu, exécutez le script sans aucun argument en ligne de commande :


```bash
python DORA.py
```
#### Importation automatique du fichier TEI XML
Le script tentera d'abord d'importer le fichier `corpus_taln_v1.tei.xml` directement. Si le fichier n'est pas trouvé dans le répertoire courant, il demandera ensuite le chemin d'accès au fichier. Assurez-vous que le fichier est situé dans le bon répertoire ou spécifiez le chemin complet si nécessaire.



### Options du menu

Le menu propose les options suivantes :

- **Livret des résumés** : Traiter et afficher des informations sur les articles de recherche.
- **Évolution par année d'un terme donné** : Analyser l'évolution d'un terme donné au fil des années.
- **Catégorisation non supervisée des articles (clustering)** : Effectuer un regroupement non supervisé des articles.
- **Taux de citation d'un auteur** : Calculer le taux de citation pour un auteur spécifique.
- **Taux de citation de tous les auteurs** : Afficher le taux de citation pour tous les auteurs.

Suivez les instructions pour saisir les informations pertinentes pour chaque option.

## Structure des fichiers

- `DORA.py` : Script Python principal contenant la classe TALN et le menu interactif.
- [`corpus_taln_v1.tei.xml`](https://www.ortolang.fr/market/corpora/corpus-taln) : Corpus TALN (TEI-XML).

## Dépendances

- `xml.etree.ElementTree` : Analyse du contenu XML.
- `fpdf` : Création de documents PDF.
- `collections` : Manipulation de collections, telles que Counter et defaultdict.
- `tabulate` : Formatage et affichage de données tabulaires.
- `numpy` : Opérations numériques.
- `matplotlib` : Tracé de graphiques et diagrammes.
- `sklearn` : Utilitaires d'apprentissage automatique, y compris l'extraction de caractéristiques et le regroupement.
- `nltk` : Kit d'outils de traitement du langage naturel.
- `mplcursors` : Ajout d'annotations interactives aux tracés Matplotlib.

## Licence

Ce script est fourni sous la licence [MIT](https://choosealicense.com/licenses/mit/). N'hésitez pas à le modifier et à le distribuer selon vos besoins. Si vous rencontrez des problèmes ou avez des suggestions d'amélioration, veuillez me le signaler.


## Remerciements

Un merci spécial à Bahar qui a été mon ingénieure QA ! Merci pour tous les bugs découverts, même l'abeille morte derrière le micro-ondes.
