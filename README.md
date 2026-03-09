# Collective Showcase

A **Meritocracy Engine** for tracking and ranking team contributions with a live leaderboard. Aggregates GitHub activity (PRs, issues, commits) with line-of-code metrics to calculate fair, transparent merit scores.

## Features

- 🏆 **Live Leaderboard** — Real-time ranking by merit score
- 📊 **Comprehensive Metrics** — Tracks contributions, lines added/deleted, issues, and more
- 🎯 **Merit-Based Scoring** — Transparent algorithm factors in contributions (↑5pts), code changes (↑0.01pts/line), and issues (↑3pts)
- 👥 **Tiered Leadership** — Founder, Lead, Mentor, Member, Learner roles
- 🏅 **Achievement Badges** — Recognize specialized contributions (Architect, Reviewer, etc.)
- 🔄 **Auto-Sync** — Periodic sync with GitHub organization data
- 📈 **Impact Percentiles** — See your contribution's share of team output

## Tech Stack

**Backend:** Django 6, Django REST Framework, Celery, PostgreSQL  
**Frontend:** React 18, TypeScript, Tailwind CSS, Vite  
**Infrastructure:** Docker Compose, GitHub API v3 (GraphQL + REST)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- GitHub Personal Access Token (org member read + repo access)

### Setup

```bash
# Clone and enter directory
git clone https://github.com/bhos-sec/showcase.git
cd showcase

# Copy environment template
cp .env.example .env

# Edit .env with your GitHub credentials
nano .env

# Start development environment
make dev

# Seed initial data and sync
make seed
make sync
```

Visit `http://localhost:3000` for the frontend leaderboard.  
Admin panel: `http://localhost:8000/admin` (create superuser: `make superuser`)

## Scoring Algorithm

```
Score = (Contributions × 5) + (Lines Added × 0.01) + 
         (Lines Deleted × 0.005) + (Issues × 3)
```

**Priority:** Contributions > Code Changes > Issues

Members are ranked by total score, with impact showing their percentage of team's combined output.

## Available Commands

```bash
make dev          # Start development environment
make prod         # Start production environment
make migrate      # Run database migrations
make superuser    # Create Django admin user
make seed         # Bootstrap members from GitHub org
make sync         # Full sync: repos + contributions + scores
make shell        # Django interactive shell
make test         # Run tests
make logs         # View Docker logs
```

## Architecture

```
showcase/
├── backend/              # Django REST API
│   ├── apps/
│   │   ├── members/     # Leaderboard, scoring, profiles
│   │   ├── projects/    # Forge repositories
│   │   └── core/        # Shared models, permissions
│   └── config/          # Settings, URLs, Celery
├── frontend/            # React + TypeScript
│   └── src/
│       ├── components/  # Leaderboard, Forge
│       ├── hooks/       # Data fetching
│       └── services/    # API client
└── docker/              # Container configs
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, setup, and beginner-friendly tasks.

## Code of Conduct

This project adheres to the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards.

## License

[See LICENSE](LICENSE) for details.

## Maintainers

- [@huseynovvusal](https://github.com/huseynovvusal) — Project lead
- [@AamilAlakbarov](https://github.com/AamilAlakbarov) — Core contributor

---

**Questions?** Open an issue or reach out to the maintainers. All contributions welcome! 🚀
