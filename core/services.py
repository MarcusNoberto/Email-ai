import io
from typing import Tuple

from PyPDF2 import PdfReader
import openai  # se for usar OpenAI

from django.conf import settings


# Configure sua API Key em settings ou variável de ambiente
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)


def extract_text_from_file(uploaded_file) -> str:
    """
    Lê o conteúdo de .txt ou .pdf e retorna o texto.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith('.txt'):
        data = uploaded_file.read()
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1')

    if filename.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    return ""


def preprocess_text(text: str) -> str:
    """
    Pré-processamento simples: lower, strip, etc.
    Você pode adicionar remoção de stopwords, lematização, etc.
    """
    text = text.strip().lower()
    # Aqui você poderia usar spaCy/nltk se quiser impressionar mais
    return text


def heuristic_classification(text: str) -> str:
    """
    Heurística melhorada para classificar emails
    em 'produtivo' ou 'improdutivo'.
    """

    t = text.lower()

    # Sinais fortes de pedido/ação
    action_keywords = [
        "status", "requisição", "requisicao", "protocolo", "chamado", "ticket",
        "erro", "falha", "502", "bug", "problema", "não consigo", "nao consigo",
        "acessar", "acesso", "bloqueio", "limite", "fatura", "boleto",
        "pagamento", "cobrança", "cobranca", "cadastro", "estorno", "reembolso",
        "regularização", "regularizacao", "documento", "comprovante", "anexo",
        "enviei", "envio em anexo"
    ]

    # Sinais fortes de mensagem social / cortesia
    social_keywords = [
        "feliz natal", "feliz ano novo", "boas festas", "feliz aniversário",
        "feliz aniversario", "parabéns", "parabens",
        "bom final de semana", "bom fim de semana", "bom fim-de-semana",
        "ótimo final de semana", "otimo final de semana",
        "agradeço", "agradeco", "agradecimentos",
        "muito obrigado", "muito obrigada",
    ]

    # Ver se é um email com pedido explícito (pergunta, verbo de ação, etc.)
    has_question = "?" in t
    intent_verbs = [
        "poderiam", "poderia", "gostaria", "preciso", "solicito", "solicitamos",
        "conseguem verificar", "pode verificar", "poderiam verificar",
        "pode me informar", "podem me informar",
    ]
    has_intent_verb = any(v in t for v in intent_verbs)

    # 1) Se for claramente social e não tiver sinais de ação → IMPRODUTIVO
    if any(k in t for k in social_keywords) and not any(k in t for k in action_keywords) and not has_question:
        return "improdutivo"

    # 2) Se falar de erro, status, pagamento, documento, etc. → PRODUTIVO
    if any(k in t for k in action_keywords):
        return "produtivo"

    # 3) Se tiver pergunta ou verbo de intenção → tende a ser PRODUTIVO
    if has_question or has_intent_verb:
        return "produtivo"

    # 4) Default: considerar produtivo (pra não perder nada importante)
    return "produtivo"


def build_fallback_response(text: str, category: str) -> str:
    """
    Gera respostas diferentes de acordo com o conteúdo,
    quando não houver API de IA configurada.
    """
    t = text.lower()

    if category == "produtivo":
        # Caso 1: pedido de status
        if "status" in t or "requisição" in t or "requisicao" in t or "protocolo" in t:
            return (
                "Olá! Recebemos sua solicitação de atualização de status e "
                "já encaminhamos para o time responsável. Assim que tivermos "
                "uma posição, retornaremos por este canal."
            )

        # Caso 2: problema técnico / erro
        if "erro" in t or "falha" in t or "502" in t or "não consigo" in t or "nao consigo" in t:
            return (
                "Olá! Identificamos o relato de erro no acesso à plataforma e "
                "já iniciamos a análise técnica. Se possível, mantenha o navegador "
                "e horário aproximado da ocorrência para facilitar a investigação. "
                "Retornaremos em breve com mais detalhes."
            )

        # Caso 3: envio de comprovante / documento
        if "comprovante" in t or "anexo" in t or "fatura" in t or "boleto" in t or "documento" in t:
            return (
                "Olá! Recebemos o documento enviado e ele será conferido pelo nosso time. "
                "Caso seja necessária alguma informação adicional, entraremos em contato "
                "por este mesmo canal."
            )

        # Genérico produtivo
        return (
            "Olá! Recebemos sua mensagem e ela já está em análise pelo time responsável. "
            "Em breve retornaremos com uma posição mais detalhada sobre a sua solicitação."
        )

    # category == "improdutivo"
    # Felicitações de festas
    if "feliz natal" in t or "boas festas" in t or "feliz ano novo" in t:
        return (
            "Olá! Muito obrigado pela mensagem e pelos votos. "
            "Desejamos também um excelente período de festas, com muita saúde e prosperidade. "
            "Conte sempre conosco!"
        )

    # Mensagens de agradecimento / elogio / bom final de semana
    if "final de semana" in t or "fim de semana" in t or "obrigado" in t or "obrigada" in t or "parabéns" in t or "parabens" in t:
        return (
            "Olá! Agradecemos muito a sua mensagem e o reconhecimento. "
            "É um prazer poder atender você. Tenha um ótimo dia!"
        )

    # Genérico improdutivo
    return (
        "Olá! Agradecemos a sua mensagem e os votos. "
        "Ficamos à disposição sempre que precisar."
    )


def ai_classify_and_respond(text: str) -> Tuple[str, str]:
    """
    Usa IA para classificar e responder.
    Se não houver API configurada, utiliza apenas a heurística + respostas padrão.
    """

    # Se não tiver chave de API → usa só heurística + fallback
    if not openai.api_key:
        categoria = heuristic_classification(text)
        resposta = build_fallback_response(text, categoria)
        return categoria, resposta

    # --- A partir daqui é igual à ideia anterior, se quiser manter a chamada à OpenAI ---
    prompt = f"""
Você é um assistente de suporte de uma grande empresa financeira.

Leia o email abaixo e:
1) classifique-o como "produtivo" ou "improdutivo".
2) gere uma resposta curta e profissional em português.

Responda APENAS em JSON no formato:
{{"categoria": "...", "resposta": "..."}}

Email:
\"\"\"{text}\"\"\"
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = completion.choices[0].message["content"]

    import json
    try:
        data = json.loads(content)
        categoria = data.get("categoria", "").lower()
        if categoria not in ["produtivo", "improdutivo"]:
            categoria = heuristic_classification(text)
        resposta = data.get("resposta", "")
        if not resposta:
            resposta = build_fallback_response(text, categoria)
    except Exception:
        categoria = heuristic_classification(text)
        resposta = build_fallback_response(text, categoria)

    return categoria, resposta