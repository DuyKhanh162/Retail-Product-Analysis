import pandas as pd
import numpy as np
import plotly.offline as pyoff
import plotly.graph_objs as go

df_retail = pd.read_csv('OnlineRetail.csv', encoding='latin1')
df_retail.info()

# Tạo cột InvoiceYearMonth mới định dạng yyyymm
df_retail.InvoiceDate = pd.to_datetime(df_retail.InvoiceDate)

df_retail['InvoiceYearMonth'] = df_retail['InvoiceDate'].map(lambda x: x.year*100 + x.month)


# ------------------------- PHÂN BIỆT KHÁCH HÀNG MỚI VÀ CŨ -------------------------


# Tạo DataFrame thời gian mua hàng lần đầu của khách hàng
df_min_purchase = df_retail.groupby('CustomerID')['InvoiceDate'].min().reset_index()
df_min_purchase.columns = ['CustomerID', 'First_purchase_date']
df_min_purchase['First_purchase_date'] = df_min_purchase['First_purchase_date'].map(lambda x: x.year*100 + x.month) # Chuyển sang định dạng yyyymm

# Tạo DataFrame phân loại khách hàng mới hay cũ
df_customer = pd.merge(df_retail, df_min_purchase, on='CustomerID')
df_customer['UserType'] = 'New'
df_customer.loc[df_customer['InvoiceYearMonth'] != df_customer['First_purchase_date'], 'UserType'] = 'Existing'

# Đếm số khách hàng mới và cũ
df_customer.UserType.value_counts()


# Tạo DataFrame doanh thu của khách hàng mới và cũ
df_usertype_revenue = df_customer.groupby(['InvoiceYearMonth', 'UserType'])['Revenue'].sum().reset_index()
df_usertype_revenue = df_usertype_revenue.query('InvoiceYearMonth != 201012 and InvoiceYearMonth != 201112') # Không tính tháng đầu tiên do không có khách cũ và tháng cuối cùng do chưa đủ dữ liệu khách mới

# Vẽ biểu đồ doanh thu giữa khách hàng mới và cũ
plot_data = [
    go.Scatter(
        x=df_usertype_revenue.query('UserType == "Existing"')['InvoiceYearMonth'],
        y=df_usertype_revenue.query('UserType == "Existing"')['Revenue'],
        name = 'Existing'
    ),
    go.Scatter(
        x=df_usertype_revenue.query('UserType == "New"')['InvoiceYearMonth'],
        y=df_usertype_revenue.query('UserType == "New"')['Revenue'],
        name = 'New'
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Revenue of New and Existing Customers'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)

# Tạo DataFrame tỉ lệ khách hàng mới tham gia
count_new = df_customer.query('UserType == "New"').groupby(['InvoiceYearMonth'])['CustomerID'].nunique()
count_existing = df_customer.query('UserType == "Existing"').groupby(['InvoiceYearMonth'])['CustomerID'].nunique()
user_ratio = {}
user_ratio['TotalNewCustomer'] = count_new
user_ratio['TotalExistingCustomer'] = count_existing
user_ratio['NewCustomerRatio'] = count_new/count_existing
df_user_ratio = pd.DataFrame(user_ratio)

df_user_ratio = df_user_ratio.reset_index()
df_user_ratio = df_user_ratio.dropna()

# Vẽ biểu đồ tỉ lệ khách hàng mới tham gia
plot_data = [
    go.Bar(
        x=df_user_ratio['InvoiceYearMonth'],
        y=df_user_ratio['NewCustomerRatio'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'New Customer Ratio'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)


# ------------------------- TỈ LỆ KHÁCH HÀNG Ở LẠI VÀ RỜI BỎ -------------------------


# Tạo DataFrame doanh thu của mỗi khách hàng theo thời gian để tính tổng doanh thu
df_user_purchase = df_customer.groupby(['InvoiceYearMonth', 'CustomerID'])['Revenue'].sum().astype(int).reset_index()
df_user_purchase.Revenue.sum()

# Tạo DataFrame mua hàng của khách hàng theo thời gian (0 là không mua, 1 là có mua)
df_retention_crosstab = pd.crosstab(df_user_purchase.CustomerID, df_user_purchase.InvoiceYearMonth).reset_index()

# Tạo DataFrame tỉ lệ giữ chân khách hàng
months = df_retention_crosstab.columns[2:] # Không tính tháng đầu tiên do sẽ không có tháng trước đó
retention = []
for i in range(len(months) - 1):
    retention_data = {}
    selected_month = months[i+1]
    previous_month = months[i]
    retention_data['InvoiceYearMonth'] = int(selected_month)
    retention_data['TotalUser'] = df_retention_crosstab[selected_month].sum() # Tổng khách hàng đã mua trong tháng được chọn
    retention_data['RetainedUser'] = df_retention_crosstab[(df_retention_crosstab[selected_month] == 1) & (df_retention_crosstab[previous_month] == 1)][selected_month].sum() # Tổng những khách hàng đã mua hàng ở cả 2 tháng được chọn và tháng trước đó
    retention.append(retention_data)
    print('------------------' + str(selected_month) + '------------------')
    print(retention)
    
df_retention = pd.DataFrame(retention)

df_retention['RetentionRate'] = df_retention['RetainedUser']/df_retention['TotalUser'] # Tạo cột tỉ lệ giữ chân

# Vẽ biểu đồ tỉ lệ giữ chân khách hàng hàng tháng
plot_data = [
    go.Scatter(
        x=df_retention['InvoiceYearMonth'],
        y=df_retention['RetentionRate'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Retention Rate'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)

# Tạo cột tỉ lệ khách hàng rời bỏ
df_retention['ChurnRate'] = 1 - df_retention['RetentionRate']

# Vẽ biểu đồ tỉ lệ khách hàng rời bỏ hàng tháng
plot_data = [
    go.Scatter(
        x=df_retention['InvoiceYearMonth'],
        y=df_retention['ChurnRate'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Churn Rate'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)


# ------------------------- TỈ LỆ GIỮ CHÂN KHÁCH HÀNG (COHORT ANALYSIS) -------------------------


# Nối 2 DataFrame để có thêm thông tin về ngày đầu tiên mua hàng
df_retention_crosstab = pd.merge(df_retention_crosstab, df_min_purchase[['CustomerID', 'First_purchase_date']], on='CustomerID')

# Đổi tên cho DataFrame
column_names = ['m_' + str(columns) for columns in df_retention_crosstab.columns[:-1]]
column_names.append('First_purchase_date')
df_retention_crosstab.columns = column_names

# Tạo DataFrame Cohort Analysis
retention = []
for i in range(len(months)):
    retention_data = {}
    selected_month = months[i]
    previous_months = months[:i]
    next_months = months[i+1:]
        
    total_user_count = df_retention_crosstab[df_retention_crosstab['First_purchase_date'] == selected_month]['First_purchase_date'].count() # Đếm tổng những khách hàng sử dụng trong tháng được chọn
    retention_data['TotalUserCount'] = total_user_count
    retention_data[selected_month] = 1 # Tỉ lệ giữ chân của tháng được chọn luôn là 1
    
    for previous_month in previous_months:
        retention_data[previous_month] = np.nan # Những tháng trước tháng được chọn sẽ không cần quan tâm
        
    query = "First_purchase_date == {}".format(selected_month)
    
    for next_month in next_months:
        new_query = query + ' and {} > 0'.format(str('m_' + str(next_month)))
        retention_data[next_month] = np.round(df_retention_crosstab.query(new_query)['m_' + str(next_month)].sum()/total_user_count, 2) # Tính tỉ lệ giữ chân khách hàng so với tháng được chọn
    retention.append(retention_data)
    
df_cohort_retention = pd.DataFrame(retention)
df_cohort_retention.index = months