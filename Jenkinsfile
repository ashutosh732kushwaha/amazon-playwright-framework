pipeline {
    // Linux agents are the recommended default because Playwright can install
    // operating-system dependencies with --with-deps. Windows agents are also
    // supported below, but must have the browser's OS dependencies preinstalled.
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        timeout(time: 45, unit: 'MINUTES')
    }

    parameters {
        choice(name: 'ENV', choices: ['prod', 'stage', 'qa'], description: 'Target configuration profile')
        choice(name: 'BROWSER', choices: ['chromium', 'firefox', 'webkit'], description: 'Playwright browser')
        choice(name: 'TEST_SUITE', choices: ['smoke', 'regression', 'all'], description: 'Pytest marker selection')
        string(name: 'WORKERS', defaultValue: '2', trim: true, description: 'Number of pytest-xdist workers (positive integer)')
        booleanParam(name: 'HEADLESS', defaultValue: true, description: 'Run the browser without a visible window')
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout & Environment Info') {
            steps {
                script {
                    if (!(params.WORKERS ==~ /[1-9][0-9]*/)) {
                        error('WORKERS must be a positive integer.')
                    }

                    // Match Jenkins-facing names to the profiles currently
                    // defined in config/environments.yaml. QA must be added
                    // there before it can be selected.
                    env.CONFIG_ENV = [
                        prod: 'production',
                        stage: 'staging',
                        qa: 'qa'
                    ][params.ENV]

                    deleteDir()
                    checkout scm

                    if (isUnix()) {
                        sh '''
                            set -eu
                            python3 --version
                            git rev-parse --short HEAD
                            git log -1 --format="Commit: %h%nAuthor: %an%nDate: %cs%nSubject: %s"
                        '''
                    } else {
                        powershell '''
                            $ErrorActionPreference = 'Stop'
                            python --version
                            git rev-parse --short HEAD
                            git log -1 --format="Commit: %h%nAuthor: %an%nDate: %cs%nSubject: %s"
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        '''
                    }
                }
            }
        }

        stage('Install Dependencies & Browsers') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            python3 -m venv .venv
                            . .venv/bin/activate
                            .venv/bin/python -m pip install --upgrade pip
                            .venv/bin/python -m pip install -r requirements.txt
                            .venv/bin/python -m playwright install --with-deps "$BROWSER"
                            .venv/bin/python -m playwright --version
                        '''
                    } else {
                        // PowerShell venv activation is process-local, so invoke
                        // the venv interpreter directly in every stage instead.
                        powershell '''
                            $ErrorActionPreference = 'Stop'
                            py -3 -m venv .venv
                            Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
                            & .\.venv\Scripts\Activate.ps1
                            $python = Join-Path $PWD '.venv\Scripts\python.exe'
                            & $python -m pip install --upgrade pip
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                            & $python -m pip install -r requirements.txt
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                            & $python -m playwright install $env:BROWSER
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                            & $python -m playwright --version
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        '''
                    }
                }
            }
        }

        stage('Code Quality & Collection') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -eu
                            .venv/bin/python -c "import os, yaml; profiles = yaml.safe_load(open('config/environments.yaml', encoding='utf-8')) or {}; key = os.environ['CONFIG_ENV']; assert key in profiles, 'No config/environments.yaml profile named ' + key + '; add the target URL before running this environment'; print('Validated environment profile:', key)"
                            .venv/bin/python -m compileall -q config pages tests utils
                            .venv/bin/python -m pytest --collect-only -q
                        '''
                    } else {
                        powershell '''
                            $ErrorActionPreference = 'Stop'
                            $python = Join-Path $PWD '.venv\Scripts\python.exe'
                            & $python -c "import os, yaml; profiles = yaml.safe_load(open('config/environments.yaml', encoding='utf-8')) or {}; key = os.environ['CONFIG_ENV']; assert key in profiles, 'No config/environments.yaml profile named ' + key + '; add the target URL before running this environment'; print('Validated environment profile:', key)"
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                            & $python -m compileall -q config pages tests utils
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                            & $python -m pytest --collect-only -q
                            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                        '''
                    }
                }
            }
        }

        stage('Run Playwright Tests') {
            steps {
                script {
                    def suiteMarker = params.TEST_SUITE == 'all' ? '' : "-m ${params.TEST_SUITE}"
                    def headedOption = params.HEADLESS ? '' : '--headed'

                    if (isUnix()) {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            sh """
                                set -eu
                                mkdir -p reports/allure-results
                                .venv/bin/python -m pytest ${suiteMarker} \\
                                    --browser="${params.BROWSER}" \\
                                    --browser-name="${params.BROWSER}" \\
                                    -n "${params.WORKERS}" \\
                                    --environment="${env.CONFIG_ENV}" \\
                                    ${headedOption} \\
                                    --alluredir=reports/allure-results \\
                                    --html=reports/report.html --self-contained-html
                            """
                        }
                    } else {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            powershell """
                                \$ErrorActionPreference = 'Stop'
                                New-Item -ItemType Directory -Force -Path 'reports\\allure-results' | Out-Null
                                \$python = Join-Path \$PWD '.venv\\Scripts\\python.exe'
                                & \$python -m pytest ${suiteMarker} `
                                    --browser="${params.BROWSER}" `
                                    --browser-name="${params.BROWSER}" `
                                    -n "${params.WORKERS}" `
                                    --environment="${env.CONFIG_ENV}" `
                                    ${headedOption} `
                                    --alluredir=reports/allure-results `
                                    --html=reports/report.html --self-contained-html
                                if (\$LASTEXITCODE -ne 0) { exit \$LASTEXITCODE }
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // These publishers run even after test failures. Install the
            // Allure, HTML Publisher, and Workspace Cleanup plugins in Jenkins.
            allure([includeProperties: false, jdk: '', results: [[path: 'reports/allure-results']]])
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Pytest HTML Report'
            ])
            archiveArtifacts(artifacts: 'reports/**', allowEmptyArchive: true, fingerprint: true)
        }
        success {
            echo "SUCCESS: ${params.TEST_SUITE} suite passed on ${params.BROWSER} (${params.ENV})."
            // Notification integration placeholder: configure Slack or email
            // credentials and replace this message with the chosen plugin step.
        }
        failure {
            echo "FAILURE: inspect the Allure/HTML reports and archived traces, screenshots, and videos."
            // Notification integration placeholder for Slack or email.
        }
        cleanup {
            cleanWs()
        }
    }
}
