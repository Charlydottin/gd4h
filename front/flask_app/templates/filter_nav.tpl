    <nav class="fr-sidemenu data-fr-js-sidemenu-list" id="filter_nav" role="navigation" aria-label="Menu latéral">
    <h4>Filtres de recherche</h4>
    <button class="fr-btn fr-fi-filter-fill fr-btn--icon-left" id="select-all">
    FILTER
    </button> 
    
    {%for section, _filters in filters.items()%}
    
    <div class="fr-sidemenu__inner">
        <button class="fr-sidemenu__btn" aria-controls="fr-sidemenu-wrapper" aria-expanded="false">Dans cette rubrique</button>
        <div class="fr-collapse" id="fr-sidemenu-wrapper">
            
            
            {%if _filters|length > 0%}
            <section id="{{section}}-{{loop.index}}" class="fr-accordion">
              <h3 class="fr-accordion__title">
              <button class="fr-accordion__btn" aria-expanded="false" aria-controls="fr-accordion-{{loop.index}}-body-{{loop.index}}" data-fr-js-collapse-button="true">{{section}}</button>
              </h3>
              <div class="fr-collapse" id="fr-accordion-{{loop.index}}-body-{{loop.index}}" data-fr-js-collapse="true" style="--collapse: -136px;">
              <ul class="fr-sidemenu__list">
                {%for _filter in _filters %}
                
                <li class="fr-sidemenu__item">
                  {% if _filter["multiple"] and _filter["is_controled"]%}
                    <div class="fr-form-group">
                    <fieldset class="fr-fieldset">
                      <legend class="fr-fieldset__legend fr-text--regular" id='checkboxes-legend'>
                          <b>{{_filter["label_fr"]}}:</b>
                      </legend>
                      <div class="fr-fieldset__content">
                        {%for val in values[_filter["slug"]] %}
                        <div class="fr-checkbox-group">
                            <input type="checkbox" id="{{_filter["slug"]}}-{{val.label_en}}" name="{{val.label_fr}}">
                            <label class="fr-label" for="{{_filter["slug"]}}-{{val.label_en}}">{{val.label_fr}}
                            </label>
                        </div>
                        {%endfor%}
                      </div>
                    </fieldset>
                    </div>
                  {% elif _filter["is_bool"] %}  
                    <div class="fr-form-group">
                      <fieldset class="fr-fieldset fr-fieldset--inline">
                          <legend class="fr-fieldset__legend fr-text--regular" id='radio-inline-legend'>
                            {{_filter["label_fr"]}}:
                          </legend>
                          <div class="fr-fieldset__content">
                            <div class="fr-radio-group">
                                <input type="radio" id="{{_filter['slug']}}-true" name="radio-inline">
                                <label class="fr-label" for="{{_filter['slug']}}-true">Oui
                                </label>
                            </div>
                            <div class="fr-radio-group">
                                <input type="radio" id="{{_filter['slug']}}-false" name="radio-inline">
                                <label class="fr-label" for="{{_filter['slug']}}-false">Non
                                </label>
                            </div>
                        </div>
                      </fieldset>
                  </div> 
                  {%elif _filter["is_controled"] %}
                  <div class="fr-select-group">
                    <label class="fr-label" for="select">
                      {{_filter["label_fr"]}}
                    </label>
                    <select class="fr-select" id="{{_filter['slug']}}" name="{{_filter['slug']}}">
                      {%for val in values[_filter["slug"]] %}
                      <option value="{{_filter["slug"]}}-{{val.label_fr}}">{{val.label_fr}}</option>
                      {%endfor%}
                    </select>
                  </div>
                  {%endif %}  
                </li>
                {%endfor%}
              </ul>
              </div>
              </div>
              <section>
              {%endif%}
              {%endfor%}
            
            
            
        </div>
      </div>
  </nav>
        