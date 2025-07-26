import google.generativeai as genai
from django.conf import settings
import markdown2

from scheduling.models import Aula


def construir_prompt(dados_aluno):
    return f"""
    **Tarefa:** Você é um instrutor de bateria experiente e um assistente pedagógico. Sua função é analisar um conjunto de relatórios de aulas de um aluno e gerar uma avaliação de desempenho detalhada, construtiva e encorajadora.

    **Instruções:**
    1. Leia todos os dados fornecidos sobre o aluno e seus relatórios de aula.
    2. Identifique padrões de progresso, dificuldades recorrentes e áreas de destaque.
    3. Não invente informações. Baseie-se estritamente nos dados fornecidos.
    4. Use uma linguagem clara, positiva e pedagógica.
    5. Estruture sua resposta EXATAMENTE nos seguintes tópicos, usando Markdown.

    ### Análise de Desempenho Pedagógico

    **1. Resumo Geral:**
    Faça um parágrafo de abertura resumindo a trajetória e o engajamento geral do aluno com base nos relatórios.

    **2. Pontos Fortes e Destaques:**
    Liste em formato de tópicos (bullet points) as áreas onde o aluno demonstra maior habilidade ou progresso.

    **3. Áreas para Melhoria:**
    Liste em formato de tópicos as áreas que necessitam de mais atenção, de forma construtiva.

    **4. Análise de Evolução Técnica:**
    Comente sobre a evolução técnica do aluno em rudimentos, ritmos ou viradas.
    Faça uma breve análise sobre o repertório e indique músicas com ritmos e pegadas parecidos

    **5. Recomendações para Próximas Aulas:**
    Sugira de 2 a 3 focos práticos para as aulas seguintes.

    **Dados brutos para análise:**
    {dados_aluno}
    """


def gerar_relatorio_ia_para_aluno(aluno):
    """
    Coleta dados, chama a API do Gemini e retorna um relatório em HTML.
    """
    aulas_com_relatorio = Aula.objects.filter(
        alunos=aluno,
        status__in=['Realizada', 'Aluno Ausente'],
        relatorio__isnull=False,
        presencas_alunos__aluno=aluno,
        presencas_alunos__status='presente'
    ).order_by('data_hora').distinct().prefetch_related(
        'relatorio__itens_rudimentos',
        'relatorio__itens_ritmo',
        'relatorio__itens_viradas',
        'relatorio__professor_que_validou'
    )

    if not aulas_com_relatorio.exists():
        return None

    dados_formatados = f"Análise de Desempenho do Aluno: {aluno.nome_completo}\n\n"
    for aula in aulas_com_relatorio:
        relatorio = aula.relatorio
        dados_formatados += f"--- AULA: {aula.data_hora.strftime('%d/%m/%Y')} ---\n"
        for item in relatorio.itens_rudimentos.all(): dados_formatados += f"- Rudimento: {item.descricao} | BPM: {item.bpm} | Obs: {item.observacoes}\n"
        for item in relatorio.itens_ritmo.all(): dados_formatados += f"- Ritmo: {item.descricao} | BPM: {item.bpm} | Obs: {item.observacoes}\n"
        for item in relatorio.itens_viradas.all(): dados_formatados += f"- Virada: {item.descricao} | BPM: {item.bpm} | Obs: {item.observacoes}\n"
        dados_formatados += "\n"

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = construir_prompt(dados_formatados)
    resposta = model.generate_content(prompt)

    html_resposta = markdown2.markdown(resposta.text)
    return html_resposta
