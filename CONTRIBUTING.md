# Contributing to Collective Showcase

Thanks for your interest in contributing! This guide is designed to be **beginner-friendly** while covering everything you need to get started.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Making Changes](#making-changes)
4. [Testing](#testing)
5. [Submitting Changes](#submitting-changes)

---

## Getting Started

### Prerequisites

You'll need:
- **Git** — Version control ([install](https://git-scm.com/))
- **Docker & Docker Compose** — Containerization ([install](https://docs.docker.com/get-docker/))
- **GitHub Account** — For authentication
- **Text Editor** — VS Code, Sublime, etc. (optional but recommended)

### Fork & Clone

```bash
# 1. Fork the repository on GitHub (click "Fork" button)

# 2. Clone your fork to your computer
git clone https://github.com/YOUR_USERNAME/showcase.git
cd showcase

# 3. Add upstream remote (to stay synced with main repo)
git remote add upstream https://github.com/bhos-sec/showcase.git
```

---

## Development Setup

### Step-by-Step Setup (First Time Only)

```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Edit .env with your GitHub token
nano .env
# Add your GitHub Personal Access Token (Settings → Developer Settings → Tokens)
# Minimum permissions needed:
#   - repo (or public_repo for public repos only)
#   - read:org (to read organization members)

# 3. Start the development environment
make dev
# This takes 2-3 minutes on first run (building Docker images)

# 4. In a new terminal, bootstrap initial data
make seed

# 5. Run the sync to fetch GitHub data
make sync

# 6. Create a superuser (admin account)
make superuser
# Follow the prompts to set username and password
```

### Verify It's Working

- **Frontend:** http://localhost:3000 — Should see the leaderboard
- **Backend API:** http://localhost:8000/api/ — Should see REST endpoints
- **Admin Panel:** http://localhost:8000/admin — Sign in with your superuser credentials

### Useful Commands During Development

```bash
# View logs in real-time
make logs

# Open Django shell (interactive Python with models loaded)
make shell

# Run database migrations
make migrate

# Stop everything
docker compose down

# Fresh restart (careful: deletes data!)
docker compose down -v && make dev
```

---

## Making Changes

### 1. Create a Feature Branch

```bash
# Always start from the latest upstream code
git fetch upstream
git checkout upstream/main
git checkout -b feature/your-feature-name

# Example: 
# git checkout -b feature/improve-scoring-algorithm
# git checkout -b fix/leaderboard-crash
# git checkout -b docs/add-screenshots
```

**Branch Naming:**
- `feature/` — New functionality
- `fix/` — Bug fixes
- `docs/` — Documentation
- `style/` — Code formatting (no logic change)
- `refactor/` — Code restructuring (no feature change)

### 2. Make Your Changes

**Backend** (Django/Python):
```bash
# Edit files in backend/apps/members/, backend/apps/projects/, etc.
# Changes auto-reload in Docker

# Python style guide: PEP 8
# Example: meaningful variable names, docstrings for functions
```

**Frontend** (React/TypeScript):
```bash
# Edit files in frontend/src/
# Changes auto-reload in browser (hot module reload)

# Format with Prettier: 
# npm run format (if available)
```

### 3. Test Your Changes Locally

```bash
# Backend tests
make test

# Manual testing:
# 1. Visit http://localhost:3000 in browser
# 2. Try the feature you added
# 3. Check admin panel for data integrity
```

---

## Testing

### Running Backend Tests

```bash
make test
```

### Manual Testing Checklist

Before submitting a PR:

- [ ] Feature works in browser
- [ ] No console errors (browser DevTools → Console)
- [ ] No Docker errors (check `make logs`)
- [ ] Mobile view works (if UI change)
- [ ] Admin panel shows correct data
- [ ] Sync still works (`make sync`)

---

## Submitting Changes

### Step 1: Commit Your Changes

```bash
# See what changed
git status

# Stage specific files (or use git add .)
git add frontend/src/components/Leaderboard.tsx
git add backend/apps/members/models.py

# Commit with a clear message
git commit -m "feat: add line contribution tracking to leaderboard

- Display additions (green) and deletions (orange)
- Update scoring formula to weight code changes
- Fetch line stats from GitHub PR endpoint"

# Commit message format:
# - First line: type and brief description (50 chars max)
#   Types: feat, fix, docs, style, refactor, test
# - Blank line
# - Body: detailed explanation (optional)
```

### Step 2: Push & Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
# - Target: bhos-sec/showcase (main branch)
# - Source: YOUR_USERNAME/showcase (your feature branch)
```

### Step 3: PR Description Template

```markdown
## Description
Brief explanation of what this PR does.

## Changes
- Added X feature
- Fixed Y bug
- Improved Z performance

## Testing
How did you test this? What should reviewers test?

## Screenshots (if UI change)
[Paste screenshots here]

## Closes
Closes #123 (if fixing an issue)
```

### Step 4: Respond to Feedback

- Reviewers may request changes
- Don't take it personally — all code is reviewed!
- Make the requested changes and push again
- The PR updates automatically

---

## Questions?

- **Stuck on setup?** Check the [README](README.md) or ask in Issues
- **Need help with code?** Open a discussion or ask in PR comments
- **Found a bug?** [Create an issue](https://github.com/bhos-sec/showcase/issues/new)

## Code Style

### Python (Backend)

```python
# ✅ Good
def calculate_member_score(member: Member) -> Decimal:
    """Calculate merit score based on contributions.
    
    Args:
        member: The member to score.
    
    Returns:
        Decimal score value.
    """
    contributions = member.contributions.count()
    return Decimal(contributions) * Decimal("5")

# ❌ Avoid
def calc_score(m):
    # Calculate score
    c = m.contributions.count()
    return Decimal(c) * Decimal("5")
```

### TypeScript (Frontend)

```typescript
// ✅ Good
interface Member {
  id: number;
  name: string;
  score: number;
}

const handleScoreClick = (memberId: number): void => {
  // Handle click
};

// ❌ Avoid
interface member {
  id: number;
  name: string;
  score: number;
}

const handleClick = (id: any) => {
  // Handler
};
```

---

## Helpful Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Git Guide](https://git-scm.com/docs)
- [GitHub Guides](https://guides.github.com/)
- [Contributor Covenant](https://www.contributor-covenant.org/)

---

**Thank you for contributing!** 🙏 Your efforts help make this project better for everyone.
