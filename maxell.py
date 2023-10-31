import datetime
from datetime import date, timedelta
from datetime import datetime, timedelta
import streamlit as st
import cx_Oracle
import pandas as pd
import numpy as np
import plotly.express as px
import psycopg2
import time
import io
import base64
import random

def pku():
    curr_now = date.today()
    tgh=datetime.now()
    tgh = tgh.strftime("%d-%m-%Y %H:%M:%S")
    tgl_akh = curr_now.strftime("%d.%m.%Y")
    tgl_awl = "01.01.2023"

    moving_text = "Periode Bulan s/d "+tgh
    col1,col2=st.columns([3,1])
    with col1:
       col1.header("Asset Healt Wellness UP Kaltim Teluk")
       col1.write(
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
                animation: moveText 6s linear infinite;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    with col2:
        col2.image('pnpp.png', width=200)


    # Config Maximo -------------------#
    usr = 'review'
    pwd = 'review'
    host= '192.168.3.205'
    port ='1521'
    sid= 'maxprd76_stby'
    tns = cx_Oracle.makedsn(host, port,service_name=sid)
    con=cx_Oracle.connect(user=usr,password=pwd,dsn=tns)


    #SQL -------------------#
    qry=(
        "SELECT "
        "B.WONUM,"
        "B.DESCRIPTION AS DES_WO,"
        "B.ASSETNUM,"
        "A.DESCRIPTION AS DES_ASSET,"
        "B.WORKTYPE,"
        "B.REPORTDATE,"
        "B.ACTSTART,"
        "B.ACTFINISH,"
        "B.STATUS,"
        "A.ISRUNNING AS DT_AST,"
        "B.NEEDDOWNTIME AS DT_WO,"
        "C.NEEDDOWNTIME AS DT_SR "
        "FROM ASSET A,"
        "WORKORDER B," 
        "TICKET C "
        "WHERE A.SITEID='KT' "
        "AND A.SITEID =B.SITEID "
        "AND B.SITEID =C.SITEID "
        "AND A.ASSETNUM =B.ASSETNUM "
        "AND B.ASSETNUM =C.ASSETNUM "
        "AND B.DESCRIPTION =C.DESCRIPTION "
        "AND B.OWNERGROUP NOT IN ('CBMU') "
        "AND B.STATUS NOT IN ('CLOSE','COMP') " 
        "AND B.WONUM LIKE 'WO%' "
        "AND B.WORKTYPE IN ('CM','EM','PAM','PDM') "
        "AND B.REPORTDATE >= TO_DATE("+"'"+tgl_awl+"'"+",'dd.mm.yyyy') " 
        "AND B.REPORTDATE <= TO_DATE("+"'"+tgl_akh+"'"+",'dd.mm.yyyy') ORDER BY B.REPORTDATE ASC"
        );

    #Running Fetching -------------------#
    df = pd.read_sql_query(qry,con)

    #Alogaritma Downtime -------------------#
    cd1=(df['DT_AST']==0)&(df['DT_SR']==0)&(df['DT_WO']==0)
    cdx=(df['DT_AST']==0)&(df['DT_SR']==0)&(df['DT_WO']==1)
    cd3=(df['DT_AST']==0)&(df['DT_SR']==1)&(df['DT_WO']==0)
    cd4=(df['DT_AST']==0)&(df['DT_SR']==1)&(df['DT_WO']==1)
    cd5=(df['DT_AST']==1)&(df['DT_SR']==0)&(df['DT_WO']==0)
    cd6=(df['DT_AST']==1)&(df['DT_SR']==0)&(df['DT_WO']==1)
    cd7=(df['DT_AST']==1)&(df['DT_SR']==1)&(df['DT_WO']==0)
    cd8=(df['DT_AST']==1)&(df['DT_SR']==1)&(df['DT_WO']==1)
    values = [1,1,1,0,1,1,1,0]
    df['ISRUNNING'] = np.select([cd1,cdx,cd3,cd4,cd5,cd6,cd7,cd8], values)
    


    #Inisiasi -------------------#
    df['UNIT'] = df['ASSETNUM'].str.slice(6, 8)
    conditions = [
        (df['UNIT'] =="00"),
        (df['UNIT'] =="10")
    ]
    values = ['Common', 'Unit #1']
    df['UNIT'] = np.select(conditions, values, default='Unit #2')

    #Add Condition -------------------#
    normal=(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==1)
    alarm=(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==0)
    values = ['Normal', 'Alarm']

    df['CONDITION'] = np.select([normal, alarm], values,'Fault')

    def apply_color(val):
        if val == 'Normal':
            color = 'background-color: green'
        elif val == 'Alarm':
            color = 'background-color: yellow'
        elif val == 'Fault':
            color = 'background-color: red'
        else:
            color = ''
        return color

    # ds = df.style.applymap(apply_color, subset=['CONDITION'])
    # st.write(ds['CONDITION'])
    

    #Normal Not WO CM DT 0 -------------------#
    #================================================#
    #Unit 1 -------------------#
    normal_u1=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==1)&(df['UNIT']=="Unit #1")]
    normal_u1=len(normal_u1)

    #Unit 2 -------------------#
    normal_u2=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==1)&(df['UNIT']=="Unit #2")]
    normal_u2=len(normal_u2)

    #Common -------------------#
    normal_cm=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==1)&(df['UNIT']=="Common")]
    normal_cm=len(normal_cm)

    #================================================#

    #Alarm Not WO CM DT 1 -------------------#
    #Unit 1 -------------------#
    #================================================#
    alarm_u1=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Unit #1")]
    alarm_u1=len(alarm_u1)

    #Unit 2 -------------------#
    alarm_u2=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Unit #2")]
    alarm_u2=len(alarm_u2)

    #Common -------------------#
    alarm_cm=df[(df['WORKTYPE'].isin(['CM','PAM','PDM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Common")]
    alarm_cm=len(alarm_cm)

    #================================================#

    #Emergency Not WO CM DT 1 -------------------#
    #Unit 1 -------------------#
    #================================================#
    fault_u1=df[(df['WORKTYPE'].isin(['EM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Unit #1")]
    fault_u1=len(fault_u1)

    #Unit 2 -------------------#
    fault_u2=df[(df['WORKTYPE'].isin(['EM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Unit #2")]
    fault_u2=len(fault_u2)

    #Common -------------------#
    fault_cm=df[(df['WORKTYPE'].isin(['EM']))&(df['ISRUNNING']==0)&(df['UNIT']=="Common")]
    fault_cm=len(fault_cm)

    #================================================#
    un1=df[df['UNIT']=="Unit #1"]
    un1=un1[['WONUM','DES_WO','ASSETNUM','WORKTYPE','REPORTDATE','ACTSTART','ACTFINISH','STATUS','CONDITION']]
    un2=df[df['UNIT']=="Unit #2"]
    un2=un2[['WONUM','DES_WO','ASSETNUM','WORKTYPE','REPORTDATE','ACTSTART','ACTFINISH','STATUS','CONDITION']]
    comn=df[df['UNIT']=="Common"]
    comn=comn[['WONUM','DES_WO','ASSETNUM','WORKTYPE','REPORTDATE','ACTSTART','ACTFINISH','STATUS','CONDITION']]
    al=df[['WONUM','DES_WO','ASSETNUM','WORKTYPE','REPORTDATE','ACTSTART','ACTFINISH','STATUS','CONDITION']]


    wty1=df[(df['WORKTYPE'].isin(['CM','PAM','PDM','EM'])&(df['UNIT']=="Unit #1"))]
    wtya1=wty1['WORKTYPE'].value_counts()
    wtyb1=wty1['STATUS'].value_counts()
    wtyc1=wty1['CONDITION'].value_counts()
    
    wty2=df[(df['WORKTYPE'].isin(['CM','PAM','PDM','EM'])&(df['UNIT']=="Unit #2"))]
    wtya2=wty2['WORKTYPE'].value_counts()
    wtyb2=wty2['STATUS'].value_counts()
    wtyc2=wty2['CONDITION'].value_counts()
    
    wty3=df[(df['WORKTYPE'].isin(['CM','PAM','PDM','EM'])&(df['UNIT']=="Common"))]
    wtya3=wty3['WORKTYPE'].value_counts()
    wtyb3=wty3['STATUS'].value_counts()
    wtyc3=wty3['CONDITION'].value_counts()

    wty4=df[(df['WORKTYPE'].isin(['CM','PAM','PDM','EM']))]
    wtya4=wty4['WORKTYPE'].value_counts()
    wtyb4=wty4['STATUS'].value_counts()
    wtyc4=wty4['CONDITION'].value_counts()
    #================================================#

    #Pie Unit --------------------#
    tab1,tab2,tab3,tab4= st.tabs(["🏭 Unit 1","🏭 Unit 2","🏭 Common","🏭 ALL"])
    l=0.20
    t=0.40
    #Unit 1 --------------------#
    labels = ['Normal', 'Alarm', 'Fault']
    sizes = [normal_u1, alarm_u1, fault_u1]
    warna = ['green', 'yellow', 'red']
    fig = px.pie(names=labels, values=sizes, title="Unit #1")
    fig.update_traces(marker=dict(colors=warna))
    fig.update_layout(title_text='Unit #1', title_x=t)
    fig.update_layout(legend=dict(orientation='h', y=0.0, x=l))
    with tab1:
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            col1.plotly_chart(fig,use_container_width=True)
        with col2:
            col2.dataframe(wtyb1,use_container_width=True)
        with col3:
            col3.dataframe(wtya1,use_container_width=True)
            col3.dataframe(wtyc1,use_container_width=True)
        tab1.dataframe(un1,use_container_width=True)

    #Unit 2 --------------------#
    labels = ['Normal', 'Alarm', 'Fault']
    sizes = [normal_u2, alarm_u2, fault_u2]
    warna = ['green', 'yellow', 'red']
    fig = px.pie(names=labels, values=sizes, title="Unit #2")
    fig.update_traces(marker=dict(colors=warna))
    fig.update_layout(title_text='Unit #2', title_x=t)
    fig.update_layout(legend=dict(orientation='h', y=0, x=l))

    with tab2:
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            col1.plotly_chart(fig,use_container_width=True)
        with col2:
            col2.dataframe(wtyb2,use_container_width=True)
        with col3:
            col3.dataframe(wtya2,use_container_width=True)
            col3.dataframe(wtyc2,use_container_width=True)
        tab2.dataframe(un2,use_container_width=True)

    #Common --------------------#
    labels = ['Normal', 'Alarm', 'Fault']
    sizes = [normal_cm, alarm_cm, fault_cm]
    warna = ['green', 'yellow', 'red']
    fig = px.pie(names=labels, values=sizes, title="Common")
    fig.update_traces(marker=dict(colors=warna))
    fig.update_layout(title_text='Common', title_x=t)
    fig.update_layout(legend=dict(orientation='h', y=0.0, x=l))

    with tab3:
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            col1.plotly_chart(fig,use_container_width=True)
        with col2:
            col2.dataframe(wtyb3,use_container_width=True)
        with col3:
            col3.dataframe(wtya3,use_container_width=True)
            col3.dataframe(wtyc3,use_container_width=True)
        tab3.dataframe(comn,use_container_width=True)


    #All --------------------#
    normal=normal_u1+normal_u2+normal_cm
    alarm=alarm_u1+alarm_u2+alarm_cm
    fault=fault_u1+fault_u2+fault_cm
    labels = ['Normal', 'Alarm', 'Fault']
    sizes = [normal, alarm, fault]
    warna = ['green', 'yellow', 'red']
    fig = px.pie(names=labels, values=sizes, title="All")
    fig.update_traces(marker=dict(colors=warna))
    fig.update_layout(title_text='All', title_x=t)
    fig.update_layout(legend=dict(orientation='h', y=0, x=l))

    with tab4:
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            col1.plotly_chart(fig,use_container_width=True)
        with col2:
            col2.dataframe(wtyb4,use_container_width=True)
        with col3:
            col3.dataframe(wtya4,use_container_width=True)
            col3.dataframe(wtyc4,use_container_width=True)
        tab4.dataframe(al,use_container_width=True)

    con.close()
def po():
    curr_now = date.today()
    tgh=datetime.now()
    tgh = tgh.strftime("%d-%m-%Y %H:%M:%S")
    tgl_akh = curr_now.strftime("%Y%m%d")
    tgl_awl = "20220101"

    moving_text = "Periode Bulan s/d "+tgh
    col1,col2=st.columns([3,1])
    with col1:
       col1.header("Reffrensi Harga")
       col1.write(
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
                animation: moveText 6s linear infinite;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    with col2:
        col2.image('pnpp.png', width=200)
    
    Kode_Distrik=st.text_input("Unit","")


    # Config Maximo -------------------#
    usr = 'ellview'
    pwd = 'PJBb3gr3@t'
    host= '192.168.3.205'
    port ='1521'
    sid= 'ellprd'
    tns = cx_Oracle.makedsn(host, port,sid=sid)
    con = cx_Oracle.connect(user=usr,password=pwd,dsn=tns)


    

    #SQL -------------------#

    qry = f"""
    SELECT 
        a.DSTRCT_CODE,
        a.PO_NO,
        a.PREQ_STK_CODE AS STOCK_CODE,
        d.ITEM_DESCX1 AS DESCRIPTION,
        b.CREATION_DATE AS TANGGAL_BUAT,
        a.DUE_SITE_DATE AS DUE_DATE,
        a.CURR_QTY_I AS QTY,
        a.CURR_NET_PR_I AS HARGA,
        c.SUPPLIER_NAME
    FROM
        ELLIPSE.MSF221 a,
        ELLIPSE.MSF231 d,
        ELLIPSE.MSF200 c,
        ELLIPSE.MSF220 b
    WHERE 
        b.PO_NO = a.PO_NO  
        AND c.SUPPLIER_NO = d.SUPPLIER_NO
        AND d.PO_ITEM_NO = a.PO_ITEM_NO 
        AND d.PO_NO = a.PO_NO
        AND a.DSTRCT_CODE ='{Kode_Distrik}'  
        AND a.PO_ITEM_TYPE = 'P'
        AND b.CREATION_DATE >= '{tgl_awl}' 
        AND b.CREATION_DATE <= '{tgl_akh}' 
    ORDER BY b.CREATION_DATE ASC
    """


    #Running Fetching -------------------#
    data = pd.read_sql_query(qry,con)
    st.dataframe(data,use_container_width=True)

    def download_excel(data):
        name=Kode_Distrik+"_reff_"+tgl_akh+".xlsx"
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, sheet_name='Sheet1', index=False)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{name}">Unduh Excel</a>'
        return href
    st.write(download_excel(data), unsafe_allow_html=True)
    con.close()
def rlt():
    tyu = st.sidebar.selectbox('Unit', ('Unit #1','Unit #2'))
    col1,col2=st.columns([3,1])
    with col1:
       col1.header("Real Time UP Kaltim Teluk "+tyu)
    with col2:
        col2.image('pnpp.png', width=200)
    placeholder_1=st.empty()
    placeholder_2=st.empty()
    ct = datetime.now()
    j = 0
    l=0
    v2 = 0  # Inisialisasi v2
    df = pd.DataFrame(columns=["date_rec", "value"])
    if st.sidebar.button("Run Time"):
        while True:
            if tyu == "Unit #1":
                conn=psycopg2.connect(user="opc",password="opc12345",host="10.7.19.140",port="5432",database="opc")
                sql= conn.cursor()
                with placeholder_1.container():
                    saiki = datetime.now()
                    saiki = saiki.strftime("%d-%m-%Y %H:%M:%S")
                    st.markdown("Date "+saiki)
                    A1,A2,A3,A4,A5,A6 = st.columns([1,1,1,1,1,1.5])
                    #Beban ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2) as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.AI.10MKA01CE004'
                    """

                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A1.metric(label="Load", value=dx +" MW")
                    conn.commit()

                    #VP ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.AI.T1AIVACUUM'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A2.metric(label="Vacuum Pump", value=dx +" kPa")
                    conn.commit()

                    #VP Entering ------------#

                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.AI.10MAA01CP113'
                    """

                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A3.metric(label="VP Entering", value=dx +" kPa")
                    conn.commit()

                    #MSP ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.AI.T1AITP1'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A4.metric(label="Main Steam Pressure", value=dx +" MPa")
                    conn.commit()

                    #MST ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.TC.10LBA10CT103'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A5.metric(label="Main Steam Temperature", value=dx +" ˚C")


                    #speed ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM1.SIGNAL.AI.10MAD10CS101'
                    """
                    
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    A6.metric(label="Speed", value=dx+"Rpm")
                    conn.commit()

                    #pac ------------#
                    col1,col2=st.columns([2,1])
                    up=13.2
                    with col1:
                        if j==0:
                            qry="""
                            select
                            date_rec,
                            round((value + ((random()/10) - 0.05))::numeric, 2) as value
                            from current
                            where address_no='KALTIM1.SIGNAL.AI.10HHL02CP101'
                            """
                            df_db = pd.read_sql_query(qry, conn)
                            new_time = datetime.now()
                            new_time=new_time.strftime('%Y-%m-%d %H:%M:%S')
                            nilai_baru = new_time
                            df_db.at[0, 'date_rec'] = nilai_baru
                            v1 = df_db['value'].iloc[-1]
                            v2 = v1 - 0.05
                            df = df.append(df_db, ignore_index=True)
                            j = 1
                            

                     
                        current_time = datetime.now()
                        new_row = {
                            'date_rec': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'value': round((random.uniform(v2,v1) + ((random.random()/10) - 0.05)), 2)
                        }
                        df = df.append(new_row, ignore_index=True)  # Menambahkan baris baru
                        if l==0:
                            df = df.drop(1)
                            l=1
                        if current_time.minute != ct.minute:
                            ct = datetime.now()
                            df = df.iloc[1:]
                            j=0
                            l=0
                            
                            
                                   
                        fig = px.line(df, x='date_rec', y='value', title='PAC Trending')
                        fig.add_hline(y=up, line_dash="dash", line_color="red", annotation_text="Threshold")
                        st.plotly_chart(fig,use_container_width=True)
                    with col2:
                        last_row = df['value'].iloc[-1]
                        if last_row>=up:
                            alrm=f"""
                            WARNING !! Saat ini nilai PAC {last_row}
                            KPa Lakukan Action Plan & Manuver Operasi sesuai dengan 
                            IK Drain Bed Material no IKKT-306-14.2.1.1-137
                            """
                            st.info(alrm)
                        else:
                            alrm=f"""
                            NORMAL!! Saat ini nilai PAC {last_row}
                            KPa
                            """
                            st.info(alrm)
                    conn.close()
                    time.sleep(0.88)
                pass
            if tyu == "Unit #2":
                conn=psycopg2.connect(user="opc",password="opc12345",host="10.7.19.140",port="5432",database="opc")
                sql=conn.cursor()
                with placeholder_2.container():
                    saiki = datetime.now()
                    saiki = saiki.strftime("%d-%m-%Y %H:%M:%S")
                    st.markdown("Date "+saiki)
                    B1,B2,B3,B4,B5,B6 = st.columns([1,1,1,1,1,1.5])
                    #Beban ------------#
                    qry="""
                    select 
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current
                    where address_no = 'KALTIM2.SIGNAL.AI.20MKA01CE004'
                    """

                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B1.metric(label="Load", value=dx +" MW")
                    conn.commit()

                    #VP ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM2.SIGNAL.AI.U2T1AIVACUUM'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B2.metric(label="Vacuum Pump", value=dx +" kPa")
                    conn.commit()

                    #VP Entering ------------#

                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM2.SIGNAL.AI.20MAA01CP113'
                    """

                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B3.metric(label="VP Entering", value=dx +" kPa")
                    conn.commit()

                    #MSP ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM2.SIGNAL.AI.U2T1AITP1'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B4.metric(label="Main Steam Pressure", value=dx +" MPa")
                    conn.commit()

                    #MST ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM2.SIGNAL.TC.20LBA10CT103'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B5.metric(label="Main Steam Temperature", value=dx +" ˚C")


                    #MSF ------------#
                    qry="""
                    select
                    round((value + ((random()/10) - 0.05))::numeric, 2)  as value
                    from current 
                    where address_no='KALTIM2.SIGNAL.AI.20MAD10CS101'
                    """
                    dx = sql.execute(qry)
                    dx = sql.fetchall()
                    dx = str(dx).replace("(Decimal","")
                    dx = str(dx).replace("(","")
                    dx = str(dx).replace(")","")
                    dx = str(dx).replace(",,"," |")
                    dx = str(dx).replace("'","")
                    dx = str(dx).replace("[","")
                    dx = str(dx).replace(",]","")
                    B6.metric(label="Speed", value=dx+" Rpm")
                    #pac ------------#
                    col1,col2=st.columns([2,1])
                    up=13.2
                    with col1:
                        if j==0:
                            qry="""
                            select
                            date_rec,
                            round((value + ((random()/10) - 0.05))::numeric, 2) as value
                            from current
                            where address_no='KALTIM2.SIGNAL.AI.20HHL02CP101'
                            """
                            df_db = pd.read_sql_query(qry, conn)
                            new_time = datetime.now()
                            new_time=new_time.strftime('%Y-%m-%d %H:%M:%S')
                            nilai_baru = new_time
                            df_db.at[0, 'date_rec'] = nilai_baru
                            v1 = df_db['value'].iloc[-1]
                            v2 = v1 - 0.05
                            df = df.append(df_db, ignore_index=True)
                            j = 1
                            

                     
                        current_time = datetime.now()
                        new_row = {
                            'date_rec': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'value': round((random.uniform(v2,v1) + ((random.random()/10) - 0.05)), 2)
                        }
                        df = df.append(new_row, ignore_index=True)  # Menambahkan baris baru
                        if l==0:
                            df = df.drop(1)
                            l=1
                        if current_time.minute != ct.minute:
                            ct = datetime.now()
                            df = df.iloc[1:]
                            j=0
                            l=0

                        fig = px.line(df, x='date_rec', y='value', title='PAC Trending')
                        fig.add_hline(y=up, line_dash="dash", line_color="red", annotation_text="Threshold")
                        st.plotly_chart(fig,use_container_width=True)
                    with col2:
                        last_row = df['value'].iloc[-1]
                        if last_row>=up:
                            alrm=f"""
                            WARNING !! Saat ini nilai PAC {last_row}
                            KPa Lakukan Action Plan & Manuver Operasi sesuai dengan 
                            IK Drain Bed Material no IKKT-306-14.2.1.1-137
                            """
                            st.info(alrm)
                        else:
                            alrm=f"""
                            NORMAL!! Saat ini nilai PAC {last_row}
                            KPa
                            """
                            st.info(alrm)
                    conn.close()
                    time.sleep(0.88)
                pass

if __name__ == "__main__":
    pass



    