import streamlit as st
import pandas as pd

st.set_page_config(page_title="Navegador de Parámetros", layout="wide")

st.title("Explorador de Parámetros")

uploaded_file = st.file_uploader("Sube un archivo Excel", type=["xlsx"])

if uploaded_file:
    dato1 = st.text_input("Ingresa el valor para 'DEVICE':", "DEVICE")
    dato2 = st.text_input("Ingresa el valor para 'DATA_SET':", "DATA_SET")

    xls = pd.ExcelFile(uploaded_file)
    estructura_global = {}

    for hoja in xls.sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=hoja, usecols=[12, 13, 14, 16])
        df.columns = ['LD', 'LN', 'Parameter desc', 'Logical Node Path']
        estructura_hoja = {}
        for _, row in df.iterrows():
            ld = str(row['LD']).strip()
            ln = str(row['LN']).strip()
            param = row['Parameter desc']
            path = str(row['Logical Node Path']).replace("DEVICE", dato1).replace("DATA_SET", dato2)
            if pd.isna(ld) or pd.isna(ln) or pd.isna(param) or pd.isna(path):
                continue
            estructura_hoja.setdefault(ld, {}).setdefault(ln, {})[param] = path
        estructura_global[hoja] = estructura_hoja

    hojas_dict = {hoja: hoja.split('_', 1)[1] if '_' in hoja else hoja for hoja in estructura_global.keys()}
    hoja_opcion = st.selectbox("Selecciona LD (hoja):", options=list(hojas_dict.values()))

    hoja_real = next(k for k, v in hojas_dict.items() if v == hoja_opcion)
    lds = list(estructura_global[hoja_real].keys())
    ld = hoja_opcion if hoja_opcion in lds else lds[0]

    lns = list(estructura_global[hoja_real][ld].keys())
    ln = st.selectbox("Selecciona LN:", options=lns)

    parametros = estructura_global[hoja_real][ld][ln]
    dos = sorted(set(p.split('.')[0] for p in parametros if '.' in p))
    do = st.selectbox("Selecciona DO:", options=dos)

    fc_posibles = sorted(set(v.split('(')[-1].strip(')') for k, v in parametros.items() if k.startswith(do + '.')))
    fc = st.selectbox("Selecciona FC:", options=fc_posibles)

    das = sorted(set(k.split('.')[1] for k, v in parametros.items() if k.startswith(do + '.') and v.endswith(f'({fc})')))
    da = st.selectbox("Selecciona DA (opcional):", options=["(ninguno)"] + das)

    if st.button("Generar valor completo"):
        if da != "(ninguno)":
            key = f"{do}.{da}"
            valor = parametros.get(key, "Valor no encontrado")
        else:
            valor = f"{dato1}.{ld}/LLN0.{dato2}.{ld}.{ln}.{do}({fc})"
        st.success(f"Valor completo asociado:\n{valor}")
