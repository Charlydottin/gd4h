<!DOCTYPE html>
<html lang="{{lang}}" data-fr-theme>
{% set navigation_bar = [
    ('/', 'index', 'A propos'),
    ('/organizations/', 'organizations', 'Institutions'),
    ('/datasets/', 'datasets', 'Jeux de données'),
    ('/references/', 'references', 'Référentiels')
] -%}
{% set active_page = active_page|default('index') -%}
{% include 'head.tpl' %}
<body>
    {% include 'header.tpl' %}
    <main role="main" id="contenu" >
        <div class="fr-container fr-py-6w fr-px-2w">
            {%block content %}{%endblock%}
        </div>
<script type="module" src="/static/js/dsfr.module.min.js"></script>
<script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</main>
{%include "footer.tpl" %}

</body>

<script type="module" src="/static/js/dsfr.module.min.js"></script>
<script type="text/javascript" nomodule src="/static/js/dsfr.nomodule.min.js"></script>
<script>
  
  
    {%block script %}{% endblock %}
</script>


</html>