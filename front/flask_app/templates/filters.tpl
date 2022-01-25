<nav class="fr-sidemenu" role="navigation" id="filter_nav" aria-label="{%if lang=="fr"%}Filtres{%else%}Filters{%endif%}">
<div class="fr-sidemenu__title">{%if lang=="fr"%}Filtres{%else%}Filters{%endif%}</div>
<ul class="fr-btns-group fr-btns-group--inline-lg">
<li class="">
<button class="fr-btn fr-btn--secondary fr-fi-search-line" id="select-all">
    FILTER
</button>  
</li>
<li>
<button class="fr-btn fr-btn--secondary fr-fi-refresh-line" onClick="window.location.reload();" id="reset-filter">
    RESET
</button></li>
</ul>
{%set target_label= "label_"+lang %}

{{target_label}}
<div class="fr-sidemenu__inner">
        {%for section, _filters in filters.items()%}
        {%if _filters|length > 0%}
        <button class="fr-sidemenu__btn" aria-controls="fr-sidemenu-wrapper" aria-expanded="false"></button>
         <div class="fr-collapse" id="fr-sidemenu-wrapper">
            <div id="{{section}}" class="fr-sidemenu__title">{{section.lower()}}</div>
            <ul class="fr-sidemenu__list">
                {%for _filter in _filters %}
                <li class="fr-sidemenu__item">
                    <button class="fr-sidemenu__btn" aria-expanded="false" aria-controls="fr-sidemenu-section-{{section}}-item-{{loop.index}}" aria-current="true">
                    {{_filter[target_label]}}
                    </button>
                    
                    <div class="fr-collapse" id="fr-sidemenu-section-{{section}}-item-{{loop.index}}">
                        <ul class="fr-sidemenu__list">
                        {% if _filter["multiple"] %}
                            <li class="fr-sidemenu__item">
                                
                                {%for val in values[_filter["slug"]] %}
                                <div class="fr-checkbox-group">
                                    <input type="checkbox" value="{{_filter.slug}}-{{val[target_label]}}" id="check-{{_filter.slug}}-{{loop.index}}">
                                    <label class="fr-label" for="check-{{_filter.slug}}-{{loop.index}}">
                                       {{val[target_label]}}
                                    </label>
                                </div>
                                {%endfor%}
                            </li>
                        {%else %}
                            <li class="fr-sidemenu__item">
                                <div class="fr-fieldset__content">
                                {%for val in values[_filter["slug"]] %}
                                <div class="fr-radio-group">
                                
                                    <input type="radio" value="{{_filter['slug']}}-{{val[target_label]}}" id="radio-{{_filter.slug}}-{{loop.index}}">
                                    <label class="fr-label" for="radio-{{_filter.slug}}-{{loop.index}}">
                                        {{val[target_label]}}
                                    </label>
                                </div>
                                {%endfor%}
                                </div>
                                
                                
                            </li>
                        {% endif %}
                        </ul>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
        {%endif %}
        {%endfor %}
    </div>
</nav>