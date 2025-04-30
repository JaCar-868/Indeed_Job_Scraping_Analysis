"""
indeed_job_data_scraping.py: Scrape Indeed job listings for a given role and location,
analyze the most common skills/requirements, and visualize them interactively with Plotly.
"""
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State
from datetime import datetime
from bs4 import BeautifulSoup
from job_scraper_utils import configure_webdriver, search_jobs, scrape_job_data, clean_data


def extract_requirements(driver, df: pd.DataFrame) -> list:
    """
    For each job link in df, navigates to the job page and extracts bullet points
    under the "Requirements" header, if present.
    """
    requirements = []
    for _, row in df.iterrows():
        link = row.get('Link')
        if not link:
            continue
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        desc = soup.find('div', id='jobDescriptionText')
        if not desc:
            continue
        # find a heading containing 'requirement'
        header = None
        for tag in desc.find_all(['h2', 'h3', 'b', 'strong']):
            if 'requirement' in tag.get_text().lower():
                header = tag
                break
        if header:
            ul = header.find_next_sibling('ul')
            if ul:
                for li in ul.find_all('li'):
                    requirements.append(li.get_text().strip())
    return requirements


def build_figure(requirements: list, job_position: str, job_location: str):
    """
    Builds a Plotly horizontal bar chart of the top 10 requirements,
    calculating percentages for hover info.
    """
    if not requirements:
        df_plot = pd.DataFrame({'Requirement': [], 'Count': [], 'Percent': []})
    else:
        counts = pd.Series(requirements).value_counts().nlargest(10)
        df_plot = counts.reset_index()
        df_plot.columns = ['Requirement', 'Count']
        df_plot['Percent'] = df_plot['Count'] / df_plot['Count'].sum() * 100

    fig = px.bar(
        df_plot,
        x='Count', y='Requirement',
        orientation='h',
        labels={'Count': 'Number of Listings', 'Requirement': 'Requirement'},
        title='Top Job Requirements'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        title_x=0.5,
        margin=dict(l=100, r=20, t=50, b=20)
    )
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Count: %{x}<br>Percent: %{customdata[0]:.1f}%',
        customdata=df_plot[['Percent']].values
    )
    return fig


# Initialize Dash app
def main():
    app = Dash(__name__)

    app.layout = html.Div([
        html.Div([
            html.Div([
                html.Label('Search Query'),
                dcc.Input(id='job-input', type='text', placeholder='e.g., Data Analyst', style={'width': '100%'}),
            ], style={'width': '30%', 'padding': '10px'}),
            html.Div([
                html.Label('Location'),
                dcc.Input(id='loc-input', type='text', placeholder='e.g., Remote', style={'width': '100%'}),
            ], style={'width': '30%', 'padding': '10px'}),
            html.Div([
                html.Button('Search', id='search-button', n_clicks=0, style={'marginTop': '22px'})
            ], style={'width': '10%', 'padding': '10px'})
        ], style={'display': 'flex', 'alignItems': 'flex-end'}),
        html.Div([
            html.H3(id='title'),
            html.P(id='updated-date'),
            dcc.Graph(id='requirements-graph')
        ], style={'width': '80%', 'padding': '10px'})
    ])

    @app.callback(
        [Output('requirements-graph', 'figure'),
         Output('title', 'children'),
         Output('updated-date', 'children')],
        [Input('search-button', 'n_clicks')],
        [State('job-input', 'value'), State('loc-input', 'value')]
    )
    def update_dashboard(n_clicks, job_position, job_location):
        if n_clicks is None or not job_position or not job_location:
            # Empty initial state
            empty_fig = px.bar(pd.DataFrame({'Requirement': [], 'Count': []}), x='Count', y='Requirement')
            return empty_fig, '', ''

        # Scrape job listings
        driver = configure_webdriver()
        base_url = 'https://www.indeed.com'
        search_jobs(driver, base_url, job_position, job_location, date_posted=7)
        df = scrape_job_data(driver, base_url)
        df_clean = clean_data(df)
        requirements = extract_requirements(driver, df_clean)
        driver.quit()

        # Build figure
        fig = build_figure(requirements, job_position, job_location)
        title_text = f"{job_position.title()}, {job_location.title()}"
        updated_text = f"Updated: {datetime.now().strftime('%B %d, %Y')}"
        return fig, title_text, updated_text

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
