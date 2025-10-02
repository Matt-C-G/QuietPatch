# CI/CD Integration Examples

## GitHub Actions: Generate Reports as Artifacts

```yaml
name: Generate QuietPatch Reports
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM
  workflow_dispatch:

jobs:
  generate-reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Download qp-report wrapper
        run: |
          curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.py -o qp-report
          chmod +x qp-report
          
      - name: Generate Technical Report
        run: |
          ./qp-report tech \
            --scan data/scan.json \
            --policy data/policy.json \
            --approval data/approval.json \
            --assets data/assets.json \
            --watermark "CI/CD Generated • $(date)" \
            --out reports/tech-report.html \
            --pdf reports/tech-report.pdf
            
      - name: Generate Executive Report
        run: |
          ./qp-report exec \
            --scan data/scan.json \
            --kpi data/kpi.json \
            --business-units data/business_units.json \
            --actions data/actions.json \
            --approval data/approval.json \
            --watermark "CI/CD Generated • $(date)" \
            --out reports/exec-report.html \
            --pdf reports/exec-report.pdf
            
      - name: Upload Reports as Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: quietpatch-reports
          path: reports/
```

## Azure DevOps: PowerShell Pipeline

```yaml
trigger:
  schedules:
    - cron: "0 2 * * 1"
      displayName: Weekly Report Generation
      branches:
        include:
          - main

pool:
  vmImage: 'windows-latest'

steps:
- task: PowerShell@2
  displayName: 'Download qp-report wrapper'
  inputs:
    targetType: 'inline'
    script: |
      Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.ps1" -OutFile "qp-report.ps1"
      
- task: PowerShell@2
  displayName: 'Generate Technical Report'
  inputs:
    targetType: 'inline'
    script: |
      .\qp-report.ps1 tech `
        --scan data\scan.json `
        --policy data\policy.json `
        --approval data\approval.json `
        --assets data\assets.json `
        --watermark "Azure DevOps Generated • $(Get-Date)" `
        --out reports\tech-report.html `
        --pdf reports\tech-report.pdf
        
- task: PowerShell@2
  displayName: 'Generate Executive Report'
  inputs:
    targetType: 'inline'
    script: |
      .\qp-report.ps1 exec `
        --scan data\scan.json `
        --kpi data\kpi.json `
        --business-units data\business_units.json `
        --actions data\actions.json `
        --approval data\approval.json `
        --watermark "Azure DevOps Generated • $(Get-Date)" `
        --out reports\exec-report.html `
        --pdf reports\exec-report.pdf
        
- task: PublishBuildArtifacts@1
  displayName: 'Publish Reports'
  inputs:
    PathtoPublish: 'reports'
    ArtifactName: 'quietpatch-reports'
```

## Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    triggers {
        cron('0 2 * * 1')  // Weekly on Monday at 2 AM
    }
    
    stages {
        stage('Download Wrapper') {
            steps {
                sh 'curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.py -o qp-report'
                sh 'chmod +x qp-report'
            }
        }
        
        stage('Generate Reports') {
            steps {
                sh '''
                    ./qp-report tech \
                      --scan data/scan.json \
                      --policy data/policy.json \
                      --approval data/approval.json \
                      --assets data/assets.json \
                      --watermark "Jenkins Generated • $(date)" \
                      --out reports/tech-report.html \
                      --pdf reports/tech-report.pdf
                      
                    ./qp-report exec \
                      --scan data/scan.json \
                      --kpi data/kpi.json \
                      --business-units data/business_units.json \
                      --actions data/actions.json \
                      --approval data/approval.json \
                      --watermark "Jenkins Generated • $(date)" \
                      --out reports/exec-report.html \
                      --pdf reports/exec-report.pdf
                '''
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/*', fingerprint: true
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'tech-report.html,exec-report.html',
                reportName: 'QuietPatch Reports'
            ])
        }
    }
}
```

## GitLab CI

```yaml
stages:
  - generate-reports

generate-reports:
  stage: generate-reports
  image: python:3.11-slim
  script:
    - curl -fsSL https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/scripts/qp-report.py -o qp-report
    - chmod +x qp-report
    - mkdir -p reports
    - ./qp-report tech --scan data/scan.json --policy data/policy.json --approval data/approval.json --assets data/assets.json --watermark "GitLab CI Generated • $(date)" --out reports/tech-report.html --pdf reports/tech-report.pdf
    - ./qp-report exec --scan data/scan.json --kpi data/kpi.json --business-units data/business_units.json --actions data/actions.json --approval data/approval.json --watermark "GitLab CI Generated • $(date)" --out reports/exec-report.html --pdf reports/exec-report.pdf
  artifacts:
    paths:
      - reports/
    expire_in: 30 days
  only:
    schedules:
      - cron: '0 2 * * 1'
```

## Benefits of CI Integration

- **Automated Reporting**: Generate reports on schedule without manual intervention
- **Artifact Storage**: Reports stored as build artifacts for audit trails
- **Version Control**: Reports linked to specific code versions
- **Distribution**: Easy sharing of reports with stakeholders
- **Compliance**: Automated report generation for audit requirements

## Sample Data for CI

Ensure your CI environment has the required sample data files:
- `data/scan.json` - Scan results
- `data/assets.json` - Asset inventory
- `data/policy.json` - Policy configuration
- `data/approval.json` - Change approval
- `data/kpi.json` - Executive KPIs
- `data/business_units.json` - Business unit breakdown
- `data/actions.json` - Action items
