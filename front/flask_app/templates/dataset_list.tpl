
<div class="fr-row fr-px-6w">
  <div class="fr-container" id="dataset_list">
      <div class="">    
      {% for dataset in results %}
          {%include "dataset_item.tpl"%}
        {% endfor %}
      </div>
    </div>
</div>