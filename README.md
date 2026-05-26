# CM Scout

Plataforma de análise esportiva para identificação de oportunidades de apostas, usando motores de análise com padrão Strategy e integração com a API football-data.org.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Django 4.2, Python 3.11 |
| Banco de dados | PostgreSQL 15 |
| Cache / Fila | Redis 7, Celery 5, Celery Beat |
| Frontend | Tailwind CSS (Play CDN), HTMX, Alpine.js, Chart.js |
| Autenticação | Django Allauth (email-based) |
| Proteção | django-axes (brute-force) |
| Estáticos | WhiteNoise |
| Containerização | Docker + Docker Compose |
| API externa | [football-data.org v4](https://www.football-data.org/) |

---

## Pré-requisitos

- Docker Desktop instalado e rodando
- Chave de API: [football-data.org](https://www.football-data.org/) (plano gratuito disponível)

---

## Setup com Docker (recomendado)

### 1. Clonar e configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e preencha:

```env
SECRET_KEY=sua-chave-secreta-longa
DEBUG=True
DB_PASSWORD=suasenha
FOOTBALL_DATA_API_KEY=sua-chave-football-data
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-email
```

### 2. Subir containers

```bash
docker compose up --build
```

### 3. Migrations e superusuário

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 4. Acesso

| Serviço | URL |
|---|---|
| Aplicação | http://localhost:8000 |
| Admin Django | http://localhost:8000/admin/ |
| Flower (Celery) | http://localhost:5555 |

---

## Sincronização de Dados

Após subir a aplicação, sincronize os dados via shell:

```bash
docker compose exec web python manage.py shell
```

```python
from services.football_api import FootballAPIService
svc = FootballAPIService()
svc.sync_leagues()
svc.sync_upcoming_fixtures()
svc.sync_standings()
svc.compute_team_statistics()
```

A sincronização diária de standings ocorre automaticamente via Celery Beat às **03:00**.

---

## Arquitetura

```
config/           → settings, urls, celery, wsgi/asgi
apps/
  accounts/       → modelo User customizado, perfil
  core/           → modelos base, middleware, templatetags
  dashboard/      → view principal com métricas
  fixtures/       → partidas, filtros, HTMX
  leagues/        → ligas suportadas
  teams/          → times
  statistics/     → standings, TeamStatistics
  odds/           → cotações por bookmaker
  analysis/       → motores de análise (Strategy Pattern)
  favorites/      → favoritos do usuário
  alerts/         → alertas de oportunidades
  reports/        → relatórios de desempenho
services/
  football_api.py → integração football-data.org (com cache Redis)
templates/        → Django Templates (hierarquia base → partials)
static/           → CSS, JS e imagens
```

### Motores de Análise

| Motor | Mercado | Descrição |
|---|---|---|
| `Over25Engine` | Over 2.5 | Score baseado em médias de gols, BTTS e histórico H2H |
| `BTTSEngine` | BTTS | Ambas equipes marcam — analisa taxas de gol e clean sheet |
| `FavoriteEngine` | 1X2 | Favorito a vencer — usa standings, forma e confrontos |
| `HandicapEngine` | Handicap | Vantagem de handicap asiático — domínio doméstico |

Score: 0–30 = Baixa · 31–60 = Média · 61–100 = Alta confiança

---

## Ligas Suportadas

| Liga | Código |
|---|---|
| Premier League (Inglaterra) | PL |
| Championship (Inglaterra) | ELC |
| La Liga (Espanha) | PD |
| Bundesliga (Alemanha) | BL1 |
| Serie A (Itália) | SA |
| Ligue 1 (França) | FL1 |
| Eredivisie (Holanda) | DED |
| Primeira Liga (Portugal) | PPL |
| UEFA Champions League | CL |
| Brasileirão Série A | BSA |

> Ligas disponíveis no plano gratuito (TIER_ONE) da football-data.org.

---

## Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|---|---|---|
| `SECRET_KEY` | Django secret key | ✅ |
| `DEBUG` | Modo debug | ✅ |
| `DB_NAME` | Nome do banco | ✅ |
| `DB_USER` | Usuário do banco | ✅ |
| `DB_PASSWORD` | Senha do banco | ✅ |
| `DB_HOST` | Host do banco | ✅ |
| `REDIS_URL` | URL do Redis | ✅ |
| `FOOTBALL_DATA_API_KEY` | Chave football-data.org | ✅ |
| `EMAIL_HOST` | Servidor SMTP | Opcional |
| `EMAIL_HOST_USER` | Usuário SMTP | Opcional |
| `EMAIL_HOST_PASSWORD` | Senha SMTP | Opcional |
| `ALLOWED_HOSTS` | Hosts permitidos (prod) | Produção |

