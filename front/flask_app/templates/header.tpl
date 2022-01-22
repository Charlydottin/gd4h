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
              <a href="/" title="Accueil">
                <p class="fr-header__service-title">{%block title%}{{title}} {% endblock %}</p>
              </a>
              <p class="fr-header__service-tagline">{%block tagline%}{{tagline}} {% endblock %}</p>
            </div>
          </div>
  
          <div class="fr-header__tools">
            <div class="fr-header__tools-links">
              <ul class="fr-links-group">
                <li>
                  <a class="fr-link fr-fi-account-fill fr-link--icon-right" href="/login" title="Connexion" target="_blank" rel="noopener">Se connecter</a>
                </li>
                <li>
                  <a class="fr-link fr-link--icon-right" href="#" title="Langue" target="_blank" rel="noopener">Langue</a>
                </li>
              </ul>
            </div>
          </div>
          
        </div>
        {%include 'main_nav.tpl' %}  
      </div>
    </div>
  </header>