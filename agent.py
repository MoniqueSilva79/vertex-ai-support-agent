"""Agente de triagem de chamados com Gemini no Vertex AI (FastAPI)."""
import json
import os
from typing import Literal

import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerationConfig, GenerativeModel

PROJECT_ID = os.environ["PROJECT_ID"]
REGION = os.environ.get("REGION", "us-central1")
MODEL = os.environ.get("MODEL", "gemini-2.0-flash")

vertexai.init(project=PROJECT_ID, location=REGION)

SYSTEM = (
    "Você é um analista sênior de suporte. Classifique o chamado do cliente. "
    "Categorias permitidas: Faturamento, Conectividade, Cadastro, Cancelamento, Técnico, Outros. "
    "Prioridade 'alta' se houver serviço parado, risco financeiro ou cliente muito insatisfeito. "
    "Escreva a resposta sugerida em português, empática, objetiva e sem prometer prazos."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "categoria": {"type": "string",
                      "enum": ["Faturamento", "Conectividade", "Cadastro", "Cancelamento", "Técnico", "Outros"]},
        "prioridade": {"type": "string", "enum": ["baixa", "media", "alta"]},
        "sentimento": {"type": "string", "enum": ["positivo", "neutro", "negativo"]},
        "resumo": {"type": "string"},
        "resposta_sugerida": {"type": "string"},
    },
    "required": ["categoria", "prioridade", "sentimento", "resumo", "resposta_sugerida"],
}

model = GenerativeModel(MODEL, system_instruction=SYSTEM)
app = FastAPI(title="Agente de Triagem de Chamados")


class Ticket(BaseModel):
    texto: str = Field(min_length=5, max_length=5000)


class Triage(BaseModel):
    categoria: Literal["Faturamento", "Conectividade", "Cadastro", "Cancelamento", "Técnico", "Outros"]
    prioridade: Literal["baixa", "media", "alta"]
    sentimento: Literal["positivo", "neutro", "negativo"]
    resumo: str
    resposta_sugerida: str


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/triage", response_model=Triage)
def triage(ticket: Ticket):
    response = model.generate_content(
        f"Chamado do cliente:\n\"\"\"{ticket.texto}\"\"\"",
        generation_config=GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
        ),
    )
    try:
        return Triage(**json.loads(response.text))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"Resposta inválida do modelo: {exc}") from exc
