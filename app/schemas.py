"""Estruturas de dados. Os mesmos modelos definem o formato que a OpenAI deve devolver."""
from pydantic import BaseModel, Field


# ---------- Dieta lida do arquivo ----------
class Alimento(BaseModel):
    nome: str
    quantidade: str  # texto livre: "2 fatias", "120 g", "à vontade"


class Refeicao(BaseModel):
    nome: str  # "Café da manhã"
    horario: str | None
    alimentos: list[Alimento]
    observacoes: str | None


class Dieta(BaseModel):
    refeicoes: list[Refeicao]
    restricoes: list[str]  # alergias, intolerâncias, "evitar X"
    observacoes_gerais: str | None
    pontos_incertos: list[str]  # trechos ilegíveis ou ambíguos


# ---------- Sugestões ----------
class Variacao(BaseModel):
    titulo: str
    tecnica: str  # ex.: "mexido cremoso", "assado no forno"
    temperos: list[str]
    passos: list[str]
    tempo_minutos: int | None


class SugestaoRefeicao(BaseModel):
    refeicao: str
    alimentos_base: list[str]
    variacoes: list[Variacao]


class Sugestoes(BaseModel):
    sugestoes: list[SugestaoRefeicao]
    avisos: list[str]


# ---------- Requisição da API ----------
class SugerirRequest(BaseModel):
    dieta: Dieta
    preferencias: str = Field(default="", max_length=1000)
    variacoes_por_refeicao: int = Field(default=3, ge=1, le=5)
