{% from "profileengine01classic/_i18n.j2" import cv_title_i18n, header_label_i18n %}
{% if cv.name %}
# {{ cv_title_i18n(cv.name, locale) }}
{% endif %}
{% if cv.headline %}
## {{ cv.headline }}
{% endif %}

{% if cv.phone %}
- {{ header_label_i18n("phone", locale) }}: {{ cv.phone|replace("tel:", "")|replace("-", " ") }}
{% endif %}
{% if cv.email %}
- {{ header_label_i18n("email", locale) }}: [{{ cv.email }}](mailto:{{ cv.email }})
{% endif %}
{% if cv.location %}
- {{ header_label_i18n("location", locale) }}: {{ cv.location }}
{% endif %}
{% if cv.website %}
- {{ header_label_i18n("website", locale) }}: [{{ cv.website|replace("https://", "")|replace("/", "") }}]({{ cv.website }})
{% endif %}
{% if cv.social_networks %}
{% for network in cv.social_networks %}
- {{ network.network }}: [{{ network.username }}]({{ network.url }})
{% endfor %}
{% endif %}
