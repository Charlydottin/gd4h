<div class="fr-row fr-px-6w">
    <div class="fr-container fr-py-2w fr-col-offset-4">
        {%if count == 0 %}
        <h2> {%if lang=="fr" %} Aucun {{page_title}} trouvé pour  {%else%} No {{page_title}} found  for{%endif%}
        {%if query %}
        <em id="user_query">{{query}}</em>{%endif%}</h2>
        <a href="/datasets/"> {%if lang=="fr"%}Retour aux jeux de données {%else%} Back to dataset list{%endif%}</a>
        {%else %}
        <h2><a class="fr-btn info-625" href="#"> {{count}}</a> {{page_title}} {%if query %}{%if lang=="fr"%}trouvé{%if count >1%}s{%endif%} pour {%else%} found for{%endif%} <em id="user_query">{{query}}</em>{%endif%}</h2>
        {%endif%}
    </div>
</div>