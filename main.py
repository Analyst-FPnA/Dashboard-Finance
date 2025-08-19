import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_plotly_events import plotly_events
from streamlit_folium import folium_static
import folium
from streamlit_folium import st_folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.colors as mcolors
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, ColumnsAutoSizeMode, GridUpdateMode
st.set_page_config(
    layout="wide" # Menggunakan layout lebar untuk visualisasi yang lebih baik
)


css = '''
<style>
    .stMainBlockContainer {
        padding: 20px !important;
        margin: 0 !important;
    }
    [data-testid="stMetricLabel"] div div{
        font-size: 18px;
        font-weight: bold;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 30px;
        border-radius: 5px 5px 0 0; /* Rounded top */
        color: black;
        white-space: pre-wrap;
        background-color: #cccccc;
        gap: 1px;
        padding-right: 10px;
        padding-left: 10px;
        padding-top: 0px;
        padding-bottom: 0px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #5d4edb !important;
        color: white;
        font-weight: bold;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)


def create_plotly_avg_daily_combined_chart(df, base_font_size=13):
    df['text_total_resto'] = df['Value'].astype(str)
    df['text_avg_daily'] = df['%'].apply(lambda x: f'{x*100:.1f}%')

    color_bar = "#5d4edb"
    color_line = "#dc840c"

    fig = go.Figure()

    # Bar chart - Value
    fig.add_trace(
        go.Bar(
            x=df['Month'],
            y=df['Value'],
            name='Value',
            text=df['text_total_resto'],
            textposition='outside',
            marker_color=color_bar,
            textfont=dict(size=base_font_size, color='black')
        )
    )

    # Line chart - %
    fig.add_trace(
        go.Scatter(
            x=df['Month'],
            y=df['%'],
            name='% of Sales',
            mode='lines+markers',
            line=dict(color=color_line, width=3),
            yaxis='y2'
        )
    )

    # Anotasi - Label % di atas titik
    for _, row in df.iterrows():
        fig.add_annotation(
            x=row['Month'],
            y=row['%'],
            text='  '+row['text_avg_daily']+'  ',
            showarrow=False,
            yshift=15,
            bgcolor="rgb(220,132,12)",  # warna latar label (green tone)
            font=dict(color="white", size=base_font_size),
            bordercolor=color_line,
            borderwidth=1,
            opacity=0.98,
            yref='y2',
            xref='x'
        )

    # Layout
    fig.update_layout(
        barmode='group',
        height=None,
        autosize=True,
        plot_bgcolor='white',
        uniformtext_minsize=base_font_size - 2,
        uniformtext_mode='hide',
        margin=dict(l=50, r=40, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=base_font_size)
        ),
        xaxis=dict(
            tickangle=-30,
            tickfont=dict(size=base_font_size-2,family="Arial Black")
        ),
        yaxis=dict(
            title="Value",
            tickfont=dict(color=color_bar, size=base_font_size-2,family="Arial Black"),
            range=[0, 14],
            showgrid=False
        ),
        yaxis2=dict(
            visible=False,
            title="% of Sales (Rp)",
            overlaying='y',
            side='right',
            tickfont=dict(color=color_line, size=base_font_size),
            showgrid=False
        )
    )

    return fig

key = "enterprise_disabled_grid"
license_key = None
enable_enterprise = True
if enable_enterprise:
    key = "enterprise_enabled_grid"
    license_key = license_key

st.write('')
st.header('📝 KPI Dashboard (Finance)')
st.markdown("<hr style='margin:0; padding:0; border:1px solid #ccc'>", unsafe_allow_html=True)
tab = st.tabs(['Dashboard','Data'])

with tab[0]:
    st.write('')
    kol = st.columns(4)

    df_raw  = pd.read_excel('Report Finance.xlsx').fillna('')
    df = df_raw.melt(id_vars=df_raw.columns.to_list()[:5], var_name='Month', value_name='Value')
    df['Month'] = pd.to_datetime(df['Month'])

    if 'selected_months' not in st.session_state:
        st.session_state.selected_months = '2025-07-01'
        
    with kol[0]:
        bulan = pd.to_datetime(st.session_state.selected_months)
        st.metric(label='Sales',value=df.loc[df['Month']==bulan,'Value'].sum(), delta=f"{round((df.loc[df['Month']==bulan,'Value'].sum()-df.loc[df['Month']==bulan-pd.offsets.MonthBegin(1),'Value'].sum())/df.loc[df['Month']==bulan-pd.offsets.MonthBegin(1),'Value'].sum()*100,2)}%")
    style_metric_cards(background_color='#FFFFFF',border_left_color='#5d4edb',border_size_px=1)
    kol = st.columns([2,1])
    with kol[0]:
        with stylable_container(
            key='grafik1',
            css_styles="""
                {   background-color: white;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    box-shadow: 4px 8px 12px rgba(0, 0, 0, 0.08);
                }
                """,
        ):
            df_bar = df[df['Kat_5']=='Laba Operational'][['Month','Value']].reset_index(drop=True)
            df_bar['%'] = df_bar['Value']/df.groupby('Month')['Value'].sum().reset_index()['Value'] 
            fig = create_plotly_avg_daily_combined_chart(df_bar)
            st.markdown("<h5 style='font-family:Arial; font-weight:bold; font-size:16px;'>Operational Income</h5>",unsafe_allow_html=True)
            st.markdown("<hr style='margin:0; padding:0; border:1px solid #ccc'>", unsafe_allow_html=True)
            selected_points_bar = st.plotly_chart(fig, on_select='rerun', selection_mode='points')
            
            try:
                selected_points_bar = selected_points_bar['selection']['points'][0]['x']
                if st.session_state.selected_months != selected_points_bar:
                    st.session_state.selected_months = selected_points_bar
                    st.rerun()
                df_pie = df[df['Month']==st.session_state.selected_months].groupby(df.columns.to_list()[:5])['Value'].sum().reset_index()
            except IndexError as a:
                if st.session_state.selected_months != '2025-07-01':
                    st.session_state.selected_months = '2025-07-01'
                    st.rerun()
                df_pie = df[df['Month']==st.session_state.selected_months].groupby(df.columns.to_list()[:5])['Value'].sum().reset_index()
            st.markdown("</div>", unsafe_allow_html=True)


    with kol[1]:
        with stylable_container(
            key='grafik2',
            css_styles="""
                {   background-color: white;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    box-shadow: 4px 8px 12px rgba(0, 0, 0, 0.08);
                }
                """,
        ):
            df_pie['%'] = (df_pie['Value'] / df_pie['Value'].sum() * 100).apply(lambda x: f"{x:.2f}%")
            fig = px.sunburst(
                df_pie.iloc[:,1:],
                path=df_pie.columns.to_list()[1:5],  # Urutan hierarki
                values='Value',
                color='Kat_3',
                custom_data = ['Value','%'],
                color_discrete_sequence=['rgb(198, 35, 0)','rgb(215, 215, 215)','rgb(220,132,12)','rgba(89,75,219,255)'],  # Skema warna kategori
                labels={
                    'Kat_2': 'Sub Kategori A',
                    'Kat_3': 'Sub Kategori B',
                    'Kat_4': 'Sub Kategori C',
                    'Kat_5': 'Sub Kategori D',
                    'Value': 'Jumlah'
                }
            )
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>%{percentRoot:.2%}<extra></extra>"
            )
            fig.update_layout(
                margin=dict(t=5, l=10, r=10, b=50))
            st.markdown("<h5 style='font-family:Arial; font-weight:bold; font-size:16px;'>Cost and Profit Breakdown of Sales</h5>",unsafe_allow_html=True)
            st.markdown(f"<hr style='margin:0; padding:0; font-family:Arial;font-weight:bold; font-size:10px; border:1px solid #ccc'>{bulan.strftime('%b-%y')}</hr>", unsafe_allow_html=True)

            selected_points_pie = plotly_events(fig, click_event=True)
            st.markdown("</div>", unsafe_allow_html=True)



    if selected_points_pie:
        point_num = selected_points_pie[0]['pointNumber']

        if 'ids' in fig.data[0]:
            clicked_id = fig.data[0]['ids'][point_num]
            st.write(f"{clicked_id}")
            
            parts = clicked_id.split('/')

            filtered_df = df_pie.copy()
            if len(parts) >= 1:
                filtered_df = filtered_df[filtered_df['Kat_2'] == parts[0]]
            if len(parts) >= 2:
                filtered_df = filtered_df[filtered_df['Kat_3'] == parts[1]]
            if len(parts) >= 3:
                filtered_df = filtered_df[filtered_df['Kat_4'] == parts[2]]
            if len(parts) >= 4:
                filtered_df = filtered_df[filtered_df['Kat_5'] == parts[3]]

            gb = GridOptionsBuilder.from_dataframe(filtered_df)
            gridOptions = gb.build()
            AgGrid(
                filtered_df,
                gridOptions, update_mode=GridUpdateMode.NO_UPDATE,
                enable_enterprise_modules=enable_enterprise,
                allow_unsafe_jscode=True)
with tab[1]:
    df_raw.columns= df_raw.columns[:5].to_list()+pd.Series(df_raw.columns[5:].values).apply(lambda x:x.strftime('%b-%Y')).to_list()
    gb = GridOptionsBuilder.from_dataframe(df_raw)
    gridOptions = gb.build()
    AgGrid(
        df_raw,
        gridOptions, update_mode=GridUpdateMode.NO_UPDATE,
        enable_enterprise_modules=enable_enterprise,fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True)
