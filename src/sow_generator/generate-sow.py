import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "service_account.json"
TEMPLATE_DOC_ID = "18f5Mg1wyYWriRnVORaBFy6agxJqtPnz4i9edLFe9xIs"
TARGET_FOLDER_ID = "1aAvRRCZ_unwkt38MZfA-_mraBV-RsZXb"

class GoogleDocsGenerator:

    def __init__(self, credentials_file):
        creds = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=SCOPES
        )

        self.docs_service = build("docs", "v1", credentials=creds)
        self.drive_service = build("drive", "v3", credentials=creds)

    # ------------------------------------------------------
    # Copy template
    # ------------------------------------------------------
    def copy_template(self, template_id, output_name):

        body = {"name": output_name, "parents": ["TARGET_FOLDER_ID"]}

        copied_file = self.drive_service.files().copy(
            fileId=template_id,
            body=body,
            supportsAllDrives=True
        ).execute()

        return copied_file["id"]

    # ------------------------------------------------------
    # Replace simple placeholders
    # ------------------------------------------------------
    def replace_text_placeholders(self, document_id, replacements):

        requests = []

        for key, value in replacements.items():

            if isinstance(value, list):
                continue

            requests.append({
                "replaceAllText": {
                    "containsText": {
                        "text": f"<<{key}>>",
                        "matchCase": True
                    },
                    "replaceText": value
                }
            })

        if requests:
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={"requests": requests}
            ).execute()

    # ------------------------------------------------------
    # Handle list placeholders
    # ------------------------------------------------------
    def replace_list_placeholder(self, document_id, key, items):

        placeholder = f"<<{key}>>"

        document = self.docs_service.documents().get(
            documentId=document_id
        ).execute()

        content = document.get("body").get("content")

        start_index = None
        end_index = None

        for element in content:

            if "paragraph" not in element:
                continue

            for elem in element["paragraph"]["elements"]:

                text = elem.get("textRun", {}).get("content")

                if text and placeholder in text:

                    start_index = elem["startIndex"]
                    end_index = elem["endIndex"]

                    break

        if start_index is None:
            return

        bullet_text = "\n".join(items)

        requests = [

            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": start_index,
                        "endIndex": end_index
                    }
                }
            },

            {
                "insertText": {
                    "location": {"index": start_index},
                    "text": bullet_text
                }
            },

            {
                "createParagraphBullets": {
                    "range": {
                        "startIndex": start_index,
                        "endIndex": start_index + len(bullet_text)
                    },
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            }
        ]

        self.docs_service.documents().batchUpdate(
            documentId=document_id,
            body={"requests": requests}
        ).execute()

    # ------------------------------------------------------
    # Main document generation
    # ------------------------------------------------------
    def generate_document(self, template_id, data, output_name):

        document_id = self.copy_template(template_id, output_name)

        self.replace_text_placeholders(document_id, data)

        for key, value in data.items():

            if isinstance(value, list):
                self.replace_list_placeholder(document_id, key, value)

        return document_id


# ------------------------------------------------------
# Example Usage
# ------------------------------------------------------

def main():

    payload = {
        "project_name": "AI SOW Generator",
        "overview": "This solution generates Statements of Work using AI.",
        "deliverables": [
            "Architecture design",
            "Implementation",
            "Testing",
            "Deployment"
        ]
    }

    generator = GoogleDocsGenerator(SERVICE_ACCOUNT_FILE)

    document_id = generator.generate_document(
        TEMPLATE_DOC_ID,
        payload,
        "Generated SOW Document"
    )

    print("Generated Document ID:", document_id)
    print("URL: https://docs.google.com/document/d/" + document_id)


if __name__ == "__main__":
    main()
