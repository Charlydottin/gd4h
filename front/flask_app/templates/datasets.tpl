<!DOCTYPE html>
<html lang="fr" data-fr-theme>
  {% set active_page = "datasets" %}
  {% include 'head.tpl' %}
<body>
  {% include 'header.tpl' %}

<main role="main" id="contenu" >
  
    <div class="fr-container fr-py-4w">
      {% include 'search_bar.tpl' %}
    </div>
    <span id="search_results">
    </span>
    <span id="datasets_list">
      {%include "search_count.tpl" %}  
      <div class="fr-row fr-px-6w">
        <div class="fr-grid-row fr-grid-row--gutters fr-grid-row--center">
          <div class="fr-col-4">  
          {%include 'filter_nav.tpl' %}
          </div>
          <div class="fr-col-8">
            <ul class="fr-btns-group fr-btns-group--inline">
              {%include "button_reactions.tpl" %}
            </ul>
            {%include "dataset_list.tpl" %} 
          </div>
        </div>
      </div>
    </span>
</main>

<script type="module" src="/static/js/dsfr.module.js"></script>
<script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.js"></script>
{%include "footer.tpl" %}


</body>
<script src="/static/js/jquery-3.6.0.min.js"></script>
<script>
  {%block script%}
    var element = document.getElementById("datasets_list");
    $("button#reset").click(function(){
        $("#datasets_list").append(element);
    });
    $("button#search-btn").click(function(){
        if ($("#datasets_list").val() != ""){
          $("#datasets_list").val() = '';
        }
        var user_query_arg = ($('#query').val());
        alert(user_query_arg);
        fetch('/search?query='+encodeURIComponent(user_query_arg))
        .then(function(response) {
            $('#search_results').empty();
            return response.json();
        })
        .then(function(myJson) {    
            $("#search_results").append(myJson.data);
        });
      });
      
{%endblock%}
  </script>
</html>