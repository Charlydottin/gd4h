<!DOCTYPE html>
<html lang="fr" data-fr-theme>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>
    
      Green Data Catalogue 
    
  </title>
  <script type="module" src="/static/js/dsfr.module.min.js"></script>
  <script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.min.js"></script>
  <link rel="stylesheet" href="/static/css/dsfr.css">
  <link rel="stylesheet" href="/static/css/custom.css">
  <link rel="apple-touch-icon" href="/static/favicons/apple-touch-icon.png"><!-- 180×180 -->
  <link rel="icon" href="/static/favicons/favicon.svg" type="image/svg+xml">
  <link rel="shortcut icon" href="/static/favicons/favicon.ico" type="image/x-icon"><!-- 32×32 -->

</head>
<body>
  <div class="fr-skiplinks">
    <nav class="fr-container" role="navigation" aria-label="Accès rapide">
        <ul class="fr-skiplinks__list">
            <li>
                <a class="fr-nav__link" href="#contenu">Contenu</a>
            </li>
            <li>
                <a class="fr-nav__link" href="#header-navigation">Menu</a>
            </li>
            <li>
                <a class="fr-nav__link" href="#header-search">Recherche</a>
            </li>
            <li>
                <a class="fr-nav__link" href="#footer">Pied de page</a>
            </li>
        </ul>
    </nav>
</div>

<header role="banner" class="fr-header">
  <div class="fr-header__body">
    <div class="fr-container">
      <div class="fr-header__body-row">
        <div class="fr-header__brand fr-enlarge-link">
          <div class="fr-header__brand-top">
            <div class="fr-header__logo">
              <p class="fr-logo">
                République
                <br>Française
              </p>
            </div>
            <div class="fr-header__navbar">
              <button class="fr-btn--menu fr-btn" data-fr-opened="false" aria-controls="modal-menu" aria-haspopup="menu" title="Menu">
                Menu
              </button>
            </div>
          </div>
          <div class="fr-header__service">
            <a href="/" title="Accueil - GDCATH">
              <p class="fr-header__service-title">Green Data 4 Health Catalogue</p>
            </a>
            <p class="fr-header__service-tagline">Outil pour le référencement des jeux de données dans Green Data For Health</p>
          </div>
        </div>

        <div class="fr-header__tools">
          <div class="fr-header__tools-links">
            <ul class="fr-links-group">
              <li>
                <a class="fr-link fr-fi-external-link-line fr-link--icon-right" href="https://gouvfr.atlassian.net/wiki/spaces/DB/" title="documentation officielle - nouvelle fenêtre" target="_blank" rel="noopener">Documentation officielle</a>
              </li>
              <li>
                <button class="fr-link fr-fi-sun-fill-line fr-link--icon-left" aria-controls=".rf-centered {
  text-align: center;
}

.rf-bg--alt, .rf-bg--alt h2 {
  background-color: var(--bf500);
  color: var(--g100);
}
p.rf-hint-text {
  margin-bottom: 0;
}
.tofill {
  background-color: #fffacd;
  font-weight: lighter;
  padding: .1em .2em;
}
span.tofill::after {
  content: "]";
}
span.tofill::before {
  content: "[";
}  " data-fr-opened="false">Langues</button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

<!-- TODO : fix arria-labellby -->
  <div class="fr-header__menu fr-modal" id="modal-menu" aria-labelledby="button-825">
    <div class="fr-container">
      <button class="fr-link--close fr-link" aria-controls="modal-menu">Fermer</button>
      <div class="fr-header__menu-links">
      </div>

      <nav class="fr-nav" role="navigation" aria-label="Menu principal" id="header-navigation">
        <ul class="fr-nav__list">
          <li class="fr-nav__item">
            <a class="fr-nav__link" href="/" target="_self" >A propos</a>
          </li>
          <li class="fr-nav__item">
            <a class="fr-nav__link active" href="/organizations" target="_self" aria-current="page" > Institutions</a>
          </li>
          <li class="fr-nav__item">
            <a class="fr-nav__link" href="/datasets" target="_self" >Jeux de données</a>
          </li>
          <li class="fr-nav__item">
            <a class="fr-nav__link" href="/references" target="_self" >Référentiels</a>
          </li>
          <li class="fr-nav__item">
            <a class="fr-nav__link" href="/contact" target="_self" >Contact</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>

</header>
<main role="main" id="contenu">
  <div class="fr-container fr-py-6w fr-px-2w">
    <div class="fr-search-bar fr-search-bar--lg" id="search-2" role="search">
   <label class="fr-label" for="search-787-input">
       Rechercher
   </label>
   <input class="fr-input" placeholder="Exemple: DGPR" type="search" id="search-787-input" name="search-787-input">
   <button class="fr-btn">
       Rechercher 
   </button>
</div> 
</div>  
<div class="fr-container fr-py-2w fr-col-offset-4">
<h3><a class="fr-btn info-625" href="#"> {{count}}</a> Organizations</h3>

</div>  
<div class="fr-container fr-py-2w">
<ul class="fr-btns-group fr-btns-group--inline">
    <li>
    <button class="fr-btn fr-btn--secondary fr-fi-error-warning-line fr-link--icon-left" title="Report and error">Report an error</button>
    </li>
    <li>
  <button class="fr-btn  fr-fi-add-circle-line fr-link--icon-left" title="Propose an new organization">Propose a new organization</button>
  </li>
</ul>
</div>
<div class="fr-container fr-py-6w fr-px-2w">
  {% for org_row in result | batch(3, '&nbsp;')%}
      
      <div class="fr-grid-row fr-grid-row--gutters">
  
      {% for org in org_row %}
      
      <div class="fr-col-4"> 
         
         <div class="fr-tile" >
          <div class="fr-tile__body">
              <h4 class="fr-tile__title">
                <a class="fr-tile__link" href='/organizations/{{org["id"]}}'>{{org['name']}}</a> 
              </h4>
              
              <p class="fr-tile__desc">
                {%if "acronym" in org %}
                <h6>
                <a href="/organizations/{{org['id']}}">
                {{org["acronym"]}}
                </a>
                </h6>
                {%endif %}
                {% if "agent_type" in org %}
                  
                  <span class="fr-tag">{{org["agent_type"]["label_en"]}} </span>
                {%endif%}  
                {% if "organization_type" in org %}
                <span class="fr-tag">{{org["organization_type"]["label_en"]}} </span>
                {%endif%}
          </div>
          <div class="fr-tile__img">
          <img src='{{org["image_url"]}}' class="fr-responsive-img" alt="">
          </div>
          </a>
        </div>
        </div>
      {%endfor%}
      </div>
  {%endfor%}

</div>   
</div>

</div>
</main>
<script type="module" src="//static/js/dsfr.module.js"></script>
<script type="text/javascript" nomodule src="//static/js/dsfr.nomodule.js"></script>

<!-- <div class="fr-follow">
    <div class="fr-container">
        <div class="fr-grid-row">
            <div class="fr-col-12">
                <div class="fr-follow__social">
                    <p class="fr-h5 fr-mb-3v fr-mb-3v">Suivez-nous
                        <br> sur les réseaux sociaux</p>
                    <ul class="fr-links-group fr-links-group--lg">
                        <li>
                            <a class="fr-link--twitter fr-link" title="Twitter @betagouv - ouvre une nouvelle fenêtre" href="https://twitter.com/betagouv?lang=fr" target="_blank">twitter</a>
                        </li>
                        <li>
                            <a class="fr-link--linkedin fr-link" title="Linkedin betagouv - ouvre une nouvelle fenêtre" href="https://www.linkedin.com/company/betagouv/mycompany/" target="_blank">linkedin</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div> -->
<footer role="contentinfo" class="fr-footer" id="footer">
  <div class="fr-container">
    <div class="fr-footer__body">
      <div class="fr-footer__brand fr-enlarge-link">
          <a href="/" title="Retour à l’accueil">
              <p class="fr-logo">
                  République
                  <br>française
              </p>
          </a>
      </div>
      <div class="fr-footer__content">
        <p class="fr-footer__content-desc">
          Green Data For Health Catalogue
        </p>
        <p class="fr-footer__content-desc">
            <a title="Voir le code source"
               href="https://github.com/c24b/gd4h"
               target="_blank"
               rel="noopener"
               >Voir le code source</a>
        </p>
        <ul class="fr-footer__content-list">
          <li class="fr-footer__content-item">
            <a class="fr-footer__content-link"
               title="Contactez-nous"
               href="#">
              Contactez-nous
            </a>
          </li>
          <li class="fr-footer__content-item">
            <a class="fr-footer__content-link" href="https://www.ecologie.gouv.fr/">Ministère de la Transition Ecologique</a>
          </li>
          <li class="fr-footer__content-item">
            <a class="fr-footer__content-link" href="https://beta.gouv.fr/">Commissariat Général au Développement Durable</a>
          </li>
          <li class="fr-footer__content-item">
            <a class="fr-footer__content-link" href="https://www.gouvernement.fr/">Ecolab</a>
          </li>
        </ul>
      </div>
    </div>
    <div class="fr-footer__bottom">
      <ul class="fr-footer__bottom-list">
        <li class="fr-footer__bottom-item">
          <a class="fr-footer__bottom-link" href="/accessibilite">Accessibilité : non conforme</a>
        </li>
        <li class="fr-footer__bottom-item">
          <a class="fr-footer__bottom-link" href="/mentions-legales">Mentions légales</a>
        </li>
        <li class="fr-footer__bottom-item">
          <a class="fr-footer__bottom-link" href="/contact">Contactez-nous</a>
        </li>
        <li class="fr-footer__bottom-item">
            <button class="fr-footer__bottom-link fr-fi-sun-fill-line fr-link--icon-left" aria-controls="fr-theme-modal" data-fr-opened="false">Paramètres d'affichage</button>
        </li>
      </ul>
      <div class="fr-footer__bottom-copy">
        <p>Sauf mention contraire, tous les textes de ce site sont sous <a href="https://github.com/etalab/licence-ouverte/blob/master/LO.md" target="_blank">licence etalab-2.0</a>
        </p>
      </div>
    </div>
  </div>
  <dialog id="fr-theme-modal" class="fr-modal" role="dialog" aria-labelledby="fr-theme-modal-title">
    <div class="fr-container--fluid fr-container-md">
        <div class="fr-grid-row fr-grid-row--center">
            <div class="fr-col-12 fr-col-md-6 fr-col-lg-4">
                <div class="fr-modal__body">
                    <div class="fr-modal__header">
                        <button class="fr-link--close fr-link" aria-controls="fr-theme-modal">Fermer</button>
                    </div>
                    <div class="fr-modal__content">
                        <h1 id="fr-theme-modal-title" class="fr-modal__title">
                            Thème
                        </h1>
                        <div id="fr-switch-theme" class="fr-form-group fr-switch-theme">
                            <fieldset class="fr-fieldset">
                                <legend class="fr-fieldset__legend">Choisissez un langue</legend>
                                <div class="fr-fieldset__content">
                                    <div class="fr-radio-group fr-radio-rich">
                                        <input type="radio" id="fr-radios-theme-light" name="fr-radios-theme" value="light">
                                        <label class="fr-label" for="fr-radios-theme-light">Clair
                                        </label>
                                    </div>
                                    <div class="fr-radio-group fr-radio-rich">
                                        <input type="radio" id="fr-radios-theme-dark" name="fr-radios-theme" value="dark">
                                        <label class="fr-label" for="fr-radios-theme-dark">Sombre
                                        </label>
                                    </div>
                                </div>
                            </fieldset>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</dialog>
</footer>
<script>
dsfr.start();
</script>
</body>
</html>
