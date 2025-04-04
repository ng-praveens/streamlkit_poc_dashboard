import streamlit as st
import base64
from jinja2 import Template
import pandas as pd



def dataframe_to_nested_dicts(df):

    grouped = df.groupby('name')

    result = []
    for name, group in grouped:
        # For each group, create a 'values' list with dictionaries for each row
        values = group.apply(lambda row: {
            'currentcolor': row['currentcolor'],
            'previouscolor': row['previouscolor'],
            'value': row['value'],
            'link': row['link']
        }, axis=1).tolist()
        
        # Append the nested dictionary to the result
        result.append({'name': name, 'color': "background-color: #F7DC6F;", 'values': values})

    return result


@st.cache_resource(ttl="10d")
def load_bootstrap_styles() -> str:
    with open('./static/html/css/bootstrap.min.css') as f:
        bs5_styles = f.read()

    st.html("""<style>""" + bs5_styles + """</style>""")


@st.cache_resource(ttl="10d")
def navigation_card_html() -> str:
    with open('./static/html/app_card.html') as f:
        html_data = f.read()

    return html_data


def navigation_card_template() -> str:

    return Template(navigation_card_html())


@st.cache_resource(ttl="10d")
def pricing_monthly_table() -> str:

    with open('./static/html/pricing_table_monthly.html') as f:
        template = Template(f.read())

    return template


@st.cache_resource(ttl="10d")
def hero_summary_html() -> str:

    with open('./static/html/hero_summary.html') as f:
        template = Template(f.read())

    return template


@st.cache_resource(ttl="10d")
def styles_and_js_html() -> str:

    with open('./static/html/styles_and_js.html') as f:
        template = Template(f.read())

    return template


@st.cache_resource(ttl="10d")
def ratecard_summary_html() -> str:

    with open('./static/html/ratecard_summary.html') as f:
        template = Template(f.read())

    return template


@st.cache_resource(ttl="10d")
def ratecohort_summary_html() -> str:

    with open('./static/html/ratecohort_summary.html') as f:
        template = Template(f.read())

    return template


@st.cache_resource(ttl="10d")
def business_insights_html() -> str:

    with open('./static/html/business_insights.html') as f:
        template = Template(f.read())

    return template

@st.cache_resource(ttl="10d")
def color_status_legend_html() -> str:

    with open('./static/html/color_legend.html') as f:
        template = Template(f.read())

    return template

#@st.cache_data(ttl="1d")
def navigation_card(title, content, image_base64, link_url):

    template = navigation_card_template()
    html = template.render(link_url=link_url, content=content, image_base64=image_base64, title=title)
    st.html(html)


def render_business_insights():

    business_insights_template = business_insights_html()
    st.html(business_insights_template.render())

def render_ratecard_summary(status_map=None):

    ratecard_summary_template = ratecard_summary_html()
    st.html(ratecard_summary_template.render(metricsdata=status_map))


def render_ratecohort_summary(status_map=None):

    ratecohort_summary_template = ratecohort_summary_html()
    st.html(ratecohort_summary_template.render(metricsdata=status_map))


def render_styles_and_js():

    stylesjs_template = styles_and_js_html()
    st.html(stylesjs_template.render())


def render_pricing_table_monthly(status_map=None):

    pricing_table_monthly_template = pricing_monthly_table()
    st.html(pricing_table_monthly_template.render(metricsdata=status_map))


def render_color_status_legend():

    color_status_legend_template = color_status_legend_html()
    st.html(color_status_legend_template.render())



#@st.cache_data(ttl="1d")
def traffic_grid():

    stylesjs_template = styles_and_js_html()
    st.html(stylesjs_template.render())

    ratecard_summary_template = ratecard_summary_html()
    st.html(ratecard_summary_template.render())

    ratecohort_summary_template = ratecohort_summary_html()
    st.html(ratecohort_summary_template.render())

    business_insights_template = business_insights_html()
    st.html(business_insights_template.render())


    #template = hero_summary_html()
    #st.html(template.render())