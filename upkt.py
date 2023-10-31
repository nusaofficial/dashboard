import streamlit as st
import pandas as pd
import psycopg2
from PIL import Image
import plotly.express as px
import plotly.graph_objs as go
import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta
from datetime import date, timedelta
import maxell as mxl
from sklearn.linear_model import LinearRegression
import time

# # CSS Open ------------#
st.set_page_config(layout='wide',initial_sidebar_state='expanded')
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        width: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Mengganti latar belakang dengan gambar
st.markdown(
    """
    <style>
    body {
        background-image: url('nn.png');
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df=pd.read_csv('tagdcs.csv',index_col=0)
conn=psycopg2.connect(user="opc",password="opc12345",host="10.7.19.140",port="5432",database="opc")

with st.sidebar:
    st.image('nn.png', use_column_width=True)
    if 'is_logged_in' not in st.session_state:
        st.session_state.is_logged_in = False
    if not st.session_state.is_logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if username == "NUSA" and password == "PNPupkt":
                st.success("Login berhasil!")
                st.session_state.is_logged_in = True
                # Me-restart aplikasi untuk menampilkan halaman berikutnya
                st.experimental_rerun()
            else:
                st.error("Login gagal. Silakan coba lagi.")

if st.session_state.is_logged_in:
    hed_tpl=True
    with st.sidebar:
        mode = st.selectbox('Mode', ('Data Science','Simplified RLA','Realtime','PKU','Ellipse'))
    if mode=="PKU":
        hed_tpl=False
        if st.sidebar.button("Logout",use_container_width=True):
            st.session_state.is_logged_in = False
            st.experimental_rerun()
        if st.sidebar.button("Update",use_container_width=True):
            st.experimental_rerun()
    elif mode=="Ellipse":
        hed_tpl=False
        if st.sidebar.button("Logout"):
            st.session_state.is_logged_in = False
            st.experimental_rerun()
    elif mode=="Realtime":
        hed_tpl=False
    else:
        if hed_tpl:
            moving_text = "Hallo Selamat Datang di Dashboard NUSA - News Update System Advance"
            st.write(
                f"""
                <div style="color: blue; font-size: 24px;" id="moving-text">
                    {moving_text}
                </div>
                <style>
                    @keyframes moveText {{
                        0% {{ transform: translateX(100%); }}
                        100% {{ transform: translateX(-100%); }}
                    }}

                    #moving-text {{
                        animation: moveText 11s linear infinite;
                    }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            hed_tpl=True
        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.experimental_rerun()
    if mode=="Data Science":
        smb =st.selectbox('Sumbu',('2 Sumbu','Lebih dari 1 Sumbu')) 
        col1, col2 = st.sidebar.columns(2)
        with col1:
            unit = col1.selectbox('Plant', ('Unit 1','Unit 2','Common','All'))
        with col2:
            swt =col2.selectbox('List',('KKS','Deskripsi'))
        if unit=='All':
            tag=df['description'].to_list()
            kks=df['address_no'].to_list()
        else:
            area = df[df['Unit']==unit]
            tag = area['description'].to_list()
            kks =area['address_no'].to_list()
        if swt=='KKS':
            if smb=="Lebih dari 1 Sumbu":
                tag = st.sidebar.multiselect('Deskripsi',kks)
                tag = df.query('address_no in @tag')
                dcs = tag['address_no'].to_list()
            else:
                tag_x = st.sidebar.selectbox('Sumbu 1 ',kks)
                l1=tag_x
                tag_y = st.sidebar.selectbox('Sumbu 2 ',kks)
                l2=tag_y
                tag_x = df.query('address_no in @tag_x')
                tag_y = df.query('address_no in @tag_y')
                dcs_x = tag_x['address_no'].to_list()
                dcs_y = tag_y['address_no'].to_list()
                dcs=dcs_x+dcs_y
                tx = tag_x['description'].to_list()
                ty = tag_y['description'].to_list()
                tgl=['tanggal_penarikan']
                tx=tgl+tx
                ty=tgl+ty
        else:
            if smb=="Lebih dari 1 Sumbu":
                tag = st.sidebar.multiselect('Deskripsi',tag)
                tag = df.query('description in @tag')
                dcs = tag['address_no'].to_list()
            else:
                tag_x = st.sidebar.selectbox('Sumbu 1 ',tag)
                l1=tag_x
                tag_y = st.sidebar.selectbox('Sumbu 2 ',tag)
                l2=tag_y
                tag_x = df.query('description in @tag_x')
                tag_y = df.query('description in @tag_y')
                dcs_x = tag_x['address_no'].to_list()
                dcs_y = tag_y['address_no'].to_list()
                dcs=dcs_x+dcs_y
                tx = tag_x['description'].to_list()
                ty = tag_y['description'].to_list()
                tgl=['tanggal_penarikan']
                tx=tgl+tx
                xt=tx
                ty=tgl+ty
                yt=ty
        dcs = str(dcs).replace("[","").replace("]","")

        wkt=st.sidebar.selectbox('interval',('1m','2m','5m','10m','15m','20m','30m','45m','60m'))
        if wkt=="2m":
            interval="0,2,4,8,10,12,14,18,20,22,24,28,30,32,34,38,40,42,44,48,50,52,54,58"
        elif wkt=="5m":
            interval="0,5,10,15,20,25,30,35,40,45,50,55"
        elif wkt=="10m":
            interval="0,10,20,30,50"
        elif wkt=="15m":
            interval="0,15,30,45"
        elif wkt=="20m":
            interval="0,20,40"
        elif wkt=="30m":
            interval="0,30"
        elif wkt=="45m":
            interval="0,45"
        elif wkt=="60m":
            interval="0,60"
        else:
            interval="0"

        tgl_awal = st.sidebar.date_input('Tanggal Awal')
        tgl_akhir = st.sidebar.date_input('Tanggal Akhir')
        col1, col2 = st.sidebar.columns(2)
        with col1:
            jam_awal = col1.time_input('Jam Awal', step=60)
        with col2:
            jam_akhir = col2.time_input('Jam Akhir',step=60)
        jam_awal =jam_awal.strftime('%H:%M:%S')
        jam_akhir=jam_akhir.strftime('%H:%M:%S')
        if st.sidebar.button('Update'):
            with st.spinner("Loading..."):
                if interval=="0":
                    qry=("select "
                        "a.date_rec as tanggal_penarikan, "
                        "b.address_no, "
                        "b.description, " 
                        "round(a.value,2) as nilai,b.satuan "
                        "from history a, address b "
                        "where a.address_no in ("+dcs+") "
                        "and a.address_no=b.address_no "
                        "and a.date_rec>='"+str(tgl_awal)+" "+jam_awal+"' "
                        "and a.date_rec<='"+str(tgl_akhir)+" "+jam_akhir+"' " )
                else:
                    qry=("select "
                        "a.date_rec as tanggal_penarikan, "
                        "b.address_no, "
                        "b.description, " 
                        "round(a.value,2) as nilai,b.satuan "
                        "from history a, address b "
                        "where a.address_no in ("+dcs+") "
                        "and a.address_no=b.address_no "
                        "and a.date_rec>='"+str(tgl_awal)+" "+jam_awal+"' "
                        "and a.date_rec<='"+str(tgl_akhir)+" "+jam_akhir+"' " 
                        "and extract (minute from a.date_rec) in ("+interval+") order by a.date_rec")
                dx = pd.read_sql_query(qry,conn)
                data_pvt = dx.pivot_table(index='tanggal_penarikan', columns='description', values='nilai', aggfunc='mean')
                data= data_pvt.reset_index()
                if smb=='2 Sumbu':
                    data_x=data[tx]
                    data_y=data[ty]
                traces = []
                if smb=="Lebih dari 1 Sumbu":
                    tab1, tab2,tab3= st.tabs(["📈 Chart", "🗃 Excel","🧮Corelation Data"])
                else:
                    tab1, tab2,tab3= st.tabs(["📈 Chart", "🗃 Excel","📈 Linear Regression"])

                if smb=="Lebih dari 1 Sumbu":
                    for column in data.columns[1:]:
                        trace = go.Scatter(x=data['tanggal_penarikan'], y=data[column], mode='lines', name=column)
                        traces.append(trace)

                    layout = go.Layout(
                    title="Trending "+unit+" Tanggal Per "+str(tgl_awal),
                    xaxis=dict(title='Tanggal Penarikan'),
                    yaxis=dict(title='Nilai Y1'),
                    legend=dict(x=1) 
                    )

                    layout['width'] = 1000

                    fig = go.Figure(data=traces, layout=layout)
                    tab1.plotly_chart(fig,use_container_width=True)
                else:
                    from plotly.subplots import make_subplots
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    for column in data_x.columns[1:]:
                        fig.add_trace(go.Scatter(x=data_x['tanggal_penarikan'], y=data_x[column], name=column, mode='lines'))
                
                    
                    for column in data_y.columns[1:]:
                        fig.add_trace(go.Scatter(x=data_y['tanggal_penarikan'], y=data_y[column], name=column, mode='lines+markers'), secondary_y=True)

                    fig.update_layout(
                    yaxis=dict(title='Y1 Axis'),
                    yaxis2=dict(title='Y2 Axis', overlaying='y', side='right'))
                    fig.update_layout(title="Trending "+unit+" Tanggal Per "+str(tgl_awal))
                    tab1.plotly_chart(fig,use_container_width=True)

                
                lencl = len(data_pvt.columns)
                plt.figure(figsize=(16,5+(.9*lencl)), dpi=200)
                for i,c in enumerate(data_pvt.columns):
                    plt.subplot((lencl+1) // 2, min(lencl,3), i+1)
                    plt.plot(data_pvt[c])
                    plt.title(c)
                    plt.xticks(rotation=45)
                plt.suptitle("Trending "+unit+" Tanggal Per "+str(tgl_awal), y=1, fontsize=20)
                plt.tight_layout()
                tab1.pyplot(plt)

                if smb=='2 Sumbu': 


                    X = data[l1].values
                    y = data[l2].values


                    # Ubah bentuk array X menjadi matriks 2D
                    X = X.reshape(-1, 1)

                    # Membuat model regresi linear
                    model = LinearRegression()

                    # Melatih model pada data
                    model.fit(X, y)

                    # Melakukan prediksi menggunakan model
                    y_pred = model.predict(X)
                    tab3.write(y_pred)

                    # print("Koefisien Regresi (m):", model.coef_[0])
                    # print("Intersep (b):", model.intercept_)

                    plt.scatter(X, y, label="Data Asli")
                    plt.plot(X, y_pred, color='red', label="Regresi Linear")
                    plt.xlabel("Kolom_X")
                    plt.ylabel("Kolom_Y")
                    tab3.write(plt)
            
                tab2.dataframe(data_pvt)
                tab2.write(data.describe().T)

                if smb=="Lebih dari 1 Sumbu":
                    corr_matrix = data.corr()
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=.5)
                    tab3.pyplot(plt)

                def download_excel(data):
                    name="Trending "+unit+" Tanggal Per "+str(tgl_awal)+str(jam_awal)+".xlsx"
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        data.to_excel(writer, sheet_name='Sheet1', index=False)
                    b64 = base64.b64encode(output.getvalue()).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{name}">Unduh Excel</a>'
                    return href
                tab2.write(download_excel(data), unsafe_allow_html=True)
    elif mode=="Simplified RLA":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            unit = col1.selectbox('Plant', ('Unit 1','Unit 2','Common','All'))
        with col2:
            swt =col2.selectbox('List',('KKS','Deskripsi'))
        if unit=='All':
            tag=df['description'].to_list()
            kks=df['address_no'].to_list()
        else:
            area = df[df['Unit']==unit]
            tag = area['description'].to_list()
            kks =area['address_no'].to_list()

        if swt=='KKS':
            tag = st.sidebar.multiselect('Deskripsi',kks)
            tag = df.query('address_no in @tag')
            dcs = tag['address_no'].to_list()
        else:
            tag = st.sidebar.multiselect('Deskripsi',tag)
            tag = df.query('description in @tag')
            dcs = tag['address_no'].to_list()
        if unit=="Unit 1":
            dcsx=['KALTIM1.SIGNAL.AI.10MKA01CE004']
            dcs=dcsx+dcs
        if unit=="Unit 2":
            dcsx=['KALTIM2.SIGNAL.AI.20MKA01CE004']
            dcs=dcsx+dcs
        dcs = str(dcs).replace("[","").replace("]","")

        
        if unit=="Common":
            wkt=st.sidebar.selectbox('Interval',('1m','2m','5m','10m','15m','20m','30m','45m','60m'))
        elif unit=="All":
            wkt=st.sidebar.selectbox('Interval',('1m','2m','5m','10m','15m','20m','30m','45m','60m'))
        else:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                wkt=col1.selectbox('Interval',('1m','2m','5m','10m','15m','20m','30m','45m','60m'))
            with col2:
                ld=col2.text_input("Filter Beban","")
                ld=str(ld)
        if wkt=="2m":
            interval="0,2,4,8,10,12,14,18,20,22,24,28,30,32,34,38,40,42,44,48,50,52,54,58"
        elif wkt=="5m":
            interval="0,5,10,15,20,25,30,35,40,45,50,55"
        elif wkt=="10m":
            interval="0,10,20,30,50"
        elif wkt=="15m":
            interval="0,15,30,45"
        elif wkt=="20m":
            interval="0,20,40"
        elif wkt=="30m":
            interval="0,30"
        elif wkt=="45m":
            interval="0,45"
        elif wkt=="60m":
            interval="0,60"
        else:
            interval="0" 
        tgl_awal = st.sidebar.date_input('Tanggal Awal')
        tgl_akhir = st.sidebar.date_input('Tanggal Akhir')
        col1, col2 = st.sidebar.columns(2)
        with col1:
            jam_awal = col1.time_input('Jam Awal', step=60)
        with col2:
            jam_akhir = col2.time_input('Jam Akhir',step=60)
        jam_awal =jam_awal.strftime('%H:%M:%S')
        jam_akhir=jam_akhir.strftime('%H:%M:%S')

        if st.sidebar.button('Update'):
            with st.spinner("Loading..."):
                if interval=="0":
                    qry=("select "
                        "a.date_rec as tanggal_penarikan, "
                        "b.address_no, "
                        "b.description, " 
                        "round(a.value,2) as nilai,b.satuan "
                        "from history a, address b "
                        "where a.address_no in ("+dcs+") "
                        "and a.address_no=b.address_no "
                        "and a.date_rec>='"+str(tgl_awal)+" "+jam_awal+"' "
                        "and a.date_rec<='"+str(tgl_akhir)+" "+jam_akhir+"' " )
                else:
                    qry=("select "
                        "a.date_rec as tanggal_penarikan, "
                        "b.address_no, "
                        "b.description, " 
                        "round(a.value,2) as nilai,b.satuan "
                        "from history a, address b "
                        "where a.address_no in ("+dcs+") "
                        "and a.address_no=b.address_no "
                        "and a.date_rec>='"+str(tgl_awal)+" "+jam_awal+"' "
                        "and a.date_rec<='"+str(tgl_akhir)+" "+jam_akhir+"' " 
                        "and extract (minute from a.date_rec) in ("+interval+") order by a.date_rec")
                dx = pd.read_sql_query(qry,conn)
                data_pvt = dx.pivot_table(index='tanggal_penarikan', columns='description', values='nilai', aggfunc='mean')
                ld=float(ld)
                if unit=="Common":
                    data= data_pvt
                elif unit=="All":
                    data= data_pvt
                else:
                    if ld==0:
                        data= data_pvt
                    else:
                        if unit=="Unit 1":
                            data= data_pvt
                            data= data[(data['Unit #1 - #1 Gen. Active Power']>=ld)]
                            data= data.drop(["Unit #1 - #1 Gen. Active Power"], axis=1)
                        elif unit=="Unit 2":
                            data= data_pvt
                            data= data[(data['Unit #2 - #2 Gen. Active Power']>=ld)]
                            data= data.drop(["Unit #2 - #2 Gen. Active Power"], axis=1)
                
                # Outlier

                calc=data.describe()

                #Normalized for Calc DataScient
                column_maxes = data.max()
                df_max = column_maxes.max()
                column_mins = data.min()
                df_min = column_mins.min()
                normalized= (data - df_min) / (df_max - df_min)

                #Anomali Detection
                q1=calc.iloc[4]
                q3=calc.iloc[6]
                iqr=q3-q1
                lo=round((q1-(1.5*iqr)),2)
                up=round((q3+(1.5*iqr)),2)

                #Count Lower Upper 
                ct_lo=data<lo
                ct_up=data>up
                ctlo=ct_lo[ct_lo==True].count(axis=0)
                ctup=ct_up[ct_up==True].count(axis=0)
                cc=data.shape[0]
                prlo=round(((ctlo/cc)*100),1)
                prup=round(((ctup/cc)*100),1)


                #Result String Lower Upper 
                slo=ctlo.astype(str)+' Lbound Outlier'
                sup=ctup.astype(str)+' Ubound Outlier'
                sprlo=prlo.astype(str)+'%'
                sprup=prup.astype(str)+'%'
                result_lo= pd.concat([slo,sprlo], axis=1)
                result_up= pd.concat([sup,sprup], axis=1)
                result_lo['Outlier'] = result_lo[0]
                result_lo.drop(0, axis=1,inplace=True)
                result_lo['Outlier %'] = result_lo[1]
                result_lo.drop(1, axis=1,inplace=True)
                result_up['Outlier'] = result_up[0]
                result_up.drop(0, axis=1,inplace=True)
                result_up['Outlier %'] = result_up[1]
                result_up.drop(1, axis=1,inplace=True)



                lencl = len(data.columns)
                plt.figure(figsize=(16,5+(.9*lencl)), dpi=200)
                for i,c in enumerate(data.columns):
                    plt.subplot((lencl+1) // 2, min(lencl,3), i+1)
                    plt.plot(data[c],'.',c='k')
                    plt.axhline(up.iloc[i],color='r',linewidth=1,label='Upper Bound',linestyle='--')
                    plt.axhline(lo.iloc[i],color='b',linewidth=1,label='Lower Bound',linestyle='--')
                    plt.title(c)
                    plt.xticks(rotation=45)
                    plt.legend()
                plt.suptitle("Outlier Simplified RLA "+unit+" Tanggal Per "+str(tgl_awal), y=1, fontsize=20)
                plt.tight_layout()
                st.pyplot(plt)
                #Resume
                col1,col2=st.columns(2)
                with col1:
                    st.write("---- Result Anomali Outlier Lower Bound Raw RLA "+unit+" -----",result_lo)
                with col2:
                    st.write("---- Result Anomali Outlier Upper Bound Raw RLA "+unit+" -----",result_up)            
    elif mode=="PKU":
        if __name__ == "__main__":
            pass
        mxl.pku()
    elif mode=="Realtime":
        if __name__ == "__main__":
            pass
        mxl.rlt()    
    else:
        if __name__ == "__main__":
            pass
        mxl.po()
        
        



conn.close()
