import pandas as pd
import plotly.offline as pyoff
import plotly.graph_objs as go

df_retail = pd.read_csv('OnlineRetail.csv', encoding='latin1')
df_retail.info()

# Tạo cột InvoiceYearMonth với định dạng yyyymm
df_retail.InvoiceDate = pd.to_datetime(df_retail.InvoiceDate)

df_retail['InvoiceYearMonth'] = df_retail['InvoiceDate'].map(lambda x: x.year*100 + x.month)


# ------------------------- TỈ LỆ TĂNG TRƯỞNG DOANH THU HÀNG THÁNG -------------------------


# Tính tổng doanh thu cho mỗi tháng
df_retail['Revenue'] = df_retail['UnitPrice'] * df_retail['Quantity']

# Tạo DataFrame doanh thu theo thời gian
df_revenue = df_retail.groupby('InvoiceYearMonth')['Revenue'].sum().reset_index()

# Tính phần trăm tăng trưởng doanh thu cho mỗi tháng
df_revenue['MonthlyGrowth'] = df_revenue['Revenue'].pct_change()

# Vẽ biểu đồ tăng trưởng doanh thu mỗi tháng
plot_data = [
    go.Scatter(
        x=df_revenue[df_revenue['InvoiceYearMonth'] != 201112]['InvoiceYearMonth'],
        y=df_revenue[df_revenue['MonthlyGrowth'] != 201112]['MonthlyGrowth'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Growth Rate'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)


# ------------------------- SỐ LƯỢNG KHÁCH HÀNG HOẠT ĐỘNG HÀNG THÁNG -------------------------

# Tạo DataFrame số khách hàng hoạt động trong một tháng
df_active = df_retail.groupby('InvoiceYearMonth')['CustomerID'].nunique().reset_index()

# Vẽ biểu đồ khách hàng hoạt động mỗi tháng
plot_data = [
    go.Bar(
        x=df_active['InvoiceYearMonth'],
        y=df_active['CustomerID'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Active Customer'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)

# Lượng khách hàng trung bình hoạt động trong tháng
df_active['CustomerID'].mean()


# ------------------------- TRUNG BÌNH SỐ LƯỢNG SẢN PHẨM BÁN RA TRONG MỘT THÁNG -------------------------


# Tạo DataFrame tổng số lượng sản phẩm theo thời gian
df_monthly_sales = df_retail.groupby('InvoiceYearMonth')['Quantity'].sum().reset_index()

# Vẽ biểu đồ trung bình sản phẩm bán ra trong một tháng
plot_data = [
    go.Bar(
        x=df_monthly_sales['InvoiceYearMonth'],
        y=df_monthly_sales['Quantity'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Total # of Order'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)

# Lượng sản phẩm trung bình bán ra trong tháng
df_monthly_sales['Quantity'].mean()


# ------------------------- DOANH THU TRUNG BÌNH TRONG MỘT THÁNG -------------------------


# Tạo DataFrame doanh thu trung bình mỗi tháng theo thời gian
df_order_avg = df_retail.groupby('InvoiceYearMonth')['Revenue'].mean().reset_index()

plot_data = [
    go.Bar(
        x=df_order_avg['InvoiceYearMonth'],
        y=df_order_avg['Revenue'],
    )
]

plot_layout = go.Layout(
        xaxis = {'type': 'category'},
        title = 'Monthly Order Average'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.plot(fig)
