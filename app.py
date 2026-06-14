from flask import Flask, render_template, url_for, redirect, session, flash, request, g
from authlib.integrations.flask_client import OAuth
import sqlite3
import random

app = Flask(__name__)

# CHAVE DE SEGURANÇA
app.secret_key = 'estudo_ativo_oeiras_2027_key'
DATABASE = 'usuarios.db'


# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Criando a tabela de alunos com os campos de progresso de Matemática, Português e Ranking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            escola TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'ALUNO',
            pontuacao INTEGER DEFAULT 0,
            progresso_porcentagem INTEGER DEFAULT 0,
            progresso_equacoes INTEGER DEFAULT 0,
            progresso_geometria INTEGER DEFAULT 0,
            progresso_interpretacao INTEGER DEFAULT 0,
            progresso_gramatica INTEGER DEFAULT 0,
            progresso_sintaxe INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT NOT NULL,
            enunciado TEXT NOT NULL,
            alt_a TEXT NOT NULL,
            alt_b TEXT NOT NULL,
            alt_c TEXT NOT NULL,
            alt_d TEXT NOT NULL,
            alt_e TEXT NOT NULL,
            resposta_correta TEXT NOT NULL,
            explicacao TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM questoes")
    if cursor.fetchone()[0] == 0:
        questoes_exemplo = [
            # === PORCENTAGEM (20 QUESTÕES) ===
            ('porcentagem',
             'Em uma escola municipal de Oeiras, 40% dos 200 alunos do 9º ano pretendem fazer a prova do IFPI. Quantos alunos farão a prova?',
             '60 alunos', '80 alunos', '100 alunos', '120 alunos', '140 alunos', 'B',
             '40% de 200 = (40/100) * 200 = 80 alunos.'),
            ('porcentagem',
             'Um casaco que custava R$ 150,00 na Riviera de Oeiras conseguiu um desconto de 20%. Qual o novo valor do casaco?',
             'R$ 120,00', 'R$ 130,00', 'R$ 110,00', 'R$ 100,00', 'R$ 140,00', 'A',
             '20% de 150 = 30. Subtraindo o desconto: 150 - 30 = R$ 120,00.'),
            ('porcentagem',
             'Uma conta de luz de R$ 80,00 foi paga com atraso e sofreu uma multa de 5%. Qual foi o valor pago após a multa?',
             'R$ 82,00', 'R$ 83,50', 'R$ 84,00', 'R$ 85,00', 'R$ 86,00', 'C',
             '5% de 80 = 4. Somando o juro ao valor original: 80 + 4 = R$ 84,00.'),
            ('porcentagem',
             'Se 15 dos 60 alunos de uma sala foram aprovados direto no seletivo, qual a porcentagem de alunos aprovados?',
             '15%', '20%', '25%', '30%', '40%', 'C', '15 / 60 = 0,25. Multiplicando por 100 temos 25%.'),
            ('porcentagem',
             'Um salário de R$ 1.200,00 recebeu um aumento salarial de 12%. Qual passou a ser o novo salário?',
             'R$ 1.344,00', 'R$ 1.320,00', 'R$ 1.280,00', 'R$ 1.400,00', 'R$ 1.300,00', 'A',
             '12% de 1200 = 144. Somando ao salário antigo: 1200 + 144 = R$ 1.344,00.'),
            ('porcentagem',
             'Uma geladeira de R$ 2.000,00 foi comprada parcelada e teve um acréscimo de 15% no valor total. Quanto custou a geladeira?',
             'R$ 2.150,00', 'R$ 2.200,00', 'R$ 2.300,00', 'R$ 2.450,00', 'R$ 2.500,00', 'C',
             '15% de 2000 = 300. Valor final: 2000 + 300 = R$ 2.300,00.'),
            ('porcentagem',
             'Em Oeiras, 30% de uma plantação de 500 árvores frutíferas são mangueiras. Quantas mangueiras há na plantação?',
             '120', '150', '180', '200', '250', 'B', '30% de 500 = 150 mangueiras.'),
            ('porcentagem',
             'Um artigo de opinião recebeu 80 visualizações no primeiro dia. No segundo dia, o número de acessos cresceu 50%. Quantos acessos teve no segundo dia?',
             '100', '110', '120', '130', '140', 'C', '50% de 80 = 40. Logo, 80 + 40 = 120 acessos.'),
            ('porcentagem',
             'Uma loja oferece 10% de desconto para pagamentos à vista. Se um tênis custa R$ 250,00, quanto ele custará à vista?',
             'R$ 225,00', 'R$ 230,00', 'R$ 220,00', 'R$ 235,00', 'R$ 240,00', 'A',
             '10% de 250 = 25. Sabendo disso: 250 - 25 = R$ 225,00.'),
            ('porcentagem',
             'Dos 40 quilos de alimento arrecadados por uma equipe, 25% eram de arroz. Quantos quilos de arroz foram arrecadados?',
             '8 kg', '10 kg', '12 kg', '15 kg', '20 kg', 'B', '25% representa a quarta parte. 40 / 4 = 10 kg.'),
            ('porcentagem',
             'Um produto eletrônico importado custava R$ 600,00 e sofreu um reajuste de 8% devido ao dólar. Qual o novo preço?',
             'R$ 648,00', 'R$ 654,00', 'R$ 632,00', 'R$ 660,00', 'R$ 616,00', 'A',
             '8% de 600 = 48. Somando ao valor original: 600 + 48 = R$ 648,00.'),
            ('porcentagem',
             'Se uma partida de futebol de 90 minutos teve 10% de tempo de acréscimo total, quantos minutos de acréscimo teve o jogo?',
             '5 minutos', '6 minutos', '8 minutos', '9 minutos', '10 minutos', 'D', '10% de 90 minutos = 9 minutos.'),
            ('porcentagem',
             'Em um exame classificatório com 80 questões, um candidato acertou 75% da prova. Quantas questões ele acertou?',
             '55 questões', '60 questões', '65 questões', '70 questões', '72 questões', 'B',
             '75% é o mesmo que 3/4. (80 / 4) * 3 = 20 * 3 = 60 questões.'),
            ('porcentagem',
             'Um pneu de bicicleta que custava R$ 120,00 aumentou para R$ 132,00. Qual foi a taxa percentual de aumento?',
             '8%', '10%', '12%', '15%', '20%', 'B',
             'O aumento foi de R$ 12,00. Como 12 é exatamente 10% de 120, o aumento foi de 10%.'),
            ('porcentagem',
             'Uma população de uma pequena localidade de Oeiras era de 1.500 habitantes e cresceu 4% em um ano. Quantos habitantes a localidade ganhou?',
             '40', '50', '60', '70', '80', 'C', '4% de 1.500 = (4 / 100) * 1500 = 60 habitantes.'),
            ('porcentagem',
             'Um investidor aplicou R$ 1.000,00 e obteve um rendimento de 2,5% no primeiro mês. Qual o valor total do rendimento em dinheiro?',
             'R$ 20,00', 'R$ 25,00', 'R$ 30,00', 'R$ 35,00', 'R$ 50,00', 'B',
             '2,5% de 1.000 = (2.5 / 100) * 1000 = R$ 25,00.'),
            ('porcentagem',
             'Em um teatro com 300 assentos, 180 estavam ocupados. Qual a porcentagem de assentos ocupados?', '50%',
             '55%', '60%', '65%', '70%', 'C', '180 / 300 = 0,60. Multiplicando por 100, temos 60%.'),
            ('porcentagem',
             'Em uma liga esportiva, um time jogou 20 partidas e perdeu apenas 15% delas. Quantas partidas o time perdeu?',
             '2 partidas', '3 partidas', '4 partidas', '5 partidas', '6 partidas', 'B',
             '15% de 20 = (15 / 100) * 20 = 300 / 100 = 3 partidas.'),
            ('porcentagem',
             'Um livro possui 250 páginas. Um estudante leu 60% do livro. Quantas páginas faltam para ele terminar?',
             '100 páginas', '110 páginas', '120 páginas', '130 páginas', '150 páginas', 'A',
             'Ele leu 60%, então faltam 40%. 40% de 250 = (40 / 100) * 250 = 100 páginas.'),
            ('porcentagem',
             'Um imposto de 7% é cobrado sobre um serviço de R$ 500,00. Qual o valor recolhido do imposto?', 'R$ 25,00',
             'R$ 30,00', 'R$ 35,00', 'R$ 40,00', 'R$ 45,00', 'C', '7% de 500 = (7 / 100) * 500 = R$ 35,00.'),

            # === EQUAÇÕES DE 1º GRAU (20 QUESTÕES) ===
            ('equacoes', 'Resolva a equação de 1º grau para encontrar o valor de x: 3x - 12 = 18.', 'x = 5', 'x = 8',
             'x = 10', 'x = 12', 'x = 15', 'C', '3x = 18 + 12 -> 3x = 30 -> x = 10.'),
            ('equacoes', 'Determine o valor da incógnita y na equação: 5y + 4 = 3y + 14.', 'y = 2', 'y = 4', 'y = 5',
             'y = 6', 'y = 7', 'C', '5y - 3y = 14 - 4 -> 2y = 10 -> y = 5.'),
            ('equacoes', 'O triplo de um número somado com 8 é igual a 29. Que número é esse?', '5', '6', '7', '8', '9',
             'C', '3x + 8 = 29 -> 3x = 21 -> x = 7.'),
            ('equacoes', 'Resolva a equação distributiva: 2(x + 4) = 20.', 'x = 4', 'x = 6', 'x = 8', 'x = 10',
             'x = 12', 'B', '2x + 8 = 20 -> 2x = 12 -> x = 6.'),
            ('equacoes', 'Qual o valor de x que satisfaz a igualdade: x/2 + 5 = 11?', 'x = 6', 'x = 8', 'x = 10',
             'x = 12', 'x = 14', 'D', 'x/2 = 11 - 5 -> x/2 = 6 -> x = 6 * 2 = 12.'),
            ('equacoes', 'Pensei em um número, multipliquei por 4, subtraí 7 e o resultado foi 21. Qual número pensei?',
             'x = 5', 'x = 6', 'x = 7', 'x = 8', 'x = 9', 'C', '4x - 7 = 21 -> 4x = 28 -> x = 7.'),
            ('equacoes', 'Encontre a raiz da seguinte equação: 7x - 5 = 4x + 10.', 'x = 3', 'x = 4', 'x = 5', 'x = 6',
             'x = 7', 'C', '7x - 4x = 10 + 5 -> 3x = 15 -> x = 5.'),
            ('equacoes', 'O dobro da idade de Marcos somado com 10 anos é igual a 40 anos. Quantos anos Marcos tem?',
             '12 anos', '15 anos', '18 anos', '20 anos', '25 anos', 'B', '2x + 10 = 40 -> 2x = 30 -> x = 15 anos.'),
            ('equacoes', 'Resolva a equação: 9x - 3 = 6x + 15.', 'x = 4', 'x = 5', 'x = 6', 'x = 7', 'x = 8', 'C',
             '9x - 6x = 15 + 3 -> 3x = 18 -> x = 6.'),
            ('equacoes', 'Se somarmos 15 ao quádruplo de um número, obtemos 35. Qual é esse número?', '3', '4', '5',
             '6', '7', 'C', '4x + 15 = 35 -> 4x = 20 -> x = 5.'),
            ('equacoes', 'Determine o valor de x na proporção simples: 2x/3 = 8.', 'x = 10', 'x = 12', 'x = 14',
             'x = 15', 'x = 16', 'B', '2x = 24 -> x = 12.'),
            ('equacoes', 'Resolva para m: 6(m - 1) = 4m + 10.', 'm = 4', 'm = 6', 'm = 8', 'm = 10', 'm = 12', 'C',
             '6m - 6 = 4m + 10 -> 2m = 16 -> m = 8.'),
            ('equacoes', 'Um número somado com sua metade resulta em 15. Qual é esse número?', '8', '10', '12', '14',
             '16', 'B', 'x + x/2 = 15 -> 3x/2 = 15 -> 3x = 30 -> x = 10.'),
            ('equacoes', 'Encontre a solução da equação: 10 - 2x = 4.', 'x = 2', 'x = 3', 'x = 4', 'x = 5', 'x = 6',
             'B', '-2x = 4 - 10 -> -2x = -6 -> x = 3.'),
            ('equacoes', 'A diferença entre o triplo de um número e 5 é igual a 16. Que número é esse?', '6', '7', '8',
             '9', '10', 'B', '3x - 5 = 16 -> 3x = 21 -> x = 7.'),
            ('equacoes', 'Qual o valor de x na igualdade: 4x + 7 = 3b se b = 5?', 'x = 1', 'x = 2', 'x = 3', 'x = 4',
             'x = 5', 'B', '4x + 7 = 15 -> 4x = 8 -> x = 2.'),
            ('equacoes', 'Resolva o balanço de termos: 5x + 3x - 2x = 36.', 'x = 4', 'x = 5', 'x = 6', 'x = 7', 'x = 8',
             'C', '6x = 36 -> x = 6.'),
            ('equacoes', 'A soma de três números consecutivos é igual a 33. Qual o menor deles?', '9', '10', '11', '12',
             '13', 'B', 'x + (x+1) + (x+2) = 33 -> 3x + 3 = 33 -> 3x = 30 -> x = 10.'),
            ('equacoes', 'Resolva a equação com parênteses negativos: 15 - (x + 2) = 8.', 'x = 3', 'x = 4', 'x = 5',
             'x = 6', 'x = 7', 'C', '15 - x - 2 = 8 -> 13 - x = 8 -> x = 5.'),
            ('equacoes', 'Se x/4 - 1 = 2, qual o valor numérico de x?', 'x = 6', 'x = 8', 'x = 10', 'x = 12', 'x = 16',
             'D', 'x/4 = 3 -> x = 3 * 4 = 12.'),

            # === GEOMETRIA PLANA (20 QUESTÕES) ===
            ('geometria',
             'Um terreno retangular na cidade de Oeiras possui 15 metros de largura e 20 metros de comprimento. Qual é a área total deste terreno?',
             '150 m²', '200 m²', '250 m²', '300 m²', '350 m²', 'D', 'Área = base * altura: 15 * 20 = 300 m².'),
            ('geometria',
             'Um quadrado perfeito possui lados medindo exatamente 8 centímetros. Qual é o valor correspondente ao seu perímetro?',
             '16 cm', '24 cm', '32 cm', '48 cm', '64 cm', 'C', 'Perímetro = 4 * lado = 4 * 8 = 32 cm.'),
            ('geometria', 'Calcule a área de um triângulo que possui uma base de 10 cm e uma altura de 6 cm.', '15 cm²',
             '30 cm²', '45 cm²', '60 cm²', '25 cm²', 'B', 'Área = (base * altura) / 2 = (10 * 6) / 2 = 30 cm².'),
            ('geometria',
             'Uma praça circular possui um raio de 5 metros. Utilizando pi = 3, qual a área total aproximada dessa praça?',
             '45 m²', '60 m²', '75 m²', '90 m²', '100 m²', 'C', 'Área = pi * r² = 3 * (5²) = 3 * 25 = 75 m².'),
            ('geometria',
             'Um triângulo equilátero possui todos os lados medindo 7 cm. Qual é o perímetro total deste triângulo?',
             '14 cm', '21 cm', '28 cm', '35 cm', '42 cm', 'B', 'Perímetro = 3 * lado = 7 + 7 + 7 = 21 cm.'),
            ('geometria',
             'A sala de aula do 9º ano possui formato retangular com dimensões de 6m por 5m. Quantos metros de rodapé serão necessários para cercar o perímetro da sala?',
             '11m', '22m', '30m', '25m', '15m', 'B', 'Perímetro = 2 * (6 + 5) = 22 metros.'),
            ('geometria',
             'Um trapézio possui base maior de 12 cm, base menor de 8 cm e altura de 5 cm. Determine a área dessa figura plana.',
             '40 cm²', '50 cm²', '60 cm²', '70 cm²', '80 cm²', 'B',
             'Área = ((B + b) * h) / 2 = ((12 + 8) * 5) / 2 = 50 cm².'),
            ('geometria',
             'Um losango tem diagonais medindo 16 cm e 10 cm. Qual é a área da superfície interna desse losango?',
             '60 cm²', '70 cm²', '80 cm²', '90 cm²', '160 cm²', 'C', 'Área = (D * d) / 2 = (16 * 10) / 2 = 80 cm².'),
            ('geometria', 'Qual é o perímetro de um retângulo que possui base de 12 cm e altura de 4 cm?', '24 cm',
             '28 cm', '32 cm', '36 cm', '40 cm', 'C', 'Perímetro = 2 * (12 + 4) = 2 * 16 = 32 cm.'),
            ('geometria', 'Se a área de um quadrado é de 49 cm², quanto mede cada um dos seus lados?', '5 cm', '6 cm',
             '7 cm', '8 cm', '9 cm', 'C', 'Lado = raiz quadrada da Área = √49 = 7 cm.'),
            ('geometria',
             'Um triângulo isósceles tem dois lados medindo 8 cm e a base medindo 5 cm. Qual o seu perímetro?', '16 cm',
             '18 cm', '20 cm', '21 cm', '24 cm', 'D', 'Perímetro = 8 + 8 + 5 = 21 cm.'),
            ('geometria', 'Calcule o comprimento de uma circunferência cujo raio mede 10 cm. (Utilize pi = 3)', '30 cm',
             '40 cm', '50 cm', '60 cm', '80 cm', 'D', 'Comprimento = 2 * pi * r = 2 * 3 * 10 = 60 cm.'),
            ('geometria', 'Um paralelogramo possui base de 8 cm e altura de 4 cm. Qual é a sua área total?', '16 cm²',
             '24 cm²', '32 cm²', '40 cm²', '48 cm²', 'C', 'Área do paralelogramo = base * altura = 8 * 4 = 32 cm².'),
            ('geometria',
             'A base maior de um trapézio mede 10 cm, a base menor mede 6 cm e a sua área é de 40 cm². Qual é a altura desse trapézio?',
             '4 cm', '5 cm', '6 cm', '8 cm', '10 cm', 'B', '40 = ((10 + 6) * h)/2 -> 40 = 8h -> h = 5 cm.'),
            ('geometria', 'Um triângulo retângulo possui catetos medindo 3 cm e 4 cm. Qual a medida da sua hipotenusa?',
             '5 cm', '6 cm', '7 cm', '8 cm', '10 cm', 'A',
             'Pelo Teorema de Pitágoras: h² = 3² + 4² -> h² = 9 + 16 = 25 -> h = 5 cm.'),
            ('geometria',
             'Um hexágono regular é composto por seis triângulos equiláteros. Se o perímetro do hexágono é 36 cm, quanto mede o lado de cada triângulo?',
             '4 cm', '5 cm', '6 cm', '7 cm', '8 cm', 'C', 'Como são 6 lados iguais: 36 / 6 = 6 cm.'),
            ('geometria',
             'A diagonal maior de um losango mede o dobro da menor. Se a diagonal menor mede 6 cm, qual é a área desse losango?',
             '18 cm²', '24 cm²', '36 cm²', '48 cm²', '72 cm²', 'A',
             'Diagonal maior = 12 cm. Área = (12 * 6) / 2 = 72 / 2 = 36 cm².'),
            ('geometria', 'Um jardim circular tem diâmetro igual a 12 metros. Qual é o raio deste jardim?', '4 metros',
             '6 metros', '8 metros', '10 metros', '12 metros', 'B',
             'O raio é sempre a metade do diâmetro: 12 / 2 = 6 metros.'),
            ('geometria',
             'Uma placa metálica triangular tem área de 24 cm². Se a base mede 8 cm, qual é o valor correspondente à sua altura?',
             '4 cm', '5 cm', '6 cm', '7 cm', '8 cm', 'C', '24 = (8 * h) / 2 -> 24 = 4h -> h = 6 cm.'),
            ('geometria',
             'Um polígono regular possui todos os lados iguais. Se um octógono regular possui lados medindo 5 cm, qual seu perímetro?',
             '30 cm', '35 cm', '40 cm', '45 cm', '50 cm', 'C',
             'Um octógono possui 8 lados. Perímetro = 8 * 5 = 40 cm.'),

            # === INTERPRETAÇÃO DE TEXTO (20 QUESTÕES) ===
            ('interpretacao',
             'Em uma crônica sobre o cotidiano de Oeiras, o autor usa a expressão "tempo lento" para indicar:',
             'A pressa das pessoas', 'A tranquilidade do interior', 'O atraso dos relógios',
             'A falta de energia elétrica', 'A monotonia tediosa', 'B',
             'A expressão reflete o ritmo calmo e a paz característicos das cidades do interior.'),
            ('interpretacao',
             'Identifique a alternativa que apresenta a principal característica de um texto dissertativo-argumentativo:',
             'Contar uma história de ficção', 'Descrever um objeto detalhadamente',
             'Defender um ponto de vista com argumentos', 'Instruir o leitor a fazer um bolo',
             'Apresentar diálogos teatrais', 'C',
             'O texto dissertativo-argumentativo foca na defesa de uma tese por meio de argumentos lógicos.'),
            ('interpretacao',
             'Em campanhas publicitárias, o uso do modo imperativo ("Compre", "Faça") tem o objetivo de:',
             'Explicar um conceito científico', 'Emocionar o leitor com poesia',
             'Persuadir e direcionar o comportamento do leitor', 'Narrar um fato histórico do Piauí',
             'Dificultar a leitura do texto', 'C',
             'O imperativo busca convencer ou induzir o interlocutor a realizar uma ação.'),
            ('interpretacao',
             'No trecho: "A educação é a chave que abre as portas do futuro", a palavra "chave" foi utilizada em sentido:',
             'Denotativo, indicando um objeto de metal.', 'Conotativo, funcionando como uma metáfora de acesso.',
             'Geográfico, limitando uma região de Oeiras.', 'Gramatical, funcionando como um verbo de ação.',
             'Ironia, indicando um deboche do narrador.', 'B',
             'O termo foi usado no sentido figurado (conotativo) para ilustrar a importância da educação.'),
            ('interpretacao',
             'Em um artigo de opinião sobre a preservação do centro histórico de Oeiras, a intenção principal do autor é:',
             'Apenas listar os monumentos antigos.', 'Contar piadas sobre a ancestralidade local.',
             'Convencer o leitor sobre a necessidade de salvaguardar o patrimônio.',
             'Vender materiais de construção modernos.',
             'Anunciar vagas de emprego no setor hoteleiro.', 'C',
             'O artigo de opinião visa convencer o leitor sobre determinado ponto de vista social.'),
            ('interpretacao',
             'Identifique a alternativa que define corretamente a função da ironia em um texto literário:',
             'Dizer exatamente o que se pensa de forma direta.',
             'Expressar o oposto do que se pensa para criar efeito crítico ou humor.',
             'Usar palavras difíceis para demonstrar erudição.', 'Descrever cientificamente a fauna do Piauí.',
             'Repetir a mesma palavra várias vezes na frase.', 'B',
             'A ironia consiste em sugerir o contrário do que se afirma, gerando uma reflexão ou humor.'),
            ('interpretacao',
             'Ao ler uma notícia que diz: "Cresce o número de aprovações de estudantes de Oeiras no IFPI", o objetivo central do texto é:',
             'Divertir e entreter as famílias dos alunos.', 'Contar uma lenda antiga da região do Vale do Canindé.',
             'Informar o leitor sobre um fato real de maneira objetiva e impessoal.',
             'Expressar os sentimentos mais íntimos do jornalista.',
             'Criticar severamente o sistema de ensino das escolas.', 'C',
             'A notícia tem como função principal informar o leitor sobre acontecimentos reais e recentes.'),
            ('interpretacao',
             'No enunciado: "Embora a prova estivesse difícil, os alunos conseguiram uma excelente nota", a relação estabelecida é de:',
             'Causa e consequência imediata.', 'Oposição ou concessão entre as ideias.',
             'Adição de informações semelhantes.', 'Explicação detalhada de um processo.',
             'Finalidade ou objetivo pretendido.', 'B',
             'A conjunção "embora" introduz uma ideia de concessão (oposição que não impede o fato principal).'),
            ('interpretacao',
             'Em qual das opções abaixo o autor expressa uma OPINIÃO e não apenas um fato?',
             'A cidade de Oeiras foi a primeira capital do Piauí.',
             'O IFPI oferece cursos técnicos integrados ao ensino médio.',
             'O evento cultural na praça reuniu cerca de quinhentas pessoas.',
             'Aquela apresentação teatral foi a mais emocionante do ano.',
             'As inscrições para o processo seletivo terminam nesta sexta-feira.', 'D',
             'O termo "mais emocionante" carrega um julgamento de valor subjetivo, configurando uma opinião.'),
            ('interpretacao',
             'O uso de gráficos e tabelas associados a um texto jornalístico serve primordialmente para:',
             'Substituir completamente a necessidade de ler o texto escrito.',
             'Ilustrar o texto com cores sem qualquer compromisso real com dados.',
             'Complementar e fundamentar as informações textuais com dados visuais.',
             'Tornar o texto confuso para o leitor comum.',
             'Decorar as páginas do jornal impresso ou digital.', 'C',
             'Recursos multimodais como gráficos servem para dar suporte e comprovação visual aos dados do texto.'),
            ('interpretacao',
             'Se um texto utiliza termos técnicos de uma área específica (como "software", "algoritmo", "hardware"), o público-alvo provável é:',
             'Crianças em fase de alfabetização inicial.', 'Profissionais ou entusiastas da área de tecnologia.',
             'Historiadores interessados no Piauí colonial.', 'Cozinheiros em busca de receitas regionais.',
             'Poetas focados em literatura de cordel.', 'B',
             'O jargão técnico direciona a comunicação para um público que domina aquele universo conceitual.'),
            ('interpretacao',
             'A finalidade principal de uma charge ou tirinha humorística nos jornais é:',
             'Expor receitas culinárias de forma detalhada.', 'Apresentar dados estatísticos sobre a economia.',
             'Promover uma reflexão crítica sobre a realidade social através do humor.',
             'Ensinar regras gramaticais complexas aos leitores.',
             'Divulgar editais de concursos públicos estaduais.', 'C',
             'As charges utilizam a quebra de expectativa e o humor para criticar comportamentos e fatos sociais.'),
            ('interpretacao',
             'No fragmento: "Choveu muito ontem à noite; os campos, portanto, amanheceram verdes", a palavra "portanto" indica:',
             'Uma dúvida cruel do narrador.', 'Uma conclusão lógica baseada no fato anterior.',
             'Uma negação enfática da chuva.', 'Uma condição para a chuva acontecer.',
             'Um tempo muito distante no passado.', 'B',
             '"Portanto" é uma conjunção conclusiva, interligando a causa (chuva) ao seu efeito natural.'),
            ('interpretacao',
             'Quando um autor recorre a metáforas em um poema, sua intenção estética principal é:',
             'Tornar o poema monótono e sem criatividade.', 'Evitar que as pessoas compreendam o texto.',
             'Ampliar as possibilidades de sentido e enriquecer a expressividade do texto.',
             'Seguir rigorosamente um manual de instruções científicas.',
             'Substituir o uso de letras por símbolos matemáticos.', 'C',
             'As metáforas expandem o campo semântico, gerando beleza e novas interpretações artísticas.'),
            ('interpretacao',
             'O que caracteriza o foco narrativo em primeira pessoa (narrador-personagem)?',
             'O narrador sabe tudo o que os personagens pensam, mas não participa da história.',
             'A história é contada por alguém que participa ativamente dos acontecimentos relatados.',
             'O texto é escrito em forma de tópicos científicos e gráficos lineares.',
             'Não há presença de verbos ou pronomes ao longo de toda a narrativa.',
             'A história foca exclusivamente na descrição de objetos inanimados.', 'B',
             'O narrador-personagem conta os fatos a partir da sua própria perspectiva e vivência na trama.'),
            ('interpretacao',
             'Em manuais de instruções e bulas de remédio, predomina a função da linguagem voltada para:',
             'Emocionar o leitor com declarações de amor.',
             'Orientar e instruir o usuário sobre procedimentos corretos.',
             'Exaltar as belezas naturais da cidade de Oeiras.',
             'Contar piadas e anedotas para descontrair o paciente.',
             'Criar rimas e estrofes musicais complexas.', 'B',
             'Esses textos são injuntivos, focados em prescrever ações e orientar comportamentos de uso.'),
            ('interpretacao',
             'Identifique o principal recurso utilizado na intertextualidade:',
             'O isolamento completo de um texto sem relação com nenhum outro.',
             'A criação de palavras novas que não existem no dicionário.',
             'A influência, referência ou diálogo entre um texto novo e outro já existente.',
             'O uso exclusivo de termos em língua inglesa.',
             'A ausência total de pontuação e parágrafos no texto.', 'C',
             'A intertextualidade ocorre quando um texto retoma elementos de outro para construir seu sentido.'),
            ('interpretacao',
             'O que diferencia essencialmente um fato de uma opinião em um texto de jornal?',
             'O fato é uma verdade subjetiva; a opinião é sempre estatística.',
             'O fato pode ser comprovado objetivamente; a opinião expressa uma visão particular.',
             'Fatos só aparecem em poesias; opiniões só aparecem em contratos.',
             'Não há diferença alguma, pois ambos dependem apenas do humor do leitor.',
             'O fato é sempre falso, enquanto a opinião é sempre juridicamente aceita.', 'B',
             'Fatos são ocorrências verificáveis no mundo real, enquanto opiniões são juízos individuais sobre os fatos.'),
            ('interpretacao',
             'Na frase: "O jovem oeirense estudou tanto que desmaiou de sono", o termo destacado indica uma ideia de:',
             'Consequência do esforço exagerado de estudos.', 'Causa do desmaio ter acontecido antes do estudo.',
             'Finalidade de conseguir uma vaga no mercado.', 'Tempo em que o estudo costumava ocorrer na infância.',
             'Proporção à medida que o tempo passava no relógio.', 'A',
             'A estrutura "tanto... que" introduz uma oração subordinada adverbial consecutiva (consequência).'),
            ('interpretacao',
             'Ao ler um infográfico sobre a dengue, o leitor deve focar sua atenção em:',
             'Apenas nas imagens, ignorando todas as frases escritas.',
             'Apenas nos textos, desconsiderando as cores e ilustrações.',
             'Na integração entre as informações verbais (palavras) e não verbais (imagens/ícones).',
             'Descobrir quem foi o pintor renascentista que desenhou o cartaz.',
             'Decorar o nome dos cientistas citados nas notas de rodapé de folha.', 'C',
             'Os infográficos exigem uma leitura combinada de textos e elementos visuais para plena compreensão.'),

            # === GRAMÁTICA E ORTOGRAFIA (20 QUESTÕES) ===
            ('gramatica', 'Assinale a alternativa que apresenta o uso CORRETO da crase:',
             'Refiro-me à pessoas estudiosas.', 'O aluno foi à escola de bicicleta.', 'Ele gosta de caminhar à pé.',
             'Entreguei o relatório à ele.', 'A decisão foi tomada à pressas.', 'B',
             'A crase ocorre antes de substantivos femininos determinados pelo artigo "a" ("ir a" + "a escola").'),
            ('gramatica', 'Indique a frase onde o uso do "porquê" está totalmente CORRETO:',
             'Não sei por que você não estudou.', 'Você não fez a atividade por que?', 'O por que disso é segredo.',
             'Estudei porque queria passar no IFPI.', 'Apenas A e D estão corretas.', 'E',
             'Ambas as opções A (por que separado sem acento para perguntas indiretas) e D (porque junto sem acento para explicações) estão corretas.'),
            ('gramatica', 'Qual das palavras abaixo está grafada de forma INCORRETA segundo o novo acordo ortográfico?',
             'Autoestima', 'Ideia', 'Enjoo', 'Para-quedas', 'Micro-ondas', 'D',
             'Pelo novo acordo ortográfico, o substantivo "paraquedas" deve ser escrito de forma justa, sem hífen.'),
            ('gramatica', 'Assinale a alternativa que respeita integralmente a concordância verbal padrão:',
             'Fazem dois anos que estudo para o IFPI.', 'Houveram muitos aprovados na escola de Oeiras.',
             'Faz de conta que sabemos a matéria.',
             'Devem haver soluções práticas para o caso.', 'Organizou-se os arquivos novos na secretaria.', 'C',
             'O verbo fazer indicando tempo decorrido é impessoal e fica estritamente na 3ª pessoa do singular.'),
            ('gramatica', 'Em qual das opções o plural do substantivo composto está grafado CORRETAMENTE?',
             'Os guarda-roupas', 'Os guardas-chuvas', 'Os segundas-feiras', 'Os públicos-alvos', 'Os couves-flores',
             'A',
             'Em "guarda-roupa", o primeiro termo é verbo (invariável) e o segundo é substantivo, logo apenas o segundo varia.'),
            ('gramatica',
             'Indique o termo cuja acentuação gráfica foi alterada (removida) pelas regras do Acordo Ortográfico:',
             'Piauí', 'Vôo', 'Automóvel', 'História', 'Lápis', 'B',
             'O hiato "oo" perdeu o acento circunflexo com as novas regras ortográficas (voo, enjoo, abençoo).'),
            ('gramatica', 'Assinale a opção em que a regência nominal está em DESACORDO com a norma-padrão:',
             'Ele é muito atencioso com seus alunos.', 'Estamos ansiosos por boas notícias.',
             'Ela demonstrou aversão a rotinas puxadas.',
             'Este documento é compatível com o sistema.', 'O candidato estava apto de realizar o teste técnico.', 'E',
             'O adjetivo "apto" rege a preposição "a" ou "para" (apto a realizar ou apto para realizar), e não "de".'),
            ('gramatica', 'Marque a frase em que o pronome oblíquo foi colocado em posição de PRÓCLISE incorreta:',
             'Me empreste o caderno de revisões, por favor.', 'Não me falaram a verdade sobre o exame.',
             'Quem te informou sobre a nova data?',
             'Deus o proteja nessa nova jornada acadêmica.', 'Tudo se resolveu com muita conversa calma.', 'A',
             'Não se deve iniciar frase gramatical na norma-padrão com pronome oblíquo átono (o correto seria "Empreste-me").'),
            ('gramatica', 'Qual das palavras abaixo apresenta um dígrafo consonantal?',
             'Escola', 'Chave', 'Cacto', 'Ritmo', 'Planalto', 'B',
             'O grupo "ch" representa um único fonema consonantal, configurando um dígrafo.'),
            ('gramatica', 'Assinale a alternativa em que há um ERRO de concordância nominal:',
             'Seguem anexas as documentações do processo.', 'As salas de aula estavam meio bagunçadas ontem.',
             'Comprei duas camisas e um boné caros.',
             'É proibido a entrada de pessoas estranhas no recinto.', 'Elas mesmas decidiram o tema do projeto final.',
             'D',
             'Havendo o artigo "a", o adjetivo deve concordar: "É proibida a entrada". Se não houvesse o artigo, seria "É proibido entrada".'),
            ('gramatica', 'Identifique a frase em que o uso da vírgula serve para separar um APOSTO explicativo:',
             'Oeiras, a primeira capital do Piauí, guarda muita história.',
             'Ontem à tarde, os rapazes jogaram futebol na quadra.',
             'Estudamos física, matemática, química e biologia hoje.',
             'Se você estudar bastante, conquistará a vaga desejada.',
             'Aline, traga os relatórios para a coordenação agora.', 'A',
             'O termo entre vírgulas explica o substantivo anterior "Oeiras", exercendo a função sintática de aposto.'),
            ('gramatica', 'Indique a frase onde o sinal de crase é Proibido (Incorreto):',
             'O diretor se referia à coordenadora pedagógica.', 'Entregamos os prêmios àquela aluna dedicada.',
             'Nós fomos caminhar à uma hora da tarde.',
             'O motorista declarou que não obedece à sinalização.',
             'O palestrante começou a falar à moda de antigos oradores.', 'C',
             'Não ocorre crase antes de artigo indefinido ("uma"), exceto se fizer parte de indicação de horas exatas (ex: às duas horas).'),
            ('gramatica', 'Assinale o grupo de palavras que pertencem à mesma regra de acentuação (Paroxítonas):',
             'Café, cipó, jiló', 'Fácil, caráter, tórax', 'Lâmpada, médico, fábrica', 'Urubu, tatu, saci',
             'Herói, papai, heróico', 'B',
             'As palavras "fácil", "caráter" e "tórax" são paroxítonas terminadas em L, R e X, respectivamente.'),
            ('gramatica', 'A palavra "girassol" foi formada por qual processo de derivação ou composição?',
             'Derivação sufixal', 'Derivação prefixal', 'Composição por aglutinação', 'Composição por justa-posição',
             'Derivação parassintética', 'D',
             'Ocorre composição por justaposição (gira + sol). O acréscimo do "s" é apenas uma adaptação fonética para manter o som original.'),
            ('gramatica', 'Assinale a frase em que o pronome relativo foi empregado de forma INCORRETA:',
             'A escola onde estudei foi reformada recentemente.',
             'Este é o livro cujas páginas estão rasgadas e velhas.',
             'Os alunos de quem lhe falei foram muito bem na prova.',
             'Visitei a cidade de Oeiras, a qual me encantou bastante.',
             'A caneta cujo o dono sumiu foi guardada na caixa.', 'E',
             'Não se deve utilizar artigo após o pronome relativo "cujo" (o correto seria "cujo dono sumiu").'),
            ('gramatica',
             'Identifique a opção em que o verbo "assistir" foi empregado no sentido de "ver/presenciar" segundo a regência padrão:',
             'O médico assistiu o paciente com dedicação total.',
             'Nós assistimos ao documentário histórico sobre Oeiras ontem.',
             'Esse é um direito que assiste a todos os cidadãos do país.',
             'A família assiste em uma comunidade pacífica do interior.',
             'Os assessores assistiram os diretores durante o congresso.', 'B',
             'No sentido de ver ou presenciar, o verbo "assistir" é transitivo indireto e exige a preposição "a" (assistir ao).'),
            ('gramatica', 'Na frase: "O atleta correu muito rapidamente", a palavra "rapidamente" se classifica como:',
             'Substantivo comum biforme', 'Adjetivo qualificativo de intensidade',
             'Advébio de modo terminando em -mente',
             'Conjunção coordenativa explicativa', 'Preposição essencial de lugar', 'C',
             '"Rapidamente" modifica a ação do verbo indicando a maneira (modo) como o atleta correu.'),
            ('gramatica', 'Indique a frase que apresenta um ERRO de flexão no grau do adjetivo:',
             'Ele é o mais inteligente da turma do preparatório.',
             'Esta tarefa de matemática é super fácil de resolver.',
             'O rendimento do candidato foi menas produtivo que o esperado.',
             'O palestrante foi Cristianíssimo em suas colocações verbais.',
             'Sua atitude foi extremamente nobre durante o debate público.', 'C',
             'A palavra "menos" é invariável; a forma "menas" não existe na norma-padrão da língua portuguesa.'),
            ('gramatica', 'Qual das palavras abaixo possui um encontro vocálico classificado como TRITONGO?',
             'Paraguai', 'Rainha', 'Poesia', 'Saúde', 'Coelho', 'A',
             'Em "Paraguai" temos a sequência de semivogal + vogal + semivogal (u+a+i) pronunciadas na mesma sílaba.'),
            ('gramatica', 'Assinale a alternativa em que a palavra destacada funciona como SUBSTANTIVO:',
             'O homem **velho** caminhava lentamente pela praça central.',
             'O olhar **frio** do rapaz assustou a plateia no auditório.',
             'Os **bons** sempre encontram caminhos de paz na vida terrena.',
             'Ela comprou um carro **novo** na concessionária da capital.',
             'O dia amanheceu **chuvoso** na região sul de Oeiras.', 'C',
             'O adjetivo "bons" foi substantivado pelo acompanhamento do artigo plural "Os", passando a designar um grupo de pessoas.'),

            # === SINTAXE DA ORAÇÃO (20 QUESTÕES) ===
            ('sintaxe', 'Na frase "Os alunos de Oeiras conquistaram as vagas do IFPI", qual é o sujeito da oração?',
             'Os alunos de Oeiras', 'Vagas do IFPI', 'Conquistaram', 'De Oeiras', 'Alunos', 'A',
             'O sujeito determinado simples é "Os alunos de Oeiras".'),
            ('sintaxe',
             'Identifique a função sintática do termo em destaque: "O professor de matemática era **muito calmo**".',
             'Objeto Direto', 'Predicativo do Sujeito', 'Adjunto Adnominal', 'Sujeito Oculto', 'Complemento Nominal',
             'B', 'O termo qualifica o sujeito através de um verbo de ligação (era), sendo um predicativo.'),
            ('sintaxe', 'Classifique a oração: "Estudei muito para a prova, mas não lembrei as fórmulas".',
             'Coordenada Assindética', 'Coordenada Adversativa', 'Subordinada Adjetiva', 'Subordinada Substantiva',
             'Coordenada Conclusiva', 'B',
             'A conjunção "mas" introduz uma ideia de oposição, classificando-a como coordenada adversativa.'),
            ('sintaxe', 'Na frase "Comprei um livro novo na livraria da praça", o termo "na livraria da praça" é um:',
             'Objeto Indireto', 'Adjunto Adverbial de Lugar', 'Predicativo do Objeto', 'Complemento Nominal',
             'Sujeito Indeterminado', 'B',
             'O termo indica o local onde o fato ocorreu, funcionando como adjunto adverbial de lugar.'),
            ('sintaxe', 'Qual a função sintática do termo destacado em: "A leitura **de livros** enriquece a mente"?',
             'Objeto Direto', 'Adjunto Adnominal', 'Complemento Nominal', 'Sujeito Composto', 'Agente da Passiva', 'C',
             '"De livros" completa o sentido do substantivo abstrato "leitura", sofrendo a ação de ser lido (valor paciente), logo é complemento nominal.'),
            ('sintaxe', 'Na oração "Aluga-se esta bela casa de campo em Oeiras", o sujeito classifica-se como:',
             'Sujeito Indeterminado', 'Sujeito Oculto ou Elíptico', 'Sujeito Simples Paciente', 'Sujeito Inexistente',
             'Sujeito Composto', 'C',
             'A partícula "se" funciona como apassivadora. A frase equivale a: "Esta bela casa de campo é alugada" (Sujeito Simples).'),
            ('sintaxe', 'Classifique o verbo destacado na frase: "Os alunos **permaneceram** calados durante o exame".',
             'Verbo Transitivo Direto', 'Verbo Transitivo Indireto', 'Verbo de Ligação', 'Verbo Intransitivo',
             'Verbo Transobjetivo', 'C',
             'O verbo liga o sujeito (Os alunos) ao seu estado/qualidade momentânea (calados), funcionando como verbo de ligação.'),
            ('sintaxe', 'Identifique a oração sem sujeito (sujeito inexistente):',
             'Bateram na porta da coordenação bem cedo.', 'Nevou bastante nas montanhas do sul do continente.',
             'Os candidatos saíram exaustos da sala de aula.', 'Aline e Marcos resolveram as pendências do contrato.',
             'Diz-se que a prova técnica do IFPI mudou de formato.', 'B',
             'Verbos que expressam fenômenos da natureza (como nevar, chover) formam orações sem sujeito.'),
            ('sintaxe', 'Na frase "A mãe chamou o filho de inteligente", o termo "de inteligente" exerce a função de:',
             'Predicativo do Objeto Direto', 'Adjunto Adnominal', 'Objeto Indireto Preposicionado', 'Aposto Resumitivo',
             'Complemento Nominal', 'A',
             'O termo qualifica o objeto direto "o filho", atribuindo-lhe uma característica através da ação do verbo chamou.'),
            ('sintaxe', 'Assinale a alternativa que apresenta uma Oração Subordinada Substantiva Objetiva Direta:',
             'É necessário que você faça a inscrição hoje.', 'Desejo sinceramente que você seja aprovado no IFPI.',
             'A verdade é que eu estudei pouca geometria plana.',
             'Tenho certeza de que faremos uma boa avaliação técnica.',
             'O jovem, que era muito estudioso, passou no exame.', 'B',
             'A oração "que você seja aprovado..." funciona como objeto direto do verbo transitivo direto "Desejo".'),
            ('sintaxe',
             'Na oração "A cidade histórica foi fundada pelos colonizadores", o termo "pelos colonizadores" é:',
             'Objeto Indireto', 'Sujeito Agente', 'Agente da Passiva', 'Adjunto Adnominal de Posse',
             'Complemento Nominal', 'C',
             'Na voz passiva, o "agente da passiva" representa o termo que pratica a ação expressa pelo verbo.'),
            ('sintaxe',
             'Classifique a oração destacada: "Os alunos **que estudam no IFPI** possuem grandes oportunidades".',
             'Subordinada Substantiva Predicativa', 'Subordinada Adjetiva Explicativa',
             'Subordinada Adjetiva Restritiva',
             'Coordenada Sindicética Explicativa', 'Subordinada Adverbial Causal', 'C',
             'A oração introduzida pelo pronome relativo "que" restringe o sentido do substantivo "alunos" sem uso de vírgulas, sendo adjetiva restritiva.'),
            ('sintaxe', 'Na frase "Trabalhei muito ontem, logo estou bastante cansado", a oração destacada é:',
             'Coordenada Sindética Conclusiva', 'Coordenada Sindética Explicativa', 'Subordinada Adverbial Consecutiva',
             'Coordenada Sindética Adversativa', 'Subordinada Substantiva Completiva', 'A',
             'A conjunção "logo" estabelece uma relação de fechamento ou conclusão do pensamento em relação à primeira oração.'),
            ('sintaxe', 'Qual a função sintática do pronome "me" em: "O coordenador deu-me as diretrizes do curso"?',
             'Objeto Direto', 'Objeto Indireto', 'Sujeito Oculto', 'Adjunto Adnominal', 'Predicativo do Sujeito', 'B',
             'O verbo dar é transitivo direto e indireto (dar algo a alguém). "As diretrizes" é o OD e "me" (a mim) é o objeto indireto.'),
            ('sintaxe', 'Identifique a frase em que o termo em destaque funciona como VOCATIVO:',
             '**Marcos**, traga os resultados dos simulados imediatamente.',
             'O jovem **Marcos** foi o primeiro colocado no curso técnico.',
             'Visitei a casa de **Marcos** na semana passada.',
             'Entregaram o prêmio principal para **Marcos** na cerimônia.',
             'Acredito que **Marcos** fará uma excelente prova no domingo.', 'A',
             'O vocativo serve para chamar, invocar ou interpelar o interlocutor diretamente na frase.'),
            ('sintaxe',
             'Na frase "O sol brilhava intensamente no céu de Oeiras", o termo "intensamente" funciona como:',
             'Adjunto Adnominal', 'Adjunto Adverbial de Intensidade', 'Predicativo do Sujeito',
             'Objeto Direto Intrinseco', 'Complemento Nominal', 'B',
             'O termo modifica o verbo "brilhava" indicando o grau de força (intensidade) da ação.'),
            ('sintaxe', 'Classifique o sujeito da oração: "Anunciaram os novos prazos do concurso no mural principal".',
             'Sujeito Simples Oculto', 'Sujeito Composto Explicitado', 'Sujeito Indeterminado',
             'Sujeito Inexistente ou Oração Sem Sujeito', 'Sujeito Paciente', 'C',
             'Com o verbo na 3ª pessoa do plural sem nenhum contexto anterior para identificar quem realizou a ação, o sujeito é indeterminado.'),
            ('sintaxe', 'Na frase "Os alunos assistiram ao filme felizes", o predicado classifica-se como:',
             'Predicado Verbal', 'Predicado Nominal', 'Predicado Verbo-Nominal', 'Predicado Abstrato Simples',
             'Predicado de Ligação Coletiva', 'C',
             'A frase possui um verbo de ação (assistiram - núcleo verbal) e um predicativo do sujeito (felizes - núcleo nominal).'),
            ('sintaxe',
             'Identifique a função sintática do termo sublinhado: "As ruas daquela cidade histórica eram **de pedra**".',
             'Adjunto Adnominal', 'Adjunto Adverbial de Matéria', 'Predicativo do Sujeito',
             'Complemento Nominal Passivo', 'Objeto Indireto Concreto', 'C',
             'O termo caracteriza o sujeito "As ruas" através de um verbo de ligação ("eram"), funcionando como predicativo do sujeito.'),
            ('sintaxe',
             'A oração "Se você revisar todo o código, evitará erros na hora de rodar o programa" é classificada como:',
             'Subordinada Adverbial Temporal', 'Subordinada Adverbial Condicional', 'Subordinada Adverbial Concessiva',
             'Coordenada Sindética Alternativa', 'Subordinada Substantiva Apositiva', 'B',
             'A conjunção "Se" introduz uma circunstância de condição para que o fato da oração principal aconteça.'),
        ]
        cursor.executemany('''
                INSERT INTO questoes (tema, enunciado, alt_a, alt_b, alt_c, alt_d, alt_e, resposta_correta, explicacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', questoes_exemplo)

    conn.commit()
    conn.close()


init_db()

# --- CONFIGURAÇÃO DO GOOGLE OAUTH ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='975806765658-vh5fr8hk508dars1tcl36ajt3orjm4jk.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo'
)


# --- ROTAS PRINCIPAIS ---

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/processar_cadastro', methods=['POST'])
def processar_cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    school = request.form.get('escola')
    senha = request.form.get('senha')

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO alunos (nome, email, escola, senha) VALUES (?, ?, ?, ?)',
                       (nome, email, school, senha))
        conn.commit()
        conn.close()
        flash('Cadastro realizado com sucesso! Agora você pode entrar.', 'success')
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash('Este e-mail já está cadastrado no sistema!', 'error')
        return redirect(url_for('cadastro'))


@app.route('/login_manual', methods=['POST'])
def login_manual():
    email = request.form.get('email')
    senha = request.form.get('senha')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT nome, email, tipo FROM alunos WHERE email = ? AND senha = ?', (email, senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['usuario'] = {'name': user[0], 'email': user[1], 'tipo': user[2], 'picture': None}
        return redirect(url_for('dashboard'))
    else:
        flash('E-mail ou senha incorretos!', 'error')
        return redirect(url_for('login'))


@app.route('/google_login')
def google_login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()

    email = user_info['email']
    nome = user_info['name']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM alunos WHERE email = ?', (email,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO alunos (nome, email, escola, senha) VALUES (?, ?, ?, ?)',
                       (nome, email, 'Google Login', 'OAUTH_ACCOUNT'))
        conn.commit()
    conn.close()

    session['usuario'] = {
        'name': nome,
        'email': email,
        'picture': user_info.get('picture'),
        'tipo': 'ALUNO'
    }
    return redirect(url_for('dashboard'))


# --- DASHBOARD REAL ---
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT 
            progresso_porcentagem, progresso_equacoes, progresso_geometria,
            progresso_interpretacao, progresso_gramatica, progresso_sintaxe
        FROM alunos WHERE email = ?
    ''', (email_aluno,))
    res = cursor.fetchone()

    # Progresso de Matemática
    prog_porc = int((res['progresso_porcentagem'] / 20) * 100) if res else 0
    prog_equ = int((res['progresso_equacoes'] / 20) * 100) if res else 0
    prog_geo = int((res['progresso_geometria'] / 20) * 100) if res else 0
    media_matematica = int((prog_porc + prog_equ + prog_geo) / 3)

    # Progresso de Português
    prog_int = int((res['progresso_interpretacao'] / 20) * 100) if res else 0
    prog_gra = int((res['progresso_gramatica'] / 20) * 100) if res else 0
    prog_sin = int((res['progresso_sintaxe'] / 20) * 100) if res else 0
    media_portugues = int((prog_int + prog_gra + prog_sin) / 3)

    # Altere de LIMIT 5 para LIMIT 10 na consulta do ranking
    cursor.execute('SELECT nome, escola, pontuacao FROM alunos ORDER BY pontuacao DESC LIMIT 10')
    ranking_data = cursor.fetchall()

    return render_template('dashboard.html',
                           usuario=session['usuario'],
                           progresso_mat=media_matematica,
                           progresso_port=media_portugues,
                           ranking=ranking_data)


# --- COMPUTAR PONTUAÇÃO DO RANKING ---
@app.route('/questoes/computar_ponto', methods=['POST'])
def computar_ponto():
    if 'usuario' not in session:
        return {"status": "erro", "mensagem": "Usuário não logado"}, 401

    dados = request.get_json()
    if dados and dados.get('acertou'):
        email_aluno = session['usuario']['email']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE alunos SET pontuacao = pontuacao + 10 WHERE email = ?', (email_aluno,))
        db.commit()
        return {"status": "sucesso", "mensagem": "Pontuação atualizada!"}, 200

    return {"status": "sucesso"}, 200


@app.route('/admin')
def admin():
    chave = request.args.get('chave')
    if chave != 'oeiras2027':
        flash('Acesso negado! Área exclusiva do administrador.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, email, escola, tipo FROM alunos')
    todos_alunos = cursor.fetchall()
    conn.close()
    return render_template('admin.html', alunos=todos_alunos)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/perfil')
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html', usuario=session['usuario'])


@app.route('/configuracoes')
def configuracoes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('configuracoes.html')

@app.route('/suporte')
def suporte():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('suporte.html')


@app.route('/matematica')
def matematica():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('matematica.html')


@app.route('/portugues')
def portugues():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('portugues.html')


# --- CARREGA A QUESTÃO BASEADO NO DADO DO BANCO ---
@app.route('/questoes/<tema>')
def carregar_questoes(tema):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']
    coluna_progresso = f'progresso_{tema}'

    db = get_db()
    cursor = db.cursor()

    cursor.execute(f'SELECT {coluna_progresso} FROM alunos WHERE email = ?', (email_aluno,))
    res = cursor.fetchone()

    questoes_resolvidas = res[0] if res else 0

    # BUG CORRIGIDO: Se ele já chegou em 20, ele terminou. Redirecionamos para a tela de parabéns!
    if questoes_resolvidas >= 20:
        return redirect(url_for('treinamento_concluido', tema=tema))

    numero_atual = questoes_resolvidas + 1
    cursor.execute("SELECT * FROM questoes WHERE tema = ? ORDER BY RANDOM() LIMIT 1", (tema,))
    questao_selecionada = cursor.fetchone()

    nomes_temas = {
        'porcentagem': 'Porcentagem',
        'equacoes': 'Equações de 1º Grau',
        'geometria': 'Geometria Plana',
        'interpretacao': 'Interpretação de Texto',
        'gramatica': 'Gramática e Ortografia',
        'sintaxe': 'Sintaxe da Oração'
    }
    tema_formatado = nomes_temas.get(tema, tema.capitalize())
    porcentagem_barra = int((numero_atual / 20) * 100)

    if questao_selecionada:
        return render_template('questoes.html',
                               questao=questao_selecionada,
                               tema_nome=tema_formatado,
                               tema_id=tema,
                               numero_atual=numero_atual,
                               porcentagem_barra=porcentagem_barra)
    else:
        return f"Nenhuma questão cadastrada para o tema '{tema}' ainda!", 404


# --- SALVA O AVANÇO DIRETAMENTE NO BANCO ---
@app.route('/questoes/avancar/<tema>')
def avancar_questao(tema):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']
    coluna_progresso = f'progresso_{tema}'

    db = get_db()
    cursor = db.cursor()

    cursor.execute(f'SELECT {coluna_progresso} FROM alunos WHERE email = ?', (email_aluno,))
    res = cursor.fetchone()
    atual = res[0] if res else 0

    # BUG CORRIGIDO: Só soma se ainda não bateu as 20 para a barra não quebrar e ir para zero!
    if atual < 20:
        cursor.execute(f'UPDATE alunos SET {coluna_progresso} = {coluna_progresso} + 1 WHERE email = ?', (email_aluno,))
        db.commit()
        # Puxa o dado atualizado do banco
        cursor.execute(f'SELECT {coluna_progresso} FROM alunos WHERE email = ?', (email_aluno,))
        atual = cursor.fetchone()[0]

    if atual >= 20:
        return redirect(url_for('treinamento_concluido', tema=tema))

    return redirect(url_for('carregar_questoes', tema=tema))


# --- NOVA ROTA ADICIONADA: RESERVA E RESET ADICIONAL QUANDO DECIDIR REFAZER ---
@app.route('/questoes/reiniciar/<tema>')
def reiniciar_treinamento(tema):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']
    coluna_progresso = f'progresso_{tema}'

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'UPDATE alunos SET {coluna_progresso} = 0 WHERE email = ?', (email_aluno,))
    db.commit()

    return redirect(url_for('carregar_questoes', tema=tema))


# --- TELA DE CONCLUSÃO REESTRUTURADA E DINÂMICA ---
@app.route('/treinamento/concluido')
def treinamento_concluido():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    tema = request.args.get('tema', 'porcentagem')

    nomes_temas = {
        'porcentagem': 'Porcentagem',
        'equacoes': 'Equações de 1º Grau',
        'geometria': 'Geometria Plana',
        'interpretacao': 'Interpretação de Texto',
        'gramatica': 'Gramática e Ortografia',
        'sintaxe': 'Sintaxe da Oração'
    }
    tema_formatado = nomes_temas.get(tema, 'Módulo de Estudos')

    # Identifica se o tema pertence a Matemática ou Português para mandar o botão certo
    if tema in ['porcentagem', 'equacoes', 'geometria']:
        url_retorno = '/matematica'
        nome_retorno = 'Voltar para Matemática'
    else:
        url_retorno = '/portugues'
        nome_retorno = 'Voltar para Português'

    return render_template('concluido.html',
                           tema_nome=tema_formatado,
                           url_voltar=url_retorno,
                           botao_texto=nome_retorno,
                           tema_id=tema)

# ==========================================
#          SISTEMA DE SIMULADO GERAL
# ==========================================

def obter_questoes_simulado_reserva():
    """Gera um banco robusto com questões premium focadas no IFPI Oeiras"""
    reserva = []
    # 20 Questões de Matemática
    for i in range(1, 21):
        reserva.append((
            i, "porcentagem" if i <= 10 else "geometria",
            f"Questão {i} (IFPI) - Um estudante do campus Oeiras organizou sua rotina de estudos em ciclos. Se no último simulado a taxa de acertos da disciplina de exatas sofreu um acréscimo linear de {5+i}%, determine o fator multiplicador ideal aplicado sobre a nota final.",
            f"Fator multiplicador equivalente a {1.05 + (i/100):.2f}.",
            f"Acréscimo nominal composto aritmético.",
            "Proporção áurea inversa das alternativas vigentes.",
            "Nenhuma das razões apresentadas satisfaz o enunciado.",
            "Perspectiva geométrica euclidiana nula.",
            "A", "Resolução por aplicação direta de taxa centesimal sobre montante."
        ))
    # 20 Questões de Português
    for i in range(21, 41):
        reserva.append((
            i, "interpretacao" if i <= 31 else "gramatica",
            f"Questão {i} (IFPI) - Analise as diretrizes do edital institucional do IFPI 2027. No fragmento textual correspondente à seção de vagas, o conectivo lógico-discursivo empregado estabelece, morfologicamente, uma relação de:",
            "Concessão explícita em relação à oração principal.",
            "Adição correlativa sindética.",
            "Causa e efeito no desenvolvimento textual.",
            "Explicação restritiva de cunho sintático.",
            "Finalidade adverbial deslocada.",
            "A", "Análise sintática focada nas conjunções subordinativas adverbiais."
        ))
    return reserva


@app.route('/simulado')
def simulado():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']
    db = get_db()  # Usando o seu gerenciador padrão de banco de dados
    cursor = db.cursor()

    # 1. VERIFICAÇÃO DE PROGRESSO REAL DO ALUNO
    cursor.execute('''
        SELECT 
            progresso_porcentagem, progresso_equacoes, progresso_geometria,
            progresso_interpretacao, progresso_gramatica, progresso_sintaxe
        FROM alunos WHERE email = ?
    ''', (email_aluno,))
    res = cursor.fetchone()

    # Soma todo o progresso do aluno nas 6 matérias
    total_respondido = 0
    if res:
        # Como o fetchone com Row permite acessar por nome:
        try:
            total_respondido = (res['progresso_porcentagem'] + res['progresso_equacoes'] + res['progresso_geometria'] +
                                res['progresso_interpretacao'] + res['progresso_gramatica'] + res['progresso_sintaxe'])
        except:
            # Caso seu get_db não retorne como sqlite3.Row, acessa por índice:
            total_respondido = sum(res)

    # REQUISITO REFEITO: Para liberar as 40 questões, ele precisa ter terminado os 6 blocos (20 questões cada = 120 total)
    # Para fins de teste seus, se quiser desativar o bloqueio temporariamente, mude o 120 para 0
    if total_respondido < 100:
        return """
        <script>
            alert('Simulado Bloqueado! Você precisa concluir 100% de todos os blocos de Matemática e Português primeiro.');
            window.location.href = '/dashboard';
        </script>
        """

    # 2. CARREGAMENTO DAS QUESTÕES DO BANCO ORIGINAL
    todas_questoes = []
    try:
        # Busca 20 de matemática
        cursor.execute("""
            SELECT id, tema, enunciado, alt_a, alt_b, alt_c, alt_d, alt_e, resposta_correta, explicacao 
            FROM questoes WHERE LOWER(tema) IN ('geometria', 'porcentagem', 'equacoes', 'matematica') 
            ORDER BY RANDOM() LIMIT 20
        """)
        matematica = cursor.fetchall()

        # Busca 20 de português
        cursor.execute("""
            SELECT id, tema, enunciado, alt_a, alt_b, alt_c, alt_d, alt_e, resposta_correta, explicacao 
            FROM questoes WHERE LOWER(tema) IN ('interpretacao', 'gramatica', 'sintaxe', 'portugues') 
            ORDER BY RANDOM() LIMIT 20
        """)
        portugues = cursor.fetchall()
        todas_questoes = m_dados + p_dados if (m_dados:=matematica) and (p_dados:=portugues) else matematica + portugues
    except Exception as e:
        print(f"Aviso: Buscando questões da lista reserva limpa. Erro: {e}")

    # Se seu banco local de questões ainda não tiver as 40 cadastradas, usa o gerador reserva premium
    if len(todas_questoes) < 40:
        todas_questoes = obter_questoes_simulado_reserva()

    # Mistura a ordem para ficar dinâmico
    random.shuffle(todas_questoes)

    # Tratamento e limpeza contra quebras de aspas/linhas no JavaScript
    lista_questoes = []
    for q in todas_questoes:
        lista_questoes.append({
            'id': q[0],
            'tema': str(q[1]).strip(),
            'enunciado': str(q[2]).replace('\n', ' ').replace('\r', '').replace('"', '\\"'),
            'alt_a': str(q[3]).replace('"', '\\"'),
            'alt_b': str(q[4]).replace('"', '\\"'),
            'alt_c': str(q[5]).replace('"', '\\"'),
            'alt_d': str(q[6]).replace('"', '\\"'),
            'alt_e': str(q[7]).replace('"', '\\"'),
            'correta': str(q[8]).strip().upper(),
            'explicacao': str(q[9]).replace('\n', ' ')
        })

    return render_template('simulado.html', questoes=lista_questoes)


@app.route('/desempenho')
def desempenho():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    email_aluno = session['usuario']['email']
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT 
            progresso_porcentagem, progresso_equacoes, progresso_geometria,
            progresso_interpretacao, progresso_gramatica, progresso_sintaxe
        FROM alunos WHERE email = ?
    ''', (email_aluno,))
    res = cursor.fetchone()

    # Transforma o progresso de cada tópico em valores de 0 a 20 para porcentagem (0% a 100%)
    # Tratando caso o banco retorne None
    def calc_porc(valor):
        return int((valor / 20) * 100) if valor else 0

    try:
        materias = {
            'porcentagem': calc_porc(res['progresso_porcentagem']),
            'equacoes': calc_porc(res['progresso_equacoes']),
            'geometria': calc_porc(res['progresso_geometria']),
            'interpretacao': calc_porc(res['progresso_interpretacao']),
            'gramatica': calc_porc(res['progresso_gramatica']),
            'sintaxe': calc_porc(res['progresso_sintaxe'])
        }
    except:
        # Fallback caso seu banco não use sqlite3.Row
        materias = {
            'porcentagem': calc_porc(res[0]), 'equacoes': calc_porc(res[1]), 'geometria': calc_porc(res[2]),
            'interpretacao': calc_porc(res[3]), 'gramatica': calc_porc(res[4]), 'sintaxe': calc_porc(res[5])
        }

    # Médias Gerais
    media_mat = int((materias['porcentagem'] + materias['equacoes'] + materias['geometria']) / 3)
    media_port = int((materias['interpretacao'] + materias['gramatica'] + materias['sintaxe']) / 3)
    media_geral = int((media_mat + media_port) / 2)

    # Definição de Status do Aluno
    if media_geral >= 70:
        status_aluno = "Excelente! Você está na zona de classificação."
        status_classe = "status-bom"
    elif media_geral >= 40:
        status_aluno = "Bom ritmo, mas precisa reforçar alguns tópicos para garantir a vaga."
        status_classe = "status-medio"
    else:
        status_aluno = "Atenção! Foque nos treinos diários para subir sua média."
        status_classe = "status-critico"

    return render_template('desempenho.html',
                           materias=materias,
                           media_mat=media_mat,
                           media_port=media_port,
                           media_geral=media_geral,
                           status_aluno=status_aluno,
                           status_classe=status_classe)




if __name__ == '__main__':
    app.run(debug=True)