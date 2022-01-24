<div class="fr-container fr-py-2w>
    <h2><a class="fr-btn info-625" href="#">{{data["count"]}}</a> datasets found for <em id="user_query">{{query}}</em></h2>
</div>  
<div class="fr-row fr-px-6w">
  <div class="fr-grid-row fr-grid-row--gutters fr-grid-row--center">
      
        <ul class="fr-btns-group fr-btns-group--inline">
          {%include "button_reactions.tpl" %}
        </ul>
        <div class="fr-container fluid" id="dataset_list">
        
        {% for dataset in data["result"] %}
        <h3>{{dataset.name}}</h3>
        {%endfor %}  
        </div>
    </div>
</div>