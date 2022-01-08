import pandas as pd

# first function will export data from google sheets

def load_df(sheet_name):
  sheet_id = '1Z8c4ukwQKe91lVr38qy2EA94bSK1xyE4'
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
  df = pd.read_csv(url)
  return df

# this function will count the number of comleted and incomplited orders

def create_orders_info():

  df_orders = load_df('orders') # load DataFrame

  # data transformation functions

  def str_to_bin(str1):
    if str1 == 'да':
      return 1
    else:
      return 0

  def num_to_str(num):
    if num == 1:
      return 'Завершенные заказы'
    else:
      return 'Незавершенные заказы'

  # this labels each order as comleted (1) and incomplited (0)

  df_orders['status'] = df_orders['Оплачен'].apply(str_to_bin)
  orders_status = df_orders.groupby(['User ID', 'ID продукта']).sum().status.reset_index()

  # here we create the final DF for display and for ploting

  graph_df = orders_status.groupby('status').count()['User ID']
  graph_df = graph_df.reset_index()
  graph_df['Статус'] =  graph_df['status'].apply(num_to_str)
  graph_df['Кол-во заказов'] =  graph_df['User ID']
  graph_df = graph_df[['Статус', 'Кол-во заказов']]
  graph_df.set_index('Статус', inplace=True)

  return graph_df

# this function calculates each unit's revenue

def create_revenue_per_unit():
  # join orders and products DFs
  df_orders = load_df('orders')
  only_completed = df_orders[df_orders['Оплачен'] == 'да']
  df_products = load_df('products')
  only_completed = pd.merge(only_completed, df_products, on='ID продукта')

  # create DF for display and plot
  graph_df = only_completed.groupby('Юнит')['Сумма платежа'].sum().reset_index()
  graph_df['clients_num'] = only_completed.groupby('Юнит').count()['Order ID'].reset_index()['Order ID']
  graph_df['Выручка за заказ'] = graph_df['Сумма платежа'] / graph_df.clients_num
  graph_df.rename(columns={'Сумма платежа': 'Выручка'}, inplace=True)
  graph_df.drop(columns=['clients_num'], inplace=True)
  graph_df.set_index('Юнит', inplace=True)
  return graph_df

# this function calculates each units monthly revenue by product

def create_monthly_revenue():
  df_orders = load_df('orders')
  only_completed = df_orders[df_orders['Оплачен'] == 'да']
  df_products = load_df('products')
  only_completed = pd.merge(only_completed, df_products, on='ID продукта')

  only_completed['Месяц'] = only_completed['Дата платежа'].astype('str').apply(lambda date: int(date.split('/')[0]))

  monthly_profit = only_completed.groupby(['Юнит', 'Месяц', 'Название продукта'])['Сумма платежа'].sum().reset_index()
  monthly_profit.rename(columns={'Сумма платежа': 'Выручка'}, inplace=True)

  most_profitable_product = monthly_profit.set_index('Название продукта').groupby(['Юнит', 'Месяц']).idxmax()['Выручка'].reset_index()
  most_profitable_product.rename(columns={'Выручка':'Самый продоваемый продукт'}, inplace=True)
  most_profitable_product.sort_values(by=['Юнит', 'Месяц'], inplace=True)
  return monthly_profit, most_profitable_product

# this function calculates NPS by unit and product as well as average for each unit

def create_NPS_info():
  df_scores = load_df('NPS')
  df_products = load_df('products')
  df_products.rename(columns={'Название продукта': 'Название курса'}, inplace=True)
  df_scores = pd.merge(df_scores, df_products, on='Название курса')

  def add_category(score):
    if score >= 9:
      return 'Промоутер'
    elif score >= 7:
      return 'Неитральный'
    else:
      return 'Детрактор'

  df_scores['Категория'] = df_scores['Оценка'].apply(add_category)
  df_cat = df_scores.groupby(['Юнит', 'Название курса', 'Категория']).count().reset_index()
  df_cat.drop(columns=['ID пользователя', 'ID продукта'], inplace=True)
  df_cat.sort_values(by=['Юнит', 'Название курса', 'Категория'], inplace=True)
  df_cat.rename(columns={'Оценка': 'Кол-во'}, inplace=True)

  NPS_ls = []
  dep_ls = []
  name_ls = []
  for i in range(0, len(df_cat['Кол-во']), 3):
    sum = df_cat['Кол-во'][i] + df_cat['Кол-во'][i+1] + df_cat['Кол-во'][i+2]
    NPS = (df_cat['Кол-во'][i+2] - df_cat['Кол-во'][i])/sum
    NPS_ls.append(NPS)
    dep_ls.append(df_cat['Юнит'][i])
    name_ls.append(df_cat['Название курса'][i])

  NPS_df = pd.DataFrame({'Юнит': pd.Series(dep_ls),
                         'Название курса': pd.Series(name_ls),
                         'NPS': pd.Series(NPS_ls)})

  P_A = df_cat[(df_cat['Юнит'] == 'A') & (df_cat['Категория'] == 'Промоутер')]['Кол-во'].sum()
  D_A = df_cat[(df_cat['Юнит'] == 'A') & (df_cat['Категория'] == 'Детрактор')]['Кол-во'].sum()
  S_A = df_cat[(df_cat['Юнит'] == 'A')]['Кол-во'].sum()
  NPS_A = (P_A - D_A) / S_A

  P_B = df_cat[(df_cat['Юнит'] == 'B') & (df_cat['Категория'] == 'Промоутер')]['Кол-во'].sum()
  D_B = df_cat[(df_cat['Юнит'] == 'B') & (df_cat['Категория'] == 'Детрактор')]['Кол-во'].sum()
  S_B = df_cat[(df_cat['Юнит'] == 'B')]['Кол-во'].sum()
  NPS_B = (P_B - D_B) / S_B

  return NPS_df, NPS_A, NPS_B




