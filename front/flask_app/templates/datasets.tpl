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
    </span>
</main>

<script type="module" src="/static/js/dsfr.module.js"></script>
<script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.js"></script>
{%include "footer.tpl" %}


</body>
<script src="/static/js/jquery-3.6.0.min.js"></script>

  {%block script%}
  <script>
    const filter_nav = document.getElementById("#filter_nav");
    
    var element = document.getElementById("datasets_list");
    $("button#reset-filter").click(function(){
        console.log("click");
        //$("#filter_nav").val() = "";
        //$("#filter_nav").append(filter_nav);
        /$("#datasets_list").append(element);
        //checkboxes = nav_filters.querySelectorAll('input[type="checkbox"]');
        //radios = nav_filters.querySelectorAll('input[type="radio"]');
        //checkboxes.prop('checked',false);
        //radios.prop('checked',false); 
    });
    $("button#reset").click(function(){
        $("#search_results").val() = '';
        $("#datasets_list").append(element);
    });
    $("button#search-btn").click(function(){
        if ($("#datasets_list").val() != ""){
          $("#datasets_list").val() = '';
        }
        var user_query_arg = ($('#query').val());
        
        if (user_query_arg != ''){
          
        fetch('/search?query='+encodeURIComponent(user_query_arg))
        .then(function(response) {
            $('#search_results').empty();
            return response.json();
        })
        .then(function(myJson) {    
            
            $("#search_results").append(myJson.data);
        })
        }
    });
    $('#select-all').click(function() {
        const args = [];
        const nav_filters = document.querySelector("nav#filter_nav");
        checkboxes = nav_filters.querySelectorAll('input[type="checkbox"]');
        radios = nav_filters.querySelectorAll('input[type="radio"]');
        $(checkboxes).each(function() {
          if (this.checked == true){
            params_arg = this.value.split("-");
            params_arg = encodeURIComponent(params_arg[0])+"="+encodeURIComponent(params_arg[1]);
            args.push(params_arg); 
            };
          
        });
        $(radios).each(function() {
          if (this.checked == true){
            params_arg = this.value.split("-");
            params_arg = encodeURIComponent(params_arg[0])+"="+encodeURIComponent(params_arg[1])
            args.push(params_arg); 
          }
         });
        q = args.join("&");
        //alert(q);
        fetch('/filter?'+q)
        .then(function(response) {
            $('#search_results').empty();
            $('#datasets_list').empty();
            
            return response.json();
        })
        .then(function(myJson) {    
            console.log(myJson);
            $("#search_results").append(myJson.data);
        });
    });
    
    </script>  
{%endblock%}
  
</html>