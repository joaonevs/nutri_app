from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # precisa rodar antes de importar o módulo llm (lê OPENAI_MODEL)

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from openai import AuthenticationError, OpenAIError  # noqa: E402

from . import llm  # noqa: E402
from .schemas import Dieta, SugerirRequest, Sugestoes  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title="Variações para a dieta")


def _erro_openai(e: OpenAIError) -> HTTPException:
    if isinstance(e, AuthenticationError) or "api_key" in str(e).lower():
        return HTTPException(500, "Chave da OpenAI ausente ou inválida. Confira o arquivo .env.")
    return HTTPException(502, f"Falha ao chamar a OpenAI: {getattr(e, 'message', e)}")


@app.get("/")
def home():
    return FileResponse(BASE / "static" / "index.html")


@app.post("/api/extrair", response_model=Dieta)
def extrair(arquivos: list[UploadFile] = File(default=[]), texto: str = Form(default="")):
    """Recebe fotos, PDFs ou texto da dieta e devolve a dieta estruturada."""
    try:
        dados = [(a.filename or "arquivo", a.file.read()) for a in arquivos]
        return llm.extrair_dieta(dados, texto)
    except llm.EntradaInvalida as e:
        raise HTTPException(422, str(e))
    except llm.RespostaInvalida as e:
        raise HTTPException(502, str(e))
    except OpenAIError as e:
        raise _erro_openai(e)


@app.post("/api/sugerir", response_model=Sugestoes)
def sugerir(req: SugerirRequest):
    """Recebe a dieta (já conferida) e devolve variações de preparo e temperos."""
    if not req.dieta.refeicoes:
        raise HTTPException(422, "A dieta não tem refeições. Confira a leitura do arquivo.")
    try:
        return llm.sugerir_variacoes(req.dieta, req.preferencias, req.variacoes_por_refeicao)
    except llm.RespostaInvalida as e:
        raise HTTPException(502, str(e))
    except OpenAIError as e:
        raise _erro_openai(e)
