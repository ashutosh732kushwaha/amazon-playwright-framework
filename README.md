# Amazon Playwright Enterprise Automation Framework

A production-oriented Python + Playwright Sync API framework for Amazon UI and lightweight API verification. The framework is deliberately bot-aware: live Amazon pages may display bot challenges, and such journeys are skipped as expected rather than reported as selector failures.

## Architecture

```text
config/       Typed Pydantic settings and regional environment overlays
pages/        Page Object Model; shared browser actions live in BasePage
tests/        Pytest fixtures and smoke/regression suites
test_data/    External JSON datasets and dynamic Faker factories
utils/        Logging, HTTP helpers, and domain exceptions
reports/      Screenshots, videos, traces, HTML and Allure output
```

- **BasePage:** All browser operations use Playwright locators and web-first assertions. CSS/XPath are fallback selectors; role, label, placeholder, and test-id locators are preferred in page objects.
- **Page Object Model:** Each Amazon surface encapsulates its own locators and actions.
- **Dependency Injection:** Pytest injects `page`, typed settings, API helper, and browser configuration.
- **Factory pattern:** Page methods return the next page object, creating a navigable and readable journey.
- **Bot resilience:** HomePage detects the Continue shopping/CAPTCHA interstitial and raises a domain exception; smoke tests convert this to a clean skip.

## Setup

```powershell
cd amazon-playwright-framework
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
```

## Run

```powershell
pytest tests/smoke/test_amazon_smoke.py
pytest tests/regression -n 2 --reruns 1
pytest --collect-only
pytest --base-url=https://www.amazon.in --environment=india
pytest --headed --browser-name=chromium
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
pytest --html=reports/report.html --self-contained-html
```

Install Allure command-line software separately to run `allure serve`.

## Configuration

Precedence is CLI options, then environment variables, then `environments.yaml`, then Pydantic defaults. Copy `.env.example` to `.env` and set `AMAZON_ENV=india` to target `amazon.in`, or pass `--base-url`.

## Observability

Failure hooks capture a full-page PNG, Playwright trace ZIP, and webm video and attach all three to Allure. Rotating Loguru logs are stored in `reports/logs/framework.log`. Trace, screenshot, and video retention are retained for failed tests.

## CI/CD

GitHub Actions installs Chromium, runs tests with xdist and reruns, and uploads Allure/HTML artifacts. The live Amazon environment can challenge automated traffic, so tests intentionally detect interstitial/CAPTCHA states and skip rather than produce misleading selector failures.

## Jenkins CI/CD Integration

The root [Jenkinsfile](./Jenkinsfile) provides a parameterized CI pipeline for this test framework. It checks out source, builds a clean `.venv`, installs the pinned Python dependencies and selected Playwright browser, checks Python syntax and test collection, runs the selected test suite in parallel, and publishes test reports and failure artifacts. It does not deploy an application: this repository is a test automation project, so the pipeline currently validates code and exercises the configured target.

### Jenkins prerequisites

Install these plugins on the Jenkins controller:

- **Pipeline** (including Declarative Pipeline): runs the `Jenkinsfile`.
- **Git**: checks out the project from SCM.
- **Allure Jenkins Plugin**: publishes the Allure results as a Jenkins report.
- **HTML Publisher**: makes the self-contained pytest HTML report browsable from the build.
- **Workspace Cleanup**: removes the workspace after reports and artifacts are published.

Use an agent with Python 3.10+ and Git. Linux agents are recommended: the pipeline runs `playwright install --with-deps` to provision the browser and OS dependencies. Windows agents are supported with PowerShell, but must already have the browser's OS dependencies installed; install just the browser binary there. The agent must be allowed to access the configured test site and package/browser download endpoints.

### Create a Pipeline job from GitHub SCM

1. Push this project to a GitHub repository that the Jenkins agent can read. The profile/projects URL is not itself a Git repository URL.
2. In Jenkins, select **New Item**, give the job a name, choose **Pipeline**, and select **OK**.
3. Under **Build Triggers**, configure the GitHub webhook or polling policy used by your Jenkins installation.
4. Under **Pipeline**, set **Definition** to **Pipeline script from SCM**, select **Git**, enter the repository clone URL, and configure the branch (for example `*/main`).
5. Add a Jenkins credential if the repository is private; select it in the SCM configuration. Do not put access tokens in the `Jenkinsfile` or repository.
6. Set **Script Path** to `Jenkinsfile`, save, and choose **Build with Parameters**. Ensure the Allure, HTML Publisher, and Workspace Cleanup plugins are installed before the first run.

### Build parameters and execution

| Parameter | Choices/default | How the pipeline uses it |
|---|---|---|
| `ENV` | `prod` (default), `stage`, `qa` | Maps to `production`, `staging`, and `qa` in `config/environments.yaml`. The pipeline validates that the selected profile exists rather than silently testing a different target. This repository currently defines `production`, `staging`, and `india`; add a real `qa` profile and URL before selecting `qa`. |
| `BROWSER` | `chromium` (default), `firefox`, `webkit` | Installs the browser and passes it both to pytest-playwright (`--browser`) and this framework's settings fixture (`--browser-name`). |
| `TEST_SUITE` | `smoke` (default), `regression`, `all` | Runs `pytest -m smoke`, `pytest -m regression`, or pytest without a marker filter for `all`. |
| `WORKERS` | `2` | Must be a positive integer; passed to `pytest-xdist` as `-n`. Independent workers reduce elapsed time, but tests must avoid shared mutable state and should not overload the target site. |
| `HEADLESS` | `true` | Headless is the default. When false, pytest receives `--headed`; the agent then needs a display server or equivalent browser UI support. |

Pip uses its normal per-agent cache, so reusable Jenkins agents can avoid repeatedly downloading wheels. Each build creates a fresh virtual environment to keep project dependencies isolated and reproducible. The quality stage uses `compileall` and `pytest --collect-only` rather than an unpinned linter dependency; these catch syntax, import, and test discovery errors before browser execution.

### Reports, failures, and artifacts

Pytest writes Allure results to `reports/allure-results` and the self-contained HTML report to `reports/report.html`. The existing pytest hooks record failure screenshots, Playwright `.zip` traces, and videos under `reports/`; the `post` section publishes Allure, publishes HTML, and archives `reports/**` even when tests fail. `catchError` marks a failed test stage/build while allowing those reporting steps to run. The workspace is cleaned only after publishing and archiving.

If report publication is configured as a required release gate, verify the plugin setup on a sample build: a missing report publisher should be treated as a Jenkins configuration problem, not as a passing test result. Slack/email steps are intentionally placeholders; wire one up using a Jenkins-managed credential if notifications are required.

### Interview walkthrough: why these choices

1. **Checkout and environment info** establish exactly which commit ran and show the Python/Git versions in the console.
2. **A per-build virtual environment** isolates Python dependencies; pinned requirements improve repeatability. The agent-level pip cache speeds installs without reusing project interpreter state.
3. **Browser provisioning** uses Playwright's own installer so browser versions match the pinned Playwright package. On Linux, `--with-deps` also installs OS libraries; on Windows, those libraries are agent prerequisites.
4. **Compile and collection checks** fail quickly before expensive browser tests if syntax, imports, or pytest discovery are broken.
5. **Parameterized xdist tests** let a developer focus on smoke checks or run the broader regression set, choose a supported browser/target, and tune parallelism. Parallelism trades speed for agent/target load and needs isolated test data.
6. **Failure diagnostics** turn a red build into an actionable one: Allure gives test-level context, HTML is convenient for quick browsing, and raw screenshots/traces/videos let an engineer replay or inspect the browser state.
7. **Post-build cleanup** keeps long-lived agents healthy without deleting evidence before it has been published.

Live Amazon pages can challenge automation, so this framework intentionally skips detected bot challenges. A skip is an environmental limitation, not proof that the business flow passed. Configure `stage`/`qa` only with authorized, dedicated test targets; the current `staging` sample profile still points to a public Amazon URL and is not a private staging service. Also, the `qa` profile is not yet defined, and its parameter is intentionally rejected until a real URL is configured.

For detailed framework method/tool rationale beyond Jenkins, see [Architecture](./docs/ARCHITECTURE.md) and the [Method and Tool Reference](./docs/METHOD_REFERENCE.md).
