import streamlit as st
import pandas as pd
import os
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
st.set_page_config(page_title="PRESUPUESTOS", page_icon="⭐", layout="wide")

# =============================================================================
# ESTILOS PERSONALIZADOS
# =============================================================================
def cargar_estilos():
    st.markdown("""
        <style>
        body {
            background-color: #f5f5f5;
            font-family: 'Arial', sans-serif;
        }
        .header {
            background-color: #D50000;
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
        .subtitulo {
            color: #333;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        /* Estilos para la tabla personalizada */
        .tabla-container {
            border: 3px solid #b30000;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .tabla-personalizada {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            font-size: 13px;
        }
        .tabla-personalizada th {
            background-color: #b30000;
            color: white;
            font-weight: bold;
            padding: 8px 6px;
            text-align: center;
            border: 2px solid #8b0000;
            font-size: 13px;
            line-height: 1.2;
        }
        .tabla-personalizada td {
            padding: 6px 4px;
            text-align: center;
            border: 2px solid #ddd;
            line-height: 1.2;
        }
        .tabla-personalizada tr:nth-child(even):not(.fila-total) {
            background-color: #f9f9f9;
        }
        .tabla-personalizada tr:nth-child(odd):not(.fila-total) {
            background-color: white;
        }
        .tabla-personalizada tr:hover:not(.fila-total) {
            background-color: #f0f0f0;
            transition: background-color 0.3s;
        }
        .fila-total {
            background-color: #ff6b6b !important;
            font-weight: bold;
            color: #000;
            font-size: 13px;
        }
        .fila-total-final {
            background-color: #4CAF50 !important;
            font-weight: bold;
            color: white;
            font-size: 14px;
        }
        .fila-total-general {
            background-color: #2196F3 !important;
            font-weight: bold;
            color: white;
            font-size: 15px;
        }
        .encabezado-fila {
            background-color: #b30000;
            color: white;
            font-weight: bold;
            text-align: left;
            border: 2px solid #8b0000;
            padding: 6px 8px !important;
            line-height: 1.2;
        }
        .numero {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 12px;
        }
        .titulo-tabla {
            color: #b30000;
            text-align: center;
            margin: 20px 0 10px 0;
            font-size: 20px;
            font-weight: bold;
        }
        .boton-menu {
            background-color: #D50000;
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            width: 100%;
            margin: 15px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .boton-menu:hover {
            background-color: #b30000;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }
        .contenedor-botones {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 20px 0;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .pantalla-inicial {
            text-align: center;
            padding: 10px;
        }
        .boton-volver {
            background-color: #666;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .boton-volver:hover {
            background-color: #555;
        }
        .contenedor-logos {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .logo {
            max-width: 250px;
            height: auto;
        }
        .selector-mes {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #D50000;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)

# =============================================================================
# CACHÉ PARA OPTIMIZACIÓN
# =============================================================================

url = "https://docs.google.com/spreadsheets/d/1QyaYcqSY_j1qn4sBPgEauSFN90eMTcxoMKF7vqRMy-0/edit?usp=sharing"

@st.cache_data(ttl=600)

def cargar_datos_originales():
    """Carga el archivo original con cache para mejor rendimiento"""
    try:
       df = pd.read_csv(url)
    except FileNotFoundError:
        st.error("❌ No se pudo encontrar el archivo 'APOTEOSYS 29 OCTUBRE.XLS'. Por favor verifica que el archivo esté en la ubicación correcta.")
        return None
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def procesar_datos_sgp():
    """Función específica para procesar datos SGP - SOLO PARA PANTALLA 2"""
    df = cargar_datos_originales()
    if df is None:
        return None, None
        
    try:
        df.insert(0, "Codigo_O", df.iloc[:, 0].where(df.iloc[:, 0].astype(str).str.startswith("  O")).ffill())
        df["Concepto de gasto"] = df["Concepto de gasto"].fillna(method="ffill")

        # Extraer los últimos dos caracteres de Codigo_O y convertirlos a número
        ultimos_dos = pd.to_numeric(df["Codigo_O"].astype(str).str[-2:], errors="coerce")

        # --- 🔹 1. SGP CSF (Salarios + Parafiscales) ---
        conceptos_csf = [
            'O231010100101 Sueldo básico',
            'O231010100102 Horas extras, dominicales, festivos y recargos',
            'O231010100104 Subsidio de alimentación',
            'O231010100105 Auxilio de Transporte',
            'O231010100106 Prima de servicio',
            'O23101010010801 Prima de navidad',
            'O23101010010802 Prima de vacaciones',
            'O231010200401 Compensar',
            'O2310102006 Aportes al ICBF',
            'O2310102007 Aportes al SENA',
            'O2310102008 Aportes a la ESAP',
            'O2310102009 Aportes a escuelas industriales e institutos técnicos'
        ]

        filtro_csf = (
            (df["Nombre"] == "SGP Prest. Serv. Nómina Educació") &
            (df["Concepto de gasto"].isin(conceptos_csf)) &
            (ultimos_dos < 65)
        )

        csf = {
            "DISPONIBLE": df.loc[filtro_csf, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_csf, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_csf, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_csf, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_csf, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 2. SGP CSF FOMAG ---
        conceptos_fomag = [
            'O231010200201 Aportes a la seguridad social en salud pública',
            'O231010200101 Aportes a la seguridad social en pensiones públicas'
        ]

        filtro_fomag = (
            (df["Nombre"] == "SGP Prest. Serv. Nómina Educació") &
            (df["Concepto de gasto"].isin(conceptos_fomag)) &
            (ultimos_dos < 65)
        )

        fomag = {
            "DISPONIBLE": df.loc[filtro_fomag, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_fomag, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_fomag, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_fomag, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_fomag, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 3. SGP SSF FOMAG (Empleado) ---
        filtro_ssf_empleado = (
            (df["Nombre"] == "SGP PRESTACION DEL.SERVICIO SSF") &
            (df["Concepto de gasto"] == "O231010100101 Sueldo básico") &
            (ultimos_dos < 65)
        )

        ssf_empleado = {
            "DISPONIBLE": df.loc[filtro_ssf_empleado, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_ssf_empleado, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_ssf_empleado, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_ssf_empleado, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_ssf_empleado, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 4. SGP SSF FOMAG (Patrón) ---
        conceptos_ssf_patron = [
            'O231010200201 Aportes a la seguridad social en salud pública',
            'O231010200301 Aportes de cesantías a fondos públicos'
        ]

        filtro_ssf_patron = (
            (df["Nombre"] == "SGP PRESTACION DEL.SERVICIO SSF") &
            (df["Concepto de gasto"].isin(conceptos_ssf_patron)) &
            (ultimos_dos < 65)
        )

        ssf_patron = {
            "DISPONIBLE": df.loc[filtro_ssf_patron, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_ssf_patron, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_ssf_patron, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_ssf_patron, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_ssf_patron, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 5. ADMINISTRATIVOS SGP ---
        conceptos_administrativos = [
            'O231010100101 Sueldo básico',
            'O231010100204 Prima semestral',
            'O23101010010802 Prima de vacaciones',
            'O23101010010801 Prima de navidad',
            'O231010100107 Bonificación por servicios prestados',
            'O231010100109 Prima técnica salarial',
            'O23101010021201 Beneficios a los empleados a corto plazo',
            'O231010300103 Bonificación especial de recreación',
            'O2310103068 Prima secretarial',
            'O231010200401 Compensar',
            'O2310102006 Aportes al ICBF',
            'O2310102009 Aportes a escuelas industriales e institutos técnicos',
            'O2310102007 Aportes al SENA',
            'O2310102008 Aportes a la ESAP',
            'O231010200202 Aportes a la seguridad social en salud privada',
            'O231010200102 Aportes a la seguridad social en pensiones privadas',
            'O231010200101 Aportes a la seguridad social en pensiones públicas',
            'O231010200502 Aportes generales al sistema de riesgos laborales privados',
            'O231010200302 Aportes de cesantías a fondos privados',
            'O231010200301 Aportes de cesantías a fondos públicos'
        ]

        filtro_administrativos = (
            (df["Nombre"] == "SGP Prest. Serv. Nómina Educació") &
            (df["Concepto de gasto"].isin(conceptos_administrativos)) &
            (ultimos_dos >= 65) & (ultimos_dos <= 86)
        )

        administrativos = {
            "DISPONIBLE": df.loc[filtro_administrativos, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_administrativos, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_administrativos, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_administrativos, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_administrativos, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 6. DOC REC PROPIOS ---
        conceptos_doc_rec_propios = [
            'O231010100101 Sueldo básico',
            'O231010100102 Horas extras, dominicales, festivos y recargos',
            'O231010100104 Subsidio de alimentación',
            'O231010100105 Auxilio de Transporte',
            'O231010100106 Prima de servicio',
            'O23101010010801 Prima de navidad',
            'O23101010010802 Prima de vacaciones',
            'O231010200101 Aportes a la seguridad social en pensiones públicas',
            'O231010200201 Aportes a la seguridad social en salud pública',
            'O231010200301 Aportes de cesantías a fondos públicos',
            'O231010200401 Compensar',
            'O2310102006 Aportes al ICBF',
            'O2310102007 Aportes al SENA',
            'O2310102008 Aportes a la ESAP',
            'O2310102009 Aportes a escuelas industriales e institutos técnicos'
        ]

        filtro_doc_rec_propios = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"].isin(conceptos_doc_rec_propios)) &
            (ultimos_dos <= 57)
        )

        doc_rec_propios = {
            "DISPONIBLE": df.loc[filtro_doc_rec_propios, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_doc_rec_propios, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_doc_rec_propios, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_doc_rec_propios, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_doc_rec_propios, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 7. ADTIVOS REC PROP ---
        conceptos_adtivos_rec_prop = [
            'O231010100101 Sueldo básico',
            'O231010100104 Subsidio de alimentación',
            'O231010100105 Auxilio de Transporte',
            'O231010100107 Bonificación por servicios prestados',
            'O23101010010801 Prima de navidad',
            'O23101010010802 Prima de vacaciones',
            'O231010100109 Prima técnica salarial',
            'O231010100204 Prima semestral',
            'O23101010021201 Beneficios a los empleados a corto plazo',
            'O231010200101 Aportes a la seguridad social en pensiones públicas',
            'O231010200102 Aportes a la seguridad social en pensiones privadas',
            'O231010200202 Aportes a la seguridad social en salud privada',
            'O231010200302 Aportes de cesantías a fondos privados',
            'O231010200301 Aportes de cesantías a fondos públicos',
            'O231010200401 Compensar',
            'O231010200502 Aportes generales al sistema de riesgos laborales privados',
            'O2310102006 Aportes al ICBF',
            'O2310102007 Aportes al SENA',
            'O2310102008 Aportes a la ESAP',
            'O2310102009 Aportes a escuelas industriales e institutos técnicos',
            'O231010300103 Bonificación especial de recreación'
        ]

        filtro_adtivos_rec_prop = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"].isin(conceptos_adtivos_rec_prop)) &
            (ultimos_dos >= 65) & (ultimos_dos <= 86)
        )

        adtivos_rec_prop = {
            "DISPONIBLE": df.loc[filtro_adtivos_rec_prop, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_adtivos_rec_prop, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_adtivos_rec_prop, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_adtivos_rec_prop, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_adtivos_rec_prop, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 8. SENTENCIAS (NUEVA FILA) ---
        conceptos_sentencias = [
            'O2380501002 Multas judiciales'
        ]

        filtro_sentencias = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"].isin(conceptos_sentencias))
        )

        sentencias = {
            "DISPONIBLE": df.loc[filtro_sentencias, "DISPONIBLE"].sum(),
            "RP EMITIDOS": df.loc[filtro_sentencias, "RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": df.loc[filtro_sentencias, "GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": df.loc[filtro_sentencias, "SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": df.loc[filtro_sentencias, "RECURSOS SIN EJECUTAR"].sum()
        }

        # --- 🔹 Crear tabla resumen con nuevo orden ---
        # Primero las 4 filas principales con nuevos nombres
        resumen_principal = pd.DataFrame(
            [
                csf,                    # 1. SGP CSF (Salarios + Parafiscales)
                ssf_empleado,           # 2. SGP SSF FOMAG (Empleado)
                ssf_patron,             # 3. SGP SSF FOMAG (Patrón)
                fomag                   # 4. SGP CSF FOMAG
            ],
            index=[
                "SGP CSF (Salarios + Parafiscales)",
                "SGP SSF FOMAG (Empleado)",
                "SGP SSF FOMAG (Patrón)",
                "SGP CSF FOMAG"
            ]
        )

        # Calcular TOTAL SGP DOCENTES (suma de las primeras 4 filas)
        total_docentes = resumen_principal.sum()
        
        # Crear DataFrames individuales para las filas especiales
        total_docentes_df = pd.DataFrame([total_docentes], index=["TOTAL SGP DOCENTES"])
        administrativos_df = pd.DataFrame([administrativos], index=["Administrativos SGP"])
        doc_rec_propios_df = pd.DataFrame([doc_rec_propios], index=["DOC REC PROPIOS"])
        adtivos_rec_prop_df = pd.DataFrame([adtivos_rec_prop], index=["ADTIVOS REC PROP"])
        sentencias_df = pd.DataFrame([sentencias], index=["SENTENCIAS"])
        
        # Calcular TOTAL SGP P8033 (TOTAL SGP DOCENTES + Administrativos SGP)
        total_docentes_dict = total_docentes.to_dict()
        administrativos_dict = administrativos
        
        total_p8033 = {}
        for key in total_docentes_dict.keys():
            total_p8033[key] = total_docentes_dict[key] + administrativos_dict[key]
        
        total_p8033_df = pd.DataFrame([total_p8033], index=["TOTAL SGP P8033"])

        # Calcular TOTAL RECURSOS PROPIOS P8033 (DOC REC PROPIOS + ADTIVOS REC PROP + SENTENCIAS)
        total_recursos_propios = {}
        for key in doc_rec_propios.keys():
            total_recursos_propios[key] = doc_rec_propios[key] + adtivos_rec_prop[key] + sentencias[key]
        
        total_recursos_propios_df = pd.DataFrame([total_recursos_propios], index=["TOTAL RECURSOS PROPIOS P8033"])

        # Calcular TOTAL SGP+RP P8033 (TOTAL SGP P8033 + TOTAL RECURSOS PROPIOS P8033)
        total_sgp_rp = {}
        for key in total_p8033.keys():
            total_sgp_rp[key] = total_p8033[key] + total_recursos_propios[key]
        
        total_sgp_rp_df = pd.DataFrame([total_sgp_rp], index=["TOTAL SGP+RP P8033"])

        # Concatenar todo en el orden correcto
        resumen = pd.concat([
            resumen_principal,          # Filas 1-4
            total_docentes_df,          # TOTAL SGP DOCENTES
            administrativos_df,         # Administrativos SGP (bolsillo 5)
            total_p8033_df,             # TOTAL SGP P8033
            doc_rec_propios_df,         # DOC REC PROPIOS (bolsillo 6)
            adtivos_rec_prop_df,        # ADTIVOS REC PROP (bolsillo 7)
            sentencias_df,              # SENTENCIAS (bolsillo 8)
            total_recursos_propios_df,  # TOTAL RECURSOS PROPIOS P8033
            total_sgp_rp_df             # TOTAL SGP+RP P8033
        ])

        return df, resumen

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar los datos: {str(e)}")
        import traceback
        st.error(f"Detalle del error: {traceback.format_exc()}")
        return None, None

@st.cache_data(ttl=3600)
def procesar_recursos_propios(df):
    """Procesa los datos para RECURSOS PROPIOS con cache"""
    if df is None:
        return None
        
    try:
        # USAR EXACTAMENTE LA MISMA LÓGICA QUE EN EL TABLERO PRINCIPAL
        df.insert(0, "Codigo_O", df.iloc[:, 0].where(df.iloc[:, 0].astype(str).str.startswith("  O")).ffill())
        df["Concepto de gasto"] = df["Concepto de gasto"].fillna(method="ffill")

        # Extraer los últimos dos caracteres de Codigo_O y convertirlos a número
        ultimos_dos = pd.to_numeric(df["Codigo_O"].astype(str).str[-2:], errors="coerce")

        # FILTRO PARA SUELDO BASICO
        filtro_sueldo_basico = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010100101 Sueldo básico") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA HORAS EXTRAS
        filtro_horas_extras = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010100102 Horas extras, dominicales, festivos y recargos") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA SUBSIDIO DE ALIMENTACIÓN
        filtro_subsidio_alimentacion = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010100104 Subsidio de alimentación") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA AUXILIO DE TRANSPORTE
        filtro_auxilio_transporte = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010100105 Auxilio de Transporte") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA PRIMA DE SERVICIOS
        filtro_prima_servicios = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010100106 Prima de servicio") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA PRIMA DE VACACIONES
        filtro_prima_vacaciones = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O23101010010802 Prima de vacaciones") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTRO PARA PRIMA DE NAVIDAD
        filtro_prima_navidad = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O23101010010801 Prima de navidad") &
            (ultimos_dos < 65)  # Últimos dos dígitos menores a 65
        )

        # FILTROS PARA PARAFISCALES
        filtro_compensar = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010200401 Compensar") &
            (ultimos_dos < 65)
        )

        filtro_icbf = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O2310102006 Aportes al ICBF") &
            (ultimos_dos < 65)
        )

        filtro_sena = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O2310102007 Aportes al SENA") &
            (ultimos_dos < 65)
        )

        filtro_esap = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O2310102008 Aportes a la ESAP") &
            (ultimos_dos < 65)
        )

        filtro_escuelas_tecnicas = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O2310102009 Aportes a escuelas industriales e institutos técnicos") &
            (ultimos_dos < 65)
        )

        # NUEVOS FILTROS PARA FOMAG
        # 1. SALUD
        filtro_salud = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010200201 Aportes a la seguridad social en salud pública") &
            (ultimos_dos < 65)
        )

        # 2. PENSION
        filtro_pension = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010200101 Aportes a la seguridad social en pensiones públicas") &
            (ultimos_dos < 65)
        )

        # 3. CESANTIAS
        filtro_cesantias = (
            (df["Nombre"] == "Otros Distrito Inversión") &
            (df["Concepto de gasto"] == "O231010200301 Aportes de cesantías a fondos públicos") &
            (ultimos_dos < 65)
        )

        # Verificar si hay filas que cumplen los filtros
        filas_sueldo = df[filtro_sueldo_basico]
        filas_horas = df[filtro_horas_extras]
        filas_subsidio = df[filtro_subsidio_alimentacion]
        filas_auxilio = df[filtro_auxilio_transporte]
        filas_prima_servicios = df[filtro_prima_servicios]
        filas_prima_vacaciones = df[filtro_prima_vacaciones]
        filas_prima_navidad = df[filtro_prima_navidad]
        filas_compensar = df[filtro_compensar]
        filas_icbf = df[filtro_icbf]
        filas_sena = df[filtro_sena]
        filas_esap = df[filtro_esap]
        filas_escuelas_tecnicas = df[filtro_escuelas_tecnicas]
        filas_salud = df[filtro_salud]
        filas_pension = df[filtro_pension]
        filas_cesantias = df[filtro_cesantias]
        
        # Verificar si hay al menos alguna fila que cumpla los criterios
        todas_las_filas_vacias = (
            len(filas_sueldo) == 0 and len(filas_horas) == 0 and len(filas_subsidio) == 0 and 
            len(filas_auxilio) == 0 and len(filas_prima_servicios) == 0 and len(filas_prima_vacaciones) == 0 and 
            len(filas_prima_navidad) == 0 and len(filas_compensar) == 0 and len(filas_icbf) == 0 and 
            len(filas_sena) == 0 and len(filas_esap) == 0 and len(filas_escuelas_tecnicas) == 0 and
            len(filas_salud) == 0 and len(filas_pension) == 0 and len(filas_cesantias) == 0
        )
        
        if todas_las_filas_vacias:
            st.warning("⚠ No se encontraron filas con los criterios especificados")
            return None

        # Crear diccionarios con los datos sumados - CONCEPTOS DE NÓMINA
        sueldo_basico = {
            "DISPONIBLE": filas_sueldo["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_sueldo["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_sueldo["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_sueldo["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_sueldo["RECURSOS SIN EJECUTAR"].sum()
        }

        horas_extras = {
            "DISPONIBLE": filas_horas["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_horas["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_horas["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_horas["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_horas["RECURSOS SIN EJECUTAR"].sum()
        }

        subsidio_alimentacion = {
            "DISPONIBLE": filas_subsidio["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_subsidio["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_subsidio["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_subsidio["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_subsidio["RECURSOS SIN EJECUTAR"].sum()
        }

        auxilio_transporte = {
            "DISPONIBLE": filas_auxilio["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_auxilio["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_auxilio["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_auxilio["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_auxilio["RECURSOS SIN EJECUTAR"].sum()
        }

        prima_servicios = {
            "DISPONIBLE": filas_prima_servicios["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_prima_servicios["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_prima_servicios["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_prima_servicios["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_prima_servicios["RECURSOS SIN EJECUTAR"].sum()
        }

        prima_vacaciones = {
            "DISPONIBLE": filas_prima_vacaciones["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_prima_vacaciones["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_prima_vacaciones["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_prima_vacaciones["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_prima_vacaciones["RECURSOS SIN EJECUTAR"].sum()
        }

        prima_navidad = {
            "DISPONIBLE": filas_prima_navidad["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_prima_navidad["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_prima_navidad["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_prima_navidad["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_prima_navidad["RECURSOS SIN EJECUTAR"].sum()
        }

        # Diccionarios para PARAFISCALES
        compensar = {
            "DISPONIBLE": filas_compensar["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_compensar["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_compensar["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_compensar["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_compensar["RECURSOS SIN EJECUTAR"].sum()
        }

        icbf = {
            "DISPONIBLE": filas_icbf["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_icbf["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_icbf["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_icbf["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_icbf["RECURSOS SIN EJECUTAR"].sum()
        }

        sena = {
            "DISPONIBLE": filas_sena["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_sena["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_sena["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_sena["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_sena["RECURSOS SIN EJECUTAR"].sum()
        }

        esap = {
            "DISPONIBLE": filas_esap["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_esap["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_esap["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_esap["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_esap["RECURSOS SIN EJECUTAR"].sum()
        }

        escuelas_tecnicas = {
            "DISPONIBLE": filas_escuelas_tecnicas["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_escuelas_tecnicas["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_escuelas_tecnicas["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_escuelas_tecnicas["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_escuelas_tecnicas["RECURSOS SIN EJECUTAR"].sum()
        }

        # NUEVOS: Diccionarios para FOMAG
        salud = {
            "DISPONIBLE": filas_salud["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_salud["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_salud["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_salud["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_salud["RECURSOS SIN EJECUTAR"].sum()
        }

        pension = {
            "DISPONIBLE": filas_pension["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_pension["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_pension["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_pension["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_pension["RECURSOS SIN EJECUTAR"].sum()
        }

        cesantias = {
            "DISPONIBLE": filas_cesantias["DISPONIBLE"].sum(),
            "RP EMITIDOS": filas_cesantias["RP EMITIDOS"].sum(),
            "GIROS ACUMULADOS": filas_cesantias["GIROS ACUMULADOS"].sum(),
            "SALDO DE APROPIACION": filas_cesantias["SALDO DE APROPIACION"].sum(),
            "RECURSOS SIN EJECUTAR": filas_cesantias["RECURSOS SIN EJECUTAR"].sum()
        }

        # Calcular SUELDOS (suma de todos los conceptos de nómina)
        conceptos_nomina = [sueldo_basico, horas_extras, subsidio_alimentacion, auxilio_transporte, 
                           prima_servicios, prima_vacaciones, prima_navidad]
        
        sueldos_total = {
            "DISPONIBLE": sum(concepto["DISPONIBLE"] for concepto in conceptos_nomina),
            "RP EMITIDOS": sum(concepto["RP EMITIDOS"] for concepto in conceptos_nomina),
            "GIROS ACUMULADOS": sum(concepto["GIROS ACUMULADOS"] for concepto in conceptos_nomina),
            "SALDO DE APROPIACION": sum(concepto["SALDO DE APROPIACION"] for concepto in conceptos_nomina),
            "RECURSOS SIN EJECUTAR": sum(concepto["RECURSOS SIN EJECUTAR"] for concepto in conceptos_nomina)
        }

        # Calcular TOTAL PARAFISCALES (suma de los 5 parafiscales)
        parafiscales = [compensar, icbf, sena, esap, escuelas_tecnicas]
        
        total_parafiscales = {
            "DISPONIBLE": sum(concepto["DISPONIBLE"] for concepto in parafiscales),
            "RP EMITIDOS": sum(concepto["RP EMITIDOS"] for concepto in parafiscales),
            "GIROS ACUMULADOS": sum(concepto["GIROS ACUMULADOS"] for concepto in parafiscales),
            "SALDO DE APROPIACION": sum(concepto["SALDO DE APROPIACION"] for concepto in parafiscales),
            "RECURSOS SIN EJECUTAR": sum(concepto["RECURSOS SIN EJECUTAR"] for concepto in parafiscales)
        }

        # Calcular TOTAL FOMAG (suma de los 3 conceptos FOMAG)
        fomag_conceptos = [salud, pension, cesantias]
        
        total_fomag = {
            "DISPONIBLE": sum(concepto["DISPONIBLE"] for concepto in fomag_conceptos),
            "RP EMITIDOS": sum(concepto["RP EMITIDOS"] for concepto in fomag_conceptos),
            "GIROS ACUMULADOS": sum(concepto["GIROS ACUMULADOS"] for concepto in fomag_conceptos),
            "SALDO DE APROPIACION": sum(concepto["SALDO DE APROPIACION"] for concepto in fomag_conceptos),
            "RECURSOS SIN EJECUTAR": sum(concepto["RECURSOS SIN EJECUTAR"] for concepto in fomag_conceptos)
        }

        # NUEVO: Calcular DOC REC PROPIOS (suma de SUELDOS + TOTAL PARAFISCALES + TOTAL FOMAG)
        doc_rec_propios = {
            "DISPONIBLE": sueldos_total["DISPONIBLE"] + total_parafiscales["DISPONIBLE"] + total_fomag["DISPONIBLE"],
            "RP EMITIDOS": sueldos_total["RP EMITIDOS"] + total_parafiscales["RP EMITIDOS"] + total_fomag["RP EMITIDOS"],
            "GIROS ACUMULADOS": sueldos_total["GIROS ACUMULADOS"] + total_parafiscales["GIROS ACUMULADOS"] + total_fomag["GIROS ACUMULADOS"],
            "SALDO DE APROPIACION": sueldos_total["SALDO DE APROPIACION"] + total_parafiscales["SALDO DE APROPIACION"] + total_fomag["SALDO DE APROPIACION"],
            "RECURSOS SIN EJECUTAR": sueldos_total["RECURSOS SIN EJECUTAR"] + total_parafiscales["RECURSOS SIN EJECUTAR"] + total_fomag["RECURSOS SIN EJECUTAR"]
        }
        
        return {
            # Conceptos de nómina
            "SUELDO BASICO": sueldo_basico,
            "HORAS EXTRAS": horas_extras,
            "SUBSIDIO DE ALIMENTACIÓN": subsidio_alimentacion,
            "AUXILIO DE TRANSPORTE": auxilio_transporte,
            "PRIMA DE SERVICIOS": prima_servicios,
            "PRIMA DE VACACIONES": prima_vacaciones,
            "PRIMA DE NAVIDAD": prima_navidad,
            "SUELDOS": sueldos_total,  # Total nómina
            
            # Parafiscales
            "COMPENSAR": compensar,
            "ICBF": icbf,
            "SENA": sena,
            "ESAP": esap,
            "ESCUELAS TÉCNICAS": escuelas_tecnicas,
            "TOTAL PARAFISCALES": total_parafiscales,  # Total parafiscales
            
            # FOMAG
            "SALUD": salud,
            "PENSIÓN": pension,
            "CESANTÍAS": cesantias,
            "TOTAL FOMAG": total_fomag,  # Total FOMAG
            
            # NUEVO: TOTAL GENERAL
            "DOC REC PROPIOS": doc_rec_propios  # Total general
        }
        
    except Exception as e:
        st.error(f"❌ Error al procesar recursos propios: {str(e)}")
        import traceback
        st.error(f"Detalle del error: {traceback.format_exc()}")
        return None

# =============================================================================
# PANTALLA 1: INICIO
# =============================================================================
def mostrar_pantalla_inicial():
    st.markdown("<div class='pantalla-inicial'>", unsafe_allow_html=True)
    
    # Logos en la parte superior
    st.markdown("<div class='contenedor-logos'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("logo_bogota.png", width=250, use_container_width=True)
    with col2:
        st.markdown("<div class='header'><h1>SECRETARÍA DE EDUCACIÓN DE BOGOTÁ</h1><h2>CONTROL PRESUPUESTAL NÓMINA</h2></div>", unsafe_allow_html=True)
    with col3:
        st.image("logo_alcaldía_mayor.png", width=250, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Tres botones de navegación
    st.markdown("<div class='contenedor-botones'>", unsafe_allow_html=True)
    
    # Botón principal protagonista - TABLERO PRINCIPAL
    col_principal = st.columns([1])
    with col_principal[0]:
        if st.button("🏠 TABLERO PRINCIPAL", key="principal", use_container_width=True):
            st.session_state.pagina_actual = "POR_FUENTE"
            st.rerun()
    
    # Espacio para separar el botón principal
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # Dos botones secundarios
    col_secundarios = st.columns(2)
    
    with col_secundarios[0]:
        if st.button("💰 RECURSOS PROPIOS", key="recursos_propios", use_container_width=True):
            st.session_state.pagina_actual = "RECURSOS_PROPIOS"
            st.rerun()
    
    with col_secundarios[1]:
        if st.button("📊 SISTEMA GENERAL DE PARTICIPACIONES", key="sgp", use_container_width=True):
            st.session_state.pagina_actual = "SGP"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# PANTALLA 2: TABLERO PRINCIPAL (POR FUENTE)
# =============================================================================
def mostrar_tabla_sgp(resumen):
    """Función específica para mostrar tabla SGP - SOLO PARA PANTALLA 2"""
    if resumen is None:
        return

    # Formatear números con separadores de miles
    resumen_formateado = resumen.copy()
    for col in resumen_formateado.columns:
        resumen_formateado[col] = resumen_formateado[col].apply(
            lambda x: f"${x:,.0f}".replace(",", ".") if pd.notnull(x) else "$0"
        )

    # --- 🔹 MOSTRAR TABLA CON DISEÑO PERSONALIZADO ---
    st.markdown("<div class='titulo-tabla'>📊 TABLA RESUMEN EJECUCIÓN PRESUPUESTAL - SGP</div>", unsafe_allow_html=True)
    
    # Crear HTML personalizado para la tabla
    html_tabla = """
    <div class="tabla-container">
        <table class="tabla-personalizada">
            <thead>
                <tr>
                    <th>BOLSILLOS</th>
                    <th>CONCEPTO</th>
                    <th>DISPONIBLE</th>
                    <th>RP EMITIDOS</th>
                    <th>GIROS ACUMULADOS</th>
                    <th>SALDO DE APROPIACION</th>
                    <th>RECURSOS SIN EJECUTAR</th>
                </tr>
            </thead>
            <tbody>
    """

    # Agregar filas de datos con numeración
    bolsillos = 1
    for idx, row in resumen_formateado.iterrows():
        if idx == "TOTAL SGP DOCENTES":
            html_tabla += '<tr class="fila-total">'
            html_tabla += f'<td class="encabezado-fila"></td>'  # Celda vacía para bolsillos
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
        elif idx == "Administrativos SGP":
            html_tabla += '<tr>'
            html_tabla += f'<td class="encabezado-fila">{bolsillos}</td>'
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
            bolsillos += 1
        elif idx == "TOTAL SGP P8033":
            html_tabla += '<tr class="fila-total-final">'
            html_tabla += f'<td class="encabezado-fila"></td>'  # Celda vacía para bolsillos
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
        elif idx == "DOC REC PROPIOS":
            html_tabla += '<tr>'
            html_tabla += f'<td class="encabezado-fila">{bolsillos}</td>'
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
            bolsillos += 1
        elif idx == "ADTIVOS REC PROP":
            html_tabla += '<tr>'
            html_tabla += f'<td class="encabezado-fila">{bolsillos}</td>'
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
            bolsillos += 1
        elif idx == "SENTENCIAS":
            html_tabla += '<tr>'
            html_tabla += f'<td class="encabezado-fila">{bolsillos}</td>'
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
            bolsillos += 1
        elif idx == "TOTAL RECURSOS PROPIOS P8033":
            html_tabla += '<tr class="fila-total">'
            html_tabla += f'<td class="encabezado-fila"></td>'  # Celda vacía para bolsillos
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
        elif idx == "TOTAL SGP+RP P8033":
            html_tabla += '<tr class="fila-total-general">'
            html_tabla += f'<td class="encabezado-fila"></td>'  # Celda vacía para bolsillos
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
        else:
            html_tabla += '<tr>'
            html_tabla += f'<td class="encabezado-fila">{bolsillos}</td>'
            html_tabla += f'<td class="encabezado-fila">{idx}</td>'
            bolsillos += 1
        
        html_tabla += f'<td class="numero">{row["DISPONIBLE"]}</td>'
        html_tabla += f'<td class="numero">{row["RP EMITIDOS"]}</td>'
        html_tabla += f'<td class="numero">{row["GIROS ACUMULADOS"]}</td>'
        html_tabla += f'<td class="numero">{row["SALDO DE APROPIACION"]}</td>'
        html_tabla += f'<td class="numero">{row["RECURSOS SIN EJECUTAR"]}</td>'
        html_tabla += '</tr>'

    html_tabla += """
            </tbody>
        </table>
    </div>
    """

    st.markdown(html_tabla, unsafe_allow_html=True)

    # --- 🔹 MOSTRAR ESTADÍSTICAS ADICIONALES ---
    st.markdown("<div class='subtitulo'>Resumen Ejecutivo:</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        disponible_total = resumen.loc["TOTAL SGP+RP P8033", "DISPONIBLE"]
        if disponible_total > 0:
            porcentaje_ejecutado = (resumen.loc["TOTAL SGP+RP P8033", "GIROS ACUMULADOS"] / disponible_total) * 100
        else:
            porcentaje_ejecutado = 0
            
        st.metric(
            label="💰 % Ejecutado", 
            value=f"{porcentaje_ejecutado:.1f}%",
            delta=f"GIROS: ${resumen.loc['TOTAL SGP+RP P8033', 'GIROS ACUMULADOS']:,.0f}".replace(",", ".")
        )
    
    with col2:
        if disponible_total > 0:
            porcentaje_rp = (resumen.loc["TOTAL SGP+RP P8033", "RP EMITIDOS"] / disponible_total) * 100
            delta_text = f"{porcentaje_rp:.1f}% del disponible"
        else:
            delta_text = "0% del disponible"
            
        st.metric(
            label="📋 RP Emitidos", 
            value=f"${resumen.loc['TOTAL SGP+RP P8033', 'RP EMITIDOS']:,.0f}".replace(",", "."),
            delta=delta_text
        )
    
    with col3:
        st.metric(
            label="💸 Disponible Total", 
            value=f"${disponible_total:,.0f}".replace(",", ".")
        )
    
    with col4:
        st.metric(
            label="⏳ Por Ejecutar", 
            value=f"${resumen.loc['TOTAL SGP+RP P8033', 'RECURSOS SIN EJECUTAR']:,.0f}".replace(",", "."),
            delta_color="inverse"
        )

def mostrar_pantalla_por_fuente():
    # Botón para volver al inicio
    if st.button("← Volver al Inicio", key="volver_fuente"):
        st.session_state.pagina_actual = "INICIO"
        st.rerun()
    
    # Encabezado con ambos logos
    st.markdown("<div class='contenedor-logos'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("logo_bogota.png", width=150, use_container_width=True)
    with col2:
        st.markdown("<div class='header'><h2>Sistema General de Participaciones y Recursos Propios</h2></div>", unsafe_allow_html=True)
    with col3:
        st.image("logo_alcaldía_mayor.png", width=150, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Procesar y mostrar datos con spinner
    with st.spinner("Cargando datos presupuestales..."):
        df, resumen = procesar_datos_sgp()
    
    if resumen is not None:
        mostrar_tabla_sgp(resumen)

# =============================================================================
# PANTALLA 3: RECURSOS PROPIOS
# =============================================================================
def mostrar_tabla_recursos_propios(datos, seccion_titulo):
    """Muestra la tabla de RECURSOS PROPIOS con opción de desplegar detalles"""
    if datos is None:
        return
    
    # Crear DataFrame con todas las filas
    filas = []
    for concepto, valores in datos.items():
        fila = valores.copy()
        fila['CONCEPTO'] = concepto
        filas.append(fila)
    
    df_recursos = pd.DataFrame(filas)
    df_recursos.set_index('CONCEPTO', inplace=True)
    
    # Formatear números con separadores de miles
    df_formateado = df_recursos.copy()
    for col in df_formateado.columns:
        if col != 'CONCEPTO':
            df_formateado[col] = df_formateado[col].apply(
                lambda x: f"${x:,.0f}".replace(",", ".") if pd.notnull(x) and x != 0 else "$0"
            )
    
    # Mostrar tabla con estilo similar al tablero principal
    st.markdown(f"<div class='titulo-tabla'>{seccion_titulo}</div>", unsafe_allow_html=True)
    
    # Checkbox para mostrar/ocultar detalles (más confiable que botones)
    mostrar_detalles = st.checkbox("📊 Mostrar detalles desglosados", value=False, key=f"detalles_{seccion_titulo}")
    
    # Aplicar estilos CSS específicos para esta tabla
    st.markdown("""
    <style>
    .tabla-recursos-container {
        border: 2px solid #b30000;
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    .tabla-recursos {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 13px;
        background-color: white;
    }
    .tabla-recursos th {
        background-color: #b30000;
        color: white;
        font-weight: bold;
        padding: 10px 8px;
        text-align: center;
        border: 1px solid #8b0000;
        font-size: 13px;
    }
    .tabla-recursos td {
        padding: 8px 6px;
        text-align: center;
        border: 1px solid #ddd;
        color: #000000;
        background-color: white;
    }
    .tabla-recursos tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .tabla-recursos tr:hover {
        background-color: #f0f0f0;
    }
    .concepto-header {
        background-color: white !important;
        color: #000000 !important;
        font-weight: bold;
        text-align: left;
        border: 1px solid #ddd !important;
        padding: 8px 10px !important;
    }
    .numero-tabla {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 12px;
        color: #000000 !important;
        text-align: right;
        padding: 8px 6px;
    }
    .fila-total-nomina {
        background-color: #e8f5e8 !important;
        font-weight: bold;
    }
    .fila-total-parafiscales {
        background-color: #e3f2fd !important;
        font-weight: bold;
    }
    .fila-total-fomag {
        background-color: #fff3e0 !important;
        font-weight: bold;
    }
    .fila-total-general {
        background-color: #fce4ec !important;
        font-weight: bold;
    }
    .celda-total-nomina {
        color: #2e7d32 !important;
        border-top: 2px solid #2e7d32 !important;
        border-bottom: 2px solid #2e7d32 !important;
    }
    .celda-total-parafiscales {
        color: #1565c0 !important;
        border-top: 2px solid #1565c0 !important;
        border-bottom: 2px solid #1565c0 !important;
    }
    .celda-total-fomag {
        color: #ef6c00 !important;
        border-top: 2px solid #ef6c00 !important;
        border-bottom: 2px solid #ef6c00 !important;
    }
    .celda-total-general {
        color: #c2185b !important;
        border-top: 3px solid #c2185b !important;
        border-bottom: 3px solid #c2185b !important;
        font-size: 13px;
    }
    .concepto-total-nomina {
        background-color: #e8f5e8 !important;
        color: #2e7d32 !important;
        font-weight: bold;
    }
    .concepto-total-parafiscales {
        background-color: #e3f2fd !important;
        color: #1565c0 !important;
        font-weight: bold;
    }
    .concepto-total-fomag {
        background-color: #fff3e0 !important;
        color: #ef6c00 !important;
        font-weight: bold;
    }
    .concepto-total-general {
        background-color: #fce4ec !important;
        color: #c2185b !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    html_tabla = """
    <div class="tabla-recursos-container">
        <table class="tabla-recursos">
            <thead>
                <tr>
                    <th class="concepto-header">CONCEPTO</th>
                    <th>DISPONIBLE</th>
                    <th>RP EMITIDOS</th>
                    <th>GIROS ACUMULADOS</th>
                    <th>SALDO DE APROPIACION</th>
                    <th>RECURSOS SIN EJECUTAR</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Definir el orden de las filas
    conceptos_nomina = [
        "SUELDO BASICO", "HORAS EXTRAS", "SUBSIDIO DE ALIMENTACIÓN", 
        "AUXILIO DE TRANSPORTE", "PRIMA DE SERVICIOS", "PRIMA DE VACACIONES", 
        "PRIMA DE NAVIDAD", "SUELDOS"
    ]
    
    conceptos_parafiscales = [
        "COMPENSAR", "ICBF", "SENA", "ESAP", "ESCUELAS TÉCNICAS", "TOTAL PARAFISCALES"
    ]
    
    conceptos_fomag = [
        "SALUD", "PENSIÓN", "CESANTÍAS", "TOTAL FOMAG"
    ]
    
    # Determinar el nombre del total final basado en la sección
    if "TOTAL" in seccion_titulo:
        total_final = "DOC REC PROPIOS"
    elif "PRIMERA INFANCIA" in seccion_titulo:
        total_final = "PRIMERA INFANCIA REC PROPIOS"
    elif "ORIENTADORES" in seccion_titulo:
        total_final = "ORIENTADORES REC PROPIOS"
    elif "GLOBAL" in seccion_titulo:
        total_final = "GLOBAL REC PROPIOS"
    else:
        total_final = "DOC REC PROPIOS"
    
    # Determinar qué conceptos mostrar
    if mostrar_detalles:
        conceptos_ordenados = conceptos_nomina + conceptos_parafiscales + conceptos_fomag + [total_final]
    else:
        # Solo mostrar los totales
        conceptos_ordenados = ["SUELDOS", "TOTAL PARAFISCALES", "TOTAL FOMAG", total_final]
    
    for concepto in conceptos_ordenados:
        # Verificar si el concepto existe en los datos
        if concepto not in df_formateado.index:
            continue
            
        # Aplicar estilos diferentes según el tipo de fila
        if concepto == "SUELDOS":
            clase_fila = "fila-total-nomina"
            clase_celda_concepto = "concepto-total-nomina concepto-header"
            clase_celda_numero = "celda-total-nomina numero-tabla"
        elif concepto == "TOTAL PARAFISCALES":
            clase_fila = "fila-total-parafiscales"
            clase_celda_concepto = "concepto-total-parafiscales concepto-header"
            clase_celda_numero = "celda-total-parafiscales numero-tabla"
        elif concepto == "TOTAL FOMAG":
            clase_fila = "fila-total-fomag"
            clase_celda_concepto = "concepto-total-fomag concepto-header"
            clase_celda_numero = "celda-total-fomag numero-tabla"
        elif concepto == total_final:
            clase_fila = "fila-total-general"
            clase_celda_concepto = "concepto-total-general concepto-header"
            clase_celda_numero = "celda-total-general numero-tabla"
        else:
            clase_fila = ""
            clase_celda_concepto = "concepto-header"
            clase_celda_numero = "numero-tabla"
        
        html_tabla += f'<tr class="{clase_fila}">'
        html_tabla += f'<td class="{clase_celda_concepto}">{concepto}</td>'
        html_tabla += f'<td class="{clase_celda_numero}">{df_formateado.loc[concepto, "DISPONIBLE"]}</td>'
        html_tabla += f'<td class="{clase_celda_numero}">{df_formateado.loc[concepto, "RP EMITIDOS"]}</td>'
        html_tabla += f'<td class="{clase_celda_numero}">{df_formateado.loc[concepto, "GIROS ACUMULADOS"]}</td>'
        html_tabla += f'<td class="{clase_celda_numero}">{df_formateado.loc[concepto, "SALDO DE APROPIACION"]}</td>'
        html_tabla += f'<td class="{clase_celda_numero}">{df_formateado.loc[concepto, "RECURSOS SIN EJECUTAR"]}</td>'
        html_tabla += '</tr>'
    
    html_tabla += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(html_tabla, unsafe_allow_html=True)

def mostrar_pantalla_recursos_propios():
    # BOTONES DE NAVEGACIÓN MEJORADOS
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Volver al Inicio", key="volver_recursos", use_container_width=True):
            st.session_state.pagina_actual = "INICIO"
            st.rerun()
    with col2:
        # Espacio para el título
        pass
    with col3:
        # NUEVO BOTÓN PARA PROYECCIONES
        if st.button("📈 RECURSOS PROPIOS PROYECCIONES", key="ir_proyecciones", use_container_width=True):
            st.session_state.pagina_actual = "RECURSOS_PROPIOS_PROYECCIONES"
            st.rerun()
    
    # Encabezado con ambos logos
    st.markdown("<div class='contenedor-logos'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("logo_bogota.png", width=150)
    with col2:
        st.markdown("<div class='header'><h2>RECURSOS PROPIOS - ANÁLISIS POR CATEGORÍA</h2></div>", unsafe_allow_html=True)
    with col3:
        st.image("logo_alcaldía_mayor.png", width=150)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Información sobre el nuevo módulo
    st.info("💡 **Nuevo**: Ahora puedes acceder a las proyecciones de recursos propios usando el botón superior derecho 'RECURSOS PROPIOS PROYECCIONES'")
    
    # =========================================================================
    # SECCIÓN 1: TOTAL - SOLO LA TABLA SIN RESUMEN
    # =========================================================================
    st.markdown("---")
    st.subheader("🌐 TOTAL")
    
    # Cargar datos del archivo principal
    df_principal = cargar_datos_originales()
    
    if df_principal is not None:
        # Procesar RECURSOS PROPIOS
        with st.spinner("Procesando datos de recursos propios..."):
            datos_recursos = procesar_recursos_propios(df_principal)
        
        if datos_recursos is not None:
            mostrar_tabla_recursos_propios(datos_recursos, "💰 TOTAL - RECURSOS PROPIOS")
        else:
            st.error("❌ No se pudieron procesar los datos de recursos propios")
    else:
        st.error("❌ No se pudo cargar el archivo de datos")
    
    # =========================================================================
    # 🆕 NUEVA SECCIÓN: PRIMERA INFANCIA
    # =========================================================================
    st.markdown("---")
    st.subheader("👶 PRIMERA INFANCIA")
    
    if df_principal is not None:
        with st.spinner("Procesando datos de primera infancia..."):
            try:
                # Procesar PRIMERA INFANCIA (códigos 01-19)
                df_primera = df_principal.copy()
                df_primera.insert(0, "Codigo_O", df_primera.iloc[:, 0].where(df_primera.iloc[:, 0].astype(str).str.startswith("  O")).ffill())
                df_primera["Concepto de gasto"] = df_primera["Concepto de gasto"].ffill()
                
                # Extraer últimos dos dígitos y filtrar 01-19
                ultimos_dos = pd.to_numeric(df_primera["Codigo_O"].astype(str).str[-2:], errors="coerce")
                filtro_primera = (
                    (df_primera["Nombre"] == "Otros Distrito Inversión") &
                    (ultimos_dos >= 1) & (ultimos_dos <= 19)
                )
                
                # Aplicar mismos conceptos que Recursos Propios pero con filtro de Primera Infancia
                conceptos = {
                    "SUELDO BASICO": "O231010100101 Sueldo básico",
                    "HORAS EXTRAS": "O231010100102 Horas extras, dominicales, festivos y recargos",
                    "SUBSIDIO DE ALIMENTACIÓN": "O231010100104 Subsidio de alimentación",
                    "AUXILIO DE TRANSPORTE": "O231010100105 Auxilio de Transporte",
                    "PRIMA DE SERVICIOS": "O231010100106 Prima de servicio",
                    "PRIMA DE VACACIONES": "O23101010010802 Prima de vacaciones",
                    "PRIMA DE NAVIDAD": "O23101010010801 Prima de navidad",
                    "COMPENSAR": "O231010200401 Compensar",
                    "ICBF": "O2310102006 Aportes al ICBF",
                    "SENA": "O2310102007 Aportes al SENA",
                    "ESAP": "O2310102008 Aportes a la ESAP",
                    "ESCUELAS TÉCNICAS": "O2310102009 Aportes a escuelas industriales e institutos técnicos",
                    "SALUD": "O231010200201 Aportes a la seguridad social en salud pública",
                    "PENSIÓN": "O231010200101 Aportes a la seguridad social en pensiones públicas",
                    "CESANTÍAS": "O231010200301 Aportes de cesantías a fondos públicos"
                }
                
                datos_primera = {}
                for nombre, concepto in conceptos.items():
                    filtro = filtro_primera & (df_primera["Concepto de gasto"] == concepto)
                    filas = df_primera[filtro]
                    datos_primera[nombre] = {
                        "DISPONIBLE": filas["DISPONIBLE"].sum(),
                        "RP EMITIDOS": filas["RP EMITIDOS"].sum(),
                        "GIROS ACUMULADOS": filas["GIROS ACUMULADOS"].sum(),
                        "SALDO DE APROPIACION": filas["SALDO DE APROPIACION"].sum(),
                        "RECURSOS SIN EJECUTAR": filas["RECURSOS SIN EJECUTAR"].sum()
                    }
                
                # Calcular totales
                conceptos_nomina = ["SUELDO BASICO", "HORAS EXTRAS", "SUBSIDIO DE ALIMENTACIÓN", "AUXILIO DE TRANSPORTE", 
                                  "PRIMA DE SERVICIOS", "PRIMA DE VACACIONES", "PRIMA DE NAVIDAD"]
                datos_primera["SUELDOS"] = {col: sum(datos_primera[concepto][col] for concepto in conceptos_nomina) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_parafiscales = ["COMPENSAR", "ICBF", "SENA", "ESAP", "ESCUELAS TÉCNICAS"]
                datos_primera["TOTAL PARAFISCALES"] = {col: sum(datos_primera[concepto][col] for concepto in conceptos_parafiscales) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_fomag = ["SALUD", "PENSIÓN", "CESANTÍAS"]
                datos_primera["TOTAL FOMAG"] = {col: sum(datos_primera[concepto][col] for concepto in conceptos_fomag) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                # Total general
                datos_primera["PRIMERA INFANCIA REC PROPIOS"] = {
                    col: datos_primera["SUELDOS"][col] + datos_primera["TOTAL PARAFISCALES"][col] + datos_primera["TOTAL FOMAG"][col]
                    for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]
                }
                
                # Mostrar tabla
                if any(datos_primera["PRIMERA INFANCIA REC PROPIOS"][col] > 0 for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS"]):
                    mostrar_tabla_recursos_propios(datos_primera, "👶 PRIMERA INFANCIA - RECURSOS PROPIOS")
                else:
                    st.warning("⚠ No se encontraron datos para Primera Infancia")
                    
            except Exception as e:
                st.error(f"❌ Error al procesar primera infancia: {str(e)}")

    # =========================================================================
    # 🆕 NUEVA SECCIÓN: ORIENTADORES
    # =========================================================================
    st.markdown("---")
    st.subheader("🧑‍🏫 ORIENTADORES")
    
    if df_principal is not None:
        with st.spinner("Procesando datos de orientadores..."):
            try:
                # Procesar ORIENTADORES (códigos 20-32)
                df_orientadores = df_principal.copy()
                df_orientadores.insert(0, "Codigo_O", df_orientadores.iloc[:, 0].where(df_orientadores.iloc[:, 0].astype(str).str.startswith("  O")).ffill())
                df_orientadores["Concepto de gasto"] = df_orientadores["Concepto de gasto"].ffill()
                
                # Extraer últimos dos dígitos y filtrar 20-32
                ultimos_dos = pd.to_numeric(df_orientadores["Codigo_O"].astype(str).str[-2:], errors="coerce")
                filtro_orientadores = (
                    (df_orientadores["Nombre"] == "Otros Distrito Inversión") &
                    (ultimos_dos >= 20) & (ultimos_dos <= 32)
                )
                
                # Aplicar mismos conceptos que Recursos Propios pero con filtro de Orientadores
                conceptos = {
                    "SUELDO BASICO": "O231010100101 Sueldo básico",
                    "HORAS EXTRAS": "O231010100102 Horas extras, dominicales, festivos y recargos",
                    "SUBSIDIO DE ALIMENTACIÓN": "O231010100104 Subsidio de alimentación",
                    "AUXILIO DE TRANSPORTE": "O231010100105 Auxilio de Transporte",
                    "PRIMA DE SERVICIOS": "O231010100106 Prima de servicio",
                    "PRIMA DE VACACIONES": "O23101010010802 Prima de vacaciones",
                    "PRIMA DE NAVIDAD": "O23101010010801 Prima de navidad",
                    "COMPENSAR": "O231010200401 Compensar",
                    "ICBF": "O2310102006 Aportes al ICBF",
                    "SENA": "O2310102007 Aportes al SENA",
                    "ESAP": "O2310102008 Aportes a la ESAP",
                    "ESCUELAS TÉCNICAS": "O2310102009 Aportes a escuelas industriales e institutos técnicos",
                    "SALUD": "O231010200201 Aportes a la seguridad social en salud pública",
                    "PENSIÓN": "O231010200101 Aportes a la seguridad social en pensiones públicas",
                    "CESANTÍAS": "O231010200301 Aportes de cesantías a fondos públicos"
                }
                
                datos_orientadores = {}
                for nombre, concepto in conceptos.items():
                    filtro = filtro_orientadores & (df_orientadores["Concepto de gasto"] == concepto)
                    filas = df_orientadores[filtro]
                    datos_orientadores[nombre] = {
                        "DISPONIBLE": filas["DISPONIBLE"].sum(),
                        "RP EMITIDOS": filas["RP EMITIDOS"].sum(),
                        "GIROS ACUMULADOS": filas["GIROS ACUMULADOS"].sum(),
                        "SALDO DE APROPIACION": filas["SALDO DE APROPIACION"].sum(),
                        "RECURSOS SIN EJECUTAR": filas["RECURSOS SIN EJECUTAR"].sum()
                    }
                
                # Calcular totales
                conceptos_nomina = ["SUELDO BASICO", "HORAS EXTRAS", "SUBSIDIO DE ALIMENTACIÓN", "AUXILIO DE TRANSPORTE", 
                                  "PRIMA DE SERVICIOS", "PRIMA DE VACACIONES", "PRIMA DE NAVIDAD"]
                datos_orientadores["SUELDOS"] = {col: sum(datos_orientadores[concepto][col] for concepto in conceptos_nomina) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_parafiscales = ["COMPENSAR", "ICBF", "SENA", "ESAP", "ESCUELAS TÉCNICAS"]
                datos_orientadores["TOTAL PARAFISCALES"] = {col: sum(datos_orientadores[concepto][col] for concepto in conceptos_parafiscales) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_fomag = ["SALUD", "PENSIÓN", "CESANTÍAS"]
                datos_orientadores["TOTAL FOMAG"] = {col: sum(datos_orientadores[concepto][col] for concepto in conceptos_fomag) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                # Total general
                datos_orientadores["ORIENTADORES REC PROPIOS"] = {
                    col: datos_orientadores["SUELDOS"][col] + datos_orientadores["TOTAL PARAFISCALES"][col] + datos_orientadores["TOTAL FOMAG"][col]
                    for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]
                }
                
                # Mostrar tabla
                if any(datos_orientadores["ORIENTADORES REC PROPIOS"][col] > 0 for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS"]):
                    mostrar_tabla_recursos_propios(datos_orientadores, "🧑‍🏫 ORIENTADORES - RECURSOS PROPIOS")
                else:
                    st.warning("⚠ No se encontraron datos para Orientadores")
                    
            except Exception as e:
                st.error(f"❌ Error al procesar orientadores: {str(e)}")

    # =========================================================================
    # 🆕 NUEVA SECCIÓN: GLOBAL
    # =========================================================================
    st.markdown("---")
    st.subheader("👩‍🏫📚👨‍🏫 GLOBAL")
    
    if df_principal is not None:
        with st.spinner("Procesando datos globales..."):
            try:
                # Procesar GLOBAL (códigos 33-57)
                df_global = df_principal.copy()
                df_global.insert(0, "Codigo_O", df_global.iloc[:, 0].where(df_global.iloc[:, 0].astype(str).str.startswith("  O")).ffill())
                df_global["Concepto de gasto"] = df_global["Concepto de gasto"].ffill()
                
                # Extraer últimos dos dígitos y filtrar 33-57
                ultimos_dos = pd.to_numeric(df_global["Codigo_O"].astype(str).str[-2:], errors="coerce")
                filtro_global = (
                    (df_global["Nombre"] == "Otros Distrito Inversión") &
                    (ultimos_dos >= 33) & (ultimos_dos <= 57)
                )
                
                # Aplicar mismos conceptos que Recursos Propios pero con filtro Global
                conceptos = {
                    "SUELDO BASICO": "O231010100101 Sueldo básico",
                    "HORAS EXTRAS": "O231010100102 Horas extras, dominicales, festivos y recargos",
                    "SUBSIDIO DE ALIMENTACIÓN": "O231010100104 Subsidio de alimentación",
                    "AUXILIO DE TRANSPORTE": "O231010100105 Auxilio de Transporte",
                    "PRIMA DE SERVICIOS": "O231010100106 Prima de servicio",
                    "PRIMA DE VACACIONES": "O23101010010802 Prima de vacaciones",
                    "PRIMA DE NAVIDAD": "O23101010010801 Prima de navidad",
                    "COMPENSAR": "O231010200401 Compensar",
                    "ICBF": "O2310102006 Aportes al ICBF",
                    "SENA": "O2310102007 Aportes al SENA",
                    "ESAP": "O2310102008 Aportes a la ESAP",
                    "ESCUELAS TÉCNICAS": "O2310102009 Aportes a escuelas industriales e institutos técnicos",
                    "SALUD": "O231010200201 Aportes a la seguridad social en salud pública",
                    "PENSIÓN": "O231010200101 Aportes a la seguridad social en pensiones públicas",
                    "CESANTÍAS": "O231010200301 Aportes de cesantías a fondos públicos"
                }
                
                datos_global = {}
                for nombre, concepto in conceptos.items():
                    filtro = filtro_global & (df_global["Concepto de gasto"] == concepto)
                    filas = df_global[filtro]
                    datos_global[nombre] = {
                        "DISPONIBLE": filas["DISPONIBLE"].sum(),
                        "RP EMITIDOS": filas["RP EMITIDOS"].sum(),
                        "GIROS ACUMULADOS": filas["GIROS ACUMULADOS"].sum(),
                        "SALDO DE APROPIACION": filas["SALDO DE APROPIACION"].sum(),
                        "RECURSOS SIN EJECUTAR": filas["RECURSOS SIN EJECUTAR"].sum()
                    }
                
                # Calcular totales
                conceptos_nomina = ["SUELDO BASICO", "HORAS EXTRAS", "SUBSIDIO DE ALIMENTACIÓN", "AUXILIO DE TRANSPORTE", 
                                  "PRIMA DE SERVICIOS", "PRIMA DE VACACIONES", "PRIMA DE NAVIDAD"]
                datos_global["SUELDOS"] = {col: sum(datos_global[concepto][col] for concepto in conceptos_nomina) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_parafiscales = ["COMPENSAR", "ICBF", "SENA", "ESAP", "ESCUELAS TÉCNICAS"]
                datos_global["TOTAL PARAFISCALES"] = {col: sum(datos_global[concepto][col] for concepto in conceptos_parafiscales) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                conceptos_fomag = ["SALUD", "PENSIÓN", "CESANTÍAS"]
                datos_global["TOTAL FOMAG"] = {col: sum(datos_global[concepto][col] for concepto in conceptos_fomag) for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]}
                
                # Total general
                datos_global["GLOBAL REC PROPIOS"] = {
                    col: datos_global["SUELDOS"][col] + datos_global["TOTAL PARAFISCALES"][col] + datos_global["TOTAL FOMAG"][col]
                    for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS", "SALDO DE APROPIACION", "RECURSOS SIN EJECUTAR"]
                }
                
                # Mostrar tabla
                if any(datos_global["GLOBAL REC PROPIOS"][col] > 0 for col in ["DISPONIBLE", "RP EMITIDOS", "GIROS ACUMULADOS"]):
                    mostrar_tabla_recursos_propios(datos_global, "🌍 GLOBAL - RECURSOS PROPIOS")
                else:
                    st.warning("⚠ No se encontraron datos para Global")
                    
            except Exception as e:
                st.error(f"❌ Error al procesar datos globales: {str(e)}")

# =============================================================================
# PANTALLA 3.1: RECURSOS PROPIOS PROYECCIONES
# =============================================================================
# =============================================================================
# PANTALLA 3.1: RECURSOS PROPIOS - PROYECCIONES
# =============================================================================
def mostrar_pantalla_recursos_propios_proyecciones():
    # Botón para volver atrás
    if st.button("← Volver a Recursos Propios", key="volver_proyecciones"):
        st.session_state.pagina_actual = "RECURSOS_PROPIOS"
        st.rerun()

    st.markdown("<div class='header'><h2>📈 PROYECCIONES - RECURSOS PROPIOS</h2></div>", unsafe_allow_html=True)

    # Rutas de los archivos
    ruta_sueldos = r"C:\Users\jrubr\OneDrive\Desktop\Sec Educación Bog\App Streamlit\RP_PROYECCION\1_ENERO\TOTAL\Nomina_Consolidada_Presupuestal(5,15,2025011,1201,2,I,).xls"
    ruta_aportes = r"C:\Users\jrubr\OneDrive\Desktop\Sec Educación Bog\App Streamlit\RP_PROYECCION\1_ENERO\TOTAL\Nomina_Consolidada_Presupuestal(5,15,2025011,1201,2,A,).xls"

    # Intentar cargar ambos archivos
    try:
        df_sueldos = pd.read_excel(ruta_sueldos)
        df_aportes = pd.read_excel(ruta_aportes)
    except FileNotFoundError:
        st.error("❌ No se encontró alguno de los archivos de proyección. Verifica las rutas.")
        return
    except Exception as e:
        st.error(f"❌ Error al cargar los archivos: {str(e)}")
        return

    # Mostrar dataframes en la pantalla
    st.markdown("### 👷‍♂️ SUELDO")
    st.dataframe(df_sueldos, use_container_width=True)

    st.markdown("---")

    st.markdown("### 🏛️ APORTES")
    st.dataframe(df_aportes, use_container_width=True)


# =============================================================================
# PANTALLA 4: SISTEMA GENERAL DE PARTICIPACIONES
# =============================================================================
def mostrar_pantalla_sgp():
    if st.button("← Volver al Inicio", key="volver_sgp"):
        st.session_state.pagina_actual = "INICIO"
        st.rerun()
    
    # Encabezado con ambos logos
    st.markdown("<div class='contenedor-logos'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("logo_bogota.png", width=150, use_container_width=True)
    with col2:
        st.markdown("<div class='header'><h2>SISTEMA GENERAL DE PARTICIPACIONES</h2></div>", unsafe_allow_html=True)
    with col3:
        st.image("logo_alcaldía_mayor.png", width=150, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.info("🚧 Módulo en construcción - Esta sección estará disponible próximamente.")

# =============================================================================
# ROUTER PRINCIPAL - CORREGIDO
# =============================================================================
def main():
    # Inicializar estado de sesión
    if "pagina_actual" not in st.session_state:
        st.session_state.pagina_actual = "INICIO"
    
    # Cargar estilos
    cargar_estilos()
    
    # Navegación entre páginas - ACTUALIZADO CON LA NUEVA PANTALLA
    if st.session_state.pagina_actual == "INICIO":
        mostrar_pantalla_inicial()
    elif st.session_state.pagina_actual == "POR_FUENTE":
        mostrar_pantalla_por_fuente()
    elif st.session_state.pagina_actual == "RECURSOS_PROPIOS":
        mostrar_pantalla_recursos_propios()
    elif st.session_state.pagina_actual == "RECURSOS_PROPIOS_PROYECCIONES":  # ✅ NUEVA PANTALLA
        mostrar_pantalla_recursos_propios_proyecciones()
    elif st.session_state.pagina_actual == "SGP":
        mostrar_pantalla_sgp()

if __name__ == "__main__":
    main()