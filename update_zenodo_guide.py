import requests
import json

access_token = 'ICoznc9omFAFLgYepuNCybKbZ5WP22HCdsTL6gTqw27SmR7a4fKuNALmDLv9'
baseUrl = 'https://sandbox.zenodo.org'
conceptDOI = '10.5072/zenodo.351033'  # Concept DOI of published guide
filename = 'book.pdf'


def getDeposition():
    '''Find the deposition corresponding to our concept DOI'''
    url = '{base_url}/api/deposit/depositions'.format(base_url=baseUrl)
    resp = requests.get(url, params={'doi': conceptDOI,
                                    'access_token': access_token})
    depositions = resp.json()

    assert resp.status_code==200, 'Failed to fetch deposition for concept DOI'
    assert len(depositions) == 1, 'Multiple submissions with same concept DOI -- something seems wrong...'

    deposition = depositions[0]
    return deposition


def newVersion(deposition):
    '''Generate a new version of the deposition'''
    url = '{base_url}/api/deposit/depositions/{id}/actions/newversion'.format(
        base_url=baseUrl, id=str(deposition['id']))
    resp = requests.post(url, params={'access_token': access_token})
    assert resp.status_code==201, 'Failed to create new version of deposition'
    return resp.json()


def updateMetadata(newVersionId):
    url = '{base_url}/api/deposit/depositions/{id}'.format(
        base_url=baseUrl, id=str(newVersionId))
    metadata = json.load(open('.zenodo.json', 'r'))
    # metadata not included in CFF format
    metadata['upload_type'] = 'publication'
    metadata['publication_type'] = 'book'
    data = { 'metadata': metadata }
    headers = { 'Content-Type': 'application/json' }
    resp = requests.put(url, data=json.dumps(data), headers=headers, params={'access_token': access_token})
    assert resp.status_code==200, 'Failed to update metadata'

def getFiles(deposition):
    '''List all files associated with our deposition'''
    url = '{base_url}/api/deposit/depositions/{id}/files'.format(
        base_url=baseUrl, id=str(deposition['id']))
    resp = requests.get(url, params={'access_token': access_token})
    assert resp.status_code==200, 'Failed to retrieve associated files'
    return resp.json()


def getNewVersionId(newVersion):
    url = '{base_url}/api/deposit/depositions/'.format(base_url=baseUrl)
    return newVersion['links']['latest_draft'].replace(url, '')


def deleteBook(newVersionId, files):
    '''Delete the book file before we can add a new file to the new deposition'''
    # deposition should be a 'newVersion'
    nameToId = {file['filename']: file['id'] for file in files}
    if filename in nameToId:
        bookId = nameToId[filename]
        url = '{base_url}/api/deposit/depositions/{id}/files/{file_id}'.format(
            base_url=baseUrl, id=newVersionId, file_id=bookId)
        resp = requests.delete(url, params={'access_token': access_token})
        assert resp.status_code==204, 'Failed to delete file'


def uploadBook(newVersionId):
    '''Upload a new file for the new deposition'''
    url = '{base_url}/api/deposit/depositions/{id}/files'.format(
        base_url=baseUrl, id=newVersionId, token=access_token)
    upload_metadata = {'filename': filename}
    files = {'file': open(filename, 'rb')}
    resp = requests.post(url, data=upload_metadata, files=files, params={
                             'access_token': access_token})
    assert resp.status_code==201, 'Failed to upload file'


def publish(newVersionId):
    '''Publish the new deposition'''
    url = '{base_url}/api/deposit/depositions/{id}/actions/publish'.format(
        base_url=baseUrl, id=newVersionId)
    resp = requests.post(url, params={'access_token': access_token})
    assert resp.status_code==202, 'Failed to publish new deposition'


if __name__ == '__main__':
    deposition = getDeposition()
    newVersion = newVersion(deposition)
    newVersionId = getNewVersionId(newVersion)
    updateMetadata(newVersionId)
    files = getFiles(newVersion)
    deleteBook(newVersionId, files)
    uploadBook(newVersionId)
    publish(newVersionId)
