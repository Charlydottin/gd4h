
<div class="fr-card fr-card--horizontal fr-enlarge-link">
<div class="fr-card__body">
    <h4 class="fr-card__title">
        {%if query %}
            <a class="fr-card__link" href="/datasets/{{dataset['_id']}}">{{dataset["name"]}}</a>
        {%else %}
            <a class="fr-card__link" href="/datasets/{{dataset['_id']['$oid']}}">{{dataset["name"]}}</a>
        {%endif%}
    </h4>
    <p class="fr-card__desc">
        {{dataset["description"]["label_fr"]}}
        {%if query %}
        {{dataset["description"]}}
        <p class="">Match: <a href="#" class="fr-tag">{{dataset["score"]}}</a>
            {%if highlight in dataset %}
            <ul>{%for highlight, content in dataset["highlight"].items() %}
                <li>{{highlight}}: {{content[0]}}</li>
                {%endfor%}
            </ul>
            </p>
            {% endif %}
        {%endif%}
        </p>
    
    
    <p class="fr-card__detail">
        {%for o in dataset["organizations"] %}
            {%if "_id" in o %}
                <a href="/organizations/{{o['_id']['$oid']}}" class="fr-tag">{{o["name"]}}</a>
            {%else %}
                <a href="/organizations/" class="fr-tag">{{o["name"]}}</a>
            {%endif%}
        {%endfor%}
    </p>
    {%if query %}
            <a class="fr-card__link" href="/datasets/{{dataset['_id']}}"></a>
    {%else %}
        <a class="fr-card__link" href="/datasets/{{dataset['_id']['$oid']}}"></a>
    {%endif%}
        
</div>
</div>
