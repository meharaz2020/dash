import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=34.126.156.95;DATABASE=bdjResumes;UID=buMeharaz;PWD=86Yj?ib49')


query1 = '''
;WIth mainCTE as(
select o.P_ID,u.accFirstName+' '+u.accLastName as name ,u.accPhone,pr.SEX,
CONCAT(DATEDIFF(year, pr.BIRTH, GETDATE()), '.', DATEDIFF(month, pr.BIRTH, GETDATE()) % 12) as age
,FORMAT(TransDate, 'dd MMM yyyy')  as [Purchase Date]
,Paidby as [Payment Method],TransStatus as [Payment Status],PaidAmount as Price ,p.pkName as [Package Name]
,CONCAT(us.TExp / 12, '.', us.TExp % 12)  AS Exp, CASE WHEN RedeemPoints > 0 THEN 1 ELSE 0 END IsPointRedeem 
, CASE WHEN RedeemPoints > 0 THEN RedeemAmount ELSE 0 END RedeemAmount , CASE WHEN RedeemPoints > 0 THEN RedeemPoints ELSE 0 END RedeemPoints 
from OnlinePaymentInfoJS o
inner join UserAccounts u on o.p_id=u.accID 
inner join mnt.Packages p on o.ServiceID=p.ServiceID
LEFT JOIN bdjResumes.dbo.PERSONAL pr ON o.P_ID = pr.ID
LEFT JOIN bdjResumes.[dbo].[UserSummary] us ON o.P_ID = us.P_ID
where  o.TransDate>='11/29/2023 20:00:00' and o.ServiceID in (87,88,89)

)
SELECT distinct m.P_ID,M.name,M.accPhone,m.Exp,m.SEX,m.age,m.[Purchase Date],M.[Package Name],
    CONVERT(VARCHAR(12), DATEADD(MONTH, u.cpkDuration, u.cpkStartDate), 106) AS [Package End Date]
	,m.[Payment Method],m.[Payment Status],m.Price, m.IsPointRedeem, m.RedeemAmount, m.RedeemPoints--, u.cpkDuration as Packageduration
FROM mainCTE m
LEFT JOIN mnt.CandidatePackages u ON m.P_ID = u.P_ID
order by m.p_id
'''



df = pd.read_sql_query(query1, conn)

df = pd.DataFrame(df)

# Calculating grouped data for the pie charts
grouped_df = df.groupby('Payment Status')['SEX'].value_counts().reset_index(name='Count')
amount_per_package = df.groupby('Package Name')['Price'].sum().reset_index()

# Initializing the Dash app
app = dash.Dash(__name__)
server = app.server
# Creating layout for the dashboard
app.layout = html.Div([
    html.H1("Dashboard"),
    
    html.Div([
        dcc.Graph(figure=px.pie(amount_per_package, values='Price', names='Package Name', title='Total Amount per Package Name'))
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(figure=px.pie(grouped_df, values='Count', names='SEX', title='Total F/M per Payment Status'))
    ], style={'width': '30%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(figure=px.bar(grouped_df, x='Payment Status', y='Count', color='SEX',
                                 title='Payment Type Wise Gender Distribution',
                                 labels={'Payment Status': 'Payment Type', 'Count': 'Count of Gender'}))
    ], style={'width': '40%', 'display': 'inline-block'})
])

# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
