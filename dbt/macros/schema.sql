{% macro generate_schema_name(custom_schema_name, node) -%}
  {%- set prefix = var('schema_prefix') -%}
  {%- if not modules.re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', prefix) -%}
    {{ exceptions.raise_compiler_error('Invalid schema_prefix') }}
  {%- endif -%}
  {{ prefix }}_{{ custom_schema_name | trim if custom_schema_name else 'silver' }}
{%- endmacro %}

{% macro stable_key(expressions) -%}
sha2(concat(
  {%- for expression in expressions -%}
    cast(length(cast({{ expression }} as string)) as string), ':', cast({{ expression }} as string)
    {%- if not loop.last %}, {% endif -%}
  {%- endfor -%}
), 256)
{%- endmacro %}
