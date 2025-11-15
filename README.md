# 📧 Email AI Classifier – Classificador de Emails com IA (Django)

Aplicação web construída em **Django** para **classificar emails** em categorias pré-definidas e **sugerir respostas automáticas** para cada caso.

O projeto demonstra:

- Automação de triagem de emails.
- Uso de heurística NLP.
- Integração preparada para IA externa (Hugging Face).
- Interface moderna em Bootstrap (tema dark).
- Deploy pronto para Render.

---

## 🚀 Funcionalidades

### 🔹 Interface Web

A página principal permite:

- Upload de arquivos `.txt` ou `.pdf`.
- Entrada manual de texto do email.
- Classificação automática em:
  - `Produtivo`
  - `Improdutivo`
- Exibição do texto enviado.
- Geração automática de resposta sugerida.

Tecnologias do front-end:

- **Bootstrap 5**
- Tema dark responsivo
- Duas colunas (formulário / resultado)

---

## 🧠 Inteligência do Sistema

A aplicação utiliza duas camadas:

1. **Heurística NLP (sempre ativa)**
2. **IA externa (opcional via Hugging Face)**

---

## 🔍 1. Heurística de Classificação

A função `heuristic_classification` analisa:

- Palavras de ação:
  - `erro`, `status`, `falha`, `pagamento`, `boleto`, `documento`, `ticket`, etc.
- Palavras sociais:
  - `bom dia`, `boa tarde`, `feliz natal`, `parabéns`, `obrigado`, etc.
- Presença de pergunta `?`
- Verbos de intenção:
  - `gostaria`, `preciso`, `solicito`, `poderiam`, etc.
- Tamanho da mensagem

Regras gerais:

- Mensagens com problema, status ou documento → **Produtivo**
- Cumprimentos sem pedido → **Improdutivo**
- Apenas “Olá”, “Boa tarde” → **Improdutivo**
- Pedidos com intenção → **Produtivo**
- Casos neutros → assume **Produtivo** para não perder urgências

---

## ✉️ 2. Respostas Automáticas

A função `build_fallback_response` cria respostas automáticas baseadas na categoria:

Exemplos:

- Problemas técnicos → mensagem informando análise
- Envio de documento → confirmação recebida
- Mensagens sociais → agradecimento cordial

---

## 🤖 3. IA Externa (Hugging Face) – Opcional

Funciona via **Zero-Shot Classification**:

- Labels usadas: `produtivo`, `improdutivo`
- Modelo configurado via `.env`
- Quaisquer erros → fallback automático para a heurística

---

---

# ⚙️ Configuração de Ambiente

## 1. Pré-requisitos

- Python 3.10+
- pip
- virtualenv (opcional)
- Git
- (Opcional) Conta na Hugging Face

---

## 2. Clonar o repositório

Clone o projeto para sua máquina local usando Git:

```bash
git clone https://github.com/MarcusNoberto/Email-ai


3. Criar o ambiente virtual

4. Instalar dependências

```bash
pip install -r requirements.txt
