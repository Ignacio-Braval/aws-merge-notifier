import json
import boto3
import os
import hmac
import hashlib

# Variables de entorno
STEP_FUNCTION_ARN = os.environ.get("STEP_FUNCTION_ARN")
TARGET_BRANCH = "qa"
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")

# Cliente Step Functions
client = boto3.client('stepfunctions')


def verify_github_signature(event):
    """
    Verifica que la petición provenga realmente de GitHub usando el secreto.
    """
    signature = event['headers'].get('X-Hub-Signature-256')
    if signature is None:
        return False

    sha_name, signature = signature.split('=')
    mac = hmac.new(
        bytes(GITHUB_WEBHOOK_SECRET, 'utf-8'),
        msg=event['body'].encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return hmac.compare_digest(mac.hexdigest(), signature)


def lambda_handler(event, context):
    """
    Lambda principal que recibe el evento de GitHub.
    - Verifica la firma con el secreto
    - Verifica que sea un merge a la rama QA
    - Lanza la Step Function
    """

    # Validar el secreto de GitHub
    if not verify_github_signature(event):
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'Invalid signature'})
        }

    # Parsear el payload enviado por GitHub
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid payload", "error": str(e)})
        }

    # Validar que el evento sea un merge cerrado a TARGET_BRANCH
    ref = body.get("ref")  # Rama de destino del merge
    action = body.get("action")  # 'closed' para PR cerrado
    merged = body.get("pull_request", {}).get("merged", False)

    if action == "closed" and merged and ref.endswith(TARGET_BRANCH):
        # Ejecutar Step Function
        input_payload = {
            "repository": body.get("repository", {}).get("full_name"),
            "merged_by": body.get("pull_request", {}).get("user", {}).get("login"),
            "branch": ref,
            "pull_request_id": body.get("pull_request", {}).get("number")
        }

        try:
            response = client.start_execution(
                stateMachineArn=STEP_FUNCTION_ARN,
                input=json.dumps(input_payload)
            )
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"Merge en {TARGET_BRANCH} detectado. Step Function ejecutada.",
                    "executionArn": response['executionArn']
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Error al iniciar Step Function", "error": str(e)})
            }

    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"No se ejecuta Step Function. Merge no en {TARGET_BRANCH} o PR no cerrado/mergeado."
            })
        }
