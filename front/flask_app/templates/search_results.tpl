{%include "search_count.tpl" %}
<div class="fr-row fr-px-6w">
<div class="fr-grid-row fr-grid-row--gutters fr-grid-row--center">
    <div class="fr-col-4">  
    {%include 'filters.tpl' %}
    </div>
    <div class="fr-col-8">
    <ul class="fr-btns-group fr-btns-group--inline">
        {%include "button_reactions.tpl" %}
    </ul>
    {%include "dataset_list.tpl" %} 
    </div>
</div>
</div>