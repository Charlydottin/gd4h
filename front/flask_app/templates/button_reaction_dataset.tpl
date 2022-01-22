<%block%>
<button onclick="location.href='https://github.com/c24b/gd4h/issues/new?assignees=c24b&labels=question&template=general-comment.md&title=%5BCOMMENT%5D{{dataset['name']}}" class="fr-btn fr-fi-chat-quote-line fr-btn--icon-right">
    Make a  Comment
</button>

<button onclick="location.href='https://github.com/c24b/gd4h/issues/new?assignees=c24b&labels=bug%2Ctriage&template=.bug_report.yaml&title=%5BBug%5D%3A+{{dataset['name']}}" class="fr-btn fr-btn--secondary fr-fi-error-warning-line fr-btn--icon-right">
Report an error
</button>
<button onclick="location.href='https://github.com/c24b/gd4h/discussions/new'" class="fr-btn fr-btn--secondary fr-fi-external-link-line fr-btn--icon-right">
Discuss with the community
</button>
<%endblock %>