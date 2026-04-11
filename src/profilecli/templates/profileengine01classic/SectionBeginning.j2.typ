{% from "profileengine01classic/_i18n.j2" import section_title_i18n %}
== {{ section_title_i18n(section_title, locale) }}
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}
