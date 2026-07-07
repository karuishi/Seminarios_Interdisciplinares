import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

GRAFICOS_DIR = BASE_DIR / "outputs" / "graficos"
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

excel_path = DATA_DIR / "raw" / "questionario.xlsx"
csv_path = DATA_DIR / "processed" /"questionario_interdisciplinar.csv"

df = pd.read_csv(csv_path)

# Removendo colunas inúteis
df = df.drop(columns=['Start time', 'Completion time', 'Email', 'Name']) 
df = df.drop_duplicates()

# Otimizando o nome das colunas
novas_colunas = [
    "id",
    "semestre_ingresso",
    "status_curso", 
    "genero",
    "professores_relacionam_conteudo", 
    "frequencia_uso_outras_areas",
    "area_maior_dificuldade_integracao",
    "relevancia_materias_humanas",
    "areas_contato_curso",
    "atividades_percebe_interdisciplinaridade",
    "conceito_explicito_inicio",
    "necessidade_mais_eventos",
    "faltam_ics_interdisciplinares", 
    "curso_promove_interdisciplinaridade",
    "eficacia_disciplinas_projetos_reais",
    "area_maior_interacao_si",
    "escala_interdisciplinaridade_semestre",
    "atividades_extracurriculares",
    "area_desafios_futuros"
]

df.columns = novas_colunas
df['relevancia_materias_humanas'] = df['relevancia_materias_humanas'].fillna('-')
df['atividades_extracurriculares'] = df['atividades_extracurriculares'].fillna('-')
df['area_desafios_futuros'] = df['area_desafios_futuros'].fillna('-')

# Garante que colunas númericas estejam no tipo certo
df['escala_interdisciplinaridade_semestre'] = pd.to_numeric(df["escala_interdisciplinaridade_semestre"], errors='coerce')

print("\n Primeiras linhas do dataset ")
print(df.head())
print("-" * 70)

print("\n Informações gerais (tipos de dados, valores nulos) ")
print(df.info())
print("-" * 70)

print("\nValores nulos por coluna:")
print(df.isnull().sum())
print("-" * 70)

# Filtrando o semestre 2024.1
df_semestre_2024_1 = df[df['semestre_ingresso'] == '2024.1']

"""
1. Clareza da Interdisciplinaridade e Perfil do aluno (Semestralizado/Dessemestralizado)
"""
contagem_status_curso = df_semestre_2024_1['status_curso'].value_counts()
print("Distribuição de Alunos por Situação:")
for status, quantidade in contagem_status_curso.items():
    print(f"    - {status}: {quantidade} alunos")

print("="*70 + "\n")

# Compara o status do aluno com a percepção de interdisciplinaridade no inicio do curso
contagem_conceito_status = df_semestre_2024_1.groupby('conceito_explicito_inicio')['status_curso'].value_counts()
print("O conceito estava explícito no início? (Por situação):")
for (conceito, status), quantidade in contagem_conceito_status.items():
    print(f"    - '{conceito}' ({status}): {quantidade} aluno(s)")
    
print("="*70 + "\n")

"""
2. Aplicações Práticas da Interdisciplinaridade no curso
"""
# Separa as múltiplas respostas presentes em cada célula (transforma em lista) e retirar os itens de cada lista
splited_df = (
    df_semestre_2024_1['atividades_percebe_interdisciplinaridade']
    .str.split(';')
    .explode()
    .str.strip()
)
splited_df = splited_df[splited_df.astype(bool)]  # remove vazios/None

# Contagem de atividades mais citadas transformada em Series
contagem_atividades = splited_df.value_counts()
print(" Ranking de Atividades Mais Citadas:")
posicao = 1
for atividade, votos in contagem_atividades.items():
    print(f"    {posicao}º lugar: {atividade} ({votos} votos)")
    posicao += 1

print("="*70 + "\n")

"""
3. Desafios encontrados no curso e Relevância de disciplinas
"""
media_escala_interdisciplinar = df_semestre_2024_1['escala_interdisciplinaridade_semestre'].mean()
print(f"Nota média de interdisciplinaridade do semestre: {media_escala_interdisciplinar:.2f} / 10.0")

print("-" * 70)
# Contagem das áreas com maior dificuldade de integração interdisciplinar
contagem_maior_dificuldade = df_semestre_2024_1['area_maior_dificuldade_integracao'].value_counts()
print("Áreas com Maior Dificuldade de Integração:")
posicao = 1
for area, votos in contagem_maior_dificuldade.items():
    print(f"    {posicao}º lugar: {area} ({votos} votos)")
    posicao += 1
    
print("="*70 + "\n")

"""
PLOTTING
"""
# 1. Clareza da Interdisciplinaridade e Perfil do aluno (Semestralizado/Dessemestralizado)
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

# sns.countplot conta automaticamente as ocorrências.
sns.countplot(
    data=df_semestre_2024_1, 
    x='conceito_explicito_inicio', 
    hue='status_curso', 
    palette='Set2'
)

plt.title("Percepção da Interdisciplinaridade por Situação no Curso (Turma 2024.1)")
plt.xlabel("O conceito estava explícito no início?")
plt.ylabel("Quantidade de Alunos")

plt.xticks(rotation=45, ha='right')
plt.xticks()
plt.tight_layout()

plt.savefig(GRAFICOS_DIR / 'clareza_status.png')

# 2. Aplicações Práticas da Interdisciplinaridade no curso
plt.figure(figsize=(10, 6))
plt.barh(
    contagem_atividades.index, 
    contagem_atividades.values, 
    color=sns.color_palette(
        'viridis', 
        len(contagem_atividades)
    )
)

plt.title("Atividades onde a Turma 2024.1 mais percebe a Interdisciplinaridade")
plt.xlabel("Quantidade de Votos")
plt.ylabel("Tipo de Atividade")
plt.tight_layout()
plt.savefig(GRAFICOS_DIR/'atividades_praticas.png')

# 3. Desafios encontrados no curso e Relevância de disciplinas
plt.figure(figsize=(10, 6))

sns.histplot(df_semestre_2024_1['escala_interdisciplinaridade_semestre'], color='darkblue')
plt.title("Avaliação de Interdisciplinaridade das disciplinas")
plt.xlabel("Nota")
plt.ylabel("Frequência")
plt.tight_layout()

plt.savefig(GRAFICOS_DIR / 'escala_interdisciplinaridade.png')

plt.figure(figsize=(10, 6))

plt.barh(
    contagem_maior_dificuldade.index,
    contagem_maior_dificuldade.values,
    color=sns.color_palette(
        'pastel',
        len(contagem_maior_dificuldade)
    )
)

plt.title("Áreas com maior dificuldade de percepção de Interdisciplinaridade")
plt.xlabel("Quantidade de Votos")
plt.ylabel("Áreas do curso")
plt.tight_layout()

plt.savefig(GRAFICOS_DIR / 'maior_dificuldade.png')