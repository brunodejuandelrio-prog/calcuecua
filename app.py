from flask import Flask, request, jsonify
from flask_cors import CORS
from sympy import sympify, solve, Eq, expand, simplify, together, latex

app = Flask(__name__)
CORS(app)  # Esto permite que tu pantalla blanca hable con el servidor

@app.route('/resolver', methods=['POST'])
def resolver():
    datos = request.json
    entrada = datos.get('expresion', '').strip()
    entrada_procesada = entrada.replace("raiz", "sqrt")
    
    try:
        # Si es un sistema (tiene comas)
        if ',' in entrada_procesada:
            partes = entrada_procesada.split(',')
            lista_eqs = []
            for eq_texto in partes:
                if not eq_texto.strip(): continue
                if '=' in eq_texto:
                    lados = eq_texto.split('=')
                    lista_eqs.append(Eq(sympify(lados[0]), sympify(lados[1])))
                else:
                    lista_eqs.append(Eq(sympify(eq_texto), 0))
            
            letras = sorted(list(set().union(*(eq.free_symbols for eq in lista_eqs))), key=lambda s: s.name)
            solucion = solve(lista_eqs, letras)
            
            resultados = []
            if isinstance(solucion, dict):
                for var, valor in solucion.items():
                    val_p = valor.evalf(4) if hasattr(valor, 'evalf') and not valor.is_Integer else valor
                    resultados.append(f"$${latex(var)} = {latex(val_p)}$$")
            elif isinstance(solucion, list) and len(solucion) > 0:
                if isinstance(solucion[0], tuple):
                    for var, valor in zip(letras, solucion[0]):
                        val_p = valor.evalf(4) if hasattr(valor, 'evalf') and not valor.is_Integer else valor
                        resultados.append(f"$${latex(var)} = {latex(val_p)}$$")
            return jsonify({'tipo': 'sistema', 'resultados': resultados})
        
        # Si es una ecuación sola
        else:
            if '=' in entrada_procesada:
                partes = entrada_procesada.split('=')
                ecuacion = Eq(sympify(partes[0]), sympify(partes[1]))
            else:
                ecuacion = sympify(entrada_procesada)
                
            letras = sorted(list(ecuacion.free_symbols), key=lambda s: s.name)
            resultados = []
            
            for letra in letras:
                soluciones = solve(ecuacion, letra)
                for sol in soluciones:
                    sol_limpia = simplify(together(expand(sol)))
                    resultados.append(f"$${latex(letra)} = {latex(sol_limpia)}$$")
            return jsonify({'tipo': 'individual', 'resultados': resultados})
            
    except Exception:
        return jsonify({'error': 'Error al procesar el cálculo'}), 400

if __name__ == '__main__':
    app.run(debug=True)
