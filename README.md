# Student Dropout Prediction API (FastAPI + Machine Learning)

API REST moderna desenvolvida em **FastAPI** para disponibilizar o modelo de Machine Learning com a **melhor acurácia** (Regressão Logística - 86.67% / 87.0%) treinado no dataset de predição de evasão escolar universitária ([Google Colab Original](https://colab.research.google.com/drive/1u0L7dhDVGh_r0NCNaKmYZD72lQwU1s7K?usp=sharing)).

---

## Destaques do Projeto

- **Melhor Modelo Selecionado**: Regressão Logística (86.67% de acurácia no teste), superando SVC (85.54%), Random Forest (85.08%), Decision Tree (83.05%) e KNN (82.03%).
- **Interface Web Embutida**: Painel interativo em `http://localhost:8000/` para simulação direta no navegador.
- **Documentação Interativa**: Swagger UI (`/docs`) e ReDoc (`/redoc`) automáticos.
- **Predição Individual & Em Lote**: Endpoints otimizados `/predict` e `/predict/batch`.
- **Cálculo de Risco & Probabilidade**: Retorna o percentual de probabilidade de evasão e classificação de risco (Baixo, Médio, Alto).
- **100% Coberto por Testes**: Suíte de testes unitários com `pytest`.

---

## Inicialização Rápida

### No Windows:
Dê dois cliques em `run.bat` ou execute:
```cmd
run.bat
```

### Manualmente:
```powershell
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Acesse:
- **Painel Web**: [http://localhost:8000](http://localhost:8000)
- **Documentação Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Manual Completo

Para detalhes aprofundados sobre a arquitetura, dicionário das 34 variáveis, exemplos em Python/cURL e retreinamento, consulte o arquivo [manual.md](manual.md).
