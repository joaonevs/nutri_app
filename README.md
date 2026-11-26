# Variações para a dieta

App básico: você envia o plano alimentar (**foto, PDF ou texto**) e a IA sugere **novos preparos e temperos para os mesmos alimentos**, sem alterar o plano.

**Stack:** Python + FastAPI + OpenAI (Responses API) + página HTML simples.

## Como rodar no VS Code

1. Abra a pasta no VS Code.
2. Terminal (Ctrl+`):
   ```bash
   python -m venv .venv
   # Windows:  .venv\Scripts\activate
   # Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e coloque sua `OPENAI_API_KEY`.
   Em `OPENAI_MODEL` use um modelo com **visão** (precisa ler imagens e PDFs).
4. Rode:
   ```bash
   uvicorn app.main:app --reload
   ```
   (ou aperte **F5**: já há uma configuração em `.vscode/launch.json`)
5. Abra http://127.0.0.1:8000. A documentação da API fica em http://127.0.0.1:8000/docs.

Para testar sem arquivo, cole o conteúdo de `exemplos/dieta_exemplo.txt` na caixa de texto.

## Como funciona

```
arquivo/texto ──► POST /api/extrair ──► dieta estruturada (você confere)
                                              │
preferências ─────────────────────────────────┴─► POST /api/sugerir ──► variações
```

Dois passos de propósito: a leitura de foto/PDF pode errar, então a pessoa **confere a dieta antes** de gerar as sugestões.

| Arquivo | Função |
|---|---|
| `app/main.py` | Rotas da API |
| `app/llm.py` | Chamadas à OpenAI e montagem de imagem/PDF/texto |
| `app/prompts.py` | Regras dos dois prompts (edite aqui para ajustar o comportamento) |
| `app/schemas.py` | Formato dos dados (e da resposta do modelo) |
| `static/index.html` | Tela |

## Regras que o prompt impõe

- Só os alimentos e quantidades do plano: nada é adicionado, trocado ou removido.
- Varia técnica de preparo e temperos de baixa caloria.
- Não adiciona gordura, açúcar, queijo, molhos ou farinhas.
- Respeita restrições e alergias lidas do plano.
- Sem conselho médico; a tela lembra de confirmar com o nutricionista.

## Privacidade (dados de saúde)

- As chamadas usam `store=False`: a OpenAI não guarda a conversa para consulta posterior.
- O prompt de leitura manda ignorar nome, CPF, nascimento e contatos.
- Nada é salvo em disco pelo app.
- Em testes, use dietas fictícias. Com pacientes reais, trate sob a LGPD e peça consentimento.

## Limites

- Formatos: PDF, PNG, JPG, WEBP e TXT (até 15 MB por arquivo, 10 arquivos). Foto de iPhone em HEIC: converta para JPG.
- Sem login: use só localmente. Antes de publicar, adicione autenticação.

## Próximos passos

- Editar a dieta na tela antes de gerar.
- Integrar com o WebDiet (n8n chamando `/api/sugerir` com a prescrição do paciente).
- Salvar favoritas e evitar repetir variações já sugeridas.
# nutri_app
