import re
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from google.cloud import storage

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "prj-sandbox-presales-portal-b9a1ce61abb0.json"
TEMPLATE_ID = "18f5Mg1wyYWriRnVORaBFy6agxJqtPnz4i9edLFe9xIs"
TARGET_FOLDER_ID = "1aAvRRCZ_unwkt38MZfA-_mraBV-RsZXb"

# GCS Configuration
GCS_BUCKET_NAME = "agent_engine_depoly"  # Update with your bucket name
GCS_OUTPUT_FOLDER = "sow-generator/generated-sows"  # Folder in bucket for generated docs


class DocsTemplateEngine:

    def __init__(self, creds_file):

        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=SCOPES
        )

        self.docs_service = build("docs", "v1", credentials=creds)
        self.drive_service = build("drive", "v3", credentials=creds)
        self.storage_client = storage.Client.from_service_account_json(creds_file)

    # ---------------------------------------
    # Create new Google Doc
    # ---------------------------------------
    def create_document(self, title):

        doc = self.docs_service.documents().create(
            body={"title": title}
        ).execute()

        return doc["documentId"]

    # ---------------------------------------
    # Extract template text
    # ---------------------------------------
    def get_template_text(self, template_id):

        document = self.docs_service.documents().get(
            documentId=template_id
        ).execute()

        text_content = []

        for element in document["body"]["content"]:

            if "paragraph" in element:

                for elem in element["paragraph"]["elements"]:

                    if "textRun" in elem:

                        text_content.append(
                            elem["textRun"]["content"]
                        )

        return "".join(text_content)

    # ---------------------------------------
    # Parse template placeholders << >>
    # ---------------------------------------
    def process_template(self, template_text, data):

        sections = []

        lines = template_text.split("\n")

        pattern = r"<<(.*?)>>"

        for line in lines:

            match = re.findall(pattern, line)

            if not match:
                sections.append(("text", line))
                continue

            key = match[0].strip()

            value = data.get(key, "")

            if isinstance(value, list):
                sections.append(("list", value))
            else:
                sections.append(("text", str(value)))

        return sections

    # ---------------------------------------
    # Build document API requests
    # ---------------------------------------
    def build_requests(self, sections):

        requests = []
        index = 1

        for section_type, content in sections:

            if section_type == "text":

                text = content + "\n"

                requests.append({
                    "insertText": {
                        "location": {"index": index},
                        "text": text
                    }
                })

                index += len(text)

            elif section_type == "list":

                bullet_text = "\n".join(content) + "\n"

                start = index
                end = start + len(bullet_text)

                requests.append({
                    "insertText": {
                        "location": {"index": start},
                        "text": bullet_text
                    }
                })

                requests.append({
                    "createParagraphBullets": {
                        "range": {
                            "startIndex": start,
                            "endIndex": end
                        },
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                })

                index = end

        return requests

    # ---------------------------------------
    # Export Google Doc to DOCX
    # ---------------------------------------
    def export_to_docx(self, document_id):
        """Export Google Doc as DOCX file to memory."""

        request = self.drive_service.files().export_media(
            fileId=document_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%")

        file_stream.seek(0)
        return file_stream

    # ---------------------------------------
    # Upload to Google Cloud Storage
    # ---------------------------------------
    def upload_to_gcs(self, file_stream, filename, bucket_name, folder=""):
        """Upload file stream to Google Cloud Storage."""

        bucket = self.storage_client.bucket(bucket_name)

        # Construct blob path
        blob_path = f"{folder}/{filename}" if folder else filename
        blob = bucket.blob(blob_path)

        # Upload with proper content type
        blob.upload_from_file(
            file_stream,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            rewind=True
        )

        gcs_uri = f"gs://{bucket_name}/{blob_path}"
        public_url = blob.public_url

        return {
            "gcs_uri": gcs_uri,
            "blob_path": blob_path,
            "public_url": public_url
        }

    # ---------------------------------------
    # Delete Google Doc (cleanup)
    # ---------------------------------------
    def delete_document(self, document_id):
        """Delete a Google Doc from Drive."""
        try:
            self.drive_service.files().delete(
                fileId=document_id,
                supportsAllDrives=True
            ).execute()
            print(f"Deleted temporary Google Doc: {document_id}")
        except Exception as e:
            print(f"Warning: Could not delete document {document_id}: {e}")

    # ---------------------------------------
    # List folders and files in root folder
    # ---------------------------------------
    def list_root_contents(self):
        """List all folders and files in the root folder of Google Drive.

        Returns:
            Dictionary with 'folders' and 'files' lists, each containing:
                - id: File/folder ID
                - name: File/folder name
                - mimeType: MIME type
                - createdTime: Creation timestamp
                - modifiedTime: Last modification timestamp
        """
        try:
            # Query for items in root folder
            # 'root' in parents means files/folders directly in the root
            results = self.drive_service.files().list(
                q="'root' in parents and trashed=false",
                fields="files(id, name, mimeType, createdTime, modifiedTime)",
                orderBy="folder,name",
                supportsAllDrives=True
            ).execute()

            items = results.get('files', [])

            # Separate folders and files
            folders = []
            files = []

            folder_mime_type = 'application/vnd.google-apps.folder'

            for item in items:
                if item['mimeType'] == folder_mime_type:
                    folders.append(item)
                else:
                    files.append(item)

            return {
                'folders': folders,
                'files': files,
                'total_count': len(items)
            }

        except Exception as e:
            print(f"Error listing root contents: {e}")
            return {
                'folders': [],
                'files': [],
                'total_count': 0,
                'error': str(e)
            }

    # ---------------------------------------
    # Generate document
    # ---------------------------------------
    def generate(self, template_id, data, title, save_to_gcs=False, bucket_name=None,
                 gcs_folder="", cleanup_gdoc=True):
        """
        Generate a document from template and optionally save to GCS.

        Args:
            template_id: ID of the Google Doc template
            data: Dictionary of placeholder replacements
            title: Title for the generated document
            save_to_gcs: If True, export and upload to GCS
            bucket_name: GCS bucket name (required if save_to_gcs=True)
            gcs_folder: Folder path in GCS bucket
            cleanup_gdoc: If True and save_to_gcs=True, delete the Google Doc after upload

        Returns:
            Dictionary containing:
                - document_id: Google Doc ID
                - document_url: Google Doc URL
                - gcs_uri: GCS URI (if save_to_gcs=True)
                - blob_path: GCS blob path (if save_to_gcs=True)
        """

        # Step 1: Create and populate Google Doc
        template_text = self.get_template_text(template_id)
        sections = self.process_template(template_text, data)
        new_doc_id = self.create_document(title)

        # requests = self.build_requests(sections)

        # self.docs_service.documents().batchUpdate(
        #     documentId=new_doc_id,
        #     body={"requests": requests}
        # ).execute()

        # result = {
        #     "document_id": new_doc_id,
        #     "document_url": f"https://docs.google.com/document/d/{new_doc_id}/edit"
        # }

        # Step 2: Optionally save to GCS
        if save_to_gcs:
            if not bucket_name:
                raise ValueError("bucket_name is required when save_to_gcs=True")

            print(f"\nExporting document to DOCX...")
            docx_stream = self.export_to_docx(new_doc_id)

            print(f"Uploading to GCS bucket: {bucket_name}")
            filename = f"{title}.docx"
            gcs_info = self.upload_to_gcs(docx_stream, filename, bucket_name, gcs_folder)

            result.update(gcs_info)
            print(f"✅ Uploaded to: {gcs_info['gcs_uri']}")

            # Step 3: Optionally cleanup Google Doc
            if cleanup_gdoc:
                print(f"Cleaning up temporary Google Doc...")
                self.delete_document(new_doc_id)
                result["document_deleted"] = True

        return result


# ---------------------------------------
# Example usage
# ---------------------------------------

def main():

    payload = {
        "project_name": "AI SOW Generator",
        "overview": "This system generates Statements of Work using AI.",
        "deliverables": [
            "Architecture design",
            "Implementation",
            "Testing",
            "Deployment"
        ]
    }

    engine = DocsTemplateEngine(SERVICE_ACCOUNT_FILE)

    # List root folder contents
    print("=" * 70)
    print("Listing Root Folder Contents")
    print("=" * 70)

    root_contents = engine.list_root_contents()

    print(f"\nTotal items in root: {root_contents['total_count']}")

    print(f"\nFolders ({len(root_contents['folders'])}):")
    for folder in root_contents['folders']:
        print(f"  - {folder['name']} (ID: {folder['id']})")

    print(f"\nFiles ({len(root_contents['files'])}):")
    for file in root_contents['files']:
        print(f"  - {file['name']} (ID: {file['id']}) - {file['mimeType']}")

    print("\n" + "=" * 70)
    print("Generating SOW Document")
    print("=" * 70)

    # Option 1: Generate Google Doc only
    # result = engine.generate(
    #     TEMPLATE_ID,
    #     payload,
    #     "Generated SOW Document"
    # )

    # Option 2: Generate and save to GCS (recommended)
    result = engine.generate(
        TEMPLATE_ID,
        payload,
        "Generated_SOW_Document",
        save_to_gcs=True,
        bucket_name=GCS_BUCKET_NAME,
        gcs_folder=GCS_OUTPUT_FOLDER,
        cleanup_gdoc=True  # Delete Google Doc after uploading to GCS
    )

    print("\n" + "=" * 70)
    print("Generation Complete")
    print("=" * 70)

    if "document_url" in result:
        print(f"\n📄 Google Doc URL:")
        print(f"   {result['document_url']}")

    if "gcs_uri" in result:
        print(f"\n☁️  GCS Location:")
        print(f"   {result['gcs_uri']}")
        print(f"\n💾 Download command:")
        print(f"   gsutil cp {result['gcs_uri']} ./")

    if result.get("document_deleted"):
        print(f"\n🗑️  Temporary Google Doc was deleted")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # main()
    engine = DocsTemplateEngine(SERVICE_ACCOUNT_FILE)
    print(engine.list_root_contents())