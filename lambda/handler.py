import json
import boto3
import os

STEP_FUNCTION_ARN = os.environ.get("STEP_FUNCTION_ARN")
TARGET_BRANCH = "qa"

client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    """
    Lambda principal que recibe el evento de GitHub.
    - Verifica que sea un merge a la rama QA
    - Lanza la Step Function
    """

    # GitHub envía el payload como JSON en body si es API Gateway
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid payload", "error": str(e)})
        }

    # Validar que el evento sea un merge
    ref = body.get("ref")  # La rama del merge
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
            "body": json.dumps({"message": f"No se ejecuta Step Function. Merge no en {TARGET_BRANCH} o PR no cerrado/mergeado."})
        }
