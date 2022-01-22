<!DOCTYPE html>
<html lang="fr" data-fr-theme>
  {% set active_page = "datasets" %}
  {% include 'head.tpl' %}
<body>
  {% include 'header.tpl' %}

<main role="main" id="contenu" >
  <div class="fr-container fr-py-6w fr-px-2w">
    {% include 'search_bar.tpl' %}
         
    <div class="fr-container fr-py-2w fr-col-offset-4">
      <h2><a class="fr-btn info-625" href="#"> {{count}}</a> {{page_title}}</h2>
    </div>    
  </div>
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
</main>

<script type="module" src="/static/js/dsfr.module.js"></script>
<script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.js"></script>
{%include "footer.tpl" %}


</body>
<script>
  //dsfr.start();
  $(document).ready(function() {
    $('#reset').click(function() {
      $('input#query').val("");
      location.reload();
    });
    $("button#search-btn").click(function() {
      var search_q = ($('#query').val());
      
      var url = "/datasets/"
      var api_url = "http://localhost:3000/search/datasets/fr?q="+encodeURIComponent(search_q);
      $.getJSON(api_url, function(data, status){
        var count = data["count"];
        var results = data["results"];
        console.log(results);
        
        $("a.info-625").text(count);
        $('div#dataset_list').empty();
        $(results).each(function(index){
          $("div#dataset_list").append(
            '<div class="fr-card fr-card--horizontal fr-px-2w fr-enlarge-link">'
              +'<div class="fr-card__body ">'
                +'<h2 class="fr-card__title">'
                  +'<a href="/datasets/'+this._id+'" class="fr-card__link">'+this.name+'</a>'+this.acronym+'</h2>'
                  +'<p class="fr-card__detail">'
                    +'<a href="/organizations/" class="fr-tag">'+this.organizations[0]+'</a></p>'
                  +'<p class="fr-card__desc">'+this.description+'</p>'
              +'<span class="highligh">'+this.highlight[0].description+'</span>'
              +'</div></div>');
        });
      })})});
        
      
    
  </script>
</html>