import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Austin Zillow Homes Search", layout="centered", page_icon="🏠")
url = 'https://raw.githubusercontent.com/joe-bryan/search-zillow/main/Zillow_Austin_11-16-22.csv'

@st.cache
def load_data(filepath:str) -> pd.DataFrame:
    """ Load data from local CSV """
    return pd.read_csv(filepath).fillna("")


def search_dataframe(df:pd.DataFrame, column:str, search_str:str) -> pd.DataFrame:
    """ Search a column for a substring and return results as df """
    return df.loc[df[column].str.contains(search_str, case=False)]


def generate_barplot(results:pd.DataFrame, count_column:str, top_n:int=10):
    """load results from search_dataframe() and create barplot """
    return alt.Chart(results).transform_aggregate(
        count='count()',
        groupby=[f'{count_column}']
    ).transform_window(
        rank='rank(count)',
        sort=[alt.SortField('count', order='descending')]
    ).transform_filter(
        alt.datum.rank < top_n
    ).mark_bar().encode(
        y=alt.Y(f'{count_column}:N', sort='-x', axis=alt.Axis(title='Number of Beds')),
        x=alt.X('count:Q', axis=alt.Axis(title='Count')),
        tooltip=[alt.Tooltip(f'{count_column}:N', title='Number of beds in home'), alt.Tooltip('count:Q', title='Count of homes')]
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeWidth=0
    ).properties(
        width=700,
        height=400
    ).interactive()


def app():
    """ Search Streamlit App """
    st.title("Austin Homes Search 🏠")

    # load data from local csv as dataframe
    df = load_data(url)

    # search box
    with st.form(key='Search'):
        text_query = st.text_input(label='Enter address part to search')
        submit_button = st.form_submit_button(label='Search')
    
    # if button is clicked, run search
    if submit_button:
        with st.spinner("Searching (this could take a minute...) :hourglass:"):

            # search logic goes here! - search titles for keyword
            results = search_dataframe(df, "address", text_query)

            # notify when search is complete
            st.success(f"Search is complete :rocket: — **{len(results):,}** results found in {len(df):,}  addresses.")

        # display the first 10 results
        st.table(results.head(n=10))

        # display a bar chart of top bed sizes
        st.altair_chart(
            generate_barplot(results, "beds", 10)
        )


if __name__ == '__main__':
    app()