# Lambda GitHub Merge Trigger

Esta Lambda recibe eventos de GitHub mediante un **Webhook** conectado a **API Gateway** y ejecuta una **Step Function** si se detecta un merge a la rama `QA`. Al final del flujo, se puede notificar mediante **SNS** u otros servicios integrados en la Step Function.

---

## Funcionalidad

- Escucha eventos de GitHub (pull request cerrado y mergeado).
- Verifica que el merge sea hacia la rama `qa`.
- Dispara una **Step Function** con un payload que incluye:
  - Repositorio
  - Usuario que hizo el merge
  - Número del Pull Request
  - Rama destino
- Retorna un mensaje JSON indicando si se ejecutó la Step Function o si no se aplicó la acción.

---

## Variables de entorno requeridas

- `STEP_FUNCTION_ARN`: ARN de la Step Function que será ejecutada.

---

## Estructura del proyecto

```text
.
├── handler.py       # Código principal de la Lambda
├── README.md        # Este archivo
└── requirements.txt # Librerías Python necesarias (boto3, etc.)