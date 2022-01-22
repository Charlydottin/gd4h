{% extends "base.tpl" %}
{% set active_page = "index" %}

{% block tagline %}Recensement des données en Santé Environnement{% endblock %}
{%block content%}
  <p>
    Le Green Data for Health vise à disposer d’un espace commun
de données environnementales au service de la santé qui :
  
<ul>
  <li><b>Facilite la repérabilité et l’accès
    aux données environnementales</b>, y
    compris au niveau des territoires
  </li>
  <li>
    <b>Décrive les données
environnementales pertinentes et
disponibles </b>pour être croisées avec
des données de santé et
<b>caractériser les expositions</b> aux
facteurs environnementaux
susceptibles d’affecter la santé
  </li>
<li><b>Stimule un appariement rigoureux</b>
  des données environnementales
  avec les données de santé.</li>
  <li><b>Améliore l’interopérabilité des
    données</b> environnementales entre
    elles et avec les données de santé</li>
    <li>
      <b>Améliore la communication et
synergie </b>entre les acteurs de la
Santé-Environnement
    </li>
</ul>
</p>
<div class="fr-container-fluid fr-my-6w">
  <div class="fr-grid-row fr-grid-row--gutters">
    <div class="fr-col-12 fr-col-md-4">
  <div class="fr-card fr-enlarge-link">
    <div class="fr-card__body">
      <h2 class="fr-card__title"><a href="/organizations">Institutions</a></h2>
      <p class="fr-card__desc">Institutions éditrices de jeux de données...</p>
    </div>
    
  </div>
</div>

    <div class="fr-col-12 fr-col-md-4">
  <div class="fr-card fr-enlarge-link">
    <div class="fr-card__body">
      <h2 class="fr-card__title"><a href="/datasets">Jeux de données</a></h2>
      <p class="fr-card__desc">Jeux de données disponible sur le thème Santé Environnement</p>
    </div>
    
  </div>
</div>
  <div class="fr-col-12 fr-col-md-4">
    <div class="fr-card fr-enlarge-link">
      <div class="fr-card__body">
        <h2 class="fr-card__title"><a href="/references">Référentiels</a></h2>
        <p class="fr-card__desc">Référentiels interne et externe pour le recensement des jeux de données</p>
      </div>
    </div>
  </div>
  
  <div class="fr-container-fluid fr-my-6w">
  
    <button onclick="location.href='https://github.com/c24b/gd4h/issues/new?assignees=c24b&labels=question&template=general-comment.md&title=%5BCOMMENT%5D'" class="fr-btn fr-fi-chat-quote-line fr-btn--icon-right">
              Make a  Comment
    </button>
        <button onclick="location.href='https://github.com/c24b/gd4h/discussions/new'" class="fr-btn fr-btn--secondary fr-fi-external-link-line fr-btn--icon-right">
            Discuss with the community
        </button>
      
      <button onclick="location.href='https://github.com/c24b/gd4h/issues/'" class="fr-btn fr-btn--secondary fr-fi-external-link-line fr-btn--icon-right">
        See reported issues
    </button>  
    <button onclick="location.href='https://github.com/c24b/gd4h/issues/new?assignees=c24b&labels=bug%2Ctriage&template=.bug_report.yaml&title=%5BBug%5D%3A+'" class="fr-btn fr-btn--secondary fr-fi-external-link-line fr-btn--icon-right">
      Report a bug
    </button>
    <button onclick="location.href='/docs/'" class="fr-btn fr-btn--secondary fr-fi-external-link-line fr-btn--icon-right">
      Consult the documentation
    </button>
  </div>
{%endblock%}

{%block script%}
  // Options disponibles à l'initialisation du DSFR
  window.dsfr = {
    verbose: true,
    mode: 'manual'
  };

<!-- Script en version es6 module et nomodule pour les navigateurs le ne supportant pas -->
{%endblock%}
