---
name: devops_infrastructure-as-code
title: Infrastructure as Code (IaC)
description: "Provision and manage cloud infrastructure using Terraform, Ansible, and infrastructure-as-code practices."
tags: [devops, iac, terraform, ansible, cloud, automation, provisioning]
category: devops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Provision and manage cloud infrastructure using Terraform, Ansible, and infrastructure-as-code practices. |
| **Nerede?** | devops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Infrastructure as Code (IaC)

## 🏗️ IaC Stack Seçimi

| Araç | Kullanım | En Uygun Olduğu Durum |
|------|----------|----------------------|
| **Terraform** | Cloud provisioning | AWS/GCP/Azure kaynakları |
| **Ansible** | Configuration management | Server setup, package mgmt |
| **Pulumi** | IaC with real programming | Python/TS ile altyapı |
| **CloudFormation** | AWS native | AWS-only projeler |
| **Docker Compose** | Local dev | Geliştirme ortamları |

## 🌍 Terraform Best Practices

### Modüler Yapı

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── compute/
│   └── database/
└── global/
    ├── iam.tf
    └── route53.tf
```

### Terraform Module Örneği

```hcl
# modules/compute/main.tf
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = {
    Name        = "${var.environment}-app-server"
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = templatefile("${path.module}/scripts/bootstrap.sh", {
    environment = var.environment
    app_version = var.app_version
  })
}
```

### State Management

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-prod"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## 📜 Ansible Playbook

```yaml
---
- name: Configure web server
  hosts: webservers
  become: yes
  vars:
    app_port: 8000
    app_user: deploy

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install required packages
      apt:
        name:
          - nginx
          - python3-pip
          - certbot
          - fail2ban
        state: present

    - name: Deploy application
      copy:
        src: /tmp/build/app.tar.gz
        dest: /opt/app/app.tar.gz
      notify: restart app

    - name: Configure nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/app
      notify: reload nginx

  handlers:
    - name: reload nginx
      systemd:
        name: nginx
        state: reloaded

    - name: restart app
      systemd:
        name: app
        state: restarted
```

## 🔒 Security Best Practices

| Konu | Kural |
|------|-------|
| State dosyası | Asla git'e commit etme, remote backend kullan |
| Secrets | Terraform Vault provider, env vars |
| IAM | Least privilege, resource-level policies |
| Encryption | Terraform state'i encrypt et, S3 bucket policy |
| Audit | All changes via PR, plan review |
| Drift | `terraform plan` ile periyodik kontrol |

## 📋 Checklist

### Terraform
- [ ] `terraform fmt` çalıştır
- [ ] `terraform validate` çalıştır
- [ ] `terraform plan` incele
- [ ] State dosyası remote backend'de
- [ ] Locking mekanizması aktif
- [ ] Output'lar tanımlı
- [ ] Modüller semantic versioned

### Ansible
- [ ] Vault ile şifrelenmiş değişkenler
- [ ] Idempotent playbook'lar
- [ ] Dry-run testi (`--check`)
- [ ] Handlers tanımlı
- [ ] Tag'ler ile parçalı çalıştırma
