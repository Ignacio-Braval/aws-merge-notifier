# 🚀 AWS Merge Notifier – Serverless GitHub Webhook

Proyecto **serverless en AWS** que detecta **merges exitosos hacia la rama `qa` en GitHub** y ejecuta un flujo automatizado mediante **AWS Step Functions** para notificación y futuras acciones (deploy, Slack, approvals, etc.).

---

## 🧠 ¿Qué problema resuelve?

En equipos de desarrollo es crítico saber **cuándo, quién y hacia dónde** se mergea código, especialmente en ramas sensibles como `qa` o `main`.

Este proyecto:
- Escucha eventos reales de GitHub (webhooks)
- Valida seguridad mediante **firmas HMAC**
- Ejecuta flujos **100% serverless**
- Está definido completamente como **Infrastructure as Code**

---

## 🏗️ Arquitectura

**GitHub**
➡️
**Webhook(HMAC)**
➡️
**API Gateway**
➡️
**AWS Lambda(Python)**
➡️
**AWS Step Functions**
➡️
**SNS**
➡️
**(Email / extensible a Slack, Deploy, etc.)**

---

## 🔐 Seguridad

- Validación de firma `X-Hub-Signature-256`
- Webhook protegido con **secret compartido**
- Variables sensibles gestionadas como **Environment Variables**
- IAM con principio de **menor privilegio**
- Logs centralizados en CloudWatch

---

## ⚙️ Stack Tecnológico

- **AWS Lambda** (Python 3.11)
- **Amazon API Gateway**
- **AWS Step Functions**
- **Amazon SNS**
- **AWS SAM**
- **GitHub Webhooks**
- **CloudWatch Logs**

---

## 📁 Estructura del repositorio

* aws-merge-notifier/


   * infrastructure/

     *  stepfunctions.json # Definición del flujo Step Functions
     *  template.yaml # Infraestructura SAM (IaC)
  *  lambda/

     *  handler.py # Lógica principal del webhook
     *  requirements.txt
     *  README.md # Detalles de la Lambda


 * README.md # Documentación principal

---

## 🚦 Flujo de ejecución

1. Se crea un Pull Request hacia la rama `qa`
2. El PR es **mergeado**
3. GitHub envía un webhook firmado
4. API Gateway recibe el evento
5. Lambda valida:
   - Firma HMAC
   - Evento `pull_request`
   - PR cerrado y mergeado
   - Rama objetivo = `qa`
6. Se ejecuta una **Step Function**
7. SNS envía la notificación del merge

---

## 🧪 Pruebas

- Pruebas locales simulando firma HMAC
- Logs detallados en CloudWatch
- Validación desde GitHub Webhook UI (`Recent deliveries`)
- Manejo de errores y payload inválido

---

## 🚀 Deploy

El proyecto utiliza **AWS SAM**.

```bash
sam build
sam deploy --guided