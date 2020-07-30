import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import io
from typing import List, Optional
from datetime import datetime
from datetime import timedelta
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
import markdown

connection = psycopg2.connect(user = "...",
                                  password = "...",
                                  host = "...",
                                  port = "...",
                                  database = "...")

####changement des marges et couleur des écritures et fond####
COLOR = "black"
BACKGROUND_COLOR = "#F9F9F9"
padding_right: int = 1
padding_left: int = 1
padding_bottom: int = 10
padding_top: int = 5
max_width: int = 1200
max_width_str = f"max-width: {max_width}px;"
st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
    .reportview-container .main {{
        color: {COLOR};
        background-color: {BACKGROUND_COLOR};
    }}
</style>
""",
        unsafe_allow_html=True,
    )
###########################################################

################creation de grilles ######################
##################Classe cellule#############################
class Cell:
    """A Cell can hold text, markdown, plots etc."""

    def __init__(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        self.class_ = class_
        self.grid_column_start = grid_column_start
        self.grid_column_end = grid_column_end
        self.grid_row_start = grid_row_start
        self.grid_row_end = grid_row_end
        self.inner_html = ""

    def _to_style(self) -> str:
        return f"""
.{self.class_} {{
    grid-column-start: {self.grid_column_start};
    grid-column-end: {self.grid_column_end};
    grid-row-start: {self.grid_row_start};
    grid-row-end: {self.grid_row_end};
}}
"""

    def text(self, text: str = ""):
        self.inner_html = text

    def markdown(self, text):
        self.inner_html = markdown.markdown(text)

    def dataframe(self, dataframe: pd.DataFrame):
        self.inner_html = dataframe.to_html()

    def plotly_chart(self, fig):
        self.inner_html = f"""
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<body>
    <p>This should have been a plotly plot.
    But since *script* tags are removed when inserting MarkDown/ HTML i cannot get it to workto work.
    But I could potentially save to svg and insert that.</p>
    <div id='divPlotly'></div>
    <script>
        var plotly_data = {fig.to_json()}
        Plotly.react('divPlotly', plotly_data.data, plotly_data.layout);
    </script>
</body>
"""

    def pyplot(self, fig=None, **kwargs):
        string_io = io.StringIO()
        plt.savefig(string_io, format="svg", fig=(2, 2))
        svg = string_io.getvalue()[215:]
        plt.close(fig)
        self.inner_html = '<div height="200px">' + svg + "</div>"

    def _to_html(self):
        return f"""<div class="box {self.class_}">{self.inner_html}</div>"""
############################################################################

##################Classe grille#############################################
class Grid:
    """A (CSS) Grid"""

    def __init__(
        self,
        template_columns="1 1",
        gap="5px",
        background_color=COLOR,
        color=BACKGROUND_COLOR,
    ):
        self.template_columns = template_columns
        self.gap = gap
        self.background_color = background_color
        self.color = color
        self.cells: List[Cell] = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        st.markdown(self._get_grid_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_style(), unsafe_allow_html=True)
        st.markdown(self._get_cells_html(), unsafe_allow_html=True)

    def _get_grid_style(self):
        return f"""
<style>
    .wrapper {{
    display: grid;
    grid-template-columns: {self.template_columns};
    grid-gap: {self.gap};
    background-color: {self.background_color};
    color: {self.color};
    }}
    .box {{
    background-color: {self.color};
    color: {self.background_color};
    border-radius: 0px;
    padding: 20px;
    font-size: 150%;
    }}
    table {{
        color: {self.color}
    }}
</style>
"""

    def _get_cells_style(self):
        return (
            "<style>"
            + "\n".join([cell._to_style() for cell in self.cells])
            + "</style>"
        )

    def _get_cells_html(self):
        return (
            '<div class="wrapper">'
            + "\n".join([cell._to_html() for cell in self.cells])
            + "</div>"
        )

    def cell(
        self,
        class_: str = None,
        grid_column_start: Optional[int] = None,
        grid_column_end: Optional[int] = None,
        grid_row_start: Optional[int] = None,
        grid_row_end: Optional[int] = None,
    ):
        cell = Cell(
            class_=class_,
            grid_column_start=grid_column_start,
            grid_column_end=grid_column_end,
            grid_row_start=grid_row_start,
            grid_row_end=grid_row_end,
        )
        self.cells.append(cell)
        return cell
##########################################################################

#############################Navigation#################################
st.sidebar.image('https://github.com/coraliecoumes/Lachouettecoop/blob/master/LogoLCCVert.jpg?raw=true')
pages = st.sidebar.radio( "Menu",
        ('Accueil', 'Fournisseurs'))

##########################Accueil#######################################
if pages == 'Accueil' :
    st.markdown('<p align="center"><img \
    src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/Bandeau.png?raw=true"</p>',
                unsafe_allow_html=True)
    st.markdown('<p align="center"><img " \
        src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/Caisse.png?raw=true"</p>',
                unsafe_allow_html=True)

#######Menu deroulant fournisseurs######

elif pages == 'Fournisseurs' :
    l_fournisseurs = pd.read_sql_query(''' SELECT name AS fournisseurs
                    FROM res_partner''',connection)
    l_fournisseurs.drop(l_fournisseurs[l_fournisseurs['fournisseurs'] == "A deux pots d'ici"].index, inplace=True)
    l_fournisseurs['fournisseurs'] = l_fournisseurs['fournisseurs'].astype(str)
    l_fournisseurs.drop(l_fournisseurs[l_fournisseurs['fournisseurs'] == 'None'].index, inplace=True)
    l_fournisseurs.drop(l_fournisseurs[l_fournisseurs['fournisseurs'] == 'Ne pas utiliser BioDistriFrais'].index, inplace=True)
    l_fournisseurs.drop(l_fournisseurs[l_fournisseurs['fournisseurs'] == 'Pronatura-ne-pas-utiliser'].index, inplace=True)
    #fournisseurs sans produits
    liste_a_drop = ['Au petit grain Bio',
                    'AudiES (accepte les sols violette)',
                    'CRÉDIT COOP', 'Cécile TOURNSSA',
                    'Des Graines dans le Vent GAEC',
                    'Dila JO Gouv',
                    '',
                    'Domaine La Noiseraie',
                    'EARL Bianchini Francis',
                    'Extalea',
                    'ENERCOOP',
                    'ENGIE',
                    'EPFL',
                    'FERME de MONTPLAISIR',
                    'FRESS',
                    'Franck POMAREZ',
                    'GARDE BOIS SARL',
                    "Gourmie's",
                    'Ikoula',
                    'MAIF',
                    'MAIRIE DE TOULOUSE',
                    "MIELLERIE DE L'AIGOUAL",
                    'MMA',
                    'Monsieur Muesli ',
                    'ODOO',
                    'OVH',
                    'Produit sur son 31',
                    'Remboursements frais Chouettos',
                    'SAS Coopérative La Chouette Coop',
                    'SCI Thomas',
                    'Sextant monétique',
                    'Sud Primeurs',
                    'TETANEUTRAL',
                    'TOUPARGEL ',
                    'Tigoo',
                    'Vent de la récolte (Le)',
                    'Vincent NERCE',
                    'helene DELMAS'
                    ]
    l_fournisseurs.drop(l_fournisseurs[l_fournisseurs['fournisseurs'].isin(liste_a_drop)].index, inplace=True)
    choix_fournisseur = st.sidebar.selectbox('Choix du fournisseur :',
                                             sorted(list(l_fournisseurs['fournisseurs'].astype(str).unique())), index=0)
    if choix_fournisseur == "L'Oie Gourmande" :
        choix_fournisseur1 = "L''Oie Gourmande"
    elif choix_fournisseur == "Natur'L Cook (sols violette ok voir note interne)":
        choix_fournisseur1 = "Natur''L Cook (sols violette ok voir note interne)"
    elif choix_fournisseur == "RUCHER D'OC" :
        choix_fournisseur1 = "RUCHER D''OC"
    else :
        choix_fournisseur1 = choix_fournisseur

###########################Menu déroulant catégory produit ##########################################

    #########Coordonnées du fournisseur choisi####
    #récupération des coordonnées du fournisseur
    requete = ''' SELECT  name,
                            email,
                            phone,
                            mobile
                FROM res_partner
                WHERE name = \'''' + str(choix_fournisseur1) + "\'"

    contact_fournisseur = pd.read_sql_query(requete, connection)
    #affichage des coordonnées du fournisseur sur streamlit
    if contact_fournisseur['email'].iloc[0]!=None :
            email = contact_fournisseur['email'].iloc[0]
    else :
        email = ""
    if contact_fournisseur['phone'].iloc[0] !=None :
            telephone = 'Telephone : '+contact_fournisseur['phone'].iloc[0]
    else :
        telephone = ""
    if contact_fournisseur['mobile'].iloc[0] != None:
            mobile = 'Mobile : '+contact_fournisseur['mobile'].iloc[0]
    else :
        mobile = ""

    with Grid("1 1 1", color='#F9F9F9', background_color='Black', gap="0px") as grid:
        grid.cell("g", 1, 2, 1, 6).markdown('')
        grid.cell(
            class_="a",
            grid_column_start=2,
            grid_column_end=3,
            grid_row_start=1,
            grid_row_end=6,
        ).markdown('![alt text](https://github.com/coraliecoumes/Lachouettecoop/blob/master/Sac_prov.png?raw=true)')
        grid.cell("b", 3, 6, 1, 2).markdown('<p align="center"><font size="20"><b>' + choix_fournisseur + '</b></font> ')
        grid.cell("c", 3, 6, 2, 3).markdown('<p align="center"><font size="3">' + email + '</font> ')
        grid.cell("d", 3, 6, 3, 4).markdown('<p align="center"><font size="3">' + telephone + '</font> ')
        grid.cell("e", 3, 6, 4, 5).markdown('<p align="center"><font size="3">' + mobile + '</font> ')
        grid.cell("f", 6, 8, 1, 6).markdown('![alt text](https://github.com/coraliecoumes/Lachouettecoop/blob/master/Dame_chariot.png?raw=true)')

    ###########################dataframe produits du fournisseurs###################################
    requete_produit_fournisseur =  ''' SELECT  pt.id AS product_id,
                                               pp.id AS id,
                                               pt.name AS product_name,
                                               pt.theoritical_price,
                                               pc.name AS category_name
                                    FROM product_template pt
                                    LEFT JOIN product_category pc ON pt.categ_id=pc.id
                                    LEFT JOIN product_supplierinfo psi ON psi.product_tmpl_id=pt.id
                                    LEFT JOIN res_partner rp ON psi.name=rp.id
                                    LEFT JOIN product_product pp ON pt.id=pp.product_tmpl_id
                                    WHERE rp.name =  \'''' + str(choix_fournisseur1) + "\'"
    #la colonne id correspond à l'id de la table product_product
    #la colonne product_id correspond à l'id de la table product_template_id et au product_tmpl_id de la table product_product
    df_fournisseur = pd.read_sql_query(requete_produit_fournisseur, connection)

    categorie = ['TOUTES'] + sorted(list(df_fournisseur['category_name'].unique()))

    ##################################STOCKS DES PRODUITS DU FOURNISSEUR########################################

    liste_id = list(df_fournisseur['product_id']) #liste des ids de product_template_id du fournisseur
    liste_id = str(liste_id)
    liste_id = liste_id.replace("[", "(")
    liste_id = liste_id.replace("]", ")")

    liste_id_pp = list(df_fournisseur['id'])  # liste des ids de product_template_id du fournisseur
    liste_id_pp_requete = str(liste_id_pp)
    liste_id_pp_requete = liste_id_pp_requete.replace("[", "(")
    liste_id_pp_requete = liste_id_pp_requete.replace("]", ")")

    ### table report_stock_forecast
    report_stock_forecast = '''   SELECT rsf.product_id as id, rsf.date, rsf.quantity
            FROM report_stock_forecast AS rsf
            WHERE rsf.product_id IN ''' + liste_id_pp_requete

    report_stock_forecast = pd.read_sql_query(report_stock_forecast, connection)
    # liste des product_id présents dans report_stock_forecast
    l_id_report_stock = report_stock_forecast['id'].tolist()
    # liste des noms des produits du fournisseur sélectionné
    liste_produit = df_fournisseur['product_name'].tolist()
    liste_stock = []
    for produit in liste_id_pp :
        if produit in l_id_report_stock:
            report_stock = report_stock_forecast.loc[report_stock_forecast['id'] == produit]
            liste_stock.append(report_stock.iloc[0, 2])
        else:
            liste_stock.append('non renseigné')

    fourn_stock_global = pd.DataFrame(columns=['id', 'Nom_produit', 'Stock'])
    fourn_stock_global['id'] = liste_id_pp
    fourn_stock_global['Nom_produit'] = liste_produit
    fourn_stock_global['Stock'] = liste_stock
    fourn_stock_global = fourn_stock_global[fourn_stock_global['Stock'] != 'non renseigné']
    fourn_stock_global['id'] = fourn_stock_global['id'].astype(str)




    # graphique des stock <8
    if not (fourn_stock_global[(fourn_stock_global['Stock'] < 8) & (fourn_stock_global['Stock'] > 0)].empty) :
        st.markdown('<p align="center"><img width="850" \
                src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/ligne.png?raw=true"</p>',
                    unsafe_allow_html=True)

        st.markdown('<p align="center"><font size="6"> Stocks des produits inférieur à 8 </font> ',
                    unsafe_allow_html=True)

        fig8 = px.bar(
            x=fourn_stock_global.loc[(fourn_stock_global['Stock'] < 8) & (fourn_stock_global['Stock'] > 0)]['Nom_produit'],
            y=sorted(fourn_stock_global.loc[(fourn_stock_global['Stock'] < 8) & (fourn_stock_global['Stock'] > 0)]['Stock']),
            labels={'x': '', 'y': 'Quantité'})
        fig8.update_traces(marker_color='rgb(237,102,95)')
        fig8.update_layout(height=700, width=1400, title_font_size = 25, title_x = 0.5,
                           showlegend=False, paper_bgcolor='rgb(249,249,249)',plot_bgcolor='rgb(249,249,249)')
        fig8.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#B10DC9', linewidth=2, linecolor='#B10DC9')
        fig8.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#B10DC9', linewidth=2, linecolor='#B10DC9')
        st.plotly_chart(fig8, use_container_width=True)

    #stock nuls
    stock_nul = fourn_stock_global[fourn_stock_global['Stock'] == 0]

    #affichage des stocks nuls sous forme de tableau
    if not (stock_nul.empty) :
        fig9 = go.Figure(data=[go.Table(
            columnwidth=[90, 600, 90],
            header=dict(values=list(['<b>Identifiant</b>', '<b>Nom produit</b>', '<b>Stock</b>']),
                        line_color='darkslategray',
                        fill_color='#83c3a9',
                        font=dict(color='darkslategray', size=12),
                        align='center'),
            cells=dict(values=[stock_nul.id, stock_nul.Nom_produit, stock_nul.Stock],
                       line_color='darkslategray',
                       fill_color='#F0F2F6',
                       align=['center','left','center']))
        ])
        fig9.update_layout(width=1400,
                           showlegend=False, paper_bgcolor='#F9F9F9')
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown('<p align="center"><img width="850" \
            src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/ligne.png?raw=true"</p>',
                unsafe_allow_html=True)

    st.markdown('<p align="center"><font size="6"> Produits du fournisseur </font> ',
                unsafe_allow_html=True)
    ####################dataframe avec choix d'une categorie#################################
    choix_category = st.selectbox('Choix de la catégorie du produit :',categorie, index=0)

    if choix_category == 'TOUTES' :
            df_category = df_fournisseur
    else :
            df_category = df_fournisseur[df_fournisseur['category_name'] == choix_category]
    df_category.sort_values(by=['product_name'],inplace=True)

    ##########################affichage du dataframe des produits du fournisseur avec plotly#######################
    fig1 = go.Figure(data=[go.Table(
        columnwidth=[90, 600, 90],
        header=dict(values=['<b>Identifiant</b>','<b>Nom produit</b>','<b>Prix</b>'],
                    line_color='darkslategray',
                    fill_color='#83c3a9',
                    align='center',
                    font=dict(color='darkslategray', size=12),
                    height=30),
        cells=dict(values=[df_category.id, df_category.product_name,df_category.theoritical_price],
                   line_color='darkslategray',
                   fill_color='#F0F2F6',
                   align=['center','left','center'],
                   height=30))
    ])
    fig1.update_layout(height=500, width=1400,
                      showlegend=False, paper_bgcolor = '#F9F9F9')
    st.plotly_chart(fig1,use_container_width=True)

    ########################DETAIL D'UN PRODUIT ######################################################
    st.markdown('<p align="center"><img width="850" \
                src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/ligne.png?raw=true"</p>',
                unsafe_allow_html=True)

    st.markdown("<p align='center'><font size='6'> Choix d'un produit du fournisseur </font> ",
                unsafe_allow_html=True)

    #choix d'un produit
    choix_produit = st.selectbox('Choix du produit :', sorted(list(df_category['product_name'].unique())), index=0)
    id_product = df_category[df_category['product_name']==choix_produit]
    id_product_template = id_product['product_id'].iloc[0]#c'est aussi product_tmpl_id dans product_product
    id_product_product = id_product['id'].iloc[0]

    ##ventes
    df_produit = pd.read_sql_query(
            '''   SELECT pol.product_id, 
                        pol.create_date AS date_vente,
                        pp.name_template AS nom_produit,  
                        pol.qty
            FROM pos_order_line AS pol
            LEFT JOIN product_product AS pp ON pol.product_id=pp.id
            WHERE product_id = \'''' + str(id_product_product) + "\'"
            , connection)

    # date il y a 60 jours, pour le graphique stocks
    mois_passe = datetime.now() - timedelta(days=120)

    if not(df_produit.empty) :
        df_produit.set_index('date_vente', inplace=True)

        # ventes du produits sélectionné groupé par mois
        df_month = pd.DataFrame(df_produit['qty'].groupby(pd.Grouper(freq='M')).sum())
        df_month.reset_index(inplace=True)
        df_month['month'] = pd.DatetimeIndex(df_month['date_vente']).month
        df_month['year'] = pd.DatetimeIndex(df_month['date_vente']).year

        # ventes du produit sélectionné groupé par semaines
        df_week = pd.DataFrame(df_produit['qty'].groupby(pd.Grouper(freq='W')).sum())
        df_week.reset_index(inplace=True)
        df_week['month'] = pd.DatetimeIndex(df_week['date_vente']).month
        df_week['year'] = pd.DatetimeIndex(df_week['date_vente']).year
        df_week['week'] = df_week['date_vente'].dt.week

        # ventes du produit sélectionné groupé par jours
        df_day = pd.DataFrame(df_produit['qty'].groupby(pd.Grouper(freq='D')).sum())
        df_day.reset_index(inplace=True)
        df_day['month'] = pd.DatetimeIndex(df_day['date_vente']).month
        df_day['year'] = pd.DatetimeIndex(df_day['date_vente']).year
        df_day['day'] = df_day['date_vente'].dt.strftime('%A')
        df_day['week'] = df_day['date_vente'].dt.week
        df_day.sort_values(by="date_vente", ascending=True)

    else :
        df_month = df_week = df_day = df_produit
        df_month['year'] = df_week['year'] = df_day['year'] = ''
        df_month['month'] = df_week['month'] = df_day['month'] = ''
        df_day['day'] = ''
        df_day['week'] = ''

    requete_stock = '''   SELECT sil.product_id, 
                        sil.create_date AS date, 
                        pp.name_template AS nom_produit, 
                        sil.product_qty AS quantite
            FROM stock_inventory_line AS sil
            LEFT JOIN product_product AS pp ON pp.id=sil.product_id
            WHERE sil.product_id =\'''' + str(id_product_product) + "\'"
    inventaire_produit = pd.read_sql_query(requete_stock, connection)
    inventaire_produit = inventaire_produit.loc[inventaire_produit['date'] < mois_passe]
    inventaire_produit.sort_values(by='date', inplace=True)

    ##### Calcul des stocks avec stock_history ######
    stock_produit1 = '''   SELECT sh.product_id, sh.date, sh.quantity
            FROM stock_history AS sh
            WHERE sh.product_id =\'''' + str(id_product_product) + "\'"

    stock_produit = pd.read_sql_query(stock_produit1, connection)

    if not(stock_produit.empty) :
        if inventaire_produit.shape[0] >= 1:
            # date de l'inventaire il y a minimum 60 jours
            date_inventaire = inventaire_produit.iloc[(inventaire_produit.shape[0] - 1), 1]
       # stock à cette date là
            stock_date_inventaire = inventaire_produit.iloc[(inventaire_produit.shape[0] - 1), 3]
        # on ne prend que lignes après le dernier inventaire
        # attention: condition si la date de l'inventaire est postérieure aux dates de stock_produit
            if date_inventaire < stock_produit.iloc[(stock_produit.shape[0] - 1), 1]:
                # on ne prend que les lignes dont la date est supérieure ou égale à la date de l'inventaire
                stock_produit = stock_produit.loc[stock_produit['date'] >= date_inventaire]
                # on met les dates en index pour pouvoir grouper par jour
                stock_produit.set_index('date', inplace=True)
                stock_produit = pd.DataFrame(stock_produit['quantity'].groupby(pd.Grouper(freq='D')).sum())
                stock_produit.reset_index(inplace=True)
                # on ajoute une colonne stock
                stock_produit['stock'] = 0
                # on ajoute la valeur du stock à la première ligne du df
                # stock = stock inventaire + quantite
                stock_produit.sort_values(by='date', inplace=True)
                stock_produit.loc[0, 'stock'] = stock_date_inventaire + stock_produit.iloc[0, 2]
            else:
                # si la date de l'inventaire est postérieure aux dates de stock_produit
                # on ne prend que les lignes dont la date est supérieure ou égale à la date de l'inventaire
                # dans ce sac il n'y aura aucunes lignes
                stock_produit = stock_produit.loc[stock_produit['date'] >= date_inventaire]
                # on enlève la colonne product_id et on rajoute la colonne stock
                stock_produit.drop('product_id', axis=1, inplace=True)
                stock_produit['stock'] = 0
                # on ajoute donc la ligne correspondant au stock de l'inventaire, ça sera la seule ligne de stock_produit
                stock_produit.loc[0, :] = [date_inventaire, 0, stock_date_inventaire]
        else :
            stock_produit = pd.DataFrame(columns = ['date', 'quantity','stock'])
    else:
        stock_produit['stock'] =''
        date_inventaire = ''

    # on fait le calcul du stock pour toutes les lignes
    if stock_produit.shape[0] > 1:
        for i in range(1, stock_produit.shape[0]):
            stock_produit.iloc[i, 2] = stock_produit.iloc[i - 1, 2] + stock_produit.iloc[i, 1]

    ###commandes
    requete1 = '''SELECT pol.date_planned AS "Date",
                pol.name AS "Nom_produit",
                pol.qty_received AS "Quantité recue"
                FROM purchase_order_line pol
                WHERE pol.product_id =\'''' + str(id_product_product) + "\'"

    df_achats_pr = pd.read_sql_query(requete1, connection)

    if not(df_achats_pr.empty) :
        df_achats_pr['Mois'] = df_achats_pr['Date'].dt.strftime('%m')
        df_achats_pr['Années'] = df_achats_pr['Date'].dt.strftime('%Y')
        df_achats_pr['Semaines'] = df_achats_pr['Date'].dt.strftime('%W')
        df_achats_pr.sort_values('Date', inplace=True)
    else :
        df_achats_pr['Mois'] = ''
        df_achats_pr['Années'] =''
        df_achats_pr['Semaines'] = ''

    annee = list(df_week['year'].astype(int).unique()) + list(df_achats_pr['Années'].astype(int).unique())
    annee = pd.DataFrame(annee, columns=['année'])
    annee.sort_values(by='année', ascending=False, inplace=True)
    if annee.empty :
        st.write('Pas de données disponibles sur le produit')
        choix_annee = ''
        choix_mois = ''
        date_debut = ''
        date_fin = ''
    else :
        choix_annee = st.selectbox("Choisissez une année ", annee['année'].unique(), index=0)
        mois = list(df_week.loc[df_week['year']==choix_annee]['month'].astype(int).unique())+ list(df_achats_pr.loc[df_achats_pr['Années']==choix_annee]['Mois'].astype(int).unique())
        mois = pd.DataFrame(mois, columns=['Mois'])
        l_mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        l_mois_chiffre = sorted(list(mois['Mois'].unique()))
        l_mois_lettre = []
        for i in l_mois_chiffre :
            l_mois_lettre.append(l_mois[i-1])
        choix_mois = st.selectbox("Choisissez un mois ", l_mois_lettre, index=0)
        if choix_mois == 'Janvier' :
            choix_mois = 1
        elif choix_mois == 'Février' :
            choix_mois = 2
        elif choix_mois == 'Mars' :
            choix_mois = 3
        elif choix_mois == 'Avril' :
            choix_mois = 4
        elif choix_mois == 'Mai' :
            choix_mois = 5
        elif choix_mois == 'Juin' :
            choix_mois = 6
        elif choix_mois == 'Juillet' :
            choix_mois = 7
        elif choix_mois == 'Août' :
            choix_mois = 8
        elif choix_mois == 'Septembre' :
            choix_mois = 9
        elif choix_mois == 'Octobre' :
            choix_mois = 10
        elif choix_mois == 'Novembre' :
            choix_mois = 11
        else :
            choix_mois = 12
        df_month = df_month[df_month['year'] ==choix_annee]

    df_achats_pr_mois = df_achats_pr.groupby(['Mois','Années']).sum()
    df_achats_pr_mois.reset_index(inplace=True)
    if df_achats_pr_mois.empty :
        df_achats_pr_mois['Années'] = ''
        df_achats_pr_mois['Mois']=''
        df_achats_pr_mois['Quantité recue'] = ''

    df_achats_pr_annee = df_achats_pr.groupby(['Années']).sum()
    df_achats_pr_annee.reset_index(inplace=True)

    df_achats_pr_semaine = df_achats_pr.groupby(['Années','Semaines']).sum()
    df_achats_pr_semaine.reset_index(inplace=True)
    if df_achats_pr_semaine.empty :
        df_achats_pr_semaine['Années'] = ''
        df_achats_pr_semaine['Semaines']=''
        df_achats_pr_semaine['Quantité recue'] = ''

    #évolution prix d'un produit
    requete2 = '''SELECT pol.create_date AS "Date",
                    pol.product_id,
                    pol.name AS "Nom_produit",
                    pol.price_unit AS "Prix_unitaire"
                    FROM purchase_order_line pol
                    WHERE pol.product_id =\'''' + str(id_product_product) + "\'" +' ORDER BY pol.create_date'
    df_prix = pd.read_sql_query(requete2, connection)
    if not df_prix.empty :
        df_prix['Année'] = df_prix['Date'].dt.strftime('%Y')
        df_prix = df_prix[df_prix['Année']>=str(datetime.now().year-2)]

    st.markdown('<p align="center"><img width="300" \
                    src="https://github.com/coraliecoumes/Lachouettecoop/blob/master/ligne.png?raw=true"</p>',
                unsafe_allow_html=True)

######################subplots##################################
    fig = make_subplots(rows=3, cols=2,subplot_titles=("Commandes par années", "Stocks et ventes des 60 derniers jours", "Ventes par jour du mois", "Commandes et ventes par mois", "Evolution du prix unitaire", "Commandes par semaines"))

    #Graph1 ###Commande par années
    fig.add_trace(go.Bar(name='Commandes', x=df_achats_pr_annee['Années'],
                         y=df_achats_pr_annee['Quantité recue'],
                         text=round(df_achats_pr_annee['Quantité recue']),
                         textposition='auto',showlegend= True,marker_color='#3D9970'),
                  row=1, col=1)
    fig.update_xaxes(title_text="Années", row=1, col=1)
    fig.update_yaxes(title_text="Quantité", row=1, col=1)


    #Graph 2 ### stock et ventes des 60 derniers jours
    fig.add_trace(go.Bar(name='Ventes',
                         x=df_day.loc[df_day['date_vente'] > mois_passe]['date_vente'],
                         y=df_day.loc[df_day['date_vente'] > mois_passe]['qty'],marker_color='#39CCCC'),row=1, col=2)
    fig.add_trace(go.Scatter(name='Stocks', x=stock_produit.loc[stock_produit['date'] > mois_passe]['date'],
                   y=stock_produit.loc[stock_produit['date'] > mois_passe]['stock'],marker_color='rgb(237, 102, 95)'),row=1,col=2)
    fig.update_xaxes(title_text="Jours", row=1, col=2)
    fig.update_yaxes(title_text="Quantité", row=1, col=2)

    #Graph 3 ####Ventes par jour du mois
    fig.add_trace(go.Bar(name='Lundi',
        x = df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Lundi')]['week'],
        y = df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Lundi')]['qty'],
        marker_color = '#7FDBFF'),row=2,col=1)
    fig.add_trace(go.Bar(name='Mardi',
        x = df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Mardi')]['week'],
        y=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Mardi')]['qty'],
        marker_color = '#d3d8d3'),row=2,col=1)
    fig.add_trace(go.Bar(name='Mercredi',
        x = df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Mercredi')]['week'],
        y = df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Mercredi')]['qty'],
        marker_color='#FF851B'),row=2,col=1)
    fig.add_trace(go.Bar(name='Jeudi',
        x=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Jeudi')]['week'],
        y=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Jeudi')]['qty'],
        marker_color='#2ECC40'),row=2,col=1)
    fig.add_trace(go.Bar(name='Vendredi',
        x=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Vendredi')]['week'],
        y=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Vendredi')]['qty'],
        marker_color='#01FF70'),row=2,col=1)
    fig.add_trace(go.Bar(name='Samedi',
        x=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Samedi')]['week'],
        y=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Samedi')]['qty'],
        marker_color='#FFDC00'),row=2,col=1)
    fig.add_trace(go.Bar(name='Dimanche',
        x=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Dimanche')]['week'],
        y=df_day.loc[(df_day['month'] == choix_mois) & (df_day['year'] == choix_annee) & (df_day['day'] == 'Dimanche')]['qty'],
        marker_color='#001f3f'),row=2,col=1)
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title_text="Semaines", row=2, col=1)
    fig.update_yaxes(title_text="Quantité", row=2, col=1)

    #Graph 4
    fig.add_trace(go.Bar(name='Commande',
                         x=df_achats_pr_mois.loc[df_achats_pr_mois['Années'] == str(choix_annee)]['Mois'],
                         y=df_achats_pr_mois.loc[df_achats_pr_mois['Années'] == str(choix_annee)]['Quantité recue'],
                         text=round(df_achats_pr_mois.loc[df_achats_pr_mois['Années'] == str(choix_annee)]['Quantité recue']),
                         textposition = 'auto',
                         showlegend= False,
                         marker_color='#3D9970'),row=2, col=2)
    fig.add_trace(go.Scatter(name='Ventes',
                             x=df_month['month'],
                             y=df_month['qty'],
                             showlegend= False,
                             marker_color='#39CCCC'),row=2,col=2)
    fig.update_xaxes(title_text="Mois", row=2, col=2)
    fig.update_yaxes(title_text="Quantité", row=2, col=2)

    #Graph 5 ###Evolution du prix unitaire
    fig.add_trace(go.Scatter(x=df_prix['Date'], y=df_prix['Prix_unitaire'],showlegend= False, marker_color='#001f3f'),row=3, col=1)
    fig.update_xaxes(title_text="Dates", row=3, col=1)
    fig.update_yaxes(title_text="Prix unitaire", row=3, col=1)

    #Graph 6 ####Commande par semaines
    fig.add_trace(go.Bar(name='Commande facturée',
                         x=df_achats_pr_semaine.loc[df_achats_pr_semaine['Années'] == str(choix_annee)]['Semaines'],
                         y=df_achats_pr_semaine.loc[df_achats_pr_semaine['Années'] == str(choix_annee)]['Quantité recue'],
                         text=round(df_achats_pr_semaine.loc[df_achats_pr_semaine['Années'] == str(choix_annee)]['Quantité recue']),
                         textposition='auto',showlegend= False,
                         marker_color='#3D9970'),row=3, col=2)
    fig.update_xaxes(title_text="Semaines", row=3, col=2)
    fig.update_yaxes(title_text="Quantité", row=3, col=2)

    #style du subplot
    fig.update_layout(height=900, width=1000,
                title_text=choix_produit, title_x = 0.5, title_font_size = 25, showlegend= True, plot_bgcolor='rgb(249,249,249)', paper_bgcolor='rgb(249,249,249)',
                      legend=dict(
                          x=1.02,
                          y=1.02,
                          traceorder="normal",
                          font=dict(
                              size=12,
                              color="black"
                          ),
                          bgcolor="#F0F2F6",
                          bordercolor="#7f7f7f",
                          borderwidth=1.5
                      )
                      )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#B10DC9',linewidth=2, linecolor='#B10DC9')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#B10DC9',linewidth=2, linecolor='#B10DC9')
    if not annee.empty :
        st.plotly_chart(fig, use_container_width=True)
