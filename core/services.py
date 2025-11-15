import io
from typing import Tuple
from PyPDF2 import PdfReader
import requests
from django.conf import settings
HF_API_KEY = getattr(settings, "HUGGINGFACE_API_KEY", None)
HF_MODEL = getattr(settings, "HUGGINGFACE_MODEL", "facebook/bart-large-mnli")



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

    t = text.lower().strip()
    words = t.split()
    word_count = len(words)

    action_keywords = [
        "status", "requisição", "requisicao", "protocolo", "chamado", "ticket",
        "erro", "falha", "502", "bug", "problema", "não consigo", "nao consigo",
        "acessar", "acesso", "bloqueio", "limite", "fatura", "boleto",
        "pagamento", "cobrança", "cobranca", "cadastro", "estorno", "reembolso",
        "regularização", "regularizacao", "documento", "comprovante", "anexo",
        "enviei", "envio em anexo"
    ]

    social_keywords = [
        "feliz natal", "feliz ano novo", "boas festas", "feliz aniversário",
        "feliz aniversario", "parabéns", "parabens",
        "bom final de semana", "bom fim de semana", "bom fim-de-semana",
        "ótimo final de semana", "otimo final de semana",
        "agradeço", "agradeco", "agradecimentos",
        "muito obrigado", "muito obrigada",
        "olá", "ola", "oi",
        "bom dia", "boa tarde", "boa noite",
    ]

    has_question = "?" in t
    intent_verbs = [
        "poderiam", "poderia", "gostaria", "preciso", "solicito", "solicitamos",
        "conseguem verificar", "pode verificar", "poderiam verificar",
        "pode me informar", "podem me informar",
    ]
    has_intent_verb = any(v in t for v in intent_verbs)

    has_action_keyword = any(k in t for k in action_keywords)
    has_social_keyword = any(k in t for k in social_keywords)

    if word_count == 0:
        return "improdutivo"

    if has_social_keyword and not has_action_keyword and not has_question and not has_intent_verb:
        return "improdutivo"

    if has_action_keyword:
        return "produtivo"

    if has_question or has_intent_verb:
        return "produtivo"

    if word_count <= 4 and not has_action_keyword and not has_question and not has_intent_verb:
        return "improdutivo"

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

def hf_classify_email(text: str) -> str:
    """
    Usa a API de inferência do Hugging Face para classificar o email
    como 'produtivo' ou 'improdutivo' usando zero-shot classification.
    Se der erro ou não houver chave, cai na heurística.
    """
    if not HF_API_KEY:
        print("Entrou na heuristica")
        return heuristic_classification(text)

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["produtivo", "improdutivo"],
            "multi_label": False,
            "hypothesis_template": "Este email é {}."
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Para modelos de classificação zero-shot, normalmente vem assim:
        # {"labels": [...], "scores": [...]}
        if isinstance(data, list):
            data = data[0]

        labels = data.get("labels", [])
        scores = data.get("scores", [])

        if labels and scores:
            best_index = scores.index(max(scores))
            best_label = labels[best_index].lower()

            if "produtivo" in best_label:
                return "produtivo"
            if "improdutivo" in best_label:
                return "improdutivo"

        # Se não conseguir interpretar → heurística
        return heuristic_classification(text)

    except Exception as e:
        print("Erro na chamada Hugging Face:", e)
        return heuristic_classification(text)


def ai_classify_and_respond(text: str) -> Tuple[str, str]:
    """
    Usa Hugging Face para classificar e a nossa lógica para sugerir resposta.
    Se a API falhar ou não houver chave, cai na heurística pura.
    """
    categoria = hf_classify_email(text)
    resposta = build_fallback_response(text, categoria)
    return categoria, resposta