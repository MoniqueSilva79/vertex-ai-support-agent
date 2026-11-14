# 🎧 Agente de Triagem de Chamados com Vertex AI (Gemini) + Terraform

Agente de IA generativa que lê um chamado de suporte e devolve em **JSON estruturado**: categoria, prioridade, sentimento do cliente, resumo e uma sugestão de resposta. Toda a infraestrutura é provisionada com **Terraform** (Infraestrutura como Código).

## 🎯 Problema que resolve
Centrais de atendimento perdem tempo classificando e priorizando chamados manualmente. O agente faz a triagem em segundos e o analista só revisa.

## 🏗️ Arquitetura
```
Cliente/Sistema ──POST /triage──► Cloud Run (FastAPI)
                                       │  conta de serviço com papel mínimo
                                       ▼
                               Vertex AI – Gemini (saída JSON com schema)
Terraform ──► APIs, conta de serviço, IAM e Cloud Run
```

## 📤 Exemplo
**Entrada**
```json
{"texto": "Minha internet caiu ontem e até agora ninguém resolveu. Já liguei 3 vezes!"}
```
**Saída**
```json
{
  "categoria": "Conectividade",
  "prioridade": "alta",
  "sentimento": "negativo",
  "resumo": "Cliente sem internet desde ontem, com 3 contatos sem solução.",
  "resposta_sugerida": "Olá! Sentimos muito pelo transtorno. Já abrimos uma ocorrência prioritária..."
}
```

## 🧰 Tecnologias
Vertex AI (Gemini) · Cloud Run · FastAPI · Terraform · IAM · Artifact Registry

## 🚀 Como rodar localmente
```bash
gcloud auth application-default login
pip install -r requirements.txt
export PROJECT_ID=seu-projeto REGION=us-central1
uvicorn agent:app --reload
curl -X POST localhost:8000/triage -H "Content-Type: application/json" \
  -d '{"texto":"Não consigo emitir a segunda via da fatura"}'
```

## ☁️ Deploy com Terraform
```bash
# 1. Build da imagem
gcloud artifacts repositories create agents --repository-format=docker --location=us-central1
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/agents/support-agent:v1

# 2. Infra
cd terraform
terraform init
terraform apply -var="project_id=$PROJECT_ID" \
  -var="image=us-central1-docker.pkg.dev/$PROJECT_ID/agents/support-agent:v1"
```

## 🔒 Segurança e governança
- Conta de serviço dedicada só com `roles/aiplatform.user`
- Serviço do Cloud Run **privado** por padrão (exige autenticação IAM)
- Sem chaves no código: autenticação via identidade da conta de serviço
- Saída validada com Pydantic

## 📚 O que pratiquei
- IA generativa com saída estruturada (JSON schema)
- Prompt engineering para triagem
- Infraestrutura como Código e princípio do menor privilégio

## 🗺️ Próximos passos
- [ ] Integrar com Contact Center AI / CCaaS
- [ ] Grounding com a base de conhecimento (Vertex AI Search)
- [ ] Avaliação de qualidade das respostas (Gen AI Evaluation)
