from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# Função para criar a tabela no banco de dados, se não existir
def create_table():
    with sqlite3.connect('dados.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                idade INTEGER,
                cor TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('menu.html')

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        idade = request.form.get('idade', '')
        cor = request.form.get('cor', '')

        with sqlite3.connect('dados.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dados (nome, idade, cor) VALUES (?, ?, ?)
            ''', (nome, idade, cor))
            conn.commit()
        return render_template('menu.html', message='Dados adicionados com sucesso!')
    return render_template('menu.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    resultados = []
    estatisticas = {}
    total_pessoas = 0
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        idade = request.form.get('idade', '')
        cor = request.form.get('cor', '')

        query = 'SELECT nome, idade, cor FROM dados WHERE 1=1'
        params = []

        if nome:
            query += ' AND nome LIKE ?'
            params.append(f'%{nome}%')
        if idade:
            query += ' AND idade = ?'
            params.append(idade)
        if cor:
            query += ' AND cor LIKE ?'
            params.append(f'%{cor}%')

        with sqlite3.connect('dados.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()

            # Calcular estatísticas
            cursor.execute('SELECT COUNT(*) FROM dados')
            total_pessoas = cursor.fetchone()[0]
            cursor.execute('SELECT nome, COUNT(*) FROM dados GROUP BY nome')
            estatisticas['nomes'] = cursor.fetchall()
            cursor.execute('SELECT AVG(idade) FROM dados')
            estatisticas['idade_media'] = cursor.fetchone()[0]
            cursor.execute('SELECT cor, COUNT(*) FROM dados GROUP BY cor ORDER BY COUNT(*) DESC LIMIT 1')
            estatisticas['cor_mais_comum'] = cursor.fetchone()

    return render_template('consulta.html', resultados=resultados, estatisticas=estatisticas, total_pessoas=total_pessoas)

@app.route('/limpar', methods=['POST'])
def limpar():
    with sqlite3.connect('dados.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM dados')
        conn.commit()
    return render_template('consulta.html', resultados=[], message='Todos os dados foram removidos com sucesso!')

if __name__ == '__main__':
    create_table()
    app.run(debug=True)



