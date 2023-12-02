import xml.etree.ElementTree as ET
from fpdf import FPDF 
from collections import defaultdict
from collections import Counter
from tabulate import tabulate 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerPathCollection
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from nltk.corpus import stopwords
import mplcursors
import re


# Définition de la classe LivretDeResumes
class LivretDeResumes:
    def __init__(self, file_path, filtre_annee=None, filtre_mots_cles=None, format_sortie="console", langue = None):
        # Initialisation de l'objet LivretDeResumes avec les paramètres spécifiés
        """
        :param file_path: Chemin du fichier XML TEI à traiter.
        :param filtre_annee: Année de publication à filtrer (par défaut None pour ne pas filtrer par année).
        :param filtre_mots_cles: Liste de mots-clés à filtrer (par défaut None pour ne pas filtrer par mots-clés).
        :param format_sortie: Format de sortie, parmi "console", "texte" et "pdf" (par défaut "console").
        :param langue: Langue du résumé : fr, en ou toutes (par défaut None pour imprimer dans n'importe quelle langue).
        """
        self.file_path = file_path
        self.namespaces = {"tei": "http://www.tei-c.org/ns/1.0", "xml": "http://www.w3.org/XML/1998/namespace"}
        self.tree = None
        self.root = None
        self.filtre_annee = filtre_annee
        # Conversion des mots-clés en un ensemble pour une recherche plus efficace
        # self.filtre_mots_cles = set(filtre_mots_cles) if filtre_mots_cles else set()
        self.filtre_mots_cles = set(filtre_mots_cles) if filtre_mots_cles else []  
        self.format_sortie = format_sortie
        self.langue = None if langue == "toutes" else langue
        # print("self.langue : ", type(self.langue))
        # print("Filtre année:", self.filtre_annee)
        # print("Filtre mots-clés:", self.filtre_mots_cles)



    def load_xml(self):
        # Charge le fichier XML à partir du chemin spécifié
        self.tree = ET.parse(self.file_path)
        self.root = self.tree.getroot()

    def obtenir_texte_dans_toutes_langues(self, element, xpath):
        # Obtient le texte dans toutes les langues à partir de l'élément et du chemin XPath spécifiés
        textes = []
        for lang in element.findall(xpath, self.namespaces):
            texte = lang.text.strip() if lang.text else ""
            textes.append(texte)
        return textes

    def imprimer_info_article(self, element_tei):
        # Obtient et imprime les informations sur l'article à partir de l'élément TEI spécifié
        titre_article = element_tei.find(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", self.namespaces).text
        annee_article = element_tei.find(".//tei:date", self.namespaces)
        texte_annee_article = annee_article.text if annee_article is not None else "N/A"
        textes_resume = self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:div[@type='abstract']/tei:p")
        textes_mots_cles = self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:div[@type='keywords']/tei:p")

        # Vérifie si l'article satisfait les filtres spécifiés
        if (not self.filtre_annee or texte_annee_article == self.filtre_annee) and \
           all(keyword.lower() in ' '.join(textes_mots_cles).lower() for keyword in self.filtre_mots_cles):
            if self.format_sortie.lower() == "console":
                # Affiche les informations sur la console
                self.imprimer_console(titre_article, texte_annee_article, textes_resume, textes_mots_cles)
            elif self.format_sortie.lower() == "texte":
                # Exporte vers un document texte (par exemple, .txt)
                with open("sortie.txt", "a+", encoding="utf-8") as fichier:
                    self.imprimer_texte(fichier, titre_article, texte_annee_article, textes_resume, textes_mots_cles)
            elif self.format_sortie.lower() == "pdf":
                # Exporte vers un document PDF
                self.imprimer_pdf(titre_article, texte_annee_article, textes_resume, textes_mots_cles)

    def imprimer_console(self, titre_article, texte_annee_article, textes_resume, textes_mots_cles):
        # Imprime les informations sur la console
        print(f"Titre de l'article : {titre_article}")
        print(f"Année de publication : {texte_annee_article}")
        for i, texte_resume in enumerate(textes_resume):
            code_langue = "fr" if i == 0 else "en"
            if texte_resume != "None" and (code_langue == self.langue or self.langue is None):
                print(f"Résumé ({code_langue}): {texte_resume}")
        for i, texte_mots_cles in enumerate(textes_mots_cles):
            code_langue = "fr" if i == 0 else "en"
            if texte_mots_cles != "None" and (code_langue == self.langue or self.langue is None):
                print(f"Mots-clés ({code_langue}): {texte_mots_cles}")
        print()

    def imprimer_texte(self, fichier, titre_article, texte_annee_article, textes_resume, textes_mots_cles):
        # Exporte les informations vers un document texte
        fichier.write(f"Titre de l'article : {titre_article}\n")
        fichier.write(f"Année de publication : {texte_annee_article}\n")
        
        for i, texte_resume in enumerate(textes_resume):
            code_langue = "fr" if i == 0 else "en"

            if texte_resume != "None" and (code_langue == self.langue or self.langue is None):
                fichier.write(f"Résumé ({code_langue}): {texte_resume}\n")
        for i, texte_mots_cles in enumerate(textes_mots_cles):
            code_langue = "fr" if i == 0 else "en"
            if texte_mots_cles != "None" and (code_langue == self.langue or self.langue is None):
                fichier.write(f"Mots-clés ({code_langue}): {texte_mots_cles}\n")
        
        fichier.write("\n")

    def imprimer_pdf(self, titre_article, texte_annee_article, textes_resume, textes_mots_cles):
        # Exporte les informations vers un document PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        def convertir_texte(texte):
            return texte.encode('latin-1', 'replace').decode('latin-1')

        def ajouter_texte_multiligne(pdf, textes):
            # Ajoute du texte multi-ligne avec des sauts de ligne automatiques
            for texte in textes:
                pdf.multi_cell(0, 10, convertir_texte(texte))
            pdf.ln(5)

        pdf.set_font("Arial", size=12)

        # Itère à travers les éléments TEI
        for element_tei in self.root.findall(".//tei:TEI", self.namespaces):
            titre_article = element_tei.find(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", self.namespaces).text
            annee_article = element_tei.find(".//tei:date", self.namespaces)
            texte_annee_article = annee_article.text if annee_article is not None else "N/A"
            textes_resume = self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:div[@type='abstract']/tei:p")
            textes_mots_cles = self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:div[@type='keywords']/tei:p")

            # Vérifie si l'article satisfait les filtres spécifiés
            if (not self.filtre_annee or texte_annee_article == self.filtre_annee) and \
               all(keyword.lower() in ' '.join(textes_mots_cles).lower() for keyword in self.filtre_mots_cles):
                ajouter_texte_multiligne(pdf, [f"Titre de l'article : {titre_article}", f"Année de publication: {texte_annee_article}"])

                for i, texte_resume in enumerate(textes_resume):
                    code_langue = "fr" if i == 0 else "en"
                    if texte_resume != "None" and (code_langue == self.langue or self.langue is None):
                        ajouter_texte_multiligne(pdf, [f"Résumé ({code_langue}): {texte_resume}"])

                for i, texte_mots_cles in enumerate(textes_mots_cles):
                    code_langue = "fr" if i == 0 else "en"
                    if texte_mots_cles != "None" and (code_langue == self.langue or self.langue is None):
                        ajouter_texte_multiligne(pdf, [f"Mots-clés ({code_langue}): {texte_mots_cles}"])

        # Sortie PDF
        pdf.output("sortie.pdf")


    def iterer_elements_tei(self):
        # Itère à travers les éléments TEI et imprime les informations sur chaque article
        match_found = False  # Supposons qu'aucun match n'est trouvé

        for element_tei in self.root.findall(".//tei:TEI", self.namespaces):
            if self.imprimer_info_article(element_tei) is not None:
                match_found = True

        # Imprimer le message d'erreur si aucun match n'est trouvé
        if not match_found:
            print("\nAucun texte ne répond à ces critères !\n")


    def calculer_frequence_terme_par_annee(self, terme):
        # Initialise un dictionnaire par année pour stocker la fréquence du terme
        frequence_par_annee = defaultdict(int)

        # Itère à travers tous les éléments TEI sans considérer les filtres
        for element_tei in self.root.findall(".//tei:TEI", self.namespaces):
            annee_article = element_tei.find(".//tei:date", self.namespaces)
            texte_annee_article = annee_article.text if annee_article is not None else "N/A"

            # Obtient le texte de l'article
            texte_article = ' '.join(self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:body//tei:p"))

            # Calcule la fréquence du terme dans le texte de l'article
            frequence_terme = texte_article.lower().count(terme.lower())

            # Incrémente la fréquence par année
            frequence_par_annee[texte_annee_article] += frequence_terme

        return frequence_par_annee

    def imprimer_frequence_terme_par_annee(self, terme, sortie="tabulaire"):
        # Affiche la fréquence du terme par année sous forme tabulaire ou graphique
        frequence_par_annee = self.calculer_frequence_terme_par_annee(terme)

        if sortie == "tabulaire":
            table_data = [("Année", "Fréquence")]
            for annee, frequence in frequence_par_annee.items():
                table_data.append((annee, frequence))

            # Affichage tabulaire sur la console
            print(tabulate(table_data, headers="firstrow", tablefmt="grid"))
        elif sortie == "graphique":
            # Affichage graphique avec une ligne de tendance
            plt.plot(list(frequence_par_annee.keys()), list(frequence_par_annee.values()), marker='o', linestyle='-', color='b')
            plt.xlabel("Année")
            plt.ylabel("Fréquence")
            plt.title(f"Fréquence du terme '{terme}' par année")
            plt.grid(True)
            plt.show()
        else:
            print("Option de sortie non valide. Veuillez choisir entre 'tabulaire' et 'graphique'.")

    def cluster_articles(self, num_clusters=3, article_names=None):
        # Extraire les données textuelles des articles
        text_data = []
        for element_tei in self.root.findall(".//tei:TEI", self.namespaces):
            text_data.append(' '.join(self.obtenir_texte_dans_toutes_langues(element_tei, ".//tei:body//tei:p")))

        # Vectoriser les données textuelles en utilisant TF-IDF
        vectorizer = TfidfVectorizer(stop_words=stopwords.words('english') + stopwords.words('french'))
        text_matrix = vectorizer.fit_transform(text_data)

        # Appliquer une réduction de dimensionnalité en utilisant Truncated SVD
        svd = TruncatedSVD(n_components=100)
        text_matrix = svd.fit_transform(text_matrix)

        # Effectuer le regroupement par k-means
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        kmeans.fit(text_matrix)
        cluster_labels = kmeans.labels_

        # Afficher un nuage de points
        self.plot_scatterplot(text_matrix, cluster_labels, article_names)


    def plot_scatterplot(self, text_matrix, cluster_labels, article_names):
        # Créer un nuage de points
        plt.figure(figsize=(8, 6))
        scatter = plt.scatter(text_matrix[:, 0], text_matrix[:, 1], c=cluster_labels, cmap='viridis', s=50, alpha=0.6)

        # Obtenir les étiquettes de cluster uniques et les couleurs correspondantes
        unique_labels = np.unique(cluster_labels)
        colors = scatter.to_rgba(cluster_labels)

        # Créer des repères de légende personnalisés
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors[cluster_labels == label][0], markersize=10) for label in unique_labels]

        # Ajouter une légende avec des repères et des étiquettes personnalisés
        plt.legend(legend_handles, unique_labels, title='Clusters', loc='upper right')

        # Annoter chaque point avec le nom de l'article
        labels = article_names

        def on_hover(sel):
            index = sel.target.index
            label = f'Titre de l\'article : "{labels[index]}"'
            
            # Supprimer le caractère de saut de ligne
            label = label.replace('\n', '')

            sel.annotation.set_text(label)


        # Activer les annotations de curseur en utilisant mplcursors
        mplcursors.cursor(hover=True).connect("add", on_hover)

        plt.title("Nuage de points des clusters")
        plt.xlabel("Composante principale 1")
        plt.ylabel("Composante principale 2")

        plt.show()

    



    def compter_citations_pour_author(self, author_name):
        # Convertir le nom de l'auteur en minuscules pour une comparaison insensible à la casse
        author_name_lower = re.sub(r'[^\w\s]', '', author_name.lower())

        # Initialiser un compteur pour les citations de l'auteur donné
        citations_count = 0

        # Itérer à travers toutes les entrées <bibl> dans le fichier XML
        for bibl_entry in self.root.findall(".//tei:listBibl/tei:bibl", self.namespaces):
            # Extraire le texte de l'entrée <bibl>
            bibl_text = bibl_entry.text

            # Vérifier si bibl_text n'est pas None
            if bibl_text is not None:
                # Trouver l'indice de la parenthèse ouvrante dans le texte bibl
                paren_index = bibl_text.find("(")

                # Extraire la sous-chaîne des noms d'auteurs jusqu'à la parenthèse ouvrante
                authors_text = bibl_text[:paren_index].strip() if paren_index != -1 else bibl_text.strip()

                # Normaliser les espaces et la ponctuation dans les noms d'auteurs
                authors_text_normalized = re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', authors_text)).lower()

                # Diviser les noms d'auteurs par "&", ",", "et" et "and"
                authors = [name.strip() for name in re.split(r'&|,|et|and', authors_text_normalized)]

                # Vérifier si le nom de l'auteur donné (nom complet ou nom de famille uniquement) est dans la liste des auteurs (insensible à la casse et en considérant les limites de mots)
                if any(re.sub(r'[^\w\s]', '', author_name_lower) in re.sub(r'[^\w\s]', '', author) for author in authors):
                   citations_count += 1

                    

        # Imprimer ou retourner le résultat selon les besoins
        print(f"{author_name} a été cité {citations_count} fois dans l'ensemble du document.")
        
        return citations_count


    def count_all_authors(self, order='desc', top_n=None):
        # Créer un compteur pour compter les occurrences de chaque auteur
        authors_counter = Counter()

        # Itérer à travers toutes les entrées <bibl> dans le fichier XML
        for bibl_entry in self.root.findall(".//tei:listBibl/tei:bibl", self.namespaces):
            # Extraire le texte de l'entrée <bibl>
            bibl_text = bibl_entry.text

            # Vérifier si bibl_text n'est pas None
            if bibl_text is not None:
                # Diviser le bibl_text en lignes
                rows = [row.strip() for row in bibl_text.split('\n') if row.strip()]

                # Extraire les noms d'auteurs de chaque ligne
                for row in rows:
                    # Vérifier si la ligne contient une parenthèse ouvrante, quatre chiffres numériques et une parenthèse fermante
                    if re.search(r'\(\d{4}\)', row):
                        # Supprimer tout après r"\s("
                        row = re.sub(r'\s\(.+', '', row)

                        # Diviser les noms d'auteurs par "&", ",", "et", "and"
                        author_delimiters = r'&|,|et|and'

                        # Diviser par délimiteur, mais éviter de diviser dans des cas spécifiques
                        authors = re.split(f'(?<!\w)({author_delimiters})(?!\w)|(?<=,)(?=\s[A-Z]\.)', row)

                        # Filtrer les mots courts (initiales)
                        authors = [author.strip() for author in authors if author and len(author.split()) >= 2]

                        # Mettre à jour le compteur avec les auteurs de la ligne actuelle
                        authors_counter.update(authors)

        # Imprimer les principaux auteurs en fonction de l'ordre spécifié et de top_n dans un tableau
        sorted_authors = sorted(authors_counter.items(), key=lambda x: x[1], reverse=(order == 'desc'))

        headers = ["Auteur", "Nombre de citations"]
        table_data = [(author, count) for author, count in sorted_authors[:top_n]]

        print(tabulate(table_data, headers=headers, tablefmt="grid"))




# Fonction pour afficher le menu principal et gérer l'interaction utilisateur
def afficher_menu_principal():
    print("Menu principal:")
    print("1. Livret des résumés")
    print("2. Evolution par année d'un terme donné")
    print("3. Catégorisation non supervisée des articles (clustering)")
    print("4. Taux de citation d'un auteur")
    print("5. Taux de citation de tous les auteurs")
    print("0. Quitter")

    choix = input("Choisissez une option (1-5) ou 0 pour quitter : ")

    if choix == "1":
        traiter_livret_des_resumes()
    elif choix == "2":
        traiter_evolution_par_annee()
    elif choix == "3":
        traiter_categorisation_non_supervisee()
    elif choix == "4":
        traiter_taux_citation_auteur()
    elif choix == "5":
        traiter_taux_citation_tous_auteurs()
    elif choix == "0":
        print("Au revoir!")
        exit()
    else:
        print("Option non valide. Veuillez choisir une option valide.")



# Fonction pour traiter l'option "Livret des résumés"
def traiter_livret_des_resumes():
    file_path = "corpus_taln_v1.tei.xml"
    filtre_annee = input("Voulez-vous filtrer par année? (Oui/Non) : ")
    if filtre_annee.lower() == "oui":
        annee = input("Entrez l'année de publication : ")
    else:
        annee = None
    # print(type(annee))

    filtre_mots_cles = input("Voulez-vous filtrer par mots-clés? (Oui/Non) : ")
    if filtre_mots_cles.lower() == "oui":
        mots_cles = [kw.strip() for kw in input("Entrez les mots-clés (séparés par des virgules) : ").split(',')]
        # print("mots_cles :", mots_cles)
        # print(type(mots_cles))
    else:
        mots_cles = None
    

    langue = input("Choisissez la langue ('en', 'fr' ou 'toutes') : ")

    format_sortie = input("Comment souhaitez-vous voir les résultats? ('console', 'texte' ou 'pdf') : ")

    # Itérer à travers les éléments TEI et imprimer/exporter les informations d'article en fonction des conditions
    tei_parser = LivretDeResumes(file_path = file_path, filtre_annee=annee, filtre_mots_cles = mots_cles, langue = langue, format_sortie=format_sortie)
    tei_parser.load_xml()
    tei_parser.iterer_elements_tei()

# Fonction pour traiter l'option "Evolution par année d'un terme donné"
def traiter_evolution_par_annee():
    terme = input("Entrez le terme dont vous voulez voir l'évolution : ")
    sortie = input("Comment souhaitez-vous voir les résultats? ('tabulaire' ou 'graphique') : ")

    # Calculer et imprimer la fréquence du terme par année
    tei_parser.imprimer_frequence_terme_par_annee(terme=terme, sortie=sortie)

# Fonction pour traiter l'option "Catégorisation non supervisée des articles (clustering)"
def traiter_categorisation_non_supervisee():
    num_clusters = int(input("Entrez le nombre de clusters : "))
    
    # Liste pour stocker les noms d'articles
    article_names = []

    # Itérer à travers les éléments TEI et imprimer/exporter les informations d'article en fonction des conditions
    for element_tei in tei_parser.root.findall(".//tei:TEI", tei_parser.namespaces):
        titre_article = element_tei.find(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", tei_parser.namespaces).text
        article_names.append(titre_article)

    # Regrouper les articles et afficher le nuage de points avec les noms d'articles
    tei_parser.cluster_articles(num_clusters=num_clusters, article_names=article_names)

# Fonction pour traiter l'option "Taux de citation d'un auteur"
def traiter_taux_citation_auteur():
    auteur = input("Entrez le nom de l'auteur : ")
    
    # Compter les citations pour l'auteur spécifié
    tei_parser.compter_citations_pour_author(auteur)

# Fonction pour traiter l'option "Taux de citation de tous les auteurs"
def traiter_taux_citation_tous_auteurs():
    ordre = input("Choisissez l'ordre ('asc' ou 'desc') : ")
    top_n_filtre = int(input("Entrez le nombre d'auteurs à afficher (entrez '0' pour afficher tous les auteurs) : "))
    if top_n_filtre == 0 :
        top_n = None
    else:
        top_n = top_n_filtre
    
    # Compter les citations pour tous les auteurs
    tei_parser.count_all_authors(order=ordre, top_n=top_n)






# Bloc principal du programme
if __name__ == "__main__":


    """
    
    # EXEMPLE D'UTILISATION DIRECTE (sans passer par le menu principal):
    
    # Créer une instance de la classe LivretDeResumes avec des filtres et un format de sortie
    tei_parser = LivretDeResumes("corpus_taln_v1.tei.xml", filtre_annee = "2014", filtre_mots_cles=["machine learning", "nlp"], format_sortie="console", langue="en") # formats sortie possibles : console, texte, pdf

    # Charger le contenu XML du fichier
    tei_parser.load_xml()

    # Itérer à travers les éléments TEI et imprimer/exporter les informations d'article en fonction des conditions
    tei_parser.iterer_elements_tei()

    # Calculer et imprimer la fréquence du terme par année
    #tei_parser.imprimer_frequence_terme_par_annee(terme="tal", sortie="graphique")


    # Liste pour stocker les noms d'articles
    article_names = []

    # Itérer à travers les éléments TEI et imprimer/exporter les informations d'article en fonction des conditions
    for element_tei in tei_parser.root.findall(".//tei:TEI", tei_parser.namespaces):
        titre_article = element_tei.find(".//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", tei_parser.namespaces).text
        article_names.append(titre_article)

    # Regrouper les articles et afficher le nuage de points avec les noms d'articles
    #tei_parser.cluster_articles(num_clusters=5, article_names=article_names)
    
    # Exemple : Compter les citations pour un auteur spécifique
    author_to_count = "Tanguy"
    # tei_parser.compter_citations_pour_author(author_to_count)

    #tei_parser.count_all_authors(order='descending', top_n=10)
    
    """

    while True:
        

        # Charger le contenu XML du fichier
        tei_parser = LivretDeResumes("corpus_taln_v1.tei.xml")
        tei_parser.load_xml()
        
        afficher_menu_principal()
        





