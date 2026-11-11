# =====================================================================
# AUTO-LANZADOR: Permite presionar el botón de Play (▶️) directamente
# =====================================================================
import sys
from streamlit.runtime import exists

if not exists():
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())
# =====================================================================

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sympy as sp
from sympy.parsing.sympy_parser import (
    implicit_multiplication_application,
    standard_transformations,
)

st.set_page_config(
    page_title="NumIntegration Pro",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <meta name="google" content="notranslate">
    <style>
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    .metric-card {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
        color: white;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
        margin: 15px 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

EJERCICIOS_TALLER = {
    "1. Regla Trapezoidal": {
        "∫ e^(-x^2) dx  en [0, 1] con n = 1": {
            "f": "exp(-x^2)",
            "a": 0.0,
            "b": 1.0,
            "n": 1,
        },
        "∫ (x^2 - 3x + 2) dx  en [2, 5] con n = 6": {
            "f": "x^2 - 3x + 2",
            "a": 2.0,
            "b": 5.0,
            "n": 6,
        },
        "Personalizado (Escribir función propia)": None,
    },
    "2. Método de Jorge Boole": {
        "∫ x^4 dx  en [0, 2] con n = 4": {
            "f": "x^4",
            "a": 0.0,
            "b": 2.0,
            "n": 4,
        },
        "∫ x^4 dx  en [0, 2] con n = 8 (Mayor precisión)": {
            "f": "x^4",
            "a": 0.0,
            "b": 2.0,
            "n": 8,
        },
        "Personalizado (Escribir función propia)": None,
    },
    "3. Simpson 3/8 Newton-Cotes": {
        "∫ sqrt(x + 1) dx  en [0, 3] con n = 3": {
            "f": "sqrt(x + 1)",
            "a": 0.0,
            "b": 3.0,
            "n": 3,
        },
        "∫ cos(x) dx  en [0, 6] con n = 6": {
            "f": "cos(x)",
            "a": 0.0,
            "b": 6.0,
            "n": 6,
        },
        "Personalizado (Escribir función propia)": None,
    },
    "4. Simpson 1/3 Newton-Cotes": {
        "∫ (x^3 + 2x) dx  en [0, 2] con n = 2": {
            "f": "x^3 + 2x",
            "a": 0.0,
            "b": 2.0,
            "n": 2,
        },
        "∫ (1/x) dx  en [1, 3] con n = 4": {
            "f": "1/x",
            "a": 1.0,
            "b": 3.0,
            "n": 4,
        },
        "Personalizado (Escribir función propia)": None,
    },
    "5. Simpson Abierto / Compuesto": {
        "∫ (x^3 + 2x) dx  en [0, 2] con n = 4": {
            "f": "x^3 + 2x",
            "a": 0.0,
            "b": 2.0,
            "n": 4,
        },
        "Personalizado (Escribir función propia)": None,
    },
}

# Inicialización segura
if "expr_input" not in st.session_state:
    st.session_state["expr_input"] = "x^3 + 2x"
if "lim_a" not in st.session_state:
    st.session_state["lim_a"] = 0.0
if "lim_b" not in st.session_state:
    st.session_state["lim_b"] = 2.0
if "n_val" not in st.session_state:
    st.session_state["n_val"] = 2


def add_to_formula(token):
    if token == "CLEAR":
        st.session_state["expr_input"] = ""
    elif token == "DEL":
        st.session_state["expr_input"] = st.session_state["expr_input"][:-1]
    else:
        st.session_state["expr_input"] += token


def cargar_ejercicio_callback():
    opcion = st.session_state.get("ejercicio_seleccionado")
    met = st.session_state.get("metodo_seleccionado")
    if opcion == "Personalizado (Escribir función propia)":
        st.session_state["expr_input"] = ""
    elif opcion and met and EJERCICIOS_TALLER[met].get(opcion):
        datos = EJERCICIOS_TALLER[met][opcion]
        st.session_state["expr_input"] = datos["f"]
        st.session_state["lim_a"] = float(datos["a"])
        st.session_state["lim_b"] = float(datos["b"])
        st.session_state["n_val"] = int(datos["n"])


def on_metodo_change():
    met = st.session_state.get("metodo_seleccionado")
    if met:
        primera = list(EJERCICIOS_TALLER[met].keys())[0]
        st.session_state["ejercicio_seleccionado"] = primera
        datos = EJERCICIOS_TALLER[met][primera]
        if datos:
            st.session_state["expr_input"] = datos["f"]
            st.session_state["lim_a"] = float(datos["a"])
            st.session_state["lim_b"] = float(datos["b"])
            st.session_state["n_val"] = int(datos["n"])
        else:
            st.session_state["expr_input"] = ""


transformaciones = standard_transformations + (
    implicit_multiplication_application,
)


def preparar_expresion(expr_str):
    if not expr_str or not expr_str.strip():
        return None
    limpia = (
        expr_str.replace("^", "**").replace("sen(", "sin(").replace("ln(", "log(")
    )
    limpia = limpia.replace("e**", "exp").replace("e^", "exp")
    return sp.parse_expr(
        limpia, transformations=transformaciones, evaluate=False
    )


def evaluar_f(expr_str, val_x):
    simbolo_x = sp.Symbol("x")
    expr_sp = preparar_expresion(expr_str)
    if expr_sp is None:
        return 0.0
    res = expr_sp.subs(simbolo_x, val_x)
    return float(res.evalf() if hasattr(res, "evalf") else res)


# --- BARRA LATERAL ---
with st.sidebar:
    st.title("⚙️ Configuración")

    metodo = st.selectbox(
        "Seleccione el Método:",
        list(EJERCICIOS_TALLER.keys()),
        key="metodo_seleccionado",
        on_change=on_metodo_change,
    )

    st.markdown("---")
    st.subheader("📚 Ejercicios del Taller")
    lista_opciones = list(EJERCICIOS_TALLER[metodo].keys())
    st.selectbox(
        "Cargar ejercicio predefinido:",
        lista_opciones,
        key="ejercicio_seleccionado",
        on_change=cargar_ejercicio_callback,
    )

    st.markdown("---")
    st.subheader("Parámetros del Intervalo")

    # Controles dinámicos de n para TODOS los métodos
    if "Trapezoidal" in metodo:
        n = st.number_input(
            "Particiones (n ≥ 1):", min_value=1, step=1, key="n_val"
        )
    elif "Boole" in metodo:
        n = st.number_input(
            "Particiones n (múltiplo de 4: 4, 8, 12...):",
            min_value=4,
            step=4,
            key="n_val",
        )
    elif "3/8" in metodo:
        n = st.number_input(
            "Particiones n (múltiplo de 3: 3, 6, 9...):",
            min_value=3,
            step=3,
            key="n_val",
        )
    elif "1/3 Newton" in metodo:
        n = st.number_input(
            "Particiones n (debe ser PAR: 2, 4, 6...):",
            min_value=2,
            step=2,
            key="n_val",
        )
    elif "Abierto" in metodo:
        n = st.number_input(
            "Particiones n (debe ser PAR: 2, 4, 6...):",
            min_value=2,
            step=2,
            key="n_val",
        )

    col_a, col_b = st.columns(2)
    with col_a:
        a = st.number_input(
            "Límite inferior (a):", format="%g", step=0.5, key="lim_a"
        )
    with col_b:
        b = st.number_input(
            "Límite superior (b):", format="%g", step=0.5, key="lim_b"
        )


# --- PANEL PRINCIPAL ---
st.title("📐 Calculadora de Integración Numérica")

st.markdown("### 1. Función Matemática $f(x)$")
st.text_input(
    "Escriba o modifique la función:",
    key="expr_input",
    placeholder="Ej: x^3 + 2x, 1/x, sqrt(x + 1), exp(-x^2), cos(x)",
)

expr_actual = st.session_state.get("expr_input", "").strip()

if not expr_actual:
    st.info("✍️ Escribe una función matemática o selecciona un ejercicio del taller.")
else:
    try:
        expr_sp = preparar_expresion(expr_actual)
        latex_f = sp.latex(expr_sp)
        limite_a_str = f"{a:g}"
        limite_b_str = f"{b:g}"
        st.info("📖 **VISTA PREVIA DEL EJERCICIO:**")
        st.latex(
            rf"\int_{{{limite_a_str}}}^{{{limite_b_str}}} \left( {latex_f} \right) \, dx \quad \text{{con }} n = {n}"
        )
    except Exception:
        st.warning("⚠️ Escribiendo función...")

with st.expander("⌨️ Teclado de Símbolos Rápidos", expanded=False):
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.button("x", on_click=add_to_formula, args=("x",))
    c2.button("^2", on_click=add_to_formula, args=("^2",))
    c3.button("^3", on_click=add_to_formula, args=("^3",))
    c4.button("^", on_click=add_to_formula, args=("^",))
    c5.button("√x", on_click=add_to_formula, args=("sqrt(",))
    c6.button("(", on_click=add_to_formula, args=("(",))
    c7.button(")", on_click=add_to_formula, args=(")",))
    c8.button("/", on_click=add_to_formula, args=("/",))

    c9, c10, c11, c12, c13, c14, c15, c16 = st.columns(8)
    c9.button("+", on_click=add_to_formula, args=("+",))
    c10.button("-", on_click=add_to_formula, args=("-",))
    c11.button("·", on_click=add_to_formula, args=("*",))
    c12.button("eˣ", on_click=add_to_formula, args=("exp(",))
    c13.button("ln(x)", on_click=add_to_formula, args=("log(",))
    c14.button("cos(x)", on_click=add_to_formula, args=("cos(",))
    c15.button("sin(x)", on_click=add_to_formula, args=("sin(",))
    c16.button("π", on_click=add_to_formula, args=("pi",))

    c17, c18 = st.columns([1, 1])
    c17.button("⌫ Borrar", on_click=add_to_formula, args=("DEL",))
    c18.button(
        "Limpiar todo", on_click=add_to_formula, args=("CLEAR",), type="primary"
    )

# --- BOTÓN DE CÁLCULO ---
if st.button("🚀 Calcular Integral Paso a Paso", type="primary"):
    try:
        if not expr_actual:
            st.error("Por favor ingresa una función matemática antes de calcular.")
            st.stop()

        if a >= b:
            st.error("El límite inferior (a) debe ser estrictamente menor al límite superior (b).")
            st.stop()

        delta = (b - a) / n
        xs = [a + i * delta for i in range(n + 1)]
        fs = [evaluar_f(expr_actual, x) for x in xs]

        if "Trapezoidal" in metodo:
            coefs = [1] + [2] * (n - 1) + [1] if n > 1 else [1, 1]
            factor = delta / 2
            factor_latex = r"\frac{\Delta}{2}"
            nombre_metodo = "Regla Trapezoidal"

        elif "Boole" in metodo:
            # Coeficientes de Boole para cualquier múltiplo de 4
            coefs = [7]
            for i in range(1, n):
                if i % 4 == 0:
                    coefs.append(14)
                elif i % 2 != 0:
                    coefs.append(32)
                else:
                    coefs.append(12)
            coefs.append(7)
            factor = (2 * delta) / 45
            factor_latex = r"\frac{2\Delta}{45}"
            nombre_metodo = "Método de Jorge Boole"

        elif "3/8" in metodo:
            coefs = [1]
            for i in range(1, n):
                coefs.append(2 if i % 3 == 0 else 3)
            coefs.append(1)
            factor = (3 * delta) / 8
            factor_latex = r"\frac{3\Delta}{8}"
            nombre_metodo = "Simpson 3/8 Newton-Cotes"

        elif "1/3 Newton" in metodo or "Abierto" in metodo:
            # Coeficientes de Simpson 1/3 para cualquier n par
            coefs = [1] + [4 if i % 2 != 0 else 2 for i in range(1, n)] + [1]
            factor = delta / 3
            factor_latex = r"\frac{\Delta}{3}"
            nombre_metodo = "Simpson 1/3 Newton-Cotes" if "1/3 Newton" in metodo else "Simpson Abierto / Compuesto"

        productos = [c * f for c, f in zip(coefs, fs)]
        suma_ponderada = sum(productos)
        integral_resultado = factor * suma_ponderada

        st.markdown(
            f"""
        <div class="metric-card">
            <span style="letter-spacing: 2px; text-transform: uppercase; font-size: 13px; opacity: 0.85;">{nombre_metodo}</span>
            <h1 style="font-size: 40px; margin: 10px 0; color: white;">I ≈ {integral_resultado:.8f}</h1>
            <p style="margin: 0; opacity: 0.9;">Intervalo: [{a:g}, {b:g}] &nbsp;|&nbsp; Δ = {delta:.6f} &nbsp;|&nbsp; n = {n}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        tab_grafica, tab_tabla, tab_pasos = st.tabs(
            ["📈 Gráfica Interactiva", "📋 Tabla de Datos", "📝 Explicación Paso a Paso"]
        )

        with tab_grafica:
            x_fino = np.linspace(a - (b - a) * 0.08, b + (b - a) * 0.08, 300)
            y_fino = [evaluar_f(expr_actual, x) for x in x_fino]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=x_fino,
                    y=y_fino,
                    mode="lines",
                    name="f(x)",
                    line=dict(color="#f59e0b", width=3),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=fs,
                    mode="lines+markers",
                    name="Aproximación Numérica",
                    fill="tozeroy",
                    fillcolor="rgba(99, 102, 241, 0.25)",
                    line=dict(color="#4f46e5", width=2),
                    marker=dict(size=8, color="#4338ca"),
                )
            )

            fig.update_layout(
                title=f"Aproximación geométrica con {nombre_metodo}",
                xaxis_title="x",
                yaxis_title="f(x)",
                template="plotly_white",
                height=450,
                hovermode="x unified",
            )
            st.plotly_chart(fig, width="stretch")

        with tab_tabla:
            df = pd.DataFrame(
                {
                    "Punto": [f"x_{i+1}" if "Boole" in metodo or "3/8" in metodo or "1/3" in metodo else f"x_{i}" for i in range(len(xs))],
                    "x_i": xs,
                    "f(x_i)": fs,
                    "Coeficiente": coefs,
                    "Coef × f(x_i)": productos,
                }
            )
            st.dataframe(
                df.style.format("{:.6f}", subset=["x_i", "f(x_i)", "Coef × f(x_i)"]),
                width="stretch"
            )
            st.info(f"**Suma total ponderada (Σ):** `{suma_ponderada:.6f}`")

        with tab_pasos:
            st.markdown("### 🔍 Desarrollo Paso a Paso")
            st.markdown(r"#### Paso 1: Tamaño de paso ($\Delta$)")
            st.latex(
                rf"\Delta = \frac{{b - a}}{{n}} = \frac{{{b:g} - {a:g}}}{{{n}}} = {delta:.6f}"
            )

            st.markdown("#### Paso 2: Puntos de evaluación")
            puntos_str = ", ".join([f"x_{i} = {val:.4f}" for i, val in enumerate(xs)])
            st.write(f"Valores calculados de x: `{puntos_str}`")

            st.markdown("#### Paso 3: Sustitución en la fórmula del método")
            terminos_str = " + ".join([f"({c} \\times {f:.4f})" for c, f in zip(coefs, fs)])
            st.latex(rf"I = {factor_latex} \cdot \left[ {terminos_str} \right]")
            st.latex(rf"I \approx ({factor:.6f}) \cdot ({suma_ponderada:.6f})")

            st.markdown("#### Paso 4: Resultado")
            st.success(f"**Integral aproximada:** $I \\approx {integral_resultado:.8f}$")

    except Exception as e:
        st.error(f"Error al evaluar la función: {e}. Verifique la sintaxis.")