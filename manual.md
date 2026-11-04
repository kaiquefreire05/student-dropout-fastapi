# Manual de execução e integração

## API de previsão de evasão estudantil

Este documento explica como executar a API manualmente e como o front-end deve enviar os dados. A API foi construída com FastAPI e usa um modelo de Regressão Logística treinado com o dataset [Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), da UCI.

> **Importante:** a API prevê evasão (`Dropout`) ou não evasão (`Graduate`/`Enrolled`). Ela não retorna a classificação original de três classes separadamente. O modelo usa o alvo binário: `1 = Dropout` e `0 = Graduate ou Enrolled`.

## 1. Executar manualmente

### 1.1 Pré-requisitos

- Python 3.10 ou superior;
- `pip` instalado;
- terminal aberto na raiz do projeto, onde está `requirements.txt`.

No Linux/macOS:

```bash
cd /caminho/para/student_dropout_fastapi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

No Windows PowerShell:

```powershell
cd C:\caminho\para\student_dropout_fastapi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 1.2 Iniciar o servidor

Com o ambiente virtual ativado:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`--reload` é útil durante o desenvolvimento. Para permitir acesso por outros computadores da rede, use `--host 0.0.0.0`.

Endereços disponíveis:

- Interface: `http://127.0.0.1:8000/`
- Swagger/OpenAPI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Para encerrar, pressione `Ctrl+C`.

### 1.3 Verificar a instalação

Em outro terminal:

```bash
curl http://127.0.0.1:8000/health
python -m pytest tests -v
```

## 2. Endpoints

| Método | Caminho | Finalidade |
|---|---|---|
| `GET` | `/` | Abre a interface HTML de teste. |
| `GET` | `/health` | Verifica se a API e o modelo estão carregados. |
| `GET` | `/model/info` | Retorna features, métricas e informações do modelo. |
| `POST` | `/predict` | Prevê o risco de um estudante. |
| `POST` | `/predict/batch` | Prevê o risco de vários estudantes. |

Todas as requisições `POST` devem usar `Content-Type: application/json`.

## 3. Como o front-end deve montar os inputs

O formulário deve coletar os 34 campos da seção 4. Recomenda-se enviar todos eles, mesmo que o schema tenha valores padrão. Não use texto livre para campos codificados: use `select`, radio buttons ou controles equivalentes e envie o código inteiro.

A API aceita uma destas convenções de nomes:

- nomes originais, por exemplo `"Marital status"`;
- nomes `snake_case`, por exemplo `"marital_status"`.

Para um front-end novo, recomenda-se `snake_case`. Não misture convenções no mesmo payload.

Tipos:

- `int`: número inteiro, não uma string como `"1"`;
- `float`: número decimal JSON com ponto, como `15.5`;
- indicadores: `0` para não e `1` para sim, salvo indicação específica;
- notas: normalmente de `0` a `20`;
- contagens de disciplinas: inteiros maiores ou iguais a zero.

## 4. Dicionário dos 34 campos de entrada

Os nomes abaixo são os nomes `snake_case` recomendados. O nome original aparece entre parênteses.

### 4.1 Dados de candidatura e perfil

| Campo | Tipo | Valores e significado |
|---|---:|---|
| `marital_status` (`Marital status`) | int | `1` solteiro; `2` casado; `3` viúvo; `4` divorciado; `5` união de facto; `6` separado legalmente. |
| `application_mode` (`Application mode`) | int | Código do modo de candidatura; consulte a seção 5. |
| `application_order` (`Application order`) | int | Ordem do curso: `0` primeira escolha até `9` última. |
| `course` (`Course`) | int | Código do curso; consulte a seção 5. |
| `daytime_evening_attendance` (`Daytime/evening attendance`) | int | `1` diurno; `0` noturno. |
| `previous_qualification` (`Previous qualification`) | int | Código da escolaridade anterior; consulte a seção 5. |
| `nationality` (`Nationality`) | int | Código da nacionalidade; `1` portuguesa. |
| `age_at_enrollment` (`Age at enrollment`) | int | Idade na matrícula. |
| `gender` (`Gender`) | int | `1` masculino; `0` feminino. |
| `international` (`International`) | int | `1` internacional; `0` não internacional. |

### 4.2 Família e situação socioeconômica

| Campo | Tipo | Valores e significado |
|---|---:|---|
| `mothers_qualification` (`Mother's qualification`) | int | Código da escolaridade da mãe. |
| `fathers_qualification` (`Father's qualification`) | int | Código da escolaridade do pai. |
| `mothers_occupation` (`Mother's occupation`) | int | Código da ocupação da mãe. |
| `fathers_occupation` (`Father's occupation`) | int | Código da ocupação do pai. |
| `displaced` (`Displaced`) | int | `1` deslocado da residência de origem; `0` não. |
| `educational_special_needs` (`Educational special needs`) | int | `1` possui necessidades especiais; `0` não. |
| `debtor` (`Debtor`) | int | `1` possui dívida; `0` não possui. |
| `tuition_fees_up_to_date` (`Tuition fees up to date`) | int | `1` mensalidades em dia; `0` não. |
| `scholarship_holder` (`Scholarship holder`) | int | `1` bolsista; `0` não bolsista. |

### 4.3 Desempenho acadêmico

Os seis campos de cada semestre têm o mesmo significado, mudando apenas `1st` para primeiro semestre e `2nd` para segundo semestre:

| Sufixo | Tipo | Significado |
|---|---:|---|
| `credited` | int | Disciplinas creditadas por equivalência. |
| `enrolled` | int | Disciplinas em que o aluno se matriculou. |
| `evaluations` | int | Disciplinas/avaliações realizadas. |
| `approved` | int | Disciplinas aprovadas. |
| `grade` | float | Média ponderada, normalmente de `0` a `20`. |
| `without_evaluations` | int | Disciplinas sem avaliação. |

Os nomes completos são:

- `curricular_units_1st_sem_credited`, `curricular_units_1st_sem_enrolled`, `curricular_units_1st_sem_evaluations`, `curricular_units_1st_sem_approved`, `curricular_units_1st_sem_grade`, `curricular_units_1st_sem_without_evaluations`;
- `curricular_units_2nd_sem_credited`, `curricular_units_2nd_sem_enrolled`, `curricular_units_2nd_sem_evaluations`, `curricular_units_2nd_sem_approved`, `curricular_units_2nd_sem_grade`, `curricular_units_2nd_sem_without_evaluations`.

### 4.4 Indicadores macroeconômicos

| Campo | Tipo | Significado |
|---|---:|---|
| `unemployment_rate` (`Unemployment rate`) | float | Taxa de desemprego do período/região, em porcentagem. |
| `inflation_rate` (`Inflation rate`) | float | Taxa de inflação do período, em porcentagem. |
| `gdp` (`GDP`) | float | Variação do PIB do período, em porcentagem. |

### 4.5 Diferença em relação ao dataset original

A UCI informa 36 features no dataset original. Este projeto usa 34. O campo `Previous qualification (grade)` não é aceito pela API e foi removido do conjunto usado pelo modelo. O campo `Target` também não é input: é o resultado histórico usado no treinamento e não deve ser enviado pelo front-end.

## 5. Códigos categóricos da UCI

Para candidatura, curso, escolaridade, nacionalidade e ocupação, envie o código numérico original, não o texto traduzido. O front-end pode mostrar rótulos em português e manter um dicionário `{codigo, label}`, mas deve enviar apenas `codigo` no JSON.

As listas completas e oficiais estão na tabela **Variables Table** da [página do dataset na UCI](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success). Exemplos:

- `application_mode`: `1` primeira fase/concurso geral; `42` transferência; `43` mudança de curso; `57` mudança de instituição/curso internacional;
- `course`: `33` tecnologias de produção de biocombustíveis; `9003` agronomia; `9119` engenharia informática; `9500` enfermagem; `9773` jornalismo e comunicação;
- `previous_qualification`: `1` ensino secundário; `2` bacharelado; `3` licenciatura; `4` mestrado; `5` doutorado; `42` curso técnico superior profissional;
- `nationality`: `1` portuguesa; `41` brasileira; `22` cabo-verdiana; `21` angolana; `6` espanhola.

Não presuma que códigos são sequenciais ou que um código maior representa um nível maior: são categorias nominais definidas pela UCI.

## 6. Exemplo de requisição individual

Payload completo usando `snake_case`:

```json
{
  "marital_status": 1,
  "application_mode": 8,
  "application_order": 5,
  "course": 2,
  "daytime_evening_attendance": 1,
  "previous_qualification": 1,
  "nationality": 1,
  "mothers_qualification": 13,
  "fathers_qualification": 10,
  "mothers_occupation": 6,
  "fathers_occupation": 10,
  "displaced": 1,
  "educational_special_needs": 0,
  "debtor": 0,
  "tuition_fees_up_to_date": 1,
  "gender": 1,
  "scholarship_holder": 0,
  "age_at_enrollment": 20,
  "international": 0,
  "curricular_units_1st_sem_credited": 0,
  "curricular_units_1st_sem_enrolled": 6,
  "curricular_units_1st_sem_evaluations": 6,
  "curricular_units_1st_sem_approved": 4,
  "curricular_units_1st_sem_grade": 12.5,
  "curricular_units_1st_sem_without_evaluations": 0,
  "curricular_units_2nd_sem_credited": 0,
  "curricular_units_2nd_sem_enrolled": 6,
  "curricular_units_2nd_sem_evaluations": 6,
  "curricular_units_2nd_sem_approved": 5,
  "curricular_units_2nd_sem_grade": 14.0,
  "curricular_units_2nd_sem_without_evaluations": 0,
  "unemployment_rate": 10.8,
  "inflation_rate": 1.4,
  "gdp": 1.74
}
```

Salvar como `student.json` e executar:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d @student.json
```

Em JavaScript:

```javascript
const response = await fetch("http://127.0.0.1:8000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(student)
});

if (!response.ok) {
  const error = await response.json();
  throw new Error(error.detail ?? "Falha na predição");
}

const result = await response.json();
```

## 7. Retorno detalhado de `POST /predict`

HTTP `200 OK`:

```json
{
  "prediction": 0,
  "prediction_label": "Non-Dropout (Permanência / Conclusão)",
  "risk_level": "Baixo Risco",
  "dropout_probability": 0.08,
  "retention_probability": 0.92,
  "model_used": "Logistic Regression",
  "model_accuracy": 0.8667,
  "timestamp": "2026-10-16T15:30:00.123456"
}
```

| Campo | Tipo | Interpretação |
|---|---:|---|
| `prediction` | int | `1` = evasão prevista; `0` = não evasão prevista. |
| `prediction_label` | string | Texto da classe prevista. |
| `risk_level` | string | `Baixo Risco`, `Médio Risco` ou `Alto Risco de Evasão`. |
| `dropout_probability` | float | Probabilidade de evasão, entre `0` e `1`; multiplique por `100` para percentual. |
| `retention_probability` | float | Probabilidade de permanência/conclusão, entre `0` e `1`. |
| `model_used` | string | Nome do modelo usado, atualmente `Logistic Regression`. |
| `model_accuracy` | float | Acurácia no teste, atualmente `0.8667` (86,67%); não é a probabilidade deste estudante. |
| `timestamp` | string | Data/hora da resposta em UTC, no formato ISO 8601. |

As probabilidades devem somar aproximadamente `1`. Preserve os valores originais para auditoria e formate o percentual apenas na interface.

## 8. Retorno detalhado de `POST /predict/batch`

Envie `{ "students": [ ... ] }`, em que cada item é um payload individual completo. A resposta tem o formato:

```json
{
  "total_students": 2,
  "predictions": [
    {
      "prediction": 1,
      "prediction_label": "Dropout (Evasão Escolar)",
      "risk_level": "Alto Risco de Evasão",
      "dropout_probability": 0.94,
      "retention_probability": 0.06,
      "model_used": "Logistic Regression",
      "model_accuracy": 0.8667,
      "timestamp": "2026-10-16T15:30:00.123456"
    }
  ],
  "summary": {
    "total_students": 2,
    "predicted_dropout_count": 1,
    "predicted_retention_count": 1,
    "dropout_rate_percent": 50.0,
    "average_dropout_probability": 0.48
  },
  "timestamp": "2026-10-16T15:30:00.123456"
}
```

`predictions[i]` corresponde ao estudante enviado em `students[i]`. `summary` é um agregado da lista inteira, não uma nova predição. O objeto completo de cada estudante segue o mesmo formato descrito na seção 7.

## 9. Healthcheck e informações do modelo

### `GET /health`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "Logistic Regression",
  "model_accuracy": 0.8667,
  "timestamp": "2026-10-16T15:30:00.123456"
}
```

Considere o serviço pronto somente quando `status` for `healthy` e `model_loaded` for `true`.

### `GET /model/info`

Retorna `best_model_name`, `best_accuracy`, `hyperparameters`, `target_mapping`, `features_count`, `features`, `metrics` e `benchmark_comparison`. Use `features` apenas para conferência dos nomes e da ordem esperados.

## 10. Erros

| HTTP | Situação | Formato típico |
|---:|---|---|
| `400` | Lote com `students: []`. | `{"detail":"A lista de estudantes não pode ser vazia."}` |
| `422` | JSON inválido, tipo incorreto ou erro de validação. | `{"detail":[{"loc":[...],"msg":"...","type":"..."}]}` |
| `500` | Falha durante a inferência. | `{"detail":"Erro durante o processamento da inferência: ..."}` |
| `503` | Modelo ainda não carregado em `/model/info`. | `{"detail":"O modelo de Machine Learning ainda não foi carregado em memória."}` |

O front-end deve tratar qualquer status diferente de `2xx`, mostrar uma mensagem compreensível e não interpretar uma resposta de erro como resultado de predição.

## 11. Observações do modelo e retreinamento

- O modelo atual é Regressão Logística e obteve acurácia de teste de `86,67%`.
- A probabilidade é uma estimativa estatística, não uma certeza ou diagnóstico individual.
- O modelo usa indicadores do primeiro e segundo semestre; o front-end deve deixar claro quando esses dados estiverem disponíveis.
- Os artefatos estão em `models/`: `best_model.joblib`, `scaler.joblib` e `model_metadata.json`.
- Para retreinar após atualizar o CSV, execute `python scripts/train.py` na raiz e rode os testes novamente.

## 12. Fonte dos dados

Realinho, V., Vieira Martins, M., Machado, J. e Baptista, L. (2021). *Predict Students' Dropout and Academic Success*. UCI Machine Learning Repository. DOI: [10.24432/C5MC89](https://doi.org/10.24432/C5MC89).

As descrições e os códigos categóricos devem ser conferidos na [página oficial da UCI](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), fonte de referência para interpretação das variáveis.

## 13. Catálogo completo de códigos para o front-end

Esta seção substitui os exemplos resumidos da seção 5. Os valores abaixo são os códigos completos publicados pela UCI. O front-end pode usar o texto em português como `label` e enviar o número como `value`.

### `application_mode` — modo de candidatura

`1` primeira fase — contingente geral; `2` Portaria nº 612/93; `5` primeira fase — contingente especial dos Açores; `7` titulares de outros cursos superiores; `10` Portaria nº 854-B/99; `15` estudante internacional — licenciatura; `16` primeira fase — contingente especial da Madeira; `17` segunda fase — contingente geral; `18` terceira fase — contingente geral; `26` Portaria nº 533-A/99, item b2 — plano diferente; `27` Portaria nº 533-A/99, item b3 — outra instituição; `39` maiores de 23 anos; `42` transferência; `43` mudança de curso; `44` titulares de diploma de especialização tecnológica; `51` mudança de instituição/curso; `53` titulares de diploma de ciclo curto; `57` mudança de instituição/curso — internacional.

### `course` — curso

`33` tecnologias de produção de biocombustíveis; `171` design de animação e multimídia; `8014` serviço social — turno noturno; `9003` agronomia; `9070` design de comunicação; `9085` enfermagem veterinária; `9119` engenharia informática; `9130` equinicultura; `9147` gestão; `9238` serviço social; `9254` turismo; `9500` enfermagem; `9556` higiene oral; `9670` publicidade e marketing; `9773` jornalismo e comunicação; `9853` educação básica; `9991` gestão — turno noturno.

### `previous_qualification` — escolaridade anterior

`1` ensino secundário; `2` ensino superior — bacharelado; `3` ensino superior — licenciatura; `4` ensino superior — mestrado; `5` ensino superior — doutorado; `6` frequência do ensino superior; `9` 12º ano incompleto; `10` 11º ano incompleto; `12` outra formação — 11º ano; `14` 10º ano; `15` 10º ano incompleto; `19` ensino básico — 3º ciclo (9º/10º/11º ano) ou equivalente; `38` ensino básico — 2º ciclo (6º/7º/8º ano) ou equivalente; `39` curso de especialização tecnológica; `40` ensino superior — licenciatura (1º ciclo); `42` curso técnico superior profissional; `43` ensino superior — mestrado (2º ciclo).

### `nationality` — nacionalidade

`1` portuguesa; `2` alemã; `6` espanhola; `11` italiana; `13` neerlandesa; `14` inglesa; `17` lituana; `21` angolana; `22` cabo-verdiana; `24` guineense; `25` moçambicana; `26` são-tomense; `32` turca; `41` brasileira; `62` romena; `100` moldava; `101` mexicana; `103` ucraniana; `105` russa; `108` cubana; `109` colombiana.

### `mothers_qualification` — escolaridade da mãe

`1` ensino secundário — 12º ano ou equivalente; `2` ensino superior — bacharelado; `3` ensino superior — licenciatura; `4` ensino superior — mestrado; `5` ensino superior — doutorado; `6` frequência do ensino superior; `9` 12º ano incompleto; `10` 11º ano incompleto; `11` 7º ano antigo; `12` outra formação — 11º ano; `14` 10º ano; `18` curso geral de comércio; `19` ensino básico — 3º ciclo ou equivalente; `22` curso técnico-profissional; `26` 7º ano; `27` 2º ciclo do curso geral do ensino secundário; `29` 9º ano incompleto; `30` 8º ano; `34` desconhecido; `35` não sabe ler nem escrever; `36` sabe ler, mas não concluiu o 4º ano; `37` ensino básico — 1º ciclo (4º/5º ano) ou equivalente; `38` ensino básico — 2º ciclo ou equivalente; `39` curso de especialização tecnológica; `40` ensino superior — licenciatura (1º ciclo); `41` curso de estudos superiores especializados; `42` curso técnico superior profissional; `43` ensino superior — mestrado (2º ciclo); `44` ensino superior — doutorado (3º ciclo).

### `fathers_qualification` — escolaridade do pai

`1` ensino secundário — 12º ano ou equivalente; `2` ensino superior — bacharelado; `3` ensino superior — licenciatura; `4` ensino superior — mestrado; `5` ensino superior — doutorado; `6` frequência do ensino superior; `9` 12º ano incompleto; `10` 11º ano incompleto; `11` 7º ano antigo; `12` outra formação — 11º ano; `13` 2º ano do ensino secundário complementar; `14` 10º ano; `18` curso geral de comércio; `19` ensino básico — 3º ciclo ou equivalente; `20` curso complementar do ensino secundário; `22` curso técnico-profissional; `25` curso complementar do ensino secundário incompleto; `26` 7º ano; `27` 2º ciclo do curso geral do ensino secundário; `29` 9º ano incompleto; `30` 8º ano; `31` curso geral de administração e comércio; `33` contabilidade e administração complementar; `34` desconhecido; `35` não sabe ler nem escrever; `36` sabe ler, mas não concluiu o 4º ano; `37` ensino básico — 1º ciclo ou equivalente; `38` ensino básico — 2º ciclo ou equivalente; `39` curso de especialização tecnológica; `40` ensino superior — licenciatura (1º ciclo); `41` curso de estudos superiores especializados; `42` curso técnico superior profissional; `43` ensino superior — mestrado (2º ciclo); `44` ensino superior — doutorado (3º ciclo).

### `mothers_occupation` — ocupação da mãe

`0` estudante; `1` representantes do poder legislativo e órgãos executivos, diretores e gestores executivos; `2` especialistas em atividades intelectuais e científicas; `3` técnicos e profissionais de nível intermediário; `4` pessoal administrativo; `5` trabalhadores de serviços pessoais, segurança e vendedores; `6` agricultores e trabalhadores qualificados da agricultura, pesca e silvicultura; `7` trabalhadores qualificados da indústria, construção e artesanato; `8` operadores de instalações, máquinas e trabalhadores de montagem; `9` trabalhadores não qualificados; `10` profissões das forças armadas; `90` outra situação; `99` sem informação; `122` profissionais da saúde; `123` professores; `125` especialistas em tecnologias da informação e comunicação; `131` técnicos de ciência e engenharia de nível intermediário; `132` técnicos e profissionais de saúde de nível intermediário; `134` técnicos de nível intermediário de serviços jurídicos, sociais, esportivos, culturais e similares; `141` funcionários de escritório, secretários e operadores de processamento de dados; `143` operadores de dados, contabilidade, estatística, serviços financeiros e registros; `144` outro pessoal de apoio administrativo; `151` trabalhadores de serviços pessoais; `152` vendedores; `153` cuidadores pessoais e similares; `171` trabalhadores qualificados da construção, exceto eletricistas; `173` trabalhadores qualificados de impressão, instrumentos de precisão, joalheria, artesanato e similares; `175` trabalhadores qualificados de alimentos, madeira, vestuário e outras indústrias e ofícios; `191` trabalhadores de limpeza; `192` trabalhadores não qualificados da agricultura, produção animal, pesca e silvicultura; `193` trabalhadores não qualificados da extração, construção, indústria e transporte; `194` auxiliares de preparação de refeições.

### `fathers_occupation` — ocupação do pai

`0` estudante; `1` representantes do poder legislativo e órgãos executivos, diretores e gestores executivos; `2` especialistas em atividades intelectuais e científicas; `3` técnicos e profissionais de nível intermediário; `4` pessoal administrativo; `5` trabalhadores de serviços pessoais, segurança e vendedores; `6` agricultores e trabalhadores qualificados da agricultura, pesca e silvicultura; `7` trabalhadores qualificados da indústria, construção e artesanato; `8` operadores de instalações, máquinas e trabalhadores de montagem; `9` trabalhadores não qualificados; `10` profissões das forças armadas; `90` outra situação; `99` sem informação; `101` oficiais das forças armadas; `102` sargentos das forças armadas; `103` outro pessoal das forças armadas; `112` diretores de serviços administrativos e comerciais; `114` diretores de hotéis, restauração, comércio e outros serviços; `121` especialistas em ciências físicas, matemática, engenharia e técnicas relacionadas; `122` profissionais da saúde; `123` professores; `124` especialistas em finanças, contabilidade, organização administrativa e relações públicas e comerciais; `131` técnicos de ciência e engenharia de nível intermediário; `132` técnicos e profissionais de saúde de nível intermediário; `134` técnicos de nível intermediário de serviços jurídicos, sociais, esportivos, culturais e similares; `135` técnicos de tecnologias da informação e comunicação; `141` funcionários de escritório, secretários e operadores de processamento de dados; `143` operadores de dados, contabilidade, estatística, serviços financeiros e registros; `144` outro pessoal de apoio administrativo; `151` trabalhadores de serviços pessoais; `152` vendedores; `153` cuidadores pessoais e similares; `154` pessoal de proteção e segurança; `161` agricultores orientados ao mercado e trabalhadores qualificados da produção agrícola e animal; `163` agricultores, criadores de animais, pescadores, caçadores e coletores de subsistência; `171` trabalhadores qualificados da construção, exceto eletricistas; `172` trabalhadores qualificados da metalurgia e metalomecânica; `174` trabalhadores qualificados de eletricidade e eletrônica; `175` trabalhadores qualificados de alimentos, madeira, vestuário e outras indústrias e ofícios; `181` operadores de instalações fixas e máquinas; `182` trabalhadores de montagem; `183` condutores de veículos e operadores de equipamentos móveis; `192` trabalhadores não qualificados da agricultura, produção animal, pesca e silvicultura; `193` trabalhadores não qualificados da extração, construção, indústria e transporte; `194` auxiliares de preparação de refeições; `195` vendedores ambulantes e prestadores de serviços de rua, exceto alimentação.

Os demais campos da API são binários, contagens, notas ou indicadores macroeconômicos e já estão completamente descritos nas tabelas das seções 4. Não possuem uma tabela adicional de códigos categóricos.
