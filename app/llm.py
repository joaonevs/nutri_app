"""Integração com a OpenAI (Responses API). Imagens e PDFs vão direto para o modelo."""
import base64
import os
from pathlib import Path

from openai import OpenAI

from .prompts import PROMPT_EXTRACAO, PROMPT_SUGESTAO
from .schemas import Dieta, Sugestoes

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

EXTENSOES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".txt": "text/plain",
}
MAX_BYTES = 15 * 1024 * 1024
MAX_ARQUIVOS = 10
MAX_TEXTO = 50_000


class EntradaInvalida(ValueError):
    """Arquivo ou texto fora do que o app aceita."""


class RespostaInvalida(RuntimeError):
    """O modelo não devolveu algo utilizável."""


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # lê OPENAI_API_KEY do ambiente
    return _client


def montar_partes(arquivos: list[tuple[str, bytes]], texto: str) -> list[dict]:
    """Converte arquivos/texto nos blocos de entrada da Responses API."""
    if len(arquivos) > MAX_ARQUIVOS:
        raise EntradaInvalida(f"Envie no máximo {MAX_ARQUIVOS} arquivos.")
    if len(texto) > MAX_TEXTO:
        raise EntradaInvalida("Texto muito grande.")

    partes: list[dict] = []
    for nome, conteudo in arquivos:
        mime = EXTENSOES.get(Path(nome).suffix.lower())
        if mime is None:
            raise EntradaInvalida(f"Formato não suportado: {nome}. Use PDF, PNG, JPG, WEBP ou TXT.")
        if not conteudo:
            raise EntradaInvalida(f"O arquivo {nome} está vazio.")
        if len(conteudo) > MAX_BYTES:
            raise EntradaInvalida(f"O arquivo {nome} passa de {MAX_BYTES // (1024 * 1024)} MB.")

        b64 = base64.b64encode(conteudo).decode()
        if mime == "application/pdf":
            partes.append({"type": "input_file", "filename": nome, "file_data": f"data:{mime};base64,{b64}"})
        elif mime.startswith("image/"):
            partes.append({"type": "input_image", "image_url": f"data:{mime};base64,{b64}", "detail": "high"})
        else:
            partes.append({"type": "input_text", "text": f"[Arquivo {nome}]\n{conteudo.decode('utf-8', errors='replace')}"})

    if texto.strip():
        partes.append({"type": "input_text", "text": f"[Texto colado]\n{texto.strip()}"})
    if not partes:
        raise EntradaInvalida("Envie ao menos um arquivo ou cole o texto da dieta.")
    return partes


def extrair_dieta(arquivos: list[tuple[str, bytes]], texto: str = "") -> Dieta:
    """Passo 1: lê foto/PDF/texto e devolve a dieta estruturada."""
    partes = montar_partes(arquivos, texto)
    resp = _get_client().responses.parse(
        model=MODEL,
        store=False,  # dados de saúde: não guardar a conversa na OpenAI
        instructions=PROMPT_EXTRACAO,
        input=[{"role": "user", "content": [{"type": "input_text", "text": "Transcreva o plano alimentar abaixo."}, *partes]}],
        text_format=Dieta,
    )
    if resp.output_parsed is None:
        raise RespostaInvalida("O modelo não devolveu uma resposta válida.")
    return resp.output_parsed


def sugerir_variacoes(dieta: Dieta, preferencias: str = "", por_refeicao: int = 3) -> Sugestoes:
    """Passo 2: sugere novos preparos e temperos para os mesmos alimentos."""
    pedido = (
        f"PLANO ALIMENTAR (JSON):\n{dieta.model_dump_json(indent=2)}\n\n"
        f"PREFERÊNCIAS DA PESSOA: {preferencias.strip() or 'nenhuma informada'}\n\n"
        f"Gere {por_refeicao} variações para cada refeição."
    )
    resp = _get_client().responses.parse(
        model=MODEL,
        store=False,
        instructions=PROMPT_SUGESTAO,
        input=pedido,
        text_format=Sugestoes,
    )
    if resp.output_parsed is None:
        raise RespostaInvalida("O modelo não devolveu uma resposta válida.")
    return resp.output_parsed
