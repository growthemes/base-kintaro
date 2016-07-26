from googleapiclient import discovery
from googleapiclient import errors
from grow.common import oauth
from grow.common import utils
from protorpc import messages
import logging
import grow
import httplib2


STORAGE_KEY = 'Grow SDK - Kintaro'
KINTARO_HOST = 'https://kintaro-content-server-qa.appspot.com'
KINTARO_API_ROOT = '{host}/_ah/api'.format(host=KINTARO_HOST)
DISCOVERY_URL = (
    KINTARO_API_ROOT + '/discovery/v1/apis/{api}/{apiVersion}/rest')
KINTARO_EDIT_PATH_FORMAT = (
    '{host}'
    '/app#/project/{project}'
    '/repo/{repo}'
    '/collection/{collection}'
    '/document/{document}/edit')


# Silence extra logging from googleapiclient.
discovery.logger.setLevel(logging.WARNING)


OAUTH_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'


class BindingMessage(messages.Message):
    collection = messages.StringField(1)
    kintaro_collection = messages.StringField(2)


class KintaroPreprocessor(grow.Preprocessor):
    KIND = 'kintaro'

    class Config(messages.Message):
        bind = messages.MessageField(BindingMessage, 1, repeated=True)
        repo = messages.StringField(2)
        project = messages.StringField(3)

    @staticmethod
    def create_service():
        credentials = oauth.get_or_create_credentials(
            scope=OAUTH_SCOPE, storage_key=STORAGE_KEY)
        http = httplib2.Http(ca_certs=utils.get_cacerts_path())
        http = credentials.authorize(http)
        credentials.refresh(http)
        return discovery.build(
            'content', 'v1', http=http,
            discoveryServiceUrl=DISCOVERY_URL)

    def bind_collection(self, entries, collection_pod_path):
        collection = self.pod.get_collection(collection_pod_path)
        existing_pod_paths = [
            doc.pod_path
            for doc in collection.docs(recursive=False, inject=False)]
        new_pod_paths = []
        for i, entry in enumerate(entries):
            fields, unused_body, basename = self._parse_entry(entry)
            doc = collection.create_doc(basename, fields=fields, body='')
            new_pod_paths.append(doc.pod_path)
            self.pod.logger.info('Saved -> {}'.format(doc.pod_path))
        pod_paths_to_delete = set(existing_pod_paths) - set(new_pod_paths)
        for pod_path in pod_paths_to_delete:
            self.pod.delete_file(pod_path)
            self.pod.logger.info('Deleted -> {}'.format(pod_path))

    def _parse_entry(self, entry):
        basename = '{}.yaml'.format(entry['document_id'])
        fields = {}
        for field in entry['content'].get('fields', []):
            name = field['field_name']
            if field.get('field_values'):
                value = field['field_values'][0]['value']
                fields[name] = value
        if 'title' in fields:
            fields['$title'] = fields.pop('title')
        body = ''
        return fields, body, basename

    def run(self, *args, **kwargs):
      for binding in self.config.bind:
          collection_pod_path = binding.collection
          kintaro_collection = binding.kintaro_collection
          entries = self.download_entries(
              repo_id=self.config.repo,
              collection_id=kintaro_collection,
              project_id=self.config.project)
          self.bind_collection(entries, collection_pod_path)

    def download_entries(self, repo_id, collection_id, project_id):
        service = KintaroPreprocessor.create_service()
        resp = service.documents().listDocuments(
            repo_id=repo_id,
            collection_id=collection_id,
            project_id=project_id).execute()
        return resp.get('documents', [])

    def download_entry(self, document_id, collection_id, repo_id, project_id):
        service = KintaroPreprocessor.create_service()
        resp = service.documents().getDocument(
            document_id=document_id,
            collection_id=collection_id,
            project_id=project_id,
            repo_id=repo_id).execute()
        return resp

    def get_edit_url(self, doc=None):
        kintaro_collection = ''
        kintaro_document = doc.base
        for binding in self.config.bind:
            if binding.collection == doc.collection.pod_path:
                kintaro_collection = binding.kintaro_collection
        return KINTARO_EDIT_PATH_FORMAT.format(
              host=KINTARO_HOST,
              project=self.config.project,
              repo=self.config.repo,
              collection=kintaro_collection,
              document=kintaro_document)

    def can_inject(self, doc=None, collection=None):
        if not self.injected:
            return False
        for binding in self.config.bind:
            if binding.collection == doc.collection.pod_path:
                return True
        return False

    def inject(self, doc=None, collection=None):
        document_id = doc.base
        for binding in self.config.bind:
            if binding.collection == doc.collection.pod_path:
                entry = self.download_entry(
                    document_id=document_id,
                    collection_id=binding.kintaro_collection,
                    repo_id=self.config.repo,
                    project_id=self.config.project)
                fields, body, basename = self._parse_entry(entry)
                doc.inject(fields, body='')
                return doc