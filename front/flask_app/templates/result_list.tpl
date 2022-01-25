<div class="fr-container fluid" id="dataset_list">
    {% for dataset in result %}
    <div class="fr-card fr-card--horizontal fr-px-2w fr-enlarge-link">
      <div class="fr-card__body ">
         <h2 class="fr-card__title">
             <a href="/datasets/{{dataset['_id']['$oid']}}" class="fr-card__link">{{dataset["name"]}}</a>      
         </h2>
         <p class="fr-card__desc">{{dataset["description"]["label_fr"]}}</p>
         <p class="fr-card__detail">
          {%for o in dataset["organizations"] %}  
          {%if "_id" in o %}
          <a href="/organizations/{{o['_id']['$oid']}}" class="fr-tag">{{o["name"]}}</a>
          {%else %}
          <a href="/organizations/}}" class="fr-tag">{{o["name"]}}</a>
          {%endif%}
          {%endfor%}
          </p>
          <a href="/datasets/{{dataset['_id']['$oid']}}" class="fr-card__link"></a>
      </div>  
    </div>
    {%endfor%}
</div>