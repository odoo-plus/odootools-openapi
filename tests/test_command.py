import yaml
from mock import patch, MagicMock
from odootools_openapi.command import get_document, openapi


def test_get_document_path(basic_document, simple_routes, tmp_path):
    document = {}
    document.update(basic_document)
    document.update(simple_routes)

    document_file = tmp_path / 'document.yaml'
    with document_file.open('w') as fout:
        fout.write(yaml.safe_dump(document))

    doc = get_document(url=None, path=document_file)

    assert doc == document


def test_get_document_url(basic_document, simple_routes, tmp_path):
    document = {}
    document.update(basic_document)
    document.update(simple_routes)

    document_file = tmp_path / 'document.yaml'
    doc_txt = yaml.safe_dump(document)
    with document_file.open('w') as fout:
        fout.write(doc_txt)

    with patch('odootools_openapi.command.requests') as req:
        response = MagicMock()
        response.content = doc_txt
        req.get = lambda url: response

        doc = get_document(url="some_url", path=None)

    assert doc == document


def test_openapi_command(runner, tmp_path, simple_openapi):
    result = runner.invoke(openapi, '--help')
    assert result.exit_code == 0

    (document_file, document, doc_txt) = simple_openapi

    destination = tmp_path / 'build'

    result = runner.invoke(openapi, [
        '--path', str(document_file),
        '--destination', str(destination),
    ])

    assert result.exit_code == 0

    assert destination.exists() and destination.is_dir()

    controllers_folder = destination / 'controllers'

    assert (controllers_folder / '__init__.py').exists()
    assert (controllers_folder / 'default.py').exists()
    assert (destination / '__init__.py').exists()
    assert (destination / '__manifest__.py').exists()
