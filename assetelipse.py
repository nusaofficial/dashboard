import datetime
from datetime import date, timedelta
from datetime import datetime, timedelta
import streamlit as st
import cx_Oracle
import pandas as pd
import numpy as np
import plotly.express as px
import base64
import io



def po():
    curr_now = date.today()
    tgh=datetime.now()
    tgh = tgh.strftime("%d-%m-%Y %H:%M:%S")
    tgl_akh = curr_now.strftime("%Y%m%d")
    tgl_awl = "20230101"

       
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
    tnse = cx_Oracle.makedsn(host, port,sid=sid)
    cone = cx_Oracle.connect(user=usr,password=pwd,dsn=tnse)


    

    #SQL -------------------#

    sql = cone.cursor()
    lst=[]
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
    sql.execute(qry)
    lst.extend(sql.fetchall())
    data = pd.DataFrame.from_records(lst, columns=[x[0] for x in sql.description])
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
    cone.close()
        



if __name__ == "__main__":
    pass



    