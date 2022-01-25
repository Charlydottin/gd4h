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
{%block script%}
    
    $("button#search-btn").click(function(){
        var user_query_arg = ($('#query').val());
        alert(user_query_arg);
        fetch('/search?query='+encodeURIComponent(user_query_arg))
        .then(function(response) {
            console.log(response)
            return response.json();
        })
        .then(function(myJson) {
            console.log(myJson);
            $("#results").append(myJson.data);
        });

                
                

        });
        
   
    

   
   
{%endblock%}
