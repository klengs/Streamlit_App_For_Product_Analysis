import streamlit as st
import plotly.express as px
import Etr_Tr as ETL


st.set_page_config(layout="wide")

st.sidebar.write('''
# Здравствуйте!

Перед вами дашборд, позволяющий смотреть данные по:

* Доли завершенных и незавершенных заказов
* Ежемесячной выручке кадого из бизнес юнитов
* NPS по каждому продукту

Данные выгружаются из Google Sheets при входе на страницу и храняться в кэше для удобства использования веб-приложения.

Для того, чтобы обновить данные * Нажмите С и перезагрузите страницу.*

Все представленные графики интерактивные.
Наведите курсор на обьект, чтобы узнать подробную информацию.''')

@st.cache
def load_data_cache():
  orders_info = ETL.create_orders_info()
  unit_revenue = ETL.create_revenue_per_unit()
  monthly_profit, most_profitable_product = ETL.create_monthly_revenue()
  NPS_df, NPS_A, NPS_B = ETL.create_NPS_info()
  return orders_info, unit_revenue, monthly_profit, most_profitable_product, NPS_df, NPS_A, NPS_B

orders_info, unit_revenue, monthly_profit, most_profitable_product, NPS_df, NPS_A, NPS_B = load_data_cache()

st.header('Доли завершенных и незавершенных заказов.')

fig = px.pie(orders_info,
             names=orders_info.index,
             values='Кол-во заказов',
             color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_layout(showlegend=False)
fig.update_traces(marker=dict(line=dict(color='white', width=0)),
                  opacity=0.7,
                  textposition='outside',
                  textinfo='percent+label+value')

st.plotly_chart(fig, use_container_width=True)

st.header('Выручка каждого из бизнес юнитов.')

fig = px.bar(unit_revenue,
             x=unit_revenue.index,
             y='Выручка',
             color=unit_revenue.index,
             color_discrete_sequence=px.colors.qualitative.Safe,
             hover_data=['Выручка за заказ']
             )
fig.update_layout(showlegend=False,
                  xaxis= dict(showgrid=False,
                            showline=False),
                 yaxis= dict(showgrid=False,
                            showline=True))
fig.update_traces(marker_line_width=0, opacity=0.7)

st.plotly_chart(fig, use_container_width=True)

st.header('Данные по ежемесячной выручке.')

with st.form('revenue_table1'):
    st.markdown("<h3 style='text-align: center; color: white;'>Выберите интересующие вас данные.</h3>", unsafe_allow_html=True)
    unit = st.multiselect(options=monthly_profit['Юнит'].unique(), default=monthly_profit['Юнит'].unique(), label='Выберите Юнит')
    month = st.slider(value=[1, 12], max_value=12, min_value=1, step=1, label='Выберите Месяц')
    st.form_submit_button('Выбрать')

col1, col2 = st.columns(2)

with col1:
    st.write('''Здесь представленна таблица с ежемесячной вырочкой для каждого Юнита по каждому продукту.''')
    monthly_profit[monthly_profit['Юнит'].isin(unit) & monthly_profit['Месяц'].isin(range(month[0], month[1]+1))]

with col2:
    st.write('''Здесь вы можете посмотреть самые продоваемые продукты за каждый месяц.''')
    most_profitable_product[most_profitable_product['Юнит'].isin(unit) & most_profitable_product['Месяц'].isin(range(month[0], month[1]+1))]

st.subheader('Визуализация ежемесячной выручки для юнитов по продуктам.')

fig = px.bar(monthly_profit,
             x='Юнит',
             y='Выручка',
             color='Название продукта',
             color_discrete_sequence=px.colors.qualitative.Safe,
             facet_col='Месяц',
             facet_col_wrap=6,
             labels={'Юнит':''})
fig.update_layout(showlegend=False)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)
fig.update_traces(marker_line_width=1.5, opacity=0.7)

st.plotly_chart(fig, use_container_width=True)

st.subheader('Отдельный график для каждого месяца.')

with st.form('monthly_revenue'):

    month = st.selectbox(label= 'Выберите месяц', options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    st.form_submit_button(label='Выбрать')

graph_df = monthly_profit[monthly_profit['Месяц'] == month]
fig = px.bar(graph_df,
             x='Юнит',
             y='Выручка',
             color='Название продукта',
             color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_layout(showlegend=False)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)
fig.update_traces(marker_line_width=1.5, opacity=0.7)

st.plotly_chart(fig, use_container_width=True)

st.header('NPS каждого бизнес юнита по каждому из продуктов.')

col1, col2 = st.columns([2, 1])

with col1:
    st.write(' ')
    NPS_df
with col2:
    st.write(' ')
    st.write(f'''NPS Юнита А: {NPS_A}''')
    st.write(f'''NPS Юнита B: {NPS_B}''')